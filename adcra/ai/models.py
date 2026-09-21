"""
ADCRA AI Brain — Model Registry
Manages discovery, capabilities, context windows, and cost profiles of all available AI models.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger("adcra.ai.models")


class ModelRegistry:
    def __init__(self, config_path: Optional[str] = None):
        self._models: Dict[str, Dict[str, Any]] = {}
        if config_path:
            self._config_path = Path(config_path)
        else:
            self._config_path = Path(__file__).resolve().parents[2] / "config" / "ai-model-registry.json"
        self.load()

    def load(self) -> None:
        if self._config_path.is_file():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for m in data.get("models", []):
                        self._models[m["model_id"]] = m
                logger.info(f"Loaded {len(self._models)} models from {self._config_path}")
            except Exception as e:
                logger.error(f"Failed to load model registry from {self._config_path}: {e}")

    def register_model(self, model_def: Dict[str, Any]) -> None:
        model_id = model_def.get("model_id")
        if not model_id:
            raise ValueError("model_def must include 'model_id'")
        self._models[model_id] = model_def

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        return self._models.get(model_id)

    def list_models(
        self,
        provider: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for m in self._models.values():
            if provider and m.get("provider") != provider:
                continue
            if status and m.get("status") != status:
                continue
            results.append(m)
        return results

    def find_compatible_models(
        self,
        required_capabilities: List[str],
        max_cost_input_per_m: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        compatible = []
        for m in self._models.values():
            if m.get("status") != "ACTIVE":
                continue
            caps = m.get("capabilities", {})
            has_all = True
            for req in required_capabilities:
                if not caps.get(req, False):
                    has_all = False
                    break
            if not has_all:
                continue

            if max_cost_input_per_m is not None:
                cost_in = m.get("cost_per_million_input", 999.0)
                if cost_in > max_cost_input_per_m:
                    continue

            compatible.append(m)
        return compatible


_GLOBAL_REGISTRY = ModelRegistry()

def get_model_registry() -> ModelRegistry:
    return _GLOBAL_REGISTRY
