"""
ADCRA v2.1 — Client API Routes
Handles:
GET    /api/clients
POST   /api/clients
GET    /api/clients/{client_id}
PATCH  /api/clients/{client_id}
DELETE /api/clients/{client_id}
GET    /api/clients/{client_id}/brand
PATCH  /api/clients/{client_id}/brand
GET    /api/clients/{client_id}/campaigns
"""

import json
from typing import Dict, Any, Tuple, Optional
from adcra.application.clients.client_service import get_client_service
from adcra.application.campaigns.campaign_service import get_campaign_service
from adcra.infrastructure.events.event_bus import get_event_bus


def handle_clients_request(
    method: str,
    path: str,
    body_data: Optional[Dict[str, Any]] = None,
    tenant_id: str = "default_tenant"
) -> Tuple[int, Dict[str, Any]]:
    client_service = get_client_service()
    camp_service = get_campaign_service()
    event_bus = get_event_bus()

    # Normalize path
    parts = [p for p in path.split("/") if p]
    # ['api', 'clients', ...]

    # 1. GET /api/clients
    if method == "GET" and len(parts) == 2:
        clients = client_service.list_clients(tenant_id=tenant_id)
        return 200, {
            "total": len(clients),
            "clients": [c.to_dict() for c in clients]
        }

    # 2. POST /api/clients
    if method == "POST" and len(parts) == 2:
        if not body_data:
            return 400, {"error": "BAD_REQUEST", "message": "Request body cannot be empty."}
        try:
            client = client_service.create_client(body_data, tenant_id=tenant_id)
            event_bus.publish(
                event_type="client.created",
                source="ClientAPI",
                client_id=client.id,
                campaign_id="unassigned",
                payload={"client_id": client.id, "name": client.name}
            )
            return 201, client.to_dict()
        except ValueError as ve:
            return 400, {"error": "INVALID_CLIENT_DATA", "message": str(ve)}
        except Exception as e:
            return 500, {"error": "INTERNAL_SERVER_ERROR", "message": str(e)}

    # Sub-routes with client_id
    if len(parts) >= 3:
        client_id = parts[2]
        
        # 3. GET /api/clients/{client_id}
        if method == "GET" and len(parts) == 3:
            client = client_service.get_client(client_id, tenant_id=tenant_id)
            if not client:
                return 404, {"error": "CLIENT_NOT_FOUND", "message": f"Client '{client_id}' does not exist."}
            return 200, client.to_dict()

        # 4. PATCH /api/clients/{client_id}
        if method == "PATCH" and len(parts) == 3:
            if not body_data:
                return 400, {"error": "BAD_REQUEST", "message": "No update data provided."}
            updated = client_service.update_client(client_id, body_data, tenant_id=tenant_id)
            if not updated:
                return 404, {"error": "CLIENT_NOT_FOUND", "message": f"Client '{client_id}' not found."}
            event_bus.publish(
                event_type="client.updated",
                source="ClientAPI",
                client_id=client_id,
                payload={"client_id": client_id, "updated_fields": list(body_data.keys())}
            )
            return 200, updated.to_dict()

        # 5. DELETE /api/clients/{client_id}
        if method == "DELETE" and len(parts) == 3:
            # Check for dependent campaigns first
            existing_camps = camp_service.list_campaigns(client_id=client_id, tenant_id=tenant_id)
            if existing_camps:
                return 409, {
                    "error": "CLIENT_HAS_CAMPAIGNS",
                    "message": f"Cannot delete client '{client_id}': {len(existing_camps)} active campaign(s) depend on it."
                }
            success = client_service.delete_client(client_id, tenant_id=tenant_id)
            if not success:
                return 404, {"error": "CLIENT_NOT_FOUND", "message": f"Client '{client_id}' not found."}
            return 200, {"status": "SUCCESS", "message": f"Client '{client_id}' deleted."}

        # 6. GET & PATCH /api/clients/{client_id}/brand
        if len(parts) == 4 and parts[3] == "brand":
            if method == "GET":
                brand = client_service.get_brand_dna(client_id, tenant_id=tenant_id)
                if brand is None:
                    return 404, {"error": "CLIENT_NOT_FOUND", "message": f"Client '{client_id}' not found."}
                return 200, brand
            elif method in ["PATCH", "PUT"]:
                if not body_data:
                    return 400, {"error": "BAD_REQUEST", "message": "No brand data provided."}
                updated_brand = client_service.update_brand_dna(client_id, body_data, tenant_id=tenant_id)
                if updated_brand is None:
                    return 404, {"error": "CLIENT_NOT_FOUND", "message": f"Client '{client_id}' not found."}
                return 200, updated_brand

        # 7. GET /api/clients/{client_id}/campaigns
        if method == "GET" and len(parts) == 4 and parts[3] == "campaigns":
            client = client_service.get_client(client_id, tenant_id=tenant_id)
            if not client:
                return 404, {"error": "CLIENT_NOT_FOUND", "message": f"Client '{client_id}' not found."}
            camps = camp_service.list_campaigns(client_id=client_id, tenant_id=tenant_id)
            return 200, {
                "client_id": client_id,
                "total": len(camps),
                "campaigns": [c.to_dict() for c in camps]
            }

    return 404, {"error": "NOT_FOUND", "message": f"No client route matches {method} {path}"}
