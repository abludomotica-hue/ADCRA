"""
ADCRA AI Brain — Google Gemini Provider Adapter
Supports Gemini 2.5 Flash, Gemini 2.5 Pro, and multimodal audio/visual analysis.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional, Iterator
from adcra.ai.gateway import AIProviderAdapter
from adcra.ai.types import (
    AIRequest, AIResponse, AIStreamEvent, CostEstimate,
    ModelCapability
)


class GeminiProvider(AIProviderAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self._models = [
            {
                "model_id": "gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "version": "2.5",
                "context_window": 1048576,
                "cost_per_million_input": 0.075,
                "cost_per_million_output": 0.30,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.VISION.value: True,
                    ModelCapability.AUDIO_INPUT.value: True,
                    ModelCapability.VIDEO_GENERATION.value: False,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True,
                    ModelCapability.WEB_SEARCH.value: True
                }
            },
            {
                "model_id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro (Deep Reasoning)",
                "version": "2.5",
                "context_window": 2097152,
                "cost_per_million_input": 1.25,
                "cost_per_million_output": 5.00,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.VISION.value: True,
                    ModelCapability.AUDIO_INPUT.value: True,
                    ModelCapability.VIDEO_GENERATION.value: False,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True,
                    ModelCapability.WEB_SEARCH.value: True
                }
            }
        ]

    @property
    def provider_id(self) -> str:
        return "gemini"

    @property
    def name(self) -> str:
        return "Google Gemini AI Gateway"

    def list_models(self) -> List[Dict[str, Any]]:
        return self._models

    def get_model_capabilities(self, model_id: str) -> Dict[str, bool]:
        for m in self._models:
            if m["model_id"] == model_id:
                return m["capabilities"]
        return {
            ModelCapability.REASONING.value: True,
            ModelCapability.VISION.value: True,
            ModelCapability.AUDIO_INPUT.value: True,
            ModelCapability.TOOL_CALLING.value: True,
            ModelCapability.STRUCTURED_OUTPUT.value: True
        }

    def estimate_cost(self, request: AIRequest, model_id: str) -> CostEstimate:
        char_count = sum(len(str(m.content)) for m in request.messages)
        in_tokens = max(10, char_count // 4)
        out_tokens = min(request.max_output_tokens, 1000)
        pricing = (0.075, 0.30)
        for m in self._models:
            if m["model_id"] == model_id:
                pricing = (m["cost_per_million_input"], m["cost_per_million_output"])
                break
        cost = (in_tokens * pricing[0] + out_tokens * pricing[1]) / 1_000_000.0
        return CostEstimate(
            estimated_input_tokens=in_tokens,
            estimated_output_tokens=out_tokens,
            estimated_cost_usd=round(cost, 6)
        )

    def validate_configuration(self) -> Dict[str, Any]:
        has_key = bool(self._api_key and len(self._api_key) > 5)
        return {
            "connected": has_key,
            "status": "CONNECTED" if has_key else "NOT_CONNECTED",
            "provider": "gemini",
            "has_api_key": has_key,
            "models_available": [m["model_id"] for m in self._models] if has_key else []
        }

    def generate(self, request: AIRequest) -> AIResponse:
        if not self._api_key:
            raise PermissionError("Gemini API key is missing or not configured")

        model = request.model_preference or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self._api_key}"

        # Formatear mensajes Gemini
        contents = []
        system_instruction = None
        for m in request.messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": str(m.content)}]}
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": str(m.content)}]
                })

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_output_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        if request.output_schema:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=request.timeout_ms / 1000.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidate = data.get("candidates", [{}])[0]
                content = ""
                parts = candidate.get("content", {}).get("parts", [])
                if parts:
                    content = parts[0].get("text", "")
                finish_reason = candidate.get("finishReason", "STOP")

                structured = None
                if request.output_schema:
                    try:
                        structured = json.loads(content)
                    except Exception:
                        structured = None

                usage_meta = data.get("usageMetadata", {})
                cost_est = self.estimate_cost(request, model)

                return AIResponse(
                    request_id=request.request_id,
                    provider_id="gemini",
                    model_id=model,
                    content=content,
                    structured_data=structured,
                    usage={
                        "input_tokens": usage_meta.get("promptTokenCount", 0),
                        "output_tokens": usage_meta.get("candidatesTokenCount", 0),
                        "cached_tokens": usage_meta.get("cachedContentTokenCount", 0),
                        "estimated_cost_usd": cost_est.estimated_cost_usd
                    },
                    finish_reason=finish_reason
                )
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8")
            raise RuntimeError(f"Gemini HTTP Error {he.code}: {err_body}")
        except Exception as e:
            raise RuntimeError(f"Gemini Connection Error: {str(e)}")

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        resp = self.generate(request)
        yield AIStreamEvent(event_type="content_chunk", data={"chunk": resp.content})
        yield AIStreamEvent(event_type="completed", data={"response": resp.to_dict()})
