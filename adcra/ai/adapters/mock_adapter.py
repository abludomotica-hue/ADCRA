"""
ADCRA AI Brain — Mock AI Provider Adapter
Provides deterministic, offline-capable completions and structured outputs for testing,
local development, and zero-cost test suite verification.
"""

import time
import json
import uuid
from typing import Dict, List, Any, Optional, Iterator
from adcra.ai.gateway import AIProviderAdapter
from adcra.ai.types import (
    AIRequest, AIResponse, AIStreamEvent, CostEstimate,
    ModelCapability, TaskType
)


class MockAIProvider(AIProviderAdapter):
    """
    Simulated AI provider that produces deterministic responses matching requested schemas.
    Allows simulating failures, latency, and token consumption for robust unit testing.
    """

    def __init__(self, simulate_latency_ms: float = 0.0, force_failure: bool = False):
        self._simulate_latency_ms = simulate_latency_ms
        self._force_failure = force_failure
        self._failure_counter = 0
        self._models = [
            {
                "model_id": "mock-reasoning-pro",
                "name": "Mock Reasoning Pro",
                "version": "1.0.0",
                "context_window": 128000,
                "cost_per_million_input": 2.50,
                "cost_per_million_output": 10.00,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.VISION.value: True,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True,
                    ModelCapability.WEB_SEARCH.value: False
                }
            },
            {
                "model_id": "mock-creative-flash",
                "name": "Mock Creative Flash",
                "version": "1.0.0",
                "context_window": 64000,
                "cost_per_million_input": 0.15,
                "cost_per_million_output": 0.60,
                "capabilities": {
                    ModelCapability.REASONING.value: False,
                    ModelCapability.VISION.value: True,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True,
                    ModelCapability.WEB_SEARCH.value: False
                }
            }
        ]

    @property
    def provider_id(self) -> str:
        return "mock"

    @property
    def name(self) -> str:
        return "ADCRA Mock AI Engine (Deterministic)"

    def set_force_failure(self, fail: bool, count: int = 1) -> None:
        self._force_failure = fail
        self._failure_counter = count

    def list_models(self) -> List[Dict[str, Any]]:
        return self._models

    def get_model_capabilities(self, model_id: str) -> Dict[str, bool]:
        for m in self._models:
            if m["model_id"] == model_id:
                return m["capabilities"]
        return {
            ModelCapability.REASONING.value: True,
            ModelCapability.VISION.value: True,
            ModelCapability.TOOL_CALLING.value: True,
            ModelCapability.STRUCTURED_OUTPUT.value: True,
            ModelCapability.STREAMING.value: True
        }

    def estimate_cost(self, request: AIRequest, model_id: str) -> CostEstimate:
        # Aproximación: 4 caracteres por token
        total_chars = sum(len(str(m.content)) for m in request.messages)
        in_tokens = max(10, total_chars // 4)
        out_tokens = min(request.max_output_tokens, 1000)
        cost_in = (in_tokens / 1_000_000.0) * 0.50
        cost_out = (out_tokens / 1_000_000.0) * 1.50
        return CostEstimate(
            estimated_input_tokens=in_tokens,
            estimated_output_tokens=out_tokens,
            estimated_cost_usd=round(cost_in + cost_out, 6)
        )

    def validate_configuration(self) -> Dict[str, Any]:
        return {
            "connected": True,
            "configured": True,
            "status": "HEALTHY",
            "provider": "mock",
            "execution_mode": "SIMULATION",
            "provider_type": "MOCK",
            "latency_ms": self._simulate_latency_ms,
            "auth_valid": True,
            "models_available": [m["model_id"] for m in self._models]
        }

    def test_connection(self) -> Dict[str, Any]:
        return {
            "provider_id": "mock",
            "status": "HEALTHY",
            "connected": True,
            "configured": True,
            "execution_mode": "SIMULATION",
            "provider_type": "MOCK",
            "latency_ms": self._simulate_latency_ms,
            "message": "ADCRA local simulation engine operational"
        }

    def discover_models(self) -> List[Dict[str, Any]]:
        return self._models

    def generate(self, request: AIRequest) -> AIResponse:
        if self._force_failure:
            if self._failure_counter > 0:
                self._failure_counter -= 1
                if self._failure_counter == 0:
                    self._force_failure = False
            raise RuntimeError(f"Simulated Mock Provider failure for test req {request.request_id}")

        if self._simulate_latency_ms > 0:
            time.sleep(self._simulate_latency_ms / 1000.0)

        model_id = request.model_preference or "mock-creative-flash"
        
        # Generar contenido y structured output determinista
        structured_data = None
        content_text = ""

        # Detección de tareas
        task_str = str(request.task_type.value if hasattr(request.task_type, 'value') else request.task_type)

        if "concept" in task_str or "creative" in task_str:
            structured_data = {
                "campaign_id": request.campaign_id or "camp_locos_materos_2026",
                "concept": "Donde estés, tu mate te acompaña",
                "territories": [
                    {
                        "id": "territory_1",
                        "name": "Ritual y Pertenencia",
                        "description": "El mate como conector social y símbolo de identidad compartida",
                        "tone": "Cálido, inclusivo, auténtico",
                        "hook": "¿Alguna vez viste a alguien tomar mate solo sin mirar a su alrededor?"
                    },
                    {
                        "id": "territory_2",
                        "name": "Energía Natural & Foco",
                        "description": "La vitalidad que despierta la mañana y activa proyectos",
                        "tone": "Dinámico, vibrante, juvenil",
                        "hook": "El primer sorbo que arranca tu día de verdad."
                    },
                    {
                        "id": "territory_3",
                        "name": "Momentos Compartidos",
                        "description": "De la charla casual al mateada infinita con amigos",
                        "tone": "Emocional, nostálgico, cercano",
                        "hook": "Hay silencios que solo se llenan pasando el mate."
                    }
                ],
                "selected_territory": "Ritual y Pertenencia"
            }
            content_text = json.dumps(structured_data, indent=2)
        elif "copy" in task_str:
            structured_data = {
                "headlines": [
                    "Donde estés, tu mate te acompaña.",
                    "El sabor de encontrarnos siempre.",
                    "Caliente como el sol, compartido como la vida."
                ],
                "call_to_action": "Buscá tu yerba favorita en locosmateros.com",
                "tone": "Auténtico, cálido, juvenil",
                "economy": {"word_count": 24, "reading_time_sec": 8.2}
            }
            content_text = json.dumps(structured_data, indent=2)
        elif "storyboard" in task_str:
            structured_data = {
                "scenes": [
                    {"scene": 1, "duration_sec": 3.0, "visual": "Primer plano cebando mate en amanecer", "audio": "Burbujeo de agua y acorde suave"},
                    {"scene": 2, "duration_sec": 4.5, "visual": "Grupo de amigos riendo en ronda de parque", "audio": "Percusión rítmica 108 BPM"},
                    {"scene": 3, "duration_sec": 4.5, "visual": "Cierre con logo Locos Materos y mate humeante", "audio": "Slogan cantado y llamada a la acción"}
                ],
                "total_duration_sec": 12.0
            }
            content_text = json.dumps(structured_data, indent=2)
        elif request.output_schema:
            # Construir un mock básico para el schema solicitado
            props = request.output_schema.get("properties", {})
            structured_data = {}
            for p_name, p_val in props.items():
                p_type = p_val.get("type", "string")
                if p_type == "string":
                    structured_data[p_name] = f"Mock value for {p_name}"
                elif p_type == "number":
                    structured_data[p_name] = 95.5
                elif p_type == "integer":
                    structured_data[p_name] = 3
                elif p_type == "boolean":
                    structured_data[p_name] = True
                elif p_type == "array":
                    structured_data[p_name] = ["item_1", "item_2"]
                elif p_type == "object":
                    structured_data[p_name] = {"status": "ok"}
            content_text = json.dumps(structured_data, indent=2)
        else:
            content_text = f"Mock response for task: {task_str}"

        in_tokens = max(10, sum(len(str(m.content)) for m in request.messages) // 4)
        out_tokens = max(15, len(content_text) // 4)
        cost = round((in_tokens * 0.15 + out_tokens * 0.60) / 1_000_000, 6)

        return AIResponse(
            request_id=request.request_id,
            provider_id="mock",
            model_id=model_id,
            content=content_text,
            structured_data=structured_data,
            usage={
                "input_tokens": in_tokens,
                "output_tokens": out_tokens,
                "cached_tokens": 0,
                "estimated_cost_usd": cost,
                "execution_mode": "SIMULATION",
                "provider_type": "MOCK"
            },
            latency_ms=self._simulate_latency_ms,
            finish_reason="stop"
        )

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        resp = self.generate(request)
        words = resp.content.split()
        chunk_size = max(1, len(words) // 4)
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            yield AIStreamEvent(
                event_type="content_chunk",
                data={"chunk": chunk, "request_id": request.request_id}
            )
        yield AIStreamEvent(
            event_type="completed",
            data={"response": resp.to_dict()}
        )
