"""
ADCRA v2.1 — Campaign Application Service
Coordinates Campaign creation, Brand DNA inheritance by reference,
delta override tracking, active campaign scoping, and context snapshots.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from adcra.domain.campaigns.campaign import Campaign, CampaignStatus, CampaignContextSnapshot
from adcra.infrastructure.persistence.campaign_repository import get_campaign_repository
from adcra.infrastructure.persistence.client_repository import get_client_repository

logger = logging.getLogger("adcra.application.campaign")


class CampaignService:
    def __init__(self, campaign_repo=None, client_repo=None):
        self._camp_repo = campaign_repo or get_campaign_repository()
        self._client_repo = client_repo or get_client_repository()
        self._active_campaign_by_tenant: Dict[str, str] = {"default_tenant": "camp_locos_materos_2026"}

    def create_campaign(
        self,
        client_id: str,
        data: Dict[str, Any],
        tenant_id: str = "default_tenant"
    ) -> Campaign:
        # Enforce client exists
        client = self._client_repo.get(client_id, tenant_id=tenant_id)
        if not client:
            raise KeyError(f"Cannot create campaign: Client '{client_id}' not found.")

        camp_name = data.get("name", "").strip()
        if not camp_name:
            raise ValueError("Campaign name cannot be empty.")

        camp_id = data.get("id") or f"camp_{uuid.uuid4().hex[:8]}"
        if self._camp_repo.get(camp_id):
            raise ValueError(f"Campaign with ID '{camp_id}' already exists.")

        # Delta overrides track what differs from Brand DNA
        delta_overrides = data.get("delta_overrides", {})

        campaign = Campaign(
            id=camp_id,
            client_id=client_id,
            tenant_id=tenant_id,
            name=camp_name,
            objective=data.get("objective", ""),
            status=CampaignStatus.PLANNING,
            brief=data.get("brief", {}),
            delta_overrides=delta_overrides,
            metadata=data.get("metadata", {})
        )

        saved = self._camp_repo.save(campaign)

        # Create initial context snapshot
        snapshot = CampaignContextSnapshot(
            snapshot_id=f"snap_{camp_id}_init",
            campaign_id=saved.id,
            client_id=client.id,
            tenant_id=tenant_id,
            brand_dna=client.brand_dna.to_dict(),
            audience_snapshot=data.get("audience_override", {}),
            product_snapshot=data.get("product_override", {}),
            approved_claims_snapshot=client.brand_dna.approved_claims
        )
        self._camp_repo.save_snapshot(snapshot)
        saved.context_snapshot_id = snapshot.snapshot_id
        self._camp_repo.save(saved)

        # Set as active campaign for tenant
        self.set_active_campaign_id(saved.id, tenant_id=tenant_id)
        return saved

    def get_campaign(self, campaign_id: str, tenant_id: Optional[str] = None) -> Optional[Campaign]:
        return self._camp_repo.get(campaign_id, tenant_id=tenant_id)

    def list_campaigns(self, client_id: Optional[str] = None, tenant_id: Optional[str] = None) -> List[Campaign]:
        return self._camp_repo.list(client_id=client_id, tenant_id=tenant_id)

    def update_campaign(
        self,
        campaign_id: str,
        updates: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> Optional[Campaign]:
        camp = self._camp_repo.get(campaign_id, tenant_id=tenant_id)
        if not camp:
            return None

        if "name" in updates and updates["name"]:
            camp.name = updates["name"].strip()
        if "objective" in updates:
            camp.objective = updates["objective"]
        if "status" in updates:
            raw_s = updates["status"]
            camp.status = CampaignStatus(raw_s) if raw_s in CampaignStatus.__members__ else CampaignStatus.PLANNING
        if "brief" in updates and isinstance(updates["brief"], dict):
            camp.brief.update(updates["brief"])
        if "delta_overrides" in updates and isinstance(updates["delta_overrides"], dict):
            camp.delta_overrides.update(updates["delta_overrides"])
        camp.updated_at = datetime.now(timezone.utc).isoformat()

        return self._camp_repo.save(camp)

    def delete_campaign(self, campaign_id: str, tenant_id: Optional[str] = None) -> bool:
        return self._camp_repo.delete(campaign_id, tenant_id=tenant_id)

    def activate_campaign(self, campaign_id: str, tenant_id: str = "default_tenant") -> Campaign:
        camp = self._camp_repo.get(campaign_id, tenant_id=tenant_id)
        if not camp:
            raise KeyError(f"Campaign '{campaign_id}' not found.")
        self.set_active_campaign_id(camp.id, tenant_id=tenant_id)
        return camp

    def archive_campaign(self, campaign_id: str, tenant_id: Optional[str] = None) -> Campaign:
        camp = self._camp_repo.get(campaign_id, tenant_id=tenant_id)
        if not camp:
            raise KeyError(f"Campaign '{campaign_id}' not found.")
        camp.status = CampaignStatus.ARCHIVED
        return self._camp_repo.save(camp)

    def get_active_campaign_id(self, tenant_id: str = "default_tenant") -> Optional[str]:
        return self._active_campaign_by_tenant.get(tenant_id)

    def set_active_campaign_id(self, campaign_id: str, tenant_id: str = "default_tenant") -> None:
        self._active_campaign_by_tenant[tenant_id] = campaign_id
        logger.info(f"Tenant '{tenant_id}' active campaign switched to '{campaign_id}'")

    def get_campaign_context(self, campaign_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        camp = self._camp_repo.get(campaign_id, tenant_id=tenant_id)
        if not camp:
            raise KeyError(f"Campaign '{campaign_id}' not found.")
        client = self._client_repo.get(camp.client_id, tenant_id=tenant_id)
        if not client:
            raise KeyError(f"Client '{camp.client_id}' not found for campaign '{campaign_id}'.")

        # Inherit Brand DNA and apply delta overrides
        inherited_brand = client.brand_dna.to_dict()
        if camp.delta_overrides.get("brand_dna"):
            inherited_brand.update(camp.delta_overrides["brand_dna"])

        return {
            "campaign_id": camp.id,
            "campaign_name": camp.name,
            "client_id": client.id,
            "client_name": client.name,
            "status": camp.status.value,
            "objective": camp.objective,
            "brand_dna": inherited_brand,
            "brief": camp.brief,
            "delta_overrides": camp.delta_overrides,
            "context_snapshot_id": camp.context_snapshot_id
        }


_GLOBAL_CAMPAIGN_SERVICE: Optional[CampaignService] = None

def get_campaign_service() -> CampaignService:
    global _GLOBAL_CAMPAIGN_SERVICE
    if _GLOBAL_CAMPAIGN_SERVICE is None:
        _GLOBAL_CAMPAIGN_SERVICE = CampaignService()
    return _GLOBAL_CAMPAIGN_SERVICE
