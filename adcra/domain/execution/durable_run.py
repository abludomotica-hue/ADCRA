"""
ADCRA v2.1 — Durable AI Run Domain Model
Represents an AI Run that survives process restarts through transactional
checkpoints and task graph state tracking.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from adcra.ai.runtime import AIRunStatus


@dataclass
class RunCheckpoint:
    step_id: str
    step_name: str
    completed_at: str
    output_key: str
    output_data: Any
    latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DurableRun:
    run_id: str
    client_id: str
    campaign_id: str
    intent_id: str
    task_type: str
    tenant_id: str = "default_tenant"
    parent_run_id: Optional[str] = None
    status: AIRunStatus = AIRunStatus.QUEUED
    current_step_index: int = 0
    total_steps: int = 0
    task_steps: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: Dict[str, Any] = field(default_factory=dict)
    routing_decision: Dict[str, Any] = field(default_factory=dict)
    provider: str = ""
    model: str = ""
    execution_mode: str = "REAL"  # "REAL" or "SIMULATION"
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None
    trace_id: str = field(default_factory=lambda: f"tr_{uuid.uuid4().hex[:8]}")
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    result_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def record_checkpoint(self, step_id: str, step_name: str, output_key: str, data: Any, latency_ms: float = 0.0) -> None:
        cp = RunCheckpoint(
            step_id=step_id,
            step_name=step_name,
            completed_at=datetime.now(timezone.utc).isoformat(),
            output_key=output_key,
            output_data=data,
            latency_ms=latency_ms
        )
        self.checkpoints[step_id] = cp.to_dict()
        self.current_step_index += 1
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def has_checkpoint(self, step_id: str) -> bool:
        return step_id in self.checkpoints

    def get_checkpoint_output(self, step_id: str) -> Any:
        cp = self.checkpoints.get(step_id)
        return cp.get("output_data") if cp else None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, AIRunStatus) else str(self.status)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DurableRun":
        raw_s = data.get("status", AIRunStatus.QUEUED.value)
        status = AIRunStatus(raw_s) if raw_s in AIRunStatus.__members__ else AIRunStatus.QUEUED
        
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        filtered["status"] = status
        return cls(**filtered)

    def start(self) -> None:
        self.status = AIRunStatus.RUNNING
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.started_at

    def fail(self, error: str) -> None:
        self.status = AIRunStatus.FAILED
        self.error = error
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def cancel(self) -> None:
        self.status = AIRunStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def can_resume(self) -> bool:
        return self.status in [AIRunStatus.FAILED, AIRunStatus.WAITING, AIRunStatus.BLOCKED]

    def resume(self) -> bool:
        if not self.can_resume():
            return False
        self.status = AIRunStatus.RUNNING
        self.error = None
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return True


RunStatus = AIRunStatus
