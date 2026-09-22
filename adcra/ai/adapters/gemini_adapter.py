"""
ADCRA AI Brain — Google Gemini Provider Adapter
Supports Gemini 2.5 Flash, Gemini 2.5 Pro, and multimodal audio/visual analysis.
Features real connection testing via Google Generative Language API, SecretProvider integration,
and model discovery.
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


class GeminiProvider(AIProviderAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key
        self._is_connected = False
        self._last_error: Optional[str] = None
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
                    ModelCapability.AUDIO.value: True,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True,
                    ModelCapability.LONG_CONTEXT.value: True
                }
            },
            {
                "model_id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro Multimodal",
                "version": "2.5",
                "context_window": 2097152,
                "cost_per_million_input": 1.25,
                "cost_per_million_output": 5.00,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.VISION.value: True,
                    ModelCapability.AUDIO.value: True,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True,
                    ModelCapability.LONG_CONTEXT.value: True
                }
            }
        ]

    def _get_api_key(self) -> str:
        if self._explicit_key:
            return self._explicit_key
        return get_secret_provider().get_secret("GEMINI_API_KEY", "") or ""

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
            ModelCapability.AUDIO.value: True,
            ModelCapability.STRUCTURED_OUTPUT.value: True
        }

    def estimate_cost(self, request: AIRequest, model_id: str) -> CostEstimate:
        char_count = sum(len(str(m.content)) for m in request.messages)
        in_tokens = max(10, char_count // 4)
        out_tokens = min(request.max_output_tokens, 1000)
        pricing = (0.075, 0.30)
        for m in self._models:
            if m["model_id"] == model_id:
                pricing = (m.get("cost_per_million_input", 0.075), m.get("cost_per_million_output", 0.30))
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
            "provider": "gemini",
            "has_api_key": has_key,
            "models_available": [m["model_id"] for m in self._models] if has_key else []
        }

    def test_connection(self) -> Dict[str, Any]:
        key = self._get_api_key()
        if not key or len(key) < 5:
            self._is_connected = False
            return {
                "provider_id": "gemini",
                "status": ProviderStatus.NOT_CONFIGURED.value,
                "connected": False,
                "configured": False,
                "error": "Gemini API key not configured"
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        req = urllib.request.Request(url, method="GET")
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                lat = round((time.time() - t0) * 1000, 2)
                if resp.status == 200:
                    self._is_connected = True
                    self._last_error = None
                    return {
                        "provider_id": "gemini",
                        "status": ProviderStatus.CONNECTED.value,
                        "connected": True,
                        "configured": True,
                        "latency_ms": lat,
                        "message": "Google Gemini API connected and reachable"
                    }
        except urllib.error.HTTPError as e:
            self._is_connected = False
            lat = round((time.time() - t0) * 1000, 2)
            code = e.code
            if code in [400, 401, 403]:
                err_status = "AUTHENTICATION_FAILED"
                msg = "Invalid Gemini API key or unauthorized request"
            elif code == 429:
                err_status = "RATE_LIMITED"
                msg = "Gemini rate limit or quota exceeded"
            else:
                err_status = "PROVIDER_ERROR"
                msg = f"Gemini API error HTTP {code}"
            self._last_error = msg
            return {
                "provider_id": "gemini",
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
                "provider_id": "gemini",
                "status": "NETWORK_ERROR",
                "connected": False,
                "configured": True,
                "latency_ms": lat,
                "error": f"Network error connecting to Gemini: {msg}"
            }

    def discover_models(self) -> List[Dict[str, Any]]:
        key = self._get_api_key()
        if not key:
            return self._models
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models_raw = data.get("models", [])
                    discovered = []
                    for m in models_raw:
                        mid = m.get("name", "").replace("models/", "")
                        if "gemini" in mid.lower():
                            discovered.append({
                                "model_id": mid,
                                "name": m.get("displayName", f"Gemini {mid}"),
                                "version": "discovered",
                                "context_window": m.get("inputTokenLimit", 1048576),
                                "cost_per_million_input": 0.075,
                                "cost_per_million_output": 0.30,
                                "capabilities": {
                                    ModelCapability.REASONING.value: True,
                                    ModelCapability.VISION.value: True,
                                    ModelCapability.AUDIO.value: True,
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
            get_secret_provider().set_secret("GEMINI_API_KEY", key)
            self._explicit_key = key

    def generate(self, request: AIRequest) -> AIResponse:
        key = self._get_api_key()
        if not key:
            raise AIAuthenticationError("Gemini API key is missing or not configured")

        model = request.model_preference or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

        contents = []
        for m in request.messages:
            role = "user" if m.role in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": str(m.content)}]})

        payload = {"contents": contents}
        if request.output_schema:
            payload["generationConfig"] = {"responseMimeType": "application/json"}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=request.timeout_ms / 1000.0) as resp:
                raw_data = json.loads(resp.read().decode("utf-8"))
                candidate = raw_data["candidates"][0]
                content = candidate["content"]["parts"][0]["text"]
                meta = raw_data.get("usageMetadata", {})

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
                        "input_tokens": meta.get("promptTokenCount", 0),
                        "output_tokens": meta.get("candidatesTokenCount", 0),
                        "total_tokens": meta.get("totalTokenCount", 0)
                    },
                    structured_data=structured
                )
        except Exception as e:
            sanitized = get_secret_provider().redact(str(e))
            raise RuntimeError(f"Gemini generation failed: {sanitized}")

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        resp = self.generate(request)
        yield AIStreamEvent(chunk=resp.content, is_final=True)
