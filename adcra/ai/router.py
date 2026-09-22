"""
ADCRA AI Brain — Dynamic Model Router & Policy Optimization Engine
Selects the optimal provider and model for each task based on capability matrices,
routing policies, budget, privacy constraints, connection health, circuit breakers, and fallback resilience.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

from adcra.ai.types import TaskType, ModelCapability, RoutingMode, AIRequest
from adcra.ai.models import get_model_registry, ModelRegistry
from adcra.ai.gateway import get_ai_gateway, AIProviderGateway
from adcra.ai.capabilities import get_capability_registry, CapabilityRegistry, CapabilityRequirement
from adcra.ai.policies import get_policy_engine, ModelPolicyEngine, ModelPolicy
from adcra.ai.health import get_health_monitor, ProviderHealthMonitor, HealthStatus

logger = logging.getLogger("adcra.ai.router")

DEFAULT_TASK_CAPABILITY_MATRIX: Dict[str, List[str]] = {
    TaskType.CAMPAIGN_STRATEGY.value: [ModelCapability.REASONING.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.CREATIVE_CONCEPT.value: [ModelCapability.REASONING.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.COPY_GENERATE.value: [ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.COPY_REVIEW.value: [ModelCapability.REASONING.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.AUDIO_ANALYZE.value: [ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.VIDEO_ANALYZE.value: [ModelCapability.VISION.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.IMAGE_ANALYZE.value: [ModelCapability.VISION.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.STORYBOARD_GENERATE.value: [ModelCapability.REASONING.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.CREATIVE_QC.value: [ModelCapability.REASONING.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.TECHNICAL_QC.value: [ModelCapability.REASONING.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.MARKET_RESEARCH.value: [ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.TREND_RESEARCH.value: [ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.CAMPAIGN_POSTMORTEM.value: [ModelCapability.REASONING.value, ModelCapability.STRUCTURED_OUTPUT.value],
    TaskType.CUSTOM.value: [ModelCapability.STRUCTURED_OUTPUT.value]
}


@dataclass
class RoutingDecision:
    selected_model: str
    selected_provider: str
    applied_policy: str = "BALANCED"
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    reason: str = "Optimal capability match and policy scoring"
    alternatives: List[Tuple[str, str]] = field(default_factory=list)
    fallback_chain: List[Tuple[str, str]] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_latency_ms: float = 0.0
    confidence: float = 0.95

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_model": self.selected_model,
            "selected_provider": self.selected_provider,
            "applied_policy": self.applied_policy,
            "score_breakdown": self.score_breakdown,
            "reason": self.reason,
            "alternatives": [{"provider": p, "model": m} for p, m in self.alternatives],
            "fallback_chain": [{"provider": p, "model": m} for p, m in self.fallback_chain],
            "estimated_cost": self.estimated_cost,
            "estimated_latency_ms": self.estimated_latency_ms,
            "confidence": self.confidence
        }


class ModelRouter:
    def __init__(
        self,
        registry: Optional[ModelRegistry] = None,
        gateway: Optional[AIProviderGateway] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        policy_engine: Optional[ModelPolicyEngine] = None,
        health_monitor: Optional[ProviderHealthMonitor] = None
    ):
        self.registry = registry or get_model_registry()
        self.gateway = gateway or get_ai_gateway()
        self.cap_registry = capability_registry or get_capability_registry()
        self.policy_engine = policy_engine or get_policy_engine()
        self.health_monitor = health_monitor or get_health_monitor()

    def get_task_requirements(self, task_type: str) -> List[str]:
        return DEFAULT_TASK_CAPABILITY_MATRIX.get(task_type, [ModelCapability.STRUCTURED_OUTPUT.value])

    def route_detailed(
        self,
        request: AIRequest,
        mode: RoutingMode = RoutingMode.AUTO,
        policy: Optional[ModelPolicy] = None,
        allowed_providers: Optional[List[str]] = None
    ) -> RoutingDecision:
        """
        Ejecuta el algoritmo de enrutamiento multidimensional considerando:
        1. Resolución de aliases lógicos (creative.high, copy.fast, etc.)
        2. Requisitos de capacidad (TaskType y CapabilityRegistry)
        3. Estado de salud y Circuit Breakers de proveedores
        4. Puntuación según ModelPolicy activa
        5. Cadena de fallback resiliente
        """
        task_val = request.task_type.value if hasattr(request.task_type, "value") else str(request.task_type)
        required_caps = self.get_task_requirements(task_val)

        # Determinar política efectiva
        if policy:
            active_policy = policy
        elif mode == RoutingMode.COST_OPTIMIZED:
            active_policy = ModelPolicy.COST_OPTIMIZED
        elif mode == RoutingMode.QUALITY_FIRST:
            active_policy = ModelPolicy.QUALITY_FIRST
        else:
            active_policy = ModelPolicy.BALANCED

        # 1. Chequear si el request utiliza un alias lógico
        pref = request.model_preference
        if pref and pref in self.policy_engine.list_aliases():
            alias_data = self.policy_engine.resolve_alias(pref)
            if alias_data:
                target_prov = alias_data.get("preferred_provider", "mock")
                target_mod = alias_data.get("preferred_model", "mock-creative-flash")
                fallbacks = [tuple(f) for f in alias_data.get("fallbacks", [])]
                
                # Verificar circuit breaker del target
                if self.health_monitor.is_provider_available(target_prov):
                    return RoutingDecision(
                        selected_model=target_mod,
                        selected_provider=target_prov,
                        applied_policy=alias_data.get("policy", active_policy.value),
                        reason=f"Resolved from logical alias '{pref}'",
                        fallback_chain=fallbacks,
                        confidence=0.98
                    )

        # 2. Búsqueda de modelos compatibles en el ModelRegistry
        compatible = self.registry.find_compatible_models(required_caps)

        # Filtrar por adaptadores registrados y verificar Circuit Breakers
        connected_models = []
        circuit_tripped_models = []

        for m in compatible:
            pid = m["provider"]
            if allowed_providers and pid not in allowed_providers:
                continue
            if not self.gateway.has_adapter(pid):
                continue

            # Chequear circuit breaker
            if not self.health_monitor.is_provider_available(pid):
                circuit_tripped_models.append(m)
                continue

            adapter = self.gateway.get_adapter(pid)
            health = adapter.validate_configuration()
            if health.get("connected", False):
                connected_models.append(m)
            else:
                circuit_tripped_models.append(m)

        available_models = connected_models if connected_models else circuit_tripped_models

        # Si aún no hay disponibles, relajar requerimientos de razonamiento
        if not available_models:
            relaxed_caps = [c for c in required_caps if c != ModelCapability.REASONING.value]
            compatible = self.registry.find_compatible_models(relaxed_caps)
            for m in compatible:
                pid = m["provider"]
                if self.gateway.has_adapter(pid):
                    if not allowed_providers or pid in allowed_providers:
                        available_models.append(m)

        # Fallback de emergencia a Mock
        if not available_models:
            return RoutingDecision(
                selected_model="mock-creative-flash",
                selected_provider="mock",
                applied_policy=active_policy.value,
                reason="Emergency fallback: no active external providers available",
                fallback_chain=[],
                confidence=0.50
            )

        # Si el request especifica modelo preferido físico
        if request.model_preference:
            for m in available_models:
                if m["model_id"] == request.model_preference:
                    fallbacks = [(cand["provider"], cand["model_id"]) for cand in available_models if cand["model_id"] != m["model_id"]]
                    return RoutingDecision(
                        selected_model=m["model_id"],
                        selected_provider=m["provider"],
                        applied_policy=active_policy.value,
                        reason=f"Explicit user preference '{request.model_preference}'",
                        fallback_chain=fallbacks,
                        confidence=1.0
                    )

        # 3. Puntuación y ordenamiento con ModelPolicyEngine
        scored_candidates = []
        for m in available_models:
            score, breakdown = self.policy_engine.score_candidate(m, policy=active_policy)
            scored_candidates.append((score, breakdown, m))

        # Ordenar de mayor a menor puntuación
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        top_score, top_breakdown, selected = scored_candidates[0]
        fallbacks = [(cand[2]["provider"], cand[2]["model_id"]) for cand in scored_candidates[1:]]
        alternatives = fallbacks[:3]

        est_cost = (selected.get("cost_per_million_input", 1.0) * (request.max_output_tokens / 1_000_000.0))
        est_lat = 400.0 if selected.get("speed_score", 80) > 90 else 1200.0

        decision = RoutingDecision(
            selected_model=selected["model_id"],
            selected_provider=selected["provider"],
            applied_policy=active_policy.value,
            score_breakdown=top_breakdown,
            reason=f"Optimized via {active_policy.value} policy (score: {top_score:.1f}/100)",
            alternatives=alternatives,
            fallback_chain=fallbacks,
            estimated_cost=round(est_cost, 6),
            estimated_latency_ms=est_lat,
            confidence=0.95
        )

        logger.info(
            f"ModelRouter selected: {decision.selected_provider} / {decision.selected_model} "
            f"for task '{task_val}' (policy={decision.applied_policy}, score={top_score})"
        )

        return decision

    def route(
        self,
        request: AIRequest,
        mode: RoutingMode = RoutingMode.AUTO,
        allowed_providers: Optional[List[str]] = None
    ) -> Tuple[str, str, List[Tuple[str, str]]]:
        """Interfaz retrocompatible que devuelve (provider, model, fallbacks)."""
        decision = self.route_detailed(request=request, mode=mode, allowed_providers=allowed_providers)
        return (decision.selected_provider, decision.selected_model, decision.fallback_chain)

    def explain_routing(self, request: AIRequest, decision: RoutingDecision) -> Dict[str, Any]:
        """Genera una explicación clara y legible para humanos (Routing Explainer)."""
        task_val = request.task_type.value if hasattr(request.task_type, "value") else str(request.task_type)
        return {
            "task_type": task_val,
            "requested_policy": decision.applied_policy,
            "selected_provider": decision.selected_provider,
            "selected_model": decision.selected_model,
            "rationale": decision.reason,
            "score_breakdown": decision.score_breakdown,
            "active_fallbacks_count": len(decision.fallback_chain),
            "estimated_cost_usd": decision.estimated_cost,
            "estimated_latency_ms": decision.estimated_latency_ms,
            "confidence_pct": int(decision.confidence * 100),
            "explanation": (
                f"ADCRA selected {decision.selected_provider} ({decision.selected_model}) "
                f"because it satisfies all required capabilities for '{task_val}' with the highest "
                f"composite score under the {decision.applied_policy} policy."
            )
        }


_GLOBAL_ROUTER = ModelRouter()

def get_model_router() -> ModelRouter:
    return _GLOBAL_ROUTER
