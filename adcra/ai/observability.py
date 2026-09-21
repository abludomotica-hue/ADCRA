"""
ADCRA AI Brain — Observability, Telemetry & Audit Logging
Provides end-to-end tracing, performance metrics, sanitized audit trails,
and real-time event distribution for UI activity visualizers.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger("adcra.ai.observability")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class AIObservability:
    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = workspace_root or WORKSPACE_ROOT
        self._audit_file = self.root / "campaign" / "reports" / "ai-audit-log.json"
        self._runs_file = self.root / "campaign" / "reports" / "ai-agent-runs.json"
        self._runs: Dict[str, Dict[str, Any]] = {}
        self._audit_entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self._runs_file.is_file():
            try:
                with open(self._runs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for r in data.get("runs", []):
                        self._runs[r["run_id"]] = r
            except Exception as e:
                logger.error(f"Error loading agent runs: {e}")

        if self._audit_file.is_file():
            try:
                with open(self._audit_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._audit_entries = data.get("audit_log", [])
            except Exception as e:
                logger.error(f"Error loading audit log: {e}")

    def _save_runs(self) -> None:
        try:
            self._runs_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._runs_file, "w", encoding="utf-8") as f:
                json.dump({
                    "schema_version": "1.0.0",
                    "total_runs": len(self._runs),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "runs": list(self._runs.values())
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save agent runs: {e}")

    def _save_audit(self) -> None:
        try:
            self._audit_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._audit_file, "w", encoding="utf-8") as f:
                json.dump({
                    "schema_version": "1.0.0",
                    "total_events": len(self._audit_entries),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "audit_log": self._audit_entries[-500:]  # Mantener últimos 500
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save audit log: {e}")

    def record_run(self, run_result: Dict[str, Any]) -> None:
        run_id = run_result.get("run_id")
        if run_id:
            self._runs[run_id] = run_result
            self._save_runs()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._runs.get(run_id)

    def list_runs(self, campaign_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        runs = list(self._runs.values())
        if campaign_id:
            runs = [r for r in runs if r.get("campaign_id") == campaign_id]
        return runs[-limit:]

    def record_event(
        self,
        event_type: str,
        actor: str,
        action: str,
        tenant_id: str = "default",
        campaign_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Registra un evento de auditoría sanitizado (sin secretos)."""
        safe_details = self._sanitize_dict(details or {})
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "tenant_id": tenant_id,
            "campaign_id": campaign_id or "unassigned",
            "details": safe_details
        }
        self._audit_entries.append(entry)
        self._save_audit()
        return entry

    def get_audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._audit_entries[-limit:]

    @staticmethod
    def _sanitize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina posibles secretos o credenciales antes de persistir o transmitir."""
        sensitive_keys = {"api_key", "token", "secret", "password", "authorization", "x-api-key"}
        cleaned = {}
        for k, v in d.items():
            if any(s in k.lower() for s in sensitive_keys):
                cleaned[k] = "[REDACTED]"
            elif isinstance(v, dict):
                cleaned[k] = AIObservability._sanitize_dict(v)
            else:
                cleaned[k] = v
        return cleaned


_GLOBAL_OBSERVABILITY = AIObservability()

def get_observability() -> AIObservability:
    return _GLOBAL_OBSERVABILITY
