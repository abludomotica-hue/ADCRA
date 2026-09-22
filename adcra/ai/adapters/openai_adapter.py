"""
ADCRA AI Brain — OpenAI & Compatible Provider Adapter
Supports OpenAI API, Azure OpenAI, and OpenAI-compatible local/remote endpoints (vLLM, Ollama, etc.).
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


class OpenAIProvider(AIProviderAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self._explicit_key = api_key
        self._base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self._is_connected = False
        self._last_error: Optional[str] = None
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
                "name": "GPT-4o Mini Fast & Efficient",
                "version": "2024-07-18",
                "context_window": 128000,
                "cost_per_million_input": 0.15,
                "cost_per_million_output": 0.60,
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
                "model_id": "o1",
                "name": "OpenAI o1 Advanced Reasoning",
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

    def _get_api_key(self) -> str:
        if self._explicit_key:
            return self._explicit_key
        return get_secret_provider().get_secret("OPENAI_API_KEY", "") or ""

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
                pricing = (m.get("cost_per_million_input", 2.50), m.get("cost_per_million_output", 10.00))
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
            "provider": "openai",
            "base_url": self._base_url,
            "has_api_key": has_key,
            "models_available": [m["model_id"] for m in self._models] if has_key else []
        }

    def test_connection(self) -> Dict[str, Any]:
        key = self._get_api_key()
        if not key or len(key) < 5:
            self._is_connected = False
            return {
                "provider_id": "openai",
                "status": ProviderStatus.NOT_CONFIGURED.value,
                "connected": False,
                "configured": False,
                "error": "API key not configured"
            }

        url = f"{self._base_url}/models"
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
                        "provider_id": "openai",
                        "status": ProviderStatus.CONNECTED.value,
                        "connected": True,
                        "configured": True,
                        "latency_ms": lat,
                        "message": "Authentication successful and endpoint responding"
                    }
        except urllib.error.HTTPError as e:
            self._is_connected = False
            lat = round((time.time() - t0) * 1000, 2)
            code = e.code
            if code in [401, 403]:
                err_status = "AUTHENTICATION_FAILED"
                msg = "Invalid API key or unauthorized"
            elif code == 429:
                err_status = "RATE_LIMITED"
                msg = "Quota exceeded or rate limited"
            else:
                err_status = "PROVIDER_ERROR"
                msg = f"Provider error HTTP {code}"
            self._last_error = msg
            return {
                "provider_id": "openai",
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
                "provider_id": "openai",
                "status": "NETWORK_ERROR",
                "connected": False,
                "configured": True,
                "latency_ms": lat,
                "error": f"Network error connecting to OpenAI: {msg}"
            }

    def discover_models(self) -> List[Dict[str, Any]]:
        key = self._get_api_key()
        if not key:
            return self._models
        url = f"{self._base_url}/models"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {key}"},
            method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    model_items = data.get("data", [])
                    discovered = []
                    for m in model_items:
                        mid = m.get("id", "")
                        if any(mid.startswith(prefix) for prefix in ["gpt-4", "o1", "o3", "chatgpt"]):
                            discovered.append({
                                "model_id": mid,
                                "name": f"OpenAI {mid}",
                                "version": "discovered",
                                "context_window": 128000,
                                "cost_per_million_input": 2.50,
                                "cost_per_million_output": 10.00,
                                "capabilities": {
                                    ModelCapability.REASONING.value: True,
                                    ModelCapability.VISION.value: True,
                                    ModelCapability.TOOL_CALLING.value: True,
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
            get_secret_provider().set_secret("OPENAI_API_KEY", key)
            self._explicit_key = key
        if "base_url" in credentials and credentials["base_url"]:
            self._base_url = credentials["base_url"].rstrip("/")

    def generate(self, request: AIRequest) -> AIResponse:
        key = self._get_api_key()
        if not key:
            raise AIAuthenticationError("OpenAI API key is missing or not configured")

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
                "Authorization": f"Bearer {key}"
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
            raise RuntimeError(f"OpenAI generation failed: {sanitized}")

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        # Minimal synchronous fallback for stream
        resp = self.generate(request)
        yield AIStreamEvent(chunk=resp.content, is_final=True)
