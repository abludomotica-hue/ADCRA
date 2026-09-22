"""
ADCRA AI Intelligence Control Plane — Canonical Capability System & Discovery Engine
Defines granular capabilities, capability requirements, verification probes, dynamic capability
matrices, and the central CapabilityRegistry.
"""

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
import enum

logger = logging.getLogger("adcra.ai.capabilities")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class CapabilityCategory(str, enum.Enum):
    GENERATION = "generation"
    REASONING = "reasoning"
    MULTIMODAL = "multimodal"
    CREATIVE = "creative"
    STRATEGY = "strategy"
    ANALYSIS = "analysis"
    PRODUCTION = "production"
    TOOLING = "tooling"
    STREAMING = "streaming"
    MEMORY = "memory"
    AUDIO = "audio"


class CapabilitySource(str, enum.Enum):
    PROVIDER_METADATA = "PROVIDER_METADATA"
    STATIC_REGISTRY = "STATIC_REGISTRY"
    RUNTIME_PROBE = "RUNTIME_PROBE"
    VERIFIED_TEST = "VERIFIED_TEST"
    USER_DECLARED = "USER_DECLARED"


class CapabilityStatus(str, enum.Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"
    DEGRADED = "DEGRADED"
    EXPERIMENTAL = "EXPERIMENTAL"


@dataclass
class Capability:
    id: str
    name: str
    category: str
    description: str
    input_types: List[str] = field(default_factory=lambda: ["text"])
    output_types: List[str] = field(default_factory=lambda: ["text"])
    supported_modalities: List[str] = field(default_factory=lambda: ["text"])
    required_features: List[str] = field(default_factory=list)
    optional_features: List[str] = field(default_factory=list)
    default_latency_max_ms: int = 15000
    version: str = "1.0.0"
    status: str = "stable"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CapabilityRequirement:
    capability: str
    modality: Optional[str] = None
    min_quality: str = "standard"  # "low", "standard", "high", "highest"
    max_latency_ms: Optional[int] = None
    max_cost_per_m: Optional[float] = None
    required_features: List[str] = field(default_factory=list)
    optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModelCapabilityEntry:
    capability: str
    supported: bool
    source: CapabilitySource = CapabilitySource.STATIC_REGISTRY
    confidence: float = 1.0
    last_verified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "supported": self.supported,
            "source": self.source.value if hasattr(self.source, "value") else str(self.source),
            "confidence": self.confidence,
            "last_verified": self.last_verified,
            "version": self.version,
            "metadata": self.metadata
        }


@dataclass
class CapabilityReport:
    model_id: str
    provider_id: str
    supported: List[str] = field(default_factory=list)
    unsupported: List[str] = field(default_factory=list)
    degraded: List[str] = field(default_factory=list)
    experimental: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------------------
# PROBE CACHE & BASE PROBE
# ------------------------------------------------------------------------------

class ProbeCache:
    """Cache en memoria con TTL configurable para resultados de probes."""
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["data"]
            del self._cache[key]
        return None

    def set(self, key: str, data: Any) -> None:
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }

    def clear(self) -> None:
        self._cache.clear()


class CapabilityProbe(ABC):
    """Interfaz abstracta para probes ligeros de verificación de capacidades."""
    @property
    @abstractmethod
    def capability_id(self) -> str:
        pass

    @property
    @abstractmethod
    def timeout_sec(self) -> float:
        pass

    @abstractmethod
    def execute_probe(self, provider_id: str, model_id: str, gateway: Any) -> Dict[str, Any]:
        """Ejecuta un micro-test para verificar si el modelo soporta la capacidad en runtime."""
        pass


class TextProbe(CapabilityProbe):
    capability_id = "text_generation"
    timeout_sec = 5.0

    def execute_probe(self, provider_id: str, model_id: str, gateway: Any) -> Dict[str, Any]:
        from adcra.ai.types import AIRequest, AIMessage
        req = AIRequest(
            request_id=f"probe_txt_{int(time.time()*1000)}",
            model_preference=model_id,
            messages=[AIMessage(role="user", content="Ping. Answer 'PONG'.")],
            max_output_tokens=10,
            timeout_ms=int(self.timeout_sec * 1000)
        )
        t0 = time.time()
        resp = gateway.execute(req, provider_id=provider_id)
        latency = round((time.time() - t0) * 1000, 2)
        passed = bool(resp and resp.content)
        return {
            "capability": self.capability_id,
            "passed": passed,
            "latency_ms": latency,
            "status": CapabilityStatus.SUPPORTED.value if passed else CapabilityStatus.UNSUPPORTED.value
        }


class JsonProbe(CapabilityProbe):
    capability_id = "structured_generation"
    timeout_sec = 8.0

    def execute_probe(self, provider_id: str, model_id: str, gateway: Any) -> Dict[str, Any]:
        from adcra.ai.types import AIRequest, AIMessage
        schema = {
            "type": "object",
            "properties": {"probe_status": {"type": "string"}, "score": {"type": "integer"}},
            "required": ["probe_status", "score"]
        }
        req = AIRequest(
            request_id=f"probe_json_{int(time.time()*1000)}",
            model_preference=model_id,
            messages=[AIMessage(role="user", content="Generate JSON adhering to schema.")],
            output_schema=schema,
            max_output_tokens=30,
            timeout_ms=int(self.timeout_sec * 1000)
        )
        t0 = time.time()
        resp = gateway.execute(req, provider_id=provider_id)
        latency = round((time.time() - t0) * 1000, 2)
        passed = bool(resp and (resp.structured_data or "{" in resp.content))
        return {
            "capability": self.capability_id,
            "passed": passed,
            "latency_ms": latency,
            "status": CapabilityStatus.SUPPORTED.value if passed else CapabilityStatus.DEGRADED.value
        }


class ToolProbe(CapabilityProbe):
    capability_id = "tool_use"
    timeout_sec = 8.0

    def execute_probe(self, provider_id: str, model_id: str, gateway: Any) -> Dict[str, Any]:
        from adcra.ai.types import AIRequest, AIMessage, AIToolDefinition
        dummy_tool = AIToolDefinition(
            tool_id="test_probe_tool",
            name="test_probe_tool",
            description="Returns probe confirmation",
            category="test",
            version="1.0.0",
            input_schema={"type": "object", "properties": {"val": {"type": "string"}}},
            output_schema={"type": "object"}
        )
        req = AIRequest(
            request_id=f"probe_tool_{int(time.time()*1000)}",
            model_preference=model_id,
            messages=[AIMessage(role="user", content="Call test_probe_tool with val='test'.")],
            tools=[dummy_tool],
            max_output_tokens=50,
            timeout_ms=int(self.timeout_sec * 1000)
        )
        t0 = time.time()
        resp = gateway.execute(req, provider_id=provider_id)
        latency = round((time.time() - t0) * 1000, 2)
        passed = bool(resp and (resp.tool_calls or "test_probe_tool" in resp.content))
        return {
            "capability": self.capability_id,
            "passed": passed,
            "latency_ms": latency,
            "status": CapabilityStatus.SUPPORTED.value if passed else CapabilityStatus.UNSUPPORTED.value
        }


# ------------------------------------------------------------------------------
# CAPABILITY REGISTRY & DISCOVERY ENGINE
# ------------------------------------------------------------------------------

class CapabilityRegistry:
    """
    Registro canónico y dinámico de capacidades de IA en ADCRA.
    Carga ai-capabilities.json y mapea capacidades a modelos y Brain Profiles.
    """
    def __init__(self, config_file: Optional[Path] = None):
        self._path = config_file or (WORKSPACE_ROOT / "config" / "ai-capabilities.json")
        self._capabilities: Dict[str, Capability] = {}
        self._model_matrix: Dict[str, Dict[str, ModelCapabilityEntry]] = {}
        self.probe_cache = ProbeCache(ttl_seconds=1800)
        self._probes: Dict[str, CapabilityProbe] = {
            "text_generation": TextProbe(),
            "structured_generation": JsonProbe(),
            "tool_use": ToolProbe()
        }
        self.load()

    def load(self) -> None:
        if self._path.is_file():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("capabilities", []):
                        cap = Capability(**item)
                        self._capabilities[cap.id] = cap
                logger.info(f"Loaded {len(self._capabilities)} capabilities from {self._path}")
            except Exception as e:
                logger.error(f"Failed to load capabilities config: {e}")
        else:
            logger.warning(f"Capabilities config not found at {self._path}")

    def register_capability(self, cap: Capability) -> None:
        self._capabilities[cap.id] = cap

    def get_capability(self, cap_id: str) -> Optional[Capability]:
        return self._capabilities.get(cap_id)

    def list_capabilities(self, category: Optional[str] = None) -> List[Capability]:
        if category:
            return [c for c in self._capabilities.values() if c.category == category]
        return list(self._capabilities.values())

    def register_model_capability(
        self,
        model_id: str,
        capability_id: str,
        supported: bool,
        source: CapabilitySource = CapabilitySource.STATIC_REGISTRY,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        if model_id not in self._model_matrix:
            self._model_matrix[model_id] = {}
        entry = ModelCapabilityEntry(
            capability=capability_id,
            supported=supported,
            source=source,
            confidence=confidence,
            metadata=metadata or {}
        )
        self._model_matrix[model_id][capability_id] = entry

    def get_model_capabilities(self, model_id: str) -> Dict[str, ModelCapabilityEntry]:
        """Devuelve el mapa de capacidades registradas para un modelo."""
        return self._model_matrix.get(model_id, {})

    def is_model_capable(self, model_id: str, capability_id: str) -> bool:
        caps = self._model_matrix.get(model_id, {})
        entry = caps.get(capability_id)
        return bool(entry and entry.supported)

    def evaluate_model_satisfaction(
        self,
        model_id: str,
        requirements: List[CapabilityRequirement]
    ) -> Dict[str, Any]:
        """Evalúa si un modelo satisface una lista de requisitos de capacidad."""
        missing = []
        satisfied = []
        for req in requirements:
            if self.is_model_capable(model_id, req.capability):
                satisfied.append(req.capability)
            else:
                if not req.optional:
                    missing.append(req.capability)
        return {
            "model_id": model_id,
            "compatible": len(missing) == 0,
            "satisfied": satisfied,
            "missing": missing
        }

    def run_probe(self, capability_id: str, provider_id: str, model_id: str, gateway: Any) -> Dict[str, Any]:
        """Ejecuta un probe específico para una capacidad y actualiza la matriz."""
        cache_key = f"{provider_id}:{model_id}:{capability_id}"
        cached = self.probe_cache.get(cache_key)
        if cached:
            return cached

        probe = self._probes.get(capability_id)
        if not probe:
            res = {
                "capability": capability_id,
                "passed": False,
                "status": CapabilityStatus.UNKNOWN.value,
                "error": f"No probe implementation for capability '{capability_id}'"
            }
            return res

        try:
            res = probe.execute_probe(provider_id=provider_id, model_id=model_id, gateway=gateway)
            self.register_model_capability(
                model_id=model_id,
                capability_id=capability_id,
                supported=res.get("passed", False),
                source=CapabilitySource.RUNTIME_PROBE,
                confidence=0.95,
                metadata={"latency_ms": res.get("latency_ms")}
            )
            self.probe_cache.set(cache_key, res)
            return res
        except Exception as e:
            logger.error(f"Probe execution failed for {cache_key}: {e}")
            res = {
                "capability": capability_id,
                "passed": False,
                "status": CapabilityStatus.DEGRADED.value,
                "error": str(e)
            }
            self.probe_cache.set(cache_key, res)
            return res


class CapabilityDiscoveryEngine:
    """
    Descubre y audita capacidades reales de modelos combinando:
    1. Metadatos estáticos de ModelRegistry
    2. Probes activos de runtime
    3. Health status
    4. Observaciones históricas
    """
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or get_capability_registry()

    def discover_model_capabilities(
        self,
        model_id: str,
        provider_id: str,
        raw_model_def: Dict[str, Any]
    ) -> CapabilityReport:
        report = CapabilityReport(model_id=model_id, provider_id=provider_id)
        caps = raw_model_def.get("capabilities", {})

        # Mapeo de flags antiguos a nuevas capacidades canónicas
        flag_to_cap = {
            "reasoning": "strategic_reasoning",
            "vision": "multimodal_vision",
            "audioInput": "audio_understanding",
            "imageGeneration": "image_generation",
            "videoGeneration": "video_generation",
            "toolCalling": "tool_use",
            "structuredOutput": "structured_generation",
            "streaming": "streaming"
        }

        # Siempre soportan text_generation si están activos
        self.registry.register_model_capability(
            model_id=model_id,
            capability_id="text_generation",
            supported=True,
            source=CapabilitySource.STATIC_REGISTRY
        )
        report.supported.append("text_generation")

        for flag, is_sup in caps.items():
            canonical_cap = flag_to_cap.get(flag)
            if canonical_cap:
                self.registry.register_model_capability(
                    model_id=model_id,
                    capability_id=canonical_cap,
                    supported=bool(is_sup),
                    source=CapabilitySource.STATIC_REGISTRY
                )
                if is_sup:
                    report.supported.append(canonical_cap)
                else:
                    report.unsupported.append(canonical_cap)

        # Habilidades creativas implícitas para modelos de alta calidad
        if caps.get("reasoning", False):
            for creative_cap in ["creative_writing", "brand_analysis", "audience_analysis", "storyboard_generation", "copy_generation", "marketing_analysis"]:
                self.registry.register_model_capability(
                    model_id=model_id,
                    capability_id=creative_cap,
                    supported=True,
                    source=CapabilitySource.STATIC_REGISTRY
                )
                report.supported.append(creative_cap)

        return report


_GLOBAL_CAPABILITY_REGISTRY = CapabilityRegistry()
_GLOBAL_DISCOVERY_ENGINE = CapabilityDiscoveryEngine(_GLOBAL_CAPABILITY_REGISTRY)

def get_capability_registry() -> CapabilityRegistry:
    return _GLOBAL_CAPABILITY_REGISTRY

def get_discovery_engine() -> CapabilityDiscoveryEngine:
    return _GLOBAL_DISCOVERY_ENGINE
