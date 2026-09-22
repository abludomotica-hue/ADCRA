"""
ADCRA v2.1 — Campaign Domain Entity & Snapshots
Defines the Campaign entity, CampaignStatus enum, and CampaignContextSnapshot.
Invariants:
- A Campaign MUST belong to a valid Client (enforcing client_id).
- Brand DNA is inherited by reference; Campaign stores only delta modifications.
- At execution start, an immutable CampaignContextSnapshot preserves exact context.
"""

import uuid
import enum
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    READY = "READY"
    PRODUCTION = "PRODUCTION"
    REVIEW = "REVIEW"
    QC = "QC"
    APPROVAL = "APPROVAL"
    FINAL = "FINAL"
    DELIVERED = "DELIVERED"
    ARCHIVED = "ARCHIVED"


@dataclass
class CampaignContextSnapshot:
    snapshot_id: str
    campaign_id: str
    client_id: str
    tenant_id: str = "default_tenant"
    captured_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    brand_dna_version: str = "1.0.0"
    brand_dna: Dict[str, Any] = field(default_factory=dict)
    audience_snapshot: Dict[str, Any] = field(default_factory=dict)
    product_snapshot: Dict[str, Any] = field(default_factory=dict)
    approved_claims_snapshot: List[str] = field(default_factory=list)
    creative_learnings_snapshot: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Campaign:
    id: str
    client_id: str
    name: str
    tenant_id: str = "default_tenant"
    objective: str = ""
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    brief: Dict[str, Any] = field(default_factory=dict)
    delta_overrides: Dict[str, Any] = field(default_factory=dict)
    context_snapshot_id: Optional[str] = None
    active_run_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.client_id or not isinstance(self.client_id, str):
            raise ValueError("Campaign invariant violated: A campaign MUST belong to a valid client_id.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "objective": self.objective,
            "status": self.status.value if isinstance(self.status, CampaignStatus) else str(self.status),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "brief": self.brief,
            "delta_overrides": self.delta_overrides,
            "context_snapshot_id": self.context_snapshot_id,
            "active_run_id": self.active_run_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        raw_status = data.get("status", CampaignStatus.DRAFT.value)
        status = CampaignStatus(raw_status) if raw_status in CampaignStatus.__members__ else CampaignStatus.DRAFT
        return cls(
            id=data.get("id", f"camp_{uuid.uuid4().hex[:8]}"),
            client_id=data.get("client_id", ""),
            tenant_id=data.get("tenant_id", "default_tenant"),
            name=data.get("name", "Unnamed Campaign"),
            objective=data.get("objective", ""),
            status=status,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            brief=data.get("brief", {}),
            delta_overrides=data.get("delta_overrides", {}),
            context_snapshot_id=data.get("context_snapshot_id"),
            active_run_id=data.get("active_run_id"),
            metadata=data.get("metadata", {})
        )
