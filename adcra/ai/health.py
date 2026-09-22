"""
ADCRA AI Intelligence Control Plane — Provider Health Monitor & Circuit Breakers
Tracks real-time provider availability, latency percentiles (P50/P90/P95), error rates,
and enforces circuit breakers across providers, models, and capabilities.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional
import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger("adcra.ai.health")


class HealthStatus(str, enum.Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class CircuitState(str, enum.Enum):
    CLOSED = "CLOSED"        # Normal operation: requests pass through
    OPEN = "OPEN"            # Tripped: requests are blocked and routed to fallback
    HALF_OPEN = "HALF_OPEN"  # Recovery testing: probing if provider recovered


@dataclass
class CircuitBreaker:
    target_id: str
    failure_threshold: int = 3
    cooldown_seconds: float = 30.0
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    last_state_change: float = field(default_factory=time.time)

    def record_success(self) -> None:
        self.consecutive_failures = 0
        if self.state != CircuitState.CLOSED:
            logger.info(f"Circuit breaker for '{self.target_id}' transitioned to CLOSED (recovered)")
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()

    def record_failure(self, error_msg: Optional[str] = None) -> None:
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.failure_threshold and self.state != CircuitState.OPEN:
            logger.warning(
                f"Circuit breaker tripped to OPEN for '{self.target_id}' "
                f"({self.consecutive_failures} failures). Reason: {error_msg or 'unknown'}"
            )
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            # Check if cooldown has elapsed to allow a probe
            if (time.time() - self.last_state_change) > self.cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.time()
                logger.info(f"Circuit breaker for '{self.target_id}' transitioned to HALF_OPEN (probing)")
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return True
        return False


class ProviderHealthMonitor:
    """
    Monitorea la salud, latencias y tasas de error de proveedores y modelos en runtime.
    Gestiona disyuntores (Circuit Breakers) y calcula percentiles de latencia P50/P90/P95.
    """
    def __init__(self):
        self._circuits: Dict[str, CircuitBreaker] = {}
        self._latencies: Dict[str, List[float]] = {}
        self._request_counts: Dict[str, int] = {}
        self._error_counts: Dict[str, int] = {}
        self._recent_events: List[Dict[str, Any]] = []

    def get_circuit_breaker(self, target_id: str) -> CircuitBreaker:
        if target_id not in self._circuits:
            self._circuits[target_id] = CircuitBreaker(target_id=target_id)
        return self._circuits[target_id]

    def record_request(
        self,
        provider_id: str,
        model_id: str,
        latency_ms: float,
        success: bool,
        error_type: Optional[str] = None
    ) -> None:
        key = f"{provider_id}:{model_id}"
        self._request_counts[key] = self._request_counts.get(key, 0) + 1
        
        if key not in self._latencies:
            self._latencies[key] = []
        self._latencies[key].append(latency_ms)
        # Keep sliding window of 200 samples
        if len(self._latencies[key]) > 200:
            self._latencies[key].pop(0)

        cb_provider = self.get_circuit_breaker(provider_id)
        cb_model = self.get_circuit_breaker(key)

        if success:
            cb_provider.record_success()
            cb_model.record_success()
        else:
            self._error_counts[key] = self._error_counts.get(key, 0) + 1
            cb_provider.record_failure(error_type)
            cb_model.record_failure(error_type)

        self._recent_events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider_id": provider_id,
            "model_id": model_id,
            "latency_ms": latency_ms,
            "success": success,
            "error_type": error_type
        })
        if len(self._recent_events) > 500:
            self._recent_events.pop(0)

    def calculate_percentiles(self, target_key: str) -> Dict[str, float]:
        samples = sorted(self._latencies.get(target_key, []))
        if not samples:
            return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}
        
        def pct(p: float) -> float:
            idx = int(math.ceil((p / 100.0) * len(samples))) - 1
            return round(samples[max(0, min(idx, len(samples) - 1))], 2)

        return {
            "p50": pct(50),
            "p90": pct(90),
            "p95": pct(95),
            "p99": pct(99)
        }

    def get_provider_health(self, provider_id: str) -> Dict[str, Any]:
        cb = self.get_circuit_breaker(provider_id)
        total_reqs = sum(cnt for k, cnt in self._request_counts.items() if k.startswith(f"{provider_id}:"))
        total_errs = sum(cnt for k, cnt in self._error_counts.items() if k.startswith(f"{provider_id}:"))
        err_rate = round((total_errs / total_reqs) * 100, 2) if total_reqs > 0 else 0.0

        if cb.state == CircuitState.OPEN:
            status = HealthStatus.UNAVAILABLE.value
        elif err_rate > 20.0 or cb.state == CircuitState.HALF_OPEN:
            status = HealthStatus.DEGRADED.value
        elif total_reqs > 0:
            status = HealthStatus.HEALTHY.value
        else:
            status = HealthStatus.UNKNOWN.value

        all_latencies = []
        for k, lats in self._latencies.items():
            if k.startswith(f"{provider_id}:"):
                all_latencies.extend(lats)
        all_latencies.sort()

        p50 = all_latencies[len(all_latencies)//2] if all_latencies else 0.0

        return {
            "provider_id": provider_id,
            "status": status,
            "circuit_state": cb.state.value,
            "total_requests": total_reqs,
            "error_rate_pct": err_rate,
            "latency_p50_ms": round(p50, 2)
        }

    def is_provider_available(self, provider_id: str) -> bool:
        cb = self.get_circuit_breaker(provider_id)
        return cb.can_execute()

    def is_model_available(self, provider_id: str, model_id: str) -> bool:
        if not self.is_provider_available(provider_id):
            return False
        cb = self.get_circuit_breaker(f"{provider_id}:{model_id}")
        return cb.can_execute()


_GLOBAL_HEALTH_MONITOR = ProviderHealthMonitor()

def get_health_monitor() -> ProviderHealthMonitor:
    return _GLOBAL_HEALTH_MONITOR
