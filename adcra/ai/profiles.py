"""
ADCRA AI Brain — Profiles Management & Legacy Bridge
Provides backwards-compatible interface for ProfileManager while bridging to BrainRegistry.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from adcra.ai.brains import get_brain_registry, BrainProfile

logger = logging.getLogger("adcra.ai.profiles")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class ProfileManager:
    """
    Gestiona perfiles cognitivos. Carga tanto la configuración heredada
    (ai-brain-profiles.json) como la nueva especificación canónica (ai-brains.json).
    """
    def __init__(self, profiles_file: Optional[Path] = None):
        self._path = profiles_file or (WORKSPACE_ROOT / "config" / "ai-brain-profiles.json")
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self.brain_registry = get_brain_registry()
        self._load()

    def _load(self) -> None:
        if self._path.is_file():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p in data.get("profiles", []):
                        self._profiles[p["profile_id"]] = p
            except Exception as e:
                logger.error(f"Error loading AI brain profiles: {e}")

        # Incorporar perfiles desde BrainRegistry para compatibilidad unificada
        for brain in self.brain_registry.list_brains():
            if brain.id not in self._profiles:
                self._profiles[brain.id] = {
                    "profile_id": brain.id,
                    "name": brain.name,
                    "description": brain.purpose,
                    "required_capabilities": brain.required_capabilities,
                    "quality_policy": brain.quality_policy,
                    "latency_policy": brain.latency_policy,
                    "cost_policy": brain.cost_policy,
                    "model_policy": brain.model_policy,
                    "autonomy": brain.approval_policy.lower()
                }

    def list_profiles(self) -> List[Dict[str, Any]]:
        return list(self._profiles.values())

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        if profile_id in self._profiles:
            return self._profiles[profile_id]
        brain = self.brain_registry.get_brain(profile_id)
        if brain:
            return brain.to_dict()
        return None


_GLOBAL_PROFILES = ProfileManager()

def get_profile_manager() -> ProfileManager:
    return _GLOBAL_PROFILES
