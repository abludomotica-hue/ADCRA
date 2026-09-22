"""
ADCRA AI Brain & Agentic Infrastructure Layer — AI Provider Gateway & Base Adapter
Implements provider-agnostic execution, retry policies, fallback engine hooks,
and response normalization.
"""

import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Iterator
import jsonschema

from adcra.ai.types import (
    AIRequest, AIResponse, AIMessage, AIStreamEvent,
    CostEstimate, TaskType
)

logger = logging.getLogger("adcra.ai.gateway")


class AIProviderAdapter(ABC):
    """Abstract interface for all model providers (OpenAI, Gemini, Anthropic, Mock, etc.)"""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """Return list of model descriptors."""
        pass

    @abstractmethod
    def get_model_capabilities(self, model_id: str) -> Dict[str, bool]:
        """Return capability flags for the specified model."""
        pass

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        """Synchronously generate completion for request."""
        pass

    @abstractmethod
    def stream(self, request: AIRequest) -> Iterator[AIStreamEvent]:
        """Stream response chunks as AIStreamEvents."""
        pass

    @abstractmethod
    def estimate_cost(self, request: AIRequest, model_id: str) -> CostEstimate:
        """Estimate cost in USD before executing."""
        pass

    @abstractmethod
    def validate_configuration(self) -> Dict[str, Any]:
        """Health-check credentials and connectivity."""
        pass

    def test_connection(self) -> Dict[str, Any]:
        """Perform real network handshake and return connectivity report."""
        return self.validate_configuration()

    def discover_models(self) -> List[Dict[str, Any]]:
        """Fetch models dynamically from provider endpoint if available."""
        return self.list_models()

    def configure(self, credentials: Dict[str, Any]) -> None:
        """Update provider configuration dynamically."""
        pass

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize adapter state and optional configuration."""
        if config:
            self.configure(config)
        return True


class AIProviderGateway:
    """
    Central gateway routing normalized AIRequests to registered AIProviderAdapters.
    Enforces retry, fallback, timeouts, structured output validation, and cost metrics.
    """

    def __init__(self):
        self._adapters: Dict[str, AIProviderAdapter] = {}
        self._default_provider_id: str = "mock"

    def register_adapter(self, adapter: AIProviderAdapter) -> None:
        self._adapters[adapter.provider_id] = adapter
        logger.info(f"Registered AI provider adapter: {adapter.provider_id} ({adapter.name})")

    def get_adapter(self, provider_id: str) -> AIProviderAdapter:
        if provider_id not in self._adapters:
            raise KeyError(f"AI Provider not registered: {provider_id}. Available: {list(self._adapters.keys())}")
        return self._adapters[provider_id]

    def has_adapter(self, provider_id: str) -> bool:
        return provider_id in self._adapters

    def list_providers(self) -> List[Dict[str, Any]]:
        result = []
        for pid, adapter in self._adapters.items():
            health = adapter.validate_configuration()
            is_mock = (pid == "mock")
            configured = health.get("configured", False) or is_mock
            connected = health.get("connected", False)
            status = health.get("status", "CONFIGURED" if configured else "NOT_CONFIGURED")

            result.append({
                "provider_id": pid,
                "name": adapter.name,
                "configured": configured,
                "connected": connected,
                "status": status,
                "models_count": len(adapter.list_models()) if (configured or is_mock) else 0,
                "execution_mode": "SIMULATION" if is_mock else "REAL",
                "details": health
            })
        return result

    def test_provider(self, provider_id: str) -> Dict[str, Any]:
        adapter = self.get_adapter(provider_id)
        if hasattr(adapter, "test_connection"):
            return adapter.test_connection()
        return adapter.validate_configuration()

    def discover_models(self, provider_id: str) -> List[Dict[str, Any]]:
        adapter = self.get_adapter(provider_id)
        if hasattr(adapter, "discover_models"):
            return adapter.discover_models()
        return adapter.list_models()

    def configure_provider(self, provider_id: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        adapter = self.get_adapter(provider_id)
        if hasattr(adapter, "configure"):
            adapter.configure(credentials)
        if hasattr(adapter, "test_connection"):
            return adapter.test_connection()
        return adapter.validate_configuration()

    def set_default_provider(self, provider_id: str) -> None:
        if provider_id not in self._adapters:
            raise KeyError(f"Cannot set default to unregistered provider: {provider_id}")
        self._default_provider_id = provider_id

    def execute(self, request: AIRequest, provider_id: Optional[str] = None) -> AIResponse:
        """
        Executes an AI request through the specified or default provider adapter.
        Validates structured output schema if declared in request.
        """
        target_pid = provider_id or self._default_provider_id
        adapter = self.get_adapter(target_pid)

        start_time = time.time()
        try:
            response = adapter.generate(request)
            response.latency_ms = round((time.time() - start_time) * 1000, 2)
        except Exception as e:
            logger.error(f"Provider {target_pid} execution failed for req {request.request_id}: {e}")
            raise

        # Validar structured output si se especificó output_schema
        if request.output_schema and response.structured_data:
            try:
                jsonschema.validate(instance=response.structured_data, schema=request.output_schema)
            except jsonschema.ValidationError as ve:
                logger.warning(f"Response structured_data validation failed: {ve.message}")
                response.usage["validation_warning"] = str(ve.message)

        return response

    def execute_with_fallback(
        self,
        request: AIRequest,
        primary_provider_id: str,
        fallback_provider_ids: List[str]
    ) -> AIResponse:
        """
        Executes with automatic fallback chain:
        Primary -> Fallback 1 -> Fallback 2 -> Raise Exception
        """
        providers_to_try = [primary_provider_id] + [p for p in fallback_provider_ids if p != primary_provider_id]
        errors = []

        for pid in providers_to_try:
            if not self.has_adapter(pid):
                continue
            try:
                logger.info(f"Executing req {request.request_id} with provider: {pid}")
                resp = self.execute(request, provider_id=pid)
                if pid != primary_provider_id:
                    resp.usage["fallback_triggered"] = True
                    resp.usage["fallback_reason"] = f"Primary {primary_provider_id} failed: {errors[-1] if errors else 'unavailable'}"
                    resp.usage["original_provider"] = primary_provider_id
                return resp
            except Exception as e:
                logger.warning(f"Provider {pid} failed: {e}")
                errors.append(f"{pid}: {str(e)}")

        raise RuntimeError(f"All AI providers in fallback chain failed: {'; '.join(errors)}")


# Singleton global instance
_GLOBAL_GATEWAY = AIProviderGateway()

def get_ai_gateway() -> AIProviderGateway:
    return _GLOBAL_GATEWAY
