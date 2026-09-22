"""
ADCRA AI Brain — OpenRouter Aggregator Provider Adapter
Connects to hundreds of models via OpenRouter unified API.
Features real network validation, SecretProvider integration, and model discovery.
"""

import os
import time
import json
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional, Iterator

from adcra.ai.gateway import AIProviderAdapter
from adcra.ai.types import (
    AIAuthenticationError,
    AIProviderError,
    AIRequest, AIResponse, AIStreamEvent, CostEstimate,
    ModelCapability, ProviderStatus
)
from adcra.infrastructure.secrets.secret_store import get_secret_provider


class OpenRouterProvider(AIProviderAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key
        self._is_connected = False
        self._last_error: Optional[str] = None
        self._models = [
            {
                "model_id": "meta-llama/llama-3.3-70b-instruct",
                "name": "Llama 3.3 70B Instruct",
                "version": "3.3",
                "context_window": 131072,
                "cost_per_million_input": 0.12,
                "cost_per_million_output": 0.30,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True
                }
            },
            {
                "model_id": "deepseek/deepseek-r1",
                "name": "DeepSeek R1 High Reasoning",
                "version": "r1",
                "context_window": 65536,
                "cost_per_million_input": 0.55,
                "cost_per_million_output": 2.19,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True
                }
            }
        ]

    def _get_api_key(self) -> str:
        if self._explicit_key:
            return self._explicit_key
        return get_secret_provider().get_secret("OPENROUTER_API_KEY", "") or ""

    @property
    def provider_id(self) -> str:
        return "openrouter"

    @property
    def name(self) -> str:
        return "OpenRouter Aggregator Gateway"

    def list_models(self) -> List[Dict[str, Any]]:
        return self._models

    def get_model_capabilities(self, model_id: str) -> Dict[str, bool]:
        for m in self._models:
            if m["model_id"] == model_id:
                return m["capabilities"]
        return {
            ModelCapability.REASONING.value: True,
            ModelCapability.STRUCTURED_OUTPUT.value: True
        }

    def estimate_cost(self, request: AIRequest, model_id: str) -> CostEstimate:
        char_count = sum(len(str(m.content)) for m in request.messages)
        in_tokens = max(10, char_count // 4)
        out_tokens = min(request.max_output_tokens, 1000)
        pricing = (0.12, 0.30)
        for m in self._models:
            if m["model_id"] == model_id:
                pricing = (m.get("cost_per_million_input", 0.12), m.get("cost_per_million_output", 0.30))
                break
        cost = (in_tokens * pricing[0] + out_tokens * pricing[1]) / 1_000_000.0
        return CostEstimate(
            estimated_input_tokens=in_tokens,
            estimated_output_tokens=out_tokens,
            estimated_cost_usd=round(cost, 6)
        )

    def validate_configuration(self) -> Dict[str, Any]:
        key = self._get_api_key()
        has_key = bool(key and len(key) > 5)
        status = ProviderStatus.CONFIGURED.value if has_key else ProviderStatus.NOT_CONFIGURED.value
        if self._is_connected and has_key:
            status = ProviderStatus.CONNECTED.value
        return {
            "configured": has_key,
            "connected": self._is_connected if has_key else False,
            "status": status,
            "provider": "openrouter",
            "has_api_key": has_key,
            "models_available": [m["model_id"] for m in self._models] if has_key else []
        }

    def test_connection(self) -> Dict[str, Any]:
        key = self._get_api_key()
        if not key or len(key) < 5:
            self._is_connected = False
            return {
                "provider_id": "openrouter",
                "status": ProviderStatus.NOT_CONFIGURED.value,
                "connected": False,
                "configured": False,
                "error": "OpenRouter API key not configured"
            }

        url = "https://openrouter.ai/api/v1/models"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "User-Agent": "ADCRA-v2.1-Test"
            },
            method="GET"
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                lat = round((time.time() - t0) * 1000, 2)
                if resp.status == 200:
                    self._is_connected = True
                    self._last_error = None
                    return {
                        "provider_id": "openrouter",
                        "status": ProviderStatus.CONNECTED.value,
                        "connected": True,
                        "configured": True,
                        "latency_ms": lat,
                        "message": "OpenRouter API connected successfully"
                    }
        except urllib.error.HTTPError as e:
            self._is_connected = False
            lat = round((time.time() - t0) * 1000, 2)
            code = e.code
            if code in [401, 403]:
                err_status = "AUTHENTICATION_FAILED"
                msg = "Invalid OpenRouter API key"
            elif code == 429:
                err_status = "RATE_LIMITED"
                msg = "OpenRouter rate limit exceeded"
            else:
                err_status = "PROVIDER_ERROR"
                msg = f"OpenRouter error HTTP {code}"
            self._last_error = msg
            return {
                "provider_id": "openrouter",
                "status": err_status,
                "connected": False,
                "configured": True,
                "latency_ms": lat,
                "error": msg
            }
        except Exception as e:
            self._is_connected = False
            lat = round((time.time() - t0) * 1000, 2)
            msg = get_secret_provider().redact(str(e))
            self._last_error = msg
            return {
                "provider_id": "openrouter",
                "status": "NETWORK_ERROR",
                "connected": False,
                "configured": True,
                "latency_ms": lat,
                "error": f"Network error connecting to OpenRouter: {msg}"
            }

    def discover_models(self) -> List[Dict[str, Any]]:
        key = self._get_api_key()
        if not key:
            return self._models
        url = "https://openrouter.ai/api/v1/models"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {key}"},
            method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models_raw = data.get("data", [])
                    discovered = []
                    for m in models_raw[:20]:  # Top 20 popular models
                        mid = m.get("id", "")
                        discovered.append({
                            "model_id": mid,
                            "name": m.get("name", mid),
                            "version": "discovered",
                            "context_window": m.get("context_length", 131072),
                            "cost_per_million_input": float(m.get("pricing", {}).get("prompt", 0.0)) * 1_000_000,
                            "cost_per_million_output": float(m.get("pricing", {}).get("completion", 0.0)) * 1_000_000,
                            "capabilities": {
                                ModelCapability.REASONING.value: True,
                                ModelCapability.STRUCTURED_OUTPUT.value: True
                            }
                        })
                    if discovered:
                        self._models = discovered
                        self._is_connected = True
        except Exception:
            pass
        return self._models

    def configure(self, credentials: Dict[str, Any]) -> None:
        if "api_key" in credentials:
            key = credentials["api_key"].strip()
            get_secret_provider().set_secret("OPENROUTER_API_KEY", key)
            self._explicit_key = key

    def generate(self, request: AIRequest) -> AIResponse:
        key = self._get_api_key()
        if not key:
            raise AIAuthenticationError("OpenRouter API key is missing or not configured")

        model = request.model_preference or "meta-llama/llama-3.3-70b-instruct"
        url = "https://openrouter.ai/api/v1/chat/completions"

        payload: Dict[str, Any] = {
            "model": model,
            "messages": [m.to_dict() for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
                "HTTP-Referer": "https://adcra.ai",
                "X-Title": "ADCRA Creative Operating System"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=request.timeout_ms / 1000.0) as resp:
                raw_data = json.loads(resp.read().decode("utf-8"))
                choice = raw_data["choices"][0]
                content = choice["message"]["content"]
                usage = raw_data.get("usage", {})

                structured = None
                if request.output_schema:
                    try:
                        structured = json.loads(content)
                    except json.JSONDecodeError:
                        pass

                return AIResponse(
                    content=content,
                    provider_id=self.provider_id,
                    model_id=model,
                    usage={
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    },
                    structured_data=structured
                )
        except Exception as e:
            sanitized = get_secret_provider().redact(str(e))
            raise RuntimeError(f"OpenRouter generation failed: {sanitized}")

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        resp = self.generate(request)
        yield AIStreamEvent(chunk=resp.content, is_final=True)
