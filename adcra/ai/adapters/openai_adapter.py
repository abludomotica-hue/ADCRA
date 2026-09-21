"""
ADCRA AI Brain — OpenAI & Compatible Provider Adapter
Supports OpenAI API, Azure OpenAI, and OpenAI-compatible local/remote endpoints (vLLM, Ollama, etc.).
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


class OpenAIProvider(AIProviderAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self._models = [
            {
                "model_id": "gpt-4o",
                "name": "GPT-4o Omnimodal",
                "version": "2024-11-20",
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
                "model_id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "version": "2024-07-18",
                "context_window": 128000,
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
            },
            {
                "model_id": "o1",
                "name": "OpenAI o1 Reasoning",
                "version": "2024-12-17",
                "context_window": 200000,
                "cost_per_million_input": 15.00,
                "cost_per_million_output": 60.00,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.VISION.value: True,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: False,
                    ModelCapability.WEB_SEARCH.value: False
                }
            }
        ]

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def name(self) -> str:
        return "OpenAI & OpenAI-Compatible Gateway"

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
            ModelCapability.STRUCTURED_OUTPUT.value: True
        }

    def estimate_cost(self, request: AIRequest, model_id: str) -> CostEstimate:
        char_count = sum(len(str(m.content)) for m in request.messages)
        in_tokens = max(10, char_count // 4)
        out_tokens = min(request.max_output_tokens, 1000)
        pricing = (2.50, 10.00)
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
            "provider": "openai",
            "base_url": self._base_url,
            "has_api_key": has_key,
            "models_available": [m["model_id"] for m in self._models] if has_key else []
        }

    def generate(self, request: AIRequest) -> AIResponse:
        if not self._api_key:
            raise PermissionError("OpenAI API key is missing or not configured")

        model = request.model_preference or "gpt-4o-mini"
        url = f"{self._base_url}/chat/completions"

        payload: Dict[str, Any] = {
            "model": model,
            "messages": [m.to_dict() for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens
        }

        if request.output_schema:
            payload["response_format"] = {"type": "json_object"}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=request.timeout_ms / 1000.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choice = data["choices"][0]
                content = choice["message"].get("content", "")
                finish_reason = choice.get("finish_reason", "stop")
                usage = data.get("usage", {})

                structured = None
                if request.output_schema:
                    try:
                        structured = json.loads(content)
                    except Exception:
                        structured = None

                cost_est = self.estimate_cost(request, model)

                return AIResponse(
                    request_id=request.request_id,
                    provider_id="openai",
                    model_id=model,
                    content=content,
                    structured_data=structured,
                    usage={
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "cached_tokens": usage.get("prompt_tokens_details", {}).get("cached_tokens", 0),
                        "estimated_cost_usd": cost_est.estimated_cost_usd
                    },
                    finish_reason=finish_reason
                )
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8")
            raise RuntimeError(f"OpenAI HTTP Error {he.code}: {err_body}")
        except Exception as e:
            raise RuntimeError(f"OpenAI Connection Error: {str(e)}")

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        resp = self.generate(request)
        yield AIStreamEvent(event_type="content_chunk", data={"chunk": resp.content})
        yield AIStreamEvent(event_type="completed", data={"response": resp.to_dict()})
