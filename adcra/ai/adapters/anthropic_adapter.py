"""
ADCRA AI Brain — Anthropic Claude Provider Adapter
Supports Claude 3.5 Sonnet, Claude 3.5 Haiku, and high-fidelity creative copy analysis.
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


class AnthropicProvider(AIProviderAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._models = [
            {
                "model_id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "version": "2024-10-22",
                "context_window": 200000,
                "cost_per_million_input": 3.00,
                "cost_per_million_output": 15.00,
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
                "model_id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "version": "2024-10-22",
                "context_window": 200000,
                "cost_per_million_input": 0.80,
                "cost_per_million_output": 4.00,
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
        return "anthropic"

    @property
    def name(self) -> str:
        return "Anthropic Claude Gateway"

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
        pricing = (3.00, 15.00)
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
            "provider": "anthropic",
            "has_api_key": has_key,
            "models_available": [m["model_id"] for m in self._models] if has_key else []
        }

    def generate(self, request: AIRequest) -> AIResponse:
        if not self._api_key:
            raise PermissionError("Anthropic API key is missing or not configured")

        model = request.model_preference or "claude-3-5-sonnet-20241022"
        url = "https://api.anthropic.com/v1/messages"

        system_prompt = ""
        user_messages = []
        for m in request.messages:
            if m.role == "system":
                system_prompt += str(m.content) + "\n"
            else:
                user_messages.append({"role": m.role, "content": str(m.content)})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": user_messages,
            "max_tokens": request.max_output_tokens,
            "temperature": request.temperature
        }
        if system_prompt:
            payload["system"] = system_prompt.strip()

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=request.timeout_ms / 1000.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        content += block.get("text", "")

                structured = None
                if request.output_schema:
                    try:
                        structured = json.loads(content)
                    except Exception:
                        structured = None

                usage = data.get("usage", {})
                cost_est = self.estimate_cost(request, model)

                return AIResponse(
                    request_id=request.request_id,
                    provider_id="anthropic",
                    model_id=model,
                    content=content,
                    structured_data=structured,
                    usage={
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "cached_tokens": 0,
                        "estimated_cost_usd": cost_est.estimated_cost_usd
                    },
                    finish_reason=data.get("stop_reason", "end_turn")
                )
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8")
            raise RuntimeError(f"Anthropic HTTP Error {he.code}: {err_body}")
        except Exception as e:
            raise RuntimeError(f"Anthropic Connection Error: {str(e)}")

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        resp = self.generate(request)
        yield AIStreamEvent(event_type="content_chunk", data={"chunk": resp.content})
        yield AIStreamEvent(event_type="completed", data={"response": resp.to_dict()})
