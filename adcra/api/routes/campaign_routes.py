"""
ADCRA v2.1 — Campaign API Routes
Handles:
GET    /api/campaigns
POST   /api/campaigns
GET    /api/campaigns/{campaign_id}
PATCH  /api/campaigns/{campaign_id}
DELETE /api/campaigns/{campaign_id}
POST   /api/campaigns/{campaign_id}/activate
POST   /api/campaigns/{campaign_id}/archive
GET    /api/campaigns/{campaign_id}/context
GET    /api/campaigns/{campaign_id}/runs
"""

from typing import Dict, Any, Tuple, Optional
from adcra.application.campaigns.campaign_service import get_campaign_service
from adcra.infrastructure.persistence.run_repository import get_run_repository
from adcra.infrastructure.events.event_bus import get_event_bus


def handle_campaigns_request(
    method: str,
    path: str,
    body_data: Optional[Dict[str, Any]] = None,
    tenant_id: str = "default_tenant",
    query_params: Optional[Dict[str, str]] = None
) -> Tuple[int, Dict[str, Any]]:
    camp_service = get_campaign_service()
    run_repo = get_run_repository()
    event_bus = get_event_bus()
    query_params = query_params or {}

    parts = [p for p in path.split("/") if p]
    # ['api', 'campaigns', ...]

    # 1. GET /api/campaigns
    if method == "GET" and len(parts) == 2:
        client_filter = query_params.get("client_id")
        camps = camp_service.list_campaigns(client_id=client_filter, tenant_id=tenant_id)
        active_id = camp_service.get_active_campaign_id(tenant_id=tenant_id)
        return 200, {
            "total": len(camps),
            "active_campaign_id": active_id,
            "campaigns": [c.to_dict() for c in camps]
        }

    # 2. POST /api/campaigns
    if method == "POST" and len(parts) == 2:
        if not body_data:
            return 400, {"error": "BAD_REQUEST", "message": "Campaign body cannot be empty."}
        client_id = body_data.get("client_id")
        if not client_id:
            return 400, {
                "error": "MISSING_CLIENT_ID",
                "message": "A campaign MUST specify a valid 'client_id'. No orphan campaigns permitted."
            }
        try:
            campaign = camp_service.create_campaign(client_id=client_id, data=body_data, tenant_id=tenant_id)
            event_bus.publish(
                event_type="campaign.created",
                source="CampaignAPI",
                client_id=client_id,
                campaign_id=campaign.id,
                payload={"campaign_id": campaign.id, "name": campaign.name, "client_id": client_id}
            )
            return 201, campaign.to_dict()
        except KeyError as ke:
            return 404, {"error": "CLIENT_NOT_FOUND", "message": str(ke)}
        except ValueError as ve:
            return 400, {"error": "INVALID_CAMPAIGN_DATA", "message": str(ve)}
        except Exception as e:
            return 500, {"error": "INTERNAL_SERVER_ERROR", "message": str(e)}

    # Sub-routes with campaign_id
    if len(parts) >= 3:
        campaign_id = parts[2]

        # 3. GET /api/campaigns/{campaign_id}
        if method == "GET" and len(parts) == 3:
            camp = camp_service.get_campaign(campaign_id, tenant_id=tenant_id)
            if not camp:
                return 404, {"error": "CAMPAIGN_NOT_FOUND", "message": f"Campaign '{campaign_id}' does not exist."}
            return 200, camp.to_dict()

        # 4. PATCH /api/campaigns/{campaign_id}
        if method == "PATCH" and len(parts) == 3:
            if not body_data:
                return 400, {"error": "BAD_REQUEST", "message": "No update fields provided."}
            updated = camp_service.update_campaign(campaign_id, body_data, tenant_id=tenant_id)
            if not updated:
                return 404, {"error": "CAMPAIGN_NOT_FOUND", "message": f"Campaign '{campaign_id}' not found."}
            event_bus.publish(
                event_type="campaign.updated",
                source="CampaignAPI",
                client_id=updated.client_id,
                campaign_id=campaign_id,
                payload={"campaign_id": campaign_id, "updated_fields": list(body_data.keys())}
            )
            return 200, updated.to_dict()

        # 5. DELETE /api/campaigns/{campaign_id}
        if method == "DELETE" and len(parts) == 3:
            deleted = camp_service.delete_campaign(campaign_id, tenant_id=tenant_id)
            if not deleted:
                return 404, {"error": "CAMPAIGN_NOT_FOUND", "message": f"Campaign '{campaign_id}' not found."}
            return 200, {"status": "SUCCESS", "message": f"Campaign '{campaign_id}' removed."}

        # 6. POST /api/campaigns/{campaign_id}/activate
        if method == "POST" and len(parts) == 4 and parts[3] == "activate":
            try:
                active = camp_service.activate_campaign(campaign_id, tenant_id=tenant_id)
                event_bus.publish(
                    event_type="campaign.activated",
                    source="CampaignAPI",
                    client_id=active.client_id,
                    campaign_id=campaign_id,
                    payload={"campaign_id": campaign_id}
                )
                return 200, {"status": "SUCCESS", "active_campaign": active.to_dict()}
            except KeyError as ke:
                return 404, {"error": "CAMPAIGN_NOT_FOUND", "message": str(ke)}

        # 7. POST /api/campaigns/{campaign_id}/archive
        if method == "POST" and len(parts) == 4 and parts[3] == "archive":
            try:
                archived = camp_service.archive_campaign(campaign_id, tenant_id=tenant_id)
                event_bus.publish(
                    event_type="campaign.archived",
                    source="CampaignAPI",
                    client_id=archived.client_id,
                    campaign_id=campaign_id,
                    payload={"campaign_id": campaign_id}
                )
                return 200, {"status": "SUCCESS", "campaign": archived.to_dict()}
            except KeyError as ke:
                return 404, {"error": "CAMPAIGN_NOT_FOUND", "message": str(ke)}

        # 8. GET /api/campaigns/{campaign_id}/context
        if method == "GET" and len(parts) == 4 and parts[3] == "context":
            try:
                context = camp_service.get_campaign_context(campaign_id, tenant_id=tenant_id)
                return 200, context
            except KeyError as ke:
                return 404, {"error": "CONTEXT_NOT_FOUND", "message": str(ke)}

        # 9. GET /api/campaigns/{campaign_id}/runs
        if method == "GET" and len(parts) == 4 and parts[3] == "runs":
            runs = run_repo.list(campaign_id=campaign_id, limit=50)
            return 200, {
                "campaign_id": campaign_id,
                "total_runs": len(runs),
                "runs": [r.to_dict() for r in runs]
            }

    return 404, {"error": "NOT_FOUND", "message": f"No campaign route matches {method} {path}"}
