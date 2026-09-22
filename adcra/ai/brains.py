"""
ADCRA AI Intelligence Control Plane — Brain Profiles & Brain Federation Engine
Implements cognitive role definitions, capability-oriented BrainProfiles, structured
BrainHandoff contracts, and collaborative BrainFederation orchestration.
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from adcra.ai.types import SourceEpistemology, AutonomyLevel
from adcra.ai.capabilities import CapabilityRequirement, get_capability_registry

logger = logging.getLogger("adcra.ai.brains")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class BrainProfile:
    id: str
    name: str
    purpose: str
    system_instructions: str
    required_capabilities: List[str] = field(default_factory=list)
    preferred_capabilities: List[str] = field(default_factory=list)
    forbidden_capabilities: List[str] = field(default_factory=list)
    quality_policy: str = "HIGH"         # HIGH, STANDARD, COST_OPTIMIZED
    latency_policy: str = "MEDIUM"       # FAST, MEDIUM, HIGH
    cost_policy: str = "BALANCED"        # QUALITY_FIRST, BALANCED, COST_OPTIMIZED
    memory_policy: str = "STRICT_ISOLATION"  # STRICT_ISOLATION, EPHEMERAL, FULL_ACCESS
    tool_policy: str = "AUTO"            # AUTO, STRICT_PERMISSIONS, NONE
    approval_policy: str = "AUTOPILOT"   # ASSIST, AUTOPILOT, AUTONOMOUS
    model_policy: str = "BALANCED"       # QUALITY_FIRST, COST_OPTIMIZED, BALANCED, LOW_LATENCY, HIGH_REASONING, MULTIMODAL_FIRST
    fallback_policy: str = "AUTO_RETRY"  # AUTO_RETRY, MOCK_FALLBACK, STRICT_FAIL
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if not d.get("description"):
            d["description"] = self.purpose
        return d

    def get_capability_requirements(self) -> List[CapabilityRequirement]:
        """Convierte los campos required y preferred en CapabilityRequirements tipados."""
        reqs = []
        for cap in self.required_capabilities:
            reqs.append(CapabilityRequirement(
                capability=cap,
                min_quality="high" if self.quality_policy == "HIGH" else "standard",
                optional=False
            ))
        for cap in self.preferred_capabilities:
            reqs.append(CapabilityRequirement(
                capability=cap,
                min_quality="standard",
                optional=True
            ))
        return reqs


@dataclass
class BrainHandoff:
    handoff_id: str
    source_brain: str
    target_brain: str
    campaign_id: str
    task_id: str
    input_context: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    confidence: float = 1.0
    epistemology: SourceEpistemology = SourceEpistemology.AI_INFERENCE
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "handoff_id": self.handoff_id,
            "source_brain": self.source_brain,
            "target_brain": self.target_brain,
            "campaign_id": self.campaign_id,
            "task_id": self.task_id,
            "input_context": self.input_context,
            "artifacts": self.artifacts,
            "decisions": self.decisions,
            "constraints": self.constraints,
            "open_questions": self.open_questions,
            "confidence": self.confidence,
            "epistemology": self.epistemology.value if hasattr(self.epistemology, "value") else str(self.epistemology),
            "timestamp": self.timestamp
        }


class BrainRegistry:
    """
    Registro unificado de Brain Profiles cognitivos en ADCRA.
    Carga ai-brains.json y expone perfiles tipados.
    """
    def __init__(self, config_path: Optional[Path] = None):
        self._path = config_path or (WORKSPACE_ROOT / "config" / "ai-brains.json")
        self._brains: Dict[str, BrainProfile] = {}
        self.load()

    def load(self) -> None:
        if self._path.is_file():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("brains", []):
                        profile = BrainProfile(**item)
                        self._brains[profile.id] = profile
                logger.info(f"Loaded {len(self._brains)} Brain Profiles from {self._path}")
            except Exception as e:
                logger.error(f"Failed to load brain profiles from {self._path}: {e}")
        else:
            logger.warning(f"Brain profiles configuration not found at {self._path}")

    def register_brain(self, brain: BrainProfile) -> None:
        self._brains[brain.id] = brain

    def get_brain(self, brain_id: str) -> Optional[BrainProfile]:
        return self._brains.get(brain_id)

    def list_brains(self) -> List[BrainProfile]:
        return list(self._brains.values())


class BrainFederationEngine:
    """
    Orquesta la colaboración y el paso de información contextual
    entre múltiples cerebros cognitivos especializados en una misma campaña.
    """
    def __init__(self, registry: Optional[BrainRegistry] = None):
        self.registry = registry or get_brain_registry()
        self._handoff_history: List[BrainHandoff] = []

    def create_handoff(
        self,
        source_brain: str,
        target_brain: str,
        campaign_id: str,
        task_id: str,
        input_context: Dict[str, Any],
        artifacts: Optional[List[Dict[str, Any]]] = None,
        decisions: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        open_questions: Optional[List[str]] = None,
        confidence: float = 1.0,
        epistemology: SourceEpistemology = SourceEpistemology.AI_INFERENCE
    ) -> BrainHandoff:
        src = self.registry.get_brain(source_brain)
        tgt = self.registry.get_brain(target_brain)
        if not src:
            logger.warning(f"Source brain '{source_brain}' not found in registry")
        if not tgt:
            logger.warning(f"Target brain '{target_brain}' not found in registry")

        handoff = BrainHandoff(
            handoff_id=f"handoff_{uuid.uuid4().hex[:8]}",
            source_brain=source_brain,
            target_brain=target_brain,
            campaign_id=campaign_id,
            task_id=task_id,
            input_context=input_context,
            artifacts=artifacts or [],
            decisions=decisions or [],
            constraints=constraints or [],
            open_questions=open_questions or [],
            confidence=confidence,
            epistemology=epistemology
        )
        self._handoff_history.append(handoff)
        logger.info(f"Created BrainHandoff {handoff.handoff_id}: {source_brain} -> {target_brain} (task: {task_id})")
        return handoff

    def list_handoffs(self, campaign_id: Optional[str] = None) -> List[BrainHandoff]:
        if campaign_id:
            return [h for h in self._handoff_history if h.campaign_id == campaign_id]
        return list(self._handoff_history)


_GLOBAL_BRAIN_REGISTRY = BrainRegistry()
_GLOBAL_FEDERATION_ENGINE = BrainFederationEngine(_GLOBAL_BRAIN_REGISTRY)

def get_brain_registry() -> BrainRegistry:
    return _GLOBAL_BRAIN_REGISTRY

def get_federation_engine() -> BrainFederationEngine:
    return _GLOBAL_FEDERATION_ENGINE
