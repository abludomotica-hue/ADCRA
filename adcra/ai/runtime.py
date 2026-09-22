"""
ADCRA AI Intelligence Control Plane — Provider-Agnostic Agent Runtime & Fallback Engine
Orchestrates capability resolution, model policy application, fallback chains, circuit breaker tracking,
air-tight secret redaction, and standardized AIRun state tracking.
"""

import re
import time
import uuid
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import enum

from adcra.ai.types import (
    AIRequest, AIResponse, AIMessage, TaskType, AutonomyLevel,
    RiskLevel, SourceEpistemology
)
from adcra.ai.capabilities import get_capability_registry, CapabilityRequirement
from adcra.ai.brains import get_brain_registry, BrainProfile
from adcra.ai.policies import get_policy_engine, ModelPolicy
from adcra.ai.router import get_model_router, RoutingDecision
from adcra.ai.gateway import get_ai_gateway
from adcra.ai.health import get_health_monitor
from adcra.ai.cost import get_cost_ledger, get_budget_engine

logger = logging.getLogger("adcra.ai.runtime")


# ------------------------------------------------------------------------------
# 1. SECURITY & SECRET REDACTION
# ------------------------------------------------------------------------------

class SecretRedaction:
    """Detecta y enmascara tokens y claves de API en textos, logs y JSON."""
    PATTERNS = [
        re.compile(r'sk-[a-zA-Z0-9_-]{20,}'),           # OpenAI / general sk keys
        re.compile(r'AIza[0-9A-Za-z-_]{30,45}'),           # Google Gemini / Cloud API keys
        re.compile(r'xkeys-[a-zA-Z0-9_-]{20,}'),        # Anthropic / custom
        re.compile(r'bearer\s+[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE), # Bearer tokens
        re.compile(r'(?i)(api[_-]?key|secret|token)\s*[:=]\s*["\']([^"\']+)["\']')
    ]

    @classmethod
    def redact(cls, text: str) -> str:
        if not isinstance(text, str):
            return text
        redacted = text
        for pat in cls.PATTERNS[:4]:
            redacted = pat.sub("[REDACTED_API_KEY]", redacted)
        # Redact labeled keys
        redacted = cls.PATTERNS[4].sub(r'\1="[REDACTED_SECRET]"', redacted)
        return redacted

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza recursivamente un diccionario para almacenamiento seguro."""
        clean = {}
        for k, v in data.items():
            if any(term in k.lower() for term in ["api_key", "secret", "token", "password", "authorization"]):
                clean[k] = "[REDACTED]"
            elif isinstance(v, dict):
                clean[k] = cls.sanitize_dict(v)
            elif isinstance(v, list):
                clean[k] = [cls.sanitize_dict(item) if isinstance(item, dict) else (cls.redact(str(item)) if isinstance(item, str) else item) for item in v]
            elif isinstance(v, str):
                clean[k] = cls.redact(v)
            else:
                clean[k] = v
        return clean


from adcra.infrastructure.secrets.secret_store import get_secret_provider

class SecretProvider:
    """Abstracción de acceso a credenciales conectada al SecretStore de infraestructura."""
    @staticmethod
    def get_secret(key_name: str, default: Optional[str] = None) -> Optional[str]:
        return get_secret_provider().get_secret(key_name, default)

    @staticmethod
    def set_secret(key_name: str, value: str) -> None:
        get_secret_provider().set_secret(key_name, value)

    @staticmethod
    def delete_secret(key_name: str) -> bool:
        return get_secret_provider().delete_secret(key_name)

    @staticmethod
    def exists(key_name: str) -> bool:
        return get_secret_provider().exists(key_name)


# ------------------------------------------------------------------------------
# 2. AI RUN ENTITY & STATES
# ------------------------------------------------------------------------------

class AIRunStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    RETRYING = "RETRYING"
    FALLING_BACK = "FALLING_BACK"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"


@dataclass
class AIRun:
    run_id: str
    tenant_id: str = "default_tenant"
    client_id: Optional[str] = "locos-materos"
    campaign_id: Optional[str] = "camp_2026_01"
    task_id: str = "task_root"
    agent_id: Optional[str] = "agent_default"
    brain_id: Optional[str] = "creative_director"
    capability: str = "text_generation"
    provider: str = "mock"
    model: str = "mock-creative-flash"
    status: AIRunStatus = AIRunStatus.QUEUED
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    input_hash: str = ""
    output_hash: str = ""
    parent_run_id: Optional[str] = None
    trace_id: str = field(default_factory=lambda: f"tr_{uuid.uuid4().hex[:8]}")
    approval_state: str = "NONE"  # NONE, PENDING, APPROVED, REJECTED
    fallback_count: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "tenant_id": self.tenant_id,
            "client_id": self.client_id,
            "campaign_id": self.campaign_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "brain_id": self.brain_id,
            "capability": self.capability,
            "provider": self.provider,
            "model": self.model,
            "status": self.status.value if hasattr(self.status, "value") else str(self.status),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "parent_run_id": self.parent_run_id,
            "trace_id": self.trace_id,
            "approval_state": self.approval_state,
            "fallback_count": self.fallback_count,
            "error": self.error,
            "metadata": self.metadata
        }


# ------------------------------------------------------------------------------
# 3. FALLBACK ENGINE
# ------------------------------------------------------------------------------

class FallbackEngine:
    """
    Ejecuta cadenas de fallback multinivel resilientes:
    PRIMARY -> SECONDARY -> TERTIARY -> MOCK
    Registra métricas en el HealthMonitor y actualiza el estado de disyuntores.
    """
    def __init__(self):
        self.gateway = get_ai_gateway()
        self.health_monitor = get_health_monitor()

    def execute_chain(
        self,
        request: AIRequest,
        decision: RoutingDecision,
        airun: Optional[AIRun] = None
    ) -> AIResponse:
        chain = [(decision.selected_provider, decision.selected_model)] + decision.fallback_chain
        # Asegurar que mock esté al final si no está en la cadena
        if not any(p == "mock" for p, m in chain):
            chain.append(("mock", "mock-creative-flash"))

        attempts = 0
        last_error = None

        for prov_id, mod_id in chain:
            attempts += 1
            if not self.gateway.has_adapter(prov_id):
                continue

            # Verificar circuit breaker
            if not self.health_monitor.is_provider_available(prov_id):
                logger.info(f"Skipping {prov_id} in fallback chain: Circuit breaker is OPEN")
                continue

            # Asignar modelo actual al request
            request.model_preference = mod_id
            t0 = time.time()
            try:
                if airun and attempts > 1:
                    airun.status = AIRunStatus.FALLING_BACK
                    airun.fallback_count += 1

                logger.info(f"Executing request {request.request_id} via {prov_id}:{mod_id} (attempt {attempts})")
                response = self.gateway.execute(request, provider_id=prov_id)
                lat = round((time.time() - t0) * 1000, 2)
                
                # Registrar éxito en el monitor de salud
                self.health_monitor.record_request(prov_id, mod_id, lat, success=True)

                if attempts > 1:
                    response.usage["fallback_triggered"] = True
                    response.usage["fallback_attempts"] = attempts
                    response.usage["original_provider"] = decision.selected_provider
                    response.usage["original_model"] = decision.selected_model

                return response

            except Exception as e:
                lat = round((time.time() - t0) * 1000, 2)
                last_error = str(e)
                logger.warning(f"Provider failure on {prov_id}:{mod_id} ({lat}ms): {e}")
                self.health_monitor.record_request(prov_id, mod_id, lat, success=False, error_type=type(e).__name__)

        raise RuntimeError(f"All providers in fallback chain failed after {attempts} attempts. Last error: {last_error}")


# ------------------------------------------------------------------------------
# 4. PROVIDER-AGNOSTIC AGENT RUNTIME
# ------------------------------------------------------------------------------

class AgentRuntime:
    """
    Runtime desacoplado del proveedor.
    Los agentes y cerebros solicitan capacidades; el runtime resuelve el modelo,
    la política de enrutamiento y ejecuta la llamada de forma transparente y segura.
    """
    def __init__(self):
        self.cap_registry = get_capability_registry()
        self.brain_registry = get_brain_registry()
        self.policy_engine = get_policy_engine()
        self.router = get_model_router()
        self.fallback_engine = FallbackEngine()
        self.cost_ledger = get_cost_ledger()
        self.budget_engine = get_budget_engine()
        self._runs: Dict[str, AIRun] = {}

    def execute_brain(
        self,
        brain_id: str,
        messages: List[AIMessage],
        campaign_id: str = "camp_locos_materos_2026",
        tenant_id: str = "default_tenant",
        output_schema: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        model_preference: Optional[str] = None
    ) -> Tuple[AIResponse, AIRun]:
        brain = self.brain_registry.get_brain(brain_id)
        if not brain:
            raise KeyError(f"BrainProfile '{brain_id}' not found in BrainRegistry")

        run_id = f"run_{uuid.uuid4().hex[:8]}"
        req_id = f"req_{uuid.uuid4().hex[:8]}"

        # Crear AIRun
        airun = AIRun(
            run_id=run_id,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            brain_id=brain_id,
            capability=brain.required_capabilities[0] if brain.required_capabilities else "text_generation",
            status=AIRunStatus.RUNNING
        )
        self._runs[run_id] = airun

        # Inyectar system instruction del brain si no está en messages
        prepared_messages = list(messages)
        if not any(m.role == "system" for m in prepared_messages):
            prepared_messages.insert(0, AIMessage(role="system", content=brain.system_instructions))

        # Construir AIRequest
        policy = ModelPolicy(brain.model_policy) if brain.model_policy in ModelPolicy.__members__ else ModelPolicy.BALANCED
        request = AIRequest(
            request_id=req_id,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            agent_id=brain_id,
            task_type=TaskType.CREATIVE_CONCEPT,
            model_preference=model_preference,
            messages=prepared_messages,
            output_schema=output_schema,
            tools=tools,
            context=context
        )

        # Enrutar según Brain y Política
        decision = self.router.route_detailed(request=request, policy=policy)
        airun.provider = decision.selected_provider
        airun.model = decision.selected_model
        airun.metadata["applied_policy"] = decision.applied_policy
        airun.metadata["routing_reason"] = decision.reason

        # Ejecutar con Fallback Engine
        t0 = time.time()
        try:
            response = self.fallback_engine.execute_chain(request=request, decision=decision, airun=airun)
            lat = round((time.time() - t0) * 1000, 2)
            
            # Registrar costos y telemetría
            est_cost = response.usage.get("estimated_cost_usd", 0.0)
            self.cost_ledger.record_usage(
                tenant_id=tenant_id,
                campaign_id=campaign_id,
                agent_id=brain_id,
                task="brain_execution",
                provider_id=response.provider_id,
                model_id=response.model_id,
                input_tokens=response.usage.get("input_tokens", 0),
                output_tokens=response.usage.get("output_tokens", 0),
                cached_tokens=response.usage.get("cached_tokens", 0),
                cost_usd=est_cost,
                latency_ms=lat
            )

            # Actualizar AIRun
            airun.status = AIRunStatus.COMPLETED
            airun.completed_at = datetime.now(timezone.utc).isoformat()
            airun.latency_ms = lat
            airun.cost_usd = est_cost
            airun.output_hash = hashlib.sha256(response.content.encode("utf-8")).hexdigest()[:12]

            return (response, airun)

        except Exception as e:
            airun.status = AIRunStatus.FAILED
            airun.completed_at = datetime.now(timezone.utc).isoformat()
            airun.error = str(e)
            raise

    def get_run(self, run_id: str) -> Optional[AIRun]:
        return self._runs.get(run_id)

    def list_runs(self, campaign_id: Optional[str] = None, limit: int = 50) -> List[AIRun]:
        runs = list(self._runs.values())
        if campaign_id:
            runs = [r for r in runs if r.campaign_id == campaign_id]
        return runs[-limit:]


_GLOBAL_RUNTIME = AgentRuntime()

def get_agent_runtime() -> AgentRuntime:
    return _GLOBAL_RUNTIME
