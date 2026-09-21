"""
ADCRA AI Brain — Memory Engine & Write Validator
Manages Client Memory, Campaign Memory, and Creative Genome across 7 memory types
(FACT, OBSERVATION, HYPOTHESIS, LEARNING, PREFERENCE, REJECTION, DECISION) with strict
multi-tenant isolation and write validation.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

from adcra.ai.types import MemoryType, SourceEpistemology

logger = logging.getLogger("adcra.ai.memory")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class MemoryWriteValidator:
    """Valida procedencia, confidencialidad y consistencia antes de persistir en memoria."""

    @staticmethod
    def validate_entry(entry: Dict[str, Any]) -> None:
        required = ["tenant_id", "scope", "memory_type", "source", "confidence", "content"]
        for field in required:
            if field not in entry:
                raise ValueError(f"Memory entry missing required field: '{field}'")

        # Validar tipo de memoria
        m_type = entry["memory_type"]
        valid_types = [t.value for t in MemoryType]
        if m_type not in valid_types:
            raise ValueError(f"Invalid memory_type '{m_type}'. Must be one of: {valid_types}")

        # Regla epistemológica: Una inferencia de IA no puede guardarse directamente como FACT sin confirmación
        src = entry["source"]
        if src == SourceEpistemology.AI_INFERENCE.value and m_type == MemoryType.FACT.value:
            if not entry.get("confirmed_by_human", False):
                raise ValueError(
                    "Epistemic violation: AI_INFERENCE cannot be stored as a FACT without human confirmation. "
                    "Use HYPOTHESIS or OBSERVATION instead."
                )


class MemoryEngine:
    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = workspace_root or WORKSPACE_ROOT
        self.validator = MemoryWriteValidator()
        self._memory_store_file = self.root / "campaign" / "memory" / "episodic-memory-store.json"
        self._entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self._memory_store_file.is_file():
            try:
                with open(self._memory_store_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._entries = data.get("entries", [])
            except Exception as e:
                logger.error(f"Failed to load episodic memory store: {e}")

    def _save(self) -> None:
        try:
            self._memory_store_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._memory_store_file, "w", encoding="utf-8") as f:
                json.dump({
                    "schema_version": "1.0.0",
                    "total_entries": len(self._entries),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "entries": self._entries
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save episodic memory store: {e}")

    def write_entry(
        self,
        tenant_id: str,
        scope: str,  # 'client', 'campaign', 'creative'
        memory_type: MemoryType,
        source: SourceEpistemology,
        content: Dict[str, Any],
        confidence: float = 1.0,
        confirmed_by_human: bool = False,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        entry = {
            "entry_id": f"mem_{uuid.uuid4().hex[:8]}",
            "tenant_id": tenant_id,
            "scope": scope,
            "campaign_id": campaign_id or "unassigned",
            "memory_type": memory_type.value if hasattr(memory_type, "value") else str(memory_type),
            "source": source.value if hasattr(source, "value") else str(source),
            "confidence": min(1.0, max(0.0, confidence)),
            "confirmed_by_human": confirmed_by_human,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Validar antes de almacenar
        self.validator.validate_entry(entry)

        self._entries.append(entry)
        self._save()
        logger.info(f"Persisted memory entry {entry['entry_id']} [{scope}/{memory_type.value}]")
        return entry

    def query(
        self,
        tenant_id: str,
        scope: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        campaign_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Busca entradas en memoria con aislamiento estricto por tenant_id."""
        results = []
        for e in self._entries:
            # Multi-tenant isolation: Un tenant nunca ve entradas de otro tenant
            if e.get("tenant_id") != tenant_id:
                continue
            if scope and e.get("scope") != scope:
                continue
            if memory_type:
                t_val = memory_type.value if hasattr(memory_type, "value") else str(memory_type)
                if e.get("memory_type") != t_val:
                    continue
            if campaign_id and e.get("campaign_id") != campaign_id:
                continue
            results.append(e)
        return results[-limit:]


_GLOBAL_MEMORY = MemoryEngine()

def get_memory_engine() -> MemoryEngine:
    return _GLOBAL_MEMORY
