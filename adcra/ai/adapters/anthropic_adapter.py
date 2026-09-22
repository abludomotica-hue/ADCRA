"""
ADCRA AI Brain — Anthropic Claude Provider Adapter
Supports Claude 3.5 Sonnet, Claude 3.5 Haiku, and high-fidelity creative copy analysis.
Features real connection testing, SecretProvider integration, and model discovery.
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


class AnthropicProvider(AIProviderAdapter):
    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key
        self._is_connected = False
        self._last_error: Optional[str] = None
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
                    ModelCapability.STREAMING.value: True
                }
            },
            {
                "model_id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku High-Speed",
                "version": "2024-10-22",
                "context_window": 200000,
                "cost_per_million_input": 0.80,
                "cost_per_million_output": 4.00,
                "capabilities": {
                    ModelCapability.REASONING.value: True,
                    ModelCapability.VISION.value: True,
                    ModelCapability.TOOL_CALLING.value: True,
                    ModelCapability.STRUCTURED_OUTPUT.value: True,
                    ModelCapability.STREAMING.value: True
                }
            }
        ]

    def _get_api_key(self) -> str:
        if self._explicit_key:
            return self._explicit_key
        return get_secret_provider().get_secret("ANTHROPIC_API_KEY", "") or ""

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
            ModelCapability.STRUCTURED_OUTPUT.value: True
        }

    def estimate_cost(self, request: AIRequest, model_id: str) -> CostEstimate:
        char_count = sum(len(str(m.content)) for m in request.messages)
        in_tokens = max(10, char_count // 4)
        out_tokens = min(request.max_output_tokens, 1000)
        pricing = (3.00, 15.00)
        for m in self._models:
            if m["model_id"] == model_id:
                pricing = (m.get("cost_per_million_input", 3.00), m.get("cost_per_million_output", 15.00))
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
            "provider": "anthropic",
            "has_api_key": has_key,
            "models_available": [m["model_id"] for m in self._models] if has_key else []
        }

    def test_connection(self) -> Dict[str, Any]:
        key = self._get_api_key()
        if not key or len(key) < 5:
            self._is_connected = False
            return {
                "provider_id": "anthropic",
                "status": ProviderStatus.NOT_CONFIGURED.value,
                "connected": False,
                "configured": False,
                "error": "Anthropic API key not configured"
            }

        url = "https://api.anthropic.com/v1/models"
        req = urllib.request.Request(
            url,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
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
                        "provider_id": "anthropic",
                        "status": ProviderStatus.CONNECTED.value,
                        "connected": True,
                        "configured": True,
                        "latency_ms": lat,
                        "message": "Anthropic API connected successfully"
                    }
        except urllib.error.HTTPError as e:
            self._is_connected = False
            lat = round((time.time() - t0) * 1000, 2)
            code = e.code
            if code in [401, 403]:
                err_status = "AUTHENTICATION_FAILED"
                msg = "Invalid Anthropic API key"
            elif code == 429:
                err_status = "RATE_LIMITED"
                msg = "Anthropic rate limit exceeded"
            else:
                err_status = "PROVIDER_ERROR"
                msg = f"Anthropic error HTTP {code}"
            self._last_error = msg
            return {
                "provider_id": "anthropic",
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
                "provider_id": "anthropic",
                "status": "NETWORK_ERROR",
                "connected": False,
                "configured": True,
                "latency_ms": lat,
                "error": f"Network error connecting to Anthropic: {msg}"
            }

    def discover_models(self) -> List[Dict[str, Any]]:
        key = self._get_api_key()
        if not key:
            return self._models
        url = "https://api.anthropic.com/v1/models"
        req = urllib.request.Request(
            url,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01"
            },
            method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models_raw = data.get("data", [])
                    discovered = []
                    for m in models_raw:
                        mid = m.get("id", "")
                        discovered.append({
                            "model_id": mid,
                            "name": m.get("display_name", f"Claude {mid}"),
                            "version": "discovered",
                            "context_window": 200000,
                            "cost_per_million_input": 3.00,
                            "cost_per_million_output": 15.00,
                            "capabilities": {
                                ModelCapability.REASONING.value: True,
                                ModelCapability.VISION.value: True,
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
            get_secret_provider().set_secret("ANTHROPIC_API_KEY", key)
            self._explicit_key = key

    def generate(self, request: AIRequest) -> AIResponse:
        key = self._get_api_key()
        if not key:
            raise AIAuthenticationError("Anthropic API key is missing or not configured")

        model = request.model_preference or "claude-3-5-sonnet-20241022"
        url = "https://api.anthropic.com/v1/messages"

        system_msg = ""
        user_msgs = []
        for m in request.messages:
            if m.role == "system":
                system_msg = str(m.content)
            else:
                user_msgs.append({"role": m.role, "content": str(m.content)})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": user_msgs,
            "max_tokens": request.max_output_tokens,
            "temperature": request.temperature
        }
        if system_msg:
            payload["system"] = system_msg

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=request.timeout_ms / 1000.0) as resp:
                raw_data = json.loads(resp.read().decode("utf-8"))
                content = raw_data["content"][0]["text"]
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
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                    },
                    structured_data=structured
                )
        except Exception as e:
            sanitized = get_secret_provider().redact(str(e))
            raise RuntimeError(f"Anthropic generation failed: {sanitized}")

    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        resp = self.generate(request)
        yield AIStreamEvent(chunk=resp.content, is_final=True)
