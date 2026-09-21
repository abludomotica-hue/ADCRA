"""
ADCRA AI Brain — Profiles Management
Configurable persona and capability profiles (Creative Director, Strategist, QC Director, etc.).
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger("adcra.ai.profiles")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class ProfileManager:
    def __init__(self, profiles_file: Optional[Path] = None):
        self._path = profiles_file or (WORKSPACE_ROOT / "config" / "ai-brain-profiles.json")
        self._profiles: Dict[str, Dict[str, Any]] = {}
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

    def list_profiles(self) -> List[Dict[str, Any]]:
        return list(self._profiles.values())

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        return self._profiles.get(profile_id)


_GLOBAL_PROFILES = ProfileManager()

def get_profile_manager() -> ProfileManager:
    return _GLOBAL_PROFILES
