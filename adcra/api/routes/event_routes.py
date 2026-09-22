"""
ADCRA v2.1 — Events API Routes
Handles:
GET /api/events
GET /api/runs/{run_id}/events
GET /api/campaigns/{campaign_id}/events
"""

from typing import Dict, Any, Tuple, Optional
from adcra.infrastructure.events.event_bus import get_event_bus


def handle_events_request(
    method: str,
    path: str,
    query_params: Optional[Dict[str, str]] = None
) -> Tuple[int, Dict[str, Any]]:
    event_bus = get_event_bus()
    query_params = query_params or {}

    parts = [p for p in path.split("/") if p]
    # e.g. ['api', 'events'] or ['api', 'runs', 'xyz', 'events']

    # 1. GET /api/events
    if method == "GET" and len(parts) == 2 and parts[1] == "events":
        limit = int(query_params.get("limit", 50))
        event_type = query_params.get("type")
        camp_id = query_params.get("campaign_id")
        client_id = query_params.get("client_id")
        run_id = query_params.get("run_id")

        events = event_bus.get_events(
            limit=limit,
            event_type=event_type,
            campaign_id=camp_id,
            client_id=client_id,
            run_id=run_id
        )
        return 200, {
            "total": len(events),
            "events": events
        }

    # 2. GET /api/runs/{run_id}/events
    if method == "GET" and len(parts) == 4 and parts[1] == "runs" and parts[3] == "events":
        run_id = parts[2]
        events = event_bus.get_events(run_id=run_id, limit=50)
        return 200, {
            "run_id": run_id,
            "total": len(events),
            "events": events
        }

    # 3. GET /api/campaigns/{campaign_id}/events
    if method == "GET" and len(parts) == 4 and parts[1] == "campaigns" and parts[3] == "events":
        camp_id = parts[2]
        events = event_bus.get_events(campaign_id=camp_id, limit=50)
        return 200, {
            "campaign_id": camp_id,
            "total": len(events),
            "events": events
        }

    return 404, {"error": "NOT_FOUND", "message": f"No event route matches {method} {path}"}
