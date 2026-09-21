"""
ADCRA AI Brain — Model Router & Fallback Engine
Selects the optimal provider and model for each task based on capability matrices,
routing modes, budget, privacy constraints, connection health, and fallback resilience.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from adcra.ai.types import TaskType, ModelCapability, RoutingMode, AIRequest
from adcra.ai.models import get_model_registry, ModelRegistry
from adcra.ai.gateway import get_ai_gateway, AIProviderGateway

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


class ModelRouter:
    def __init__(
        self,
        registry: Optional[ModelRegistry] = None,
        gateway: Optional[AIProviderGateway] = None
    ):
        self.registry = registry or get_model_registry()
        self.gateway = gateway or get_ai_gateway()

    def get_task_requirements(self, task_type: str) -> List[str]:
        return DEFAULT_TASK_CAPABILITY_MATRIX.get(task_type, [ModelCapability.STRUCTURED_OUTPUT.value])

    def route(
        self,
        request: AIRequest,
        mode: RoutingMode = RoutingMode.AUTO,
        allowed_providers: Optional[List[str]] = None
    ) -> Tuple[str, str, List[Tuple[str, str]]]:
        task_val = request.task_type.value if hasattr(request.task_type, "value") else str(request.task_type)
        required_caps = self.get_task_requirements(task_val)

        # 1. Búsqueda de modelos compatibles en el ModelRegistry
        compatible = self.registry.find_compatible_models(required_caps)

        # Filtrar por adaptadores registrados y conectados
        connected_models = []
        fallback_candidates = []

        for m in compatible:
            pid = m["provider"]
            if allowed_providers and pid not in allowed_providers:
                continue
            if not self.gateway.has_adapter(pid):
                continue
            
            adapter = self.gateway.get_adapter(pid)
            health = adapter.validate_configuration()
            if health.get("connected", False):
                connected_models.append(m)
            else:
                fallback_candidates.append(m)

        # Si no hay modelos con credenciales activas, incluir mock y candidatos
        available_models = connected_models if connected_models else fallback_candidates

        # Si aún no hay disponibles, relajar requerimientos de razonamiento
        if not available_models:
            relaxed_caps = [c for c in required_caps if c != ModelCapability.REASONING.value]
            compatible = self.registry.find_compatible_models(relaxed_caps)
            for m in compatible:
                pid = m["provider"]
                if self.gateway.has_adapter(pid):
                    if not allowed_providers or pid in allowed_providers:
                        available_models.append(m)

        if not available_models:
            return ("mock", "mock-creative-flash", [])

        # Si el request especifica modelo preferido
        if request.model_preference:
            for m in available_models:
                if m["model_id"] == request.model_preference:
                    fallbacks = [(cand["provider"], cand["model_id"]) for cand in available_models if cand["model_id"] != m["model_id"]]
                    return (m["provider"], m["model_id"], fallbacks)

        # Aplicar ordenamiento según RoutingMode
        if mode == RoutingMode.COST_OPTIMIZED:
            available_models.sort(key=lambda x: x.get("cost_per_million_input", 0) + x.get("cost_per_million_output", 0))
        elif mode == RoutingMode.QUALITY_FIRST:
            available_models.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        else:  # BALANCED or AUTO
            def score(x):
                q = x.get("quality_score", 80) * 0.5
                s = x.get("speed_score", 80) * 0.3
                c = (x.get("cost_per_million_input", 1.0) + x.get("cost_per_million_output", 2.0)) * 0.1
                return q + s - c
            available_models.sort(key=score, reverse=True)

        selected = available_models[0]
        fallbacks = [(m["provider"], m["model_id"]) for m in available_models[1:]]

        logger.info(
            f"ModelRouter selected: {selected['provider']} / {selected['model_id']} "
            f"for task '{task_val}' (mode={mode.value}, fallbacks={len(fallbacks)})"
        )

        return (selected["provider"], selected["model_id"], fallbacks)


_GLOBAL_ROUTER = ModelRouter()

def get_model_router() -> ModelRouter:
    return _GLOBAL_ROUTER
