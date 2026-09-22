"""
ADCRA v2.1 — Master API Router & Dispatcher
Dispatches incoming HTTP requests to domain-specific route handlers:
- Clients:   /api/clients
- Campaigns: /api/campaigns
- Providers: /api/ai/providers
- Runs:      /api/ai/runs
- Events:    /api/events

Returns None if the route is unhandled, allowing seamless fallback
to legacy endpoints in dashboard_server.py (100% backward compatibility).
"""

import logging
from typing import Dict, Any, Tuple, Optional
from adcra.api.routes.client_routes import handle_clients_request
from adcra.api.routes.campaign_routes import handle_campaigns_request
from adcra.api.routes.provider_routes import handle_providers_request
from adcra.api.routes.run_routes import handle_runs_request
from adcra.api.routes.event_routes import handle_events_request

logger = logging.getLogger("adcra.api.router")


def dispatch_api_request(
    method: str,
    path: str,
    body_data: Optional[Dict[str, Any]] = None,
    query_params: Optional[Dict[str, str]] = None,
    tenant_id: str = "default_tenant"
) -> Optional[Tuple[int, Dict[str, Any]]]:
    # 1. Clients
    if path == "/api/clients" or path.startswith("/api/clients/"):
        return handle_clients_request(method, path, body_data=body_data, tenant_id=tenant_id)

    # 2. Campaigns
    if path == "/api/campaigns" or (path.startswith("/api/campaigns/") and not path.endswith("/events")):
        return handle_campaigns_request(
            method, path, body_data=body_data, tenant_id=tenant_id, query_params=query_params
        )

    # 3. AI Providers
    if path == "/api/ai/providers" or path.startswith("/api/ai/providers/"):
        # Legacy check: /api/ai/providers/test is handled in providers_routes
        return handle_providers_request(method, path, body_data=body_data, tenant_id=tenant_id)

    # 4. AI Runs
    if path == "/api/ai/runs" or (path.startswith("/api/ai/runs/") and not path.endswith("/events")):
        return handle_runs_request(
            method, path, body_data=body_data, tenant_id=tenant_id, query_params=query_params
        )

    # 5. Events
    if path == "/api/events" or path.startswith("/api/events/") or path.endswith("/events"):
        return handle_events_request(method, path, query_params=query_params)

    # Not a new v2.1 modular route -> return None to fall back to legacy handlers
    return None
