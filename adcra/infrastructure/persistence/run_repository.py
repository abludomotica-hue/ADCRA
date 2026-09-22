"""
ADCRA v2.1 — Durable AI Run Repository
Persists and retrieves DurableRun states and checkpoints to storage/runs/<run_id>.json.
Provides crash-recovery querying and run history.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from adcra.domain.execution.durable_run import DurableRun

logger = logging.getLogger("adcra.persistence.run")
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


class RunRepository:
    def __init__(self, base_dir: Optional[Path] = None):
        self._dir = Path(base_dir) if base_dir else (WORKSPACE_ROOT / "storage" / "runs")
        self._dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, run_id: str) -> Path:
        return self._dir / f"{run_id}.json"

    def save(self, run: DurableRun) -> DurableRun:
        target = self._file_path(run.run_id)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(run.to_dict(), f, indent=2, ensure_ascii=False)
        return run

    def get(self, run_id: str) -> Optional[DurableRun]:
        target = self._file_path(run_id)
        if not target.is_file():
            return None
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            return DurableRun.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load run {run_id}: {e}")
            return None

    def list(
        self,
        campaign_id: Optional[str] = None,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[DurableRun]:
        runs = []
        if not self._dir.is_dir():
            return runs

        for f in self._dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as file:
                    data = json.load(file)
                r = DurableRun.from_dict(data)
                if campaign_id and r.campaign_id != campaign_id:
                    continue
                if client_id and r.client_id != client_id:
                    continue
                if status and r.status.value != status:
                    continue
                runs.append(r)
            except Exception as e:
                logger.warning(f"Error reading run file {f}: {e}")

        # Sort by updated_at or created_at descending
        return sorted(runs, key=lambda r: r.updated_at, reverse=True)[:limit]

    def delete(self, run_id: str) -> bool:
        target = self._file_path(run_id)
        if target.is_file():
            target.unlink()
            return True
        return False


_GLOBAL_RUN_REPO: Optional[RunRepository] = None

def get_run_repository() -> RunRepository:
    global _GLOBAL_RUN_REPO
    if _GLOBAL_RUN_REPO is None:
        _GLOBAL_RUN_REPO = RunRepository()
    return _GLOBAL_RUN_REPO

RunRepository.list_all = RunRepository.list
