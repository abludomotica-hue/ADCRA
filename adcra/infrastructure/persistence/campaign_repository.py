import shutil
"""
ADCRA v2.1 — Campaign Persistence Repository
Manages durable JSON storage for Campaigns under:
storage/clients/<client_id>/campaigns/<campaign_id>/campaign.json
Enforces:
- Every campaign belongs to an existing Client (no orphan campaigns).
- Tenant and Client data isolation.
- Immutable Context Snapshots for reproducibility.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from adcra.domain.campaigns.campaign import Campaign, CampaignStatus, CampaignContextSnapshot
from adcra.infrastructure.persistence.client_repository import get_client_repository

logger = logging.getLogger("adcra.persistence.campaign")
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


class CampaignRepository:
    def __init__(self, base_dir: Optional[Path] = None):
        self._clients_dir = Path(base_dir) if base_dir else (WORKSPACE_ROOT / "storage" / "clients")
        self._clients_dir.mkdir(parents=True, exist_ok=True)

    def _campaign_dir(self, client_id: str, campaign_id: str) -> Path:
        return self._clients_dir / client_id / "campaigns" / campaign_id

    def save(self, campaign: Campaign) -> Campaign:
        # Enforce client existence
        client_repo = get_client_repository()
        if not client_repo.exists(campaign.client_id):
            raise KeyError(f"Cannot save campaign: Client '{campaign.client_id}' does not exist.")

        camp_dir = self._campaign_dir(campaign.client_id, campaign.id)
        camp_dir.mkdir(parents=True, exist_ok=True)

        camp_file = camp_dir / "campaign.json"
        with open(camp_file, "w", encoding="utf-8") as f:
            json.dump(campaign.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Saved campaign '{campaign.id}' ({campaign.name}) under client '{campaign.client_id}'")
        return campaign

    def get(self, campaign_id: str, client_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[Campaign]:
        # If client_id is given, directly look it up
        if client_id:
            camp_file = self._campaign_dir(client_id, campaign_id) / "campaign.json"
            if camp_file.is_file():
                try:
                    with open(camp_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    c = Campaign.from_dict(data)
                    if tenant_id and c.tenant_id != tenant_id:
                        return None
                    return c
                except Exception as e:
                    logger.error(f"Error reading campaign {campaign_id}: {e}")
            return None

        # Otherwise, search across all clients
        for client_dir in self._clients_dir.iterdir():
            if client_dir.is_dir():
                c_camps_dir = client_dir / "campaigns"
                if c_camps_dir.is_dir():
                    target = c_camps_dir / campaign_id / "campaign.json"
                    if target.is_file():
                        try:
                            with open(target, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            c = Campaign.from_dict(data)
                            if tenant_id and c.tenant_id != tenant_id:
                                return None
                            return c
                        except Exception as e:
                            logger.error(f"Error reading campaign {campaign_id}: {e}")
        return None

    def list(self, client_id: Optional[str] = None, tenant_id: Optional[str] = None) -> List[Campaign]:
        campaigns = []
        clients_to_check = [self._clients_dir / client_id] if client_id else list(self._clients_dir.iterdir())

        for c_dir in clients_to_check:
            if not c_dir.is_dir():
                continue
            c_camps_dir = c_dir / "campaigns"
            if not c_camps_dir.is_dir():
                continue
            for camp_entry in c_camps_dir.iterdir():
                if camp_entry.is_dir():
                    c_file = camp_entry / "campaign.json"
                    if c_file.is_file():
                        try:
                            with open(c_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            c = Campaign.from_dict(data)
                            if tenant_id and c.tenant_id != tenant_id:
                                continue
                            campaigns.append(c)
                        except Exception as e:
                            logger.warning(f"Error reading {c_file}: {e}")

        return sorted(campaigns, key=lambda c: c.created_at, reverse=True)

    def delete(self, campaign_id: str, client_id: Optional[str] = None, tenant_id: Optional[str] = None) -> bool:
        campaign = self.get(campaign_id, client_id=client_id, tenant_id=tenant_id)
        if not campaign:
            return False
        camp_dir = self._campaign_dir(campaign.client_id, campaign.id)
        if camp_dir.is_dir():
            for f in camp_dir.glob("*"):
                if f.is_file():
                    f.unlink()
            try:
                shutil.rmtree(camp_dir, ignore_errors=True)
                return True
            except Exception as e:
                logger.warning(f"Could not delete campaign directory {camp_dir}: {e}")
                return True
        return False

    def save_snapshot(self, snapshot: CampaignContextSnapshot) -> None:
        snap_dir = self._campaign_dir(snapshot.client_id, snapshot.campaign_id) / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        snap_file = snap_dir / f"{snapshot.snapshot_id}.json"
        with open(snap_file, "w", encoding="utf-8") as f:
            json.dump(snapshot.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved snapshot '{snapshot.snapshot_id}' for campaign '{snapshot.campaign_id}'")

    def get_snapshot(self, client_id: str, campaign_id: str, snapshot_id: str) -> Optional[CampaignContextSnapshot]:
        snap_file = self._campaign_dir(client_id, campaign_id) / "snapshots" / f"{snapshot_id}.json"
        if not snap_file.is_file():
            return None
        try:
            with open(snap_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CampaignContextSnapshot(**data)
        except Exception as e:
            logger.error(f"Error reading snapshot {snapshot_id}: {e}")
            return None


_GLOBAL_CAMPAIGN_REPO: Optional[CampaignRepository] = None

def get_campaign_repository() -> CampaignRepository:
    global _GLOBAL_CAMPAIGN_REPO
    if _GLOBAL_CAMPAIGN_REPO is None:
        _GLOBAL_CAMPAIGN_REPO = CampaignRepository()
    return _GLOBAL_CAMPAIGN_REPO
