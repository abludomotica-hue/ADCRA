"""
ADCRA AI Intelligence Control Plane — Model Policy Engine & Logical Aliases
Enforces multi-objective optimization (quality, latency, cost, locality, multimodal)
and translates logical aliases (creative.high, strategy.deep, copy.fast) into physical routes.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import enum
from pathlib import Path

logger = logging.getLogger("adcra.ai.policies")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class ModelPolicy(str, enum.Enum):
    QUALITY_FIRST = "QUALITY_FIRST"
    COST_OPTIMIZED = "COST_OPTIMIZED"
    BALANCED = "BALANCED"
    LOW_LATENCY = "LOW_LATENCY"
    HIGH_REASONING = "HIGH_REASONING"
    MULTIMODAL_FIRST = "MULTIMODAL_FIRST"
    LOCAL_FIRST = "LOCAL_FIRST"
    PROVIDER_PREFERRED = "PROVIDER_PREFERRED"
    FALLBACK_FIRST = "FALLBACK_FIRST"
    EXPERIMENTAL = "EXPERIMENTAL"


class ModelPolicyEngine:
    def __init__(self, config_path: Optional[Path] = None):
        self._path = config_path or (WORKSPACE_ROOT / "config" / "ai-routing-policies.json")
        self._aliases: Dict[str, Dict[str, Any]] = {}
        self._default_policy: ModelPolicy = ModelPolicy.BALANCED
        self.load()

    def load(self) -> None:
        if self._path.is_file():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._aliases = data.get("aliases", {})
                    def_pol = data.get("default_policy", "BALANCED")
                    self._default_policy = ModelPolicy(def_pol) if def_pol in ModelPolicy.__members__ else ModelPolicy.BALANCED
                logger.info(f"Loaded {len(self._aliases)} model aliases from {self._path}")
            except Exception as e:
                logger.error(f"Failed to load routing policies: {e}")

    def resolve_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        return self._aliases.get(alias)

    def list_aliases(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._aliases)

    def score_candidate(
        self,
        model_def: Dict[str, Any],
        policy: ModelPolicy = ModelPolicy.BALANCED,
        capability_score: float = 100.0,
        historical_latency_ms: float = 500.0
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calcula el score compuesto (0 - 100) para un modelo candidato según la política activa.
        Retorna (score_total, desglose_detallado).
        """
        quality = float(model_def.get("quality_score", 80))
        speed = float(model_def.get("speed_score", 80))
        cost_in = float(model_def.get("cost_per_million_input", 1.0))
        cost_out = float(model_def.get("cost_per_million_output", 2.0))
        total_cost = cost_in + cost_out

        # Normalización de costo (menor costo = mayor puntuación, 0-100)
        cost_score = max(0.0, min(100.0, 100.0 - (total_cost * 5.0)))

        breakdown = {
            "capability_match": round(capability_score, 2),
            "quality_score": round(quality, 2),
            "speed_score": round(speed, 2),
            "cost_efficiency": round(cost_score, 2)
        }

        if policy == ModelPolicy.QUALITY_FIRST or policy == ModelPolicy.HIGH_REASONING:
            total = (capability_score * 0.4) + (quality * 0.45) + (speed * 0.1) + (cost_score * 0.05)
        elif policy == ModelPolicy.COST_OPTIMIZED:
            total = (capability_score * 0.3) + (cost_score * 0.5) + (speed * 0.1) + (quality * 0.1)
        elif policy == ModelPolicy.LOW_LATENCY:
            total = (capability_score * 0.3) + (speed * 0.5) + (quality * 0.1) + (cost_score * 0.1)
        elif policy == ModelPolicy.MULTIMODAL_FIRST:
            caps = model_def.get("capabilities", {})
            mm_bonus = 20.0 if (caps.get("vision") or caps.get("audioInput") or caps.get("videoGeneration")) else 0.0
            total = (capability_score * 0.35) + (quality * 0.35) + (cost_score * 0.1) + (speed * 0.1) + mm_bonus
        elif policy == ModelPolicy.LOCAL_FIRST:
            is_local = 30.0 if model_def.get("provider") in ["ollama", "vllm", "local"] else 0.0
            total = (capability_score * 0.3) + (quality * 0.3) + (cost_score * 0.2) + is_local
        else:  # BALANCED
            total = (capability_score * 0.35) + (quality * 0.35) + (speed * 0.15) + (cost_score * 0.15)

        return (round(total, 2), breakdown)


_GLOBAL_POLICY_ENGINE = ModelPolicyEngine()

def get_policy_engine() -> ModelPolicyEngine:
    return _GLOBAL_POLICY_ENGINE
