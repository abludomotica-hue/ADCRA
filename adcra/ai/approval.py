"""
ADCRA AI Brain — Human Approval Engine
Traps high-risk actions, emits WAITING_FOR_APPROVAL events, and manages human review gates.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
from adcra.ai.types import AutonomyLevel, RiskLevel

logger = logging.getLogger("adcra.ai.approval")


class ApprovalEngine:
    def __init__(self, approvals_file: Optional[str] = None):
        if approvals_file:
            self._path = Path(approvals_file)
        else:
            self._path = Path(__file__).resolve().parents[2] / "campaign" / "reports" / "pending-approvals.json"
        self._approvals: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self._path.is_file():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("approvals", []):
                        self._approvals[item["approval_id"]] = item
            except Exception as e:
                logger.error(f"Failed to load approvals from {self._path}: {e}")

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({
                    "schema_version": "1.0.0",
                    "total_pending": len([a for a in self._approvals.values() if a["status"] == "PENDING"]),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "approvals": list(self._approvals.values())
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save approvals to {self._path}: {e}")

    def requires_approval(
        self,
        action: str,
        risk_level: RiskLevel,
        autonomy_level: AutonomyLevel = AutonomyLevel.AUTOPILOT
    ) -> bool:
        """
        Determina si una acción requiere aprobación humana basada en el nivel de autonomía.
        """
        # Acciones intrínsecamente críticas que siempre requieren aprobación
        critical_actions = {
            "publish_campaign",
            "paid_api_call",
            "delete_original_asset",
            "credential_change",
            "external_upload",
            "final_delivery_release",
            "financial_action"
        }
        if action in critical_actions:
            return True

        if autonomy_level == AutonomyLevel.ASSIST:
            return risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        elif autonomy_level == AutonomyLevel.AUTOPILOT:
            return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        elif autonomy_level == AutonomyLevel.AUTONOMOUS:
            return risk_level == RiskLevel.CRITICAL
        return True

    def create_approval_request(
        self,
        run_id: str,
        action: str,
        why: str,
        impact: str,
        cost_usd: float = 0.0,
        destination: str = "internal",
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        approval_id = f"appr_{uuid.uuid4().hex[:8]}"
        req = {
            "approval_id": approval_id,
            "run_id": run_id,
            "campaign_id": campaign_id or "unassigned",
            "action": action,
            "why": why,
            "impact": impact,
            "cost_usd": cost_usd,
            "destination": destination,
            "risk_level": risk_level.value if isinstance(risk_level, RiskLevel) else str(risk_level),
            "status": "PENDING",  # PENDING, APPROVED, REJECTED
            "created_at": datetime.now(timezone.utc).isoformat(),
            "decided_at": None,
            "decided_by": None
        }
        self._approvals[approval_id] = req
        self._save()
        logger.info(f"Created approval request {approval_id} for action '{action}' (risk={risk_level})")
        return req

    def decide(self, approval_id: str, approved: bool, user: str = "human_operator") -> Dict[str, Any]:
        if approval_id not in self._approvals:
            raise KeyError(f"Approval request '{approval_id}' not found")
        req = self._approvals[approval_id]
        req["status"] = "APPROVED" if approved else "REJECTED"
        req["decided_at"] = datetime.now(timezone.utc).isoformat()
        req["decided_by"] = user
        self._save()
        return req

    def get_pending(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        pending = [a for a in self._approvals.values() if a["status"] == "PENDING"]
        if campaign_id:
            pending = [a for a in pending if a.get("campaign_id") == campaign_id]
        return pending

    def get_approval(self, approval_id: str) -> Optional[Dict[str, Any]]:
        return self._approvals.get(approval_id)


_GLOBAL_APPROVAL = ApprovalEngine()

def get_approval_engine() -> ApprovalEngine:
    return _GLOBAL_APPROVAL
