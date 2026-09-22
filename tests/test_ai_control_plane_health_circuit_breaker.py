"""
Unit and Integration Tests for ADCRA AI Intelligence Control Plane v2.0 - Health & Circuit Breakers
Verifies:
- CircuitBreaker state transitions: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
- Failure threshold enforcement and cooldown timers
- ProviderHealthMonitor latency percentiles (P50, P90, P95, P99)
- Provider availability checks and error rate calculations
"""

import unittest
import time
from adcra.ai.health import (
    CircuitBreaker,
    CircuitState,
    HealthStatus,
    ProviderHealthMonitor,
    get_health_monitor
)

class TestAiControlPlaneHealthCircuitBreaker(unittest.TestCase):

    def test_circuit_breaker_transitions(self):
        """Verify full lifecycle of a CircuitBreaker."""
        cb = CircuitBreaker(
            target_id="test_provider",
            failure_threshold=3,
            cooldown_seconds=0.1  # Fast cooldown for testing
        )

        # 1. Starts CLOSED
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.can_execute())

        # 2. Record 2 failures (below threshold)
        cb.record_failure("timeout_1")
        cb.record_failure("timeout_2")
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.can_execute())

        # 3. 3rd failure trips to OPEN
        cb.record_failure("timeout_3")
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.can_execute())

        # 4. Wait for cooldown to transition to HALF_OPEN
        time.sleep(0.12)
        self.assertTrue(cb.can_execute())  # Transitions to HALF_OPEN
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)

        # 5. Success recovers to CLOSED
        cb.record_success()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertEqual(cb.consecutive_failures, 0)
        self.assertTrue(cb.can_execute())

    def test_health_monitor_latencies_and_percentiles(self):
        """Verify ProviderHealthMonitor computes correct P50, P90, P95 percentiles."""
        monitor = ProviderHealthMonitor()
        provider = "test_prov"
        model = "test_model"

        # Record 100 requests with known latencies: 1ms, 2ms, ... 100ms
        for i in range(1, 101):
            monitor.record_request(
                provider_id=provider,
                model_id=model,
                latency_ms=float(i),
                success=True
            )

        pcts = monitor.calculate_percentiles(f"{provider}:{model}")
        self.assertEqual(pcts["p50"], 50.0)
        self.assertEqual(pcts["p90"], 90.0)
        self.assertEqual(pcts["p95"], 95.0)
        self.assertEqual(pcts["p99"], 99.0)

    def test_provider_health_summary(self):
        """Verify get_provider_health calculates total requests and error rates."""
        monitor = ProviderHealthMonitor()
        provider = "gemini_mock"
        model = "gemini-2.5-flash"

        # 8 successes, 2 errors = 20% error rate
        for _ in range(8):
            monitor.record_request(provider, model, 200.0, success=True)
        for _ in range(2):
            monitor.record_request(provider, model, 5000.0, success=False, error_type="503_overloaded")

        health = monitor.get_provider_health(provider)
        self.assertEqual(health["provider_id"], provider)
        self.assertEqual(health["total_requests"], 10)
        self.assertEqual(health["error_rate_pct"], 20.0)
        self.assertEqual(health["status"], HealthStatus.HEALTHY.value)

if __name__ == "__main__":
    unittest.main()
