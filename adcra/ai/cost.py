"""
ADCRA AI Brain — Cost Intelligence & Budget Engine
Maintains the immutable AI Cost Ledger and enforces granular budget policies.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from adcra.ai.types import BudgetStatus

logger = logging.getLogger("adcra.ai.cost")


class AICostLedger:
    def __init__(self, ledger_file: Optional[str] = None):
        if ledger_file:
            self._path = Path(ledger_file)
        else:
            self._path = Path(__file__).resolve().parents[2] / "campaign" / "reports" / "ai-cost-ledger.json"
        self._entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self._path.is_file():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._entries = data.get("entries", [])
            except Exception as e:
                logger.error(f"Failed to load cost ledger from {self._path}: {e}")
                self._entries = []

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({
                    "schema_version": "1.0.0",
                    "total_entries": len(self._entries),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "entries": self._entries
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cost ledger to {self._path}: {e}")

    def record_usage(
        self,
        tenant_id: str,
        campaign_id: Optional[str],
        agent_id: Optional[str],
        task: str,
        provider_id: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        cost_usd: float,
        latency_ms: float = 0.0,
        workspace_id: str = "default"
    ) -> Dict[str, Any]:
        entry = {
            "entry_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "campaign_id": campaign_id or "unassigned",
            "agent_id": agent_id or "unassigned",
            "task": task,
            "provider_id": provider_id,
            "model_id": model_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost_usd, 6),
            "latency_ms": latency_ms
        }
        self._entries.append(entry)
        self._save()
        return entry

    def get_entries(self, campaign_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if campaign_id:
            filtered = [e for e in self._entries if e.get("campaign_id") == campaign_id]
            return filtered[-limit:]
        return self._entries[-limit:]

    def get_summary(
        self,
        campaign_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = []
        for e in self._entries:
            try:
                t = datetime.fromisoformat(e["timestamp"])
                if t < cutoff:
                    continue
            except Exception:
                pass
            if campaign_id and e.get("campaign_id") != campaign_id:
                continue
            if tenant_id and e.get("tenant_id") != tenant_id:
                continue
            filtered.append(e)

        total_cost = sum(e.get("cost_usd", 0.0) for e in filtered)
        total_tokens = sum(e.get("total_tokens", 0) for e in filtered)
        total_calls = len(filtered)

        by_task: Dict[str, float] = {}
        by_model: Dict[str, float] = {}
        by_agent: Dict[str, float] = {}

        for e in filtered:
            task = e.get("task", "unknown")
            model = e.get("model_id", "unknown")
            agent = e.get("agent_id", "unknown")
            cost = e.get("cost_usd", 0.0)

            by_task[task] = round(by_task.get(task, 0.0) + cost, 4)
            by_model[model] = round(by_model.get(model, 0.0) + cost, 4)
            by_agent[agent] = round(by_agent.get(agent, 0.0) + cost, 4)

        return {
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_calls": total_calls,
            "by_task": by_task,
            "by_model": by_model,
            "by_agent": by_agent,
            "period_days": days
        }


class BudgetEngine:
    def __init__(
        self,
        cost_ledger: Optional[AICostLedger] = None,
        max_cost_per_request: float = 2.00,
        max_cost_per_campaign: float = 25.00,
        max_cost_per_day: float = 50.00
    ):
        self.ledger = cost_ledger or get_cost_ledger()
        self.max_cost_per_request = max_cost_per_request
        self.max_cost_per_campaign = max_cost_per_campaign
        self.max_cost_per_day = max_cost_per_day

    def check_budget(
        self,
        campaign_id: str,
        estimated_cost: float,
        tenant_id: str = "default"
    ) -> Tuple[BudgetStatus, str]:
        if estimated_cost > self.max_cost_per_request:
            return (
                BudgetStatus.BLOCKED,
                f"Request estimate (${estimated_cost:.4f}) exceeds max per-request limit (${self.max_cost_per_request:.2f})"
            )

        summary = self.ledger.get_summary(campaign_id=campaign_id, tenant_id=tenant_id, days=30)
        current_camp_cost = summary["total_cost_usd"]
        projected_camp_cost = current_camp_cost + estimated_cost

        if projected_camp_cost >= self.max_cost_per_campaign:
            return (
                BudgetStatus.LIMIT_REACHED,
                f"Campaign '{campaign_id}' cost (${projected_camp_cost:.2f}) reaches campaign limit (${self.max_cost_per_campaign:.2f})"
            )
        elif projected_camp_cost >= self.max_cost_per_campaign * 0.8:
            return (
                BudgetStatus.WARNING,
                f"Campaign '{campaign_id}' approaching budget limit ({projected_camp_cost / self.max_cost_per_campaign * 100:.1f}%)"
            )

        return (BudgetStatus.NORMAL, "Budget within authorized operational limits")


_GLOBAL_LEDGER = AICostLedger()
_GLOBAL_BUDGET = BudgetEngine(_GLOBAL_LEDGER)

def get_cost_ledger() -> AICostLedger:
    return _GLOBAL_LEDGER

def get_budget_engine() -> BudgetEngine:
    return _GLOBAL_BUDGET
