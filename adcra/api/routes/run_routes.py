"""
ADCRA v2.1 — AI Runs API Routes
Handles:
POST /api/ai/runs
GET  /api/ai/runs
GET  /api/ai/runs/{run_id}
POST /api/ai/runs/{run_id}/cancel
POST /api/ai/runs/{run_id}/resume
POST /api/ai/runs/{run_id}/retry
"""

import uuid
from typing import Dict, Any, Tuple, Optional
from adcra.domain.execution.durable_run import DurableRun
from adcra.ai.runtime import AIRunStatus
from adcra.infrastructure.persistence.run_repository import get_run_repository
from adcra.infrastructure.events.event_bus import get_event_bus
from adcra.infrastructure.queue.job_queue import get_job_queue


def handle_runs_request(
    method: str,
    path: str,
    body_data: Optional[Dict[str, Any]] = None,
    tenant_id: str = "default_tenant",
    query_params: Optional[Dict[str, str]] = None
) -> Tuple[int, Dict[str, Any]]:
    run_repo = get_run_repository()
    event_bus = get_event_bus()
    job_queue = get_job_queue()
    query_params = query_params or {}

    parts = [p for p in path.split("/") if p]
    # ['api', 'ai', 'runs', ...]

    # 1. GET /api/ai/runs
    if method == "GET" and len(parts) == 3:
        camp_id = query_params.get("campaign_id")
        client_id = query_params.get("client_id")
        status = query_params.get("status")
        runs = run_repo.list(campaign_id=camp_id, client_id=client_id, status=status, limit=50)
        return 200, {
            "total": len(runs),
            "runs": [r.to_dict() for r in runs]
        }

    # 2. POST /api/ai/runs
    if method == "POST" and len(parts) == 3:
        if not body_data:
            return 400, {"error": "BAD_REQUEST", "message": "Run specification cannot be empty."}

        run_id = f"run_{uuid.uuid4().hex[:8]}"
        durable_run = DurableRun(
            run_id=run_id,
            client_id=body_data.get("client_id", "default_client"),
            campaign_id=body_data.get("campaign_id", "default_campaign"),
            intent_id=body_data.get("intent_id", "custom_intent"),
            task_type=body_data.get("task_type", "creative_concept"),
            tenant_id=tenant_id,
            status=AIRunStatus.QUEUED,
            total_steps=body_data.get("total_steps", 1),
            task_steps=body_data.get("task_steps", []),
            execution_mode=body_data.get("execution_mode", "REAL")
        )
        run_repo.save(durable_run)

        # Enqueue job
        job_id = job_queue.enqueue(
            task_type=durable_run.task_type,
            payload={"run_id": run_id, "intent": body_data.get("intent")}
        )

        event_bus.publish(
            event_type="ai.run.created",
            source="RunsAPI",
            client_id=durable_run.client_id,
            campaign_id=durable_run.campaign_id,
            run_id=run_id,
            payload={"run_id": run_id, "job_id": job_id, "task_type": durable_run.task_type}
        )

        return 201, durable_run.to_dict()

    if len(parts) >= 4:
        run_id = parts[3]
        run = run_repo.get(run_id)
        if not run:
            return 404, {"error": "RUN_NOT_FOUND", "message": f"AI Run '{run_id}' not found."}

        # 3. GET /api/ai/runs/{run_id}
        if method == "GET" and len(parts) == 4:
            return 200, run.to_dict()

        # 4. POST /api/ai/runs/{run_id}/cancel
        if method == "POST" and len(parts) == 5 and parts[4] == "cancel":
            run.status = AIRunStatus.CANCELLED
            run_repo.save(run)
            event_bus.publish(
                event_type="ai.run.cancelled",
                source="RunsAPI",
                client_id=run.client_id,
                campaign_id=run.campaign_id,
                run_id=run_id,
                payload={"run_id": run_id}
            )
            return 200, {"status": "CANCELLED", "run": run.to_dict()}

        # 5. POST /api/ai/runs/{run_id}/resume
        if method == "POST" and len(parts) == 5 and parts[4] == "resume":
            if run.status in [AIRunStatus.COMPLETED, AIRunStatus.CANCELLED]:
                return 400, {"error": "INVALID_STATE", "message": f"Cannot resume run with status {run.status.value}"}
            run.status = AIRunStatus.RUNNING
            run_repo.save(run)
            event_bus.publish(
                event_type="ai.run.started",
                source="RunsAPI",
                client_id=run.client_id,
                campaign_id=run.campaign_id,
                run_id=run_id,
                payload={"run_id": run_id, "action": "resume"}
            )
            return 200, {"status": "RESUMED", "run": run.to_dict()}

        # 6. POST /api/ai/runs/{run_id}/retry
        if method == "POST" and len(parts) == 5 and parts[4] == "retry":
            run.status = AIRunStatus.RETRYING
            run.retry_count += 1
            run_repo.save(run)
            event_bus.publish(
                event_type="ai.run.started",
                source="RunsAPI",
                client_id=run.client_id,
                campaign_id=run.campaign_id,
                run_id=run_id,
                payload={"run_id": run_id, "action": "retry", "retry_count": run.retry_count}
            )
            return 200, {"status": "RETRYING", "run": run.to_dict()}

    return 404, {"error": "NOT_FOUND", "message": f"No run route matches {method} {path}"}
