"""
ADCRA v2.1 — Client Domain Entity & Brand DNA
Defines the Client entity, BrandProfile (Brand DNA), Product, and Audience models.
Encforces domain invariants:
- A Client is independent from Campaigns.
- Brand DNA is owned by the Client and inherited by Campaigns by reference.
- Client memory and learning history are isolated per client.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class BrandProfile:
    mission: str = ""
    values: List[str] = field(default_factory=list)
    personality: List[str] = field(default_factory=list)
    tone: Dict[str, Any] = field(default_factory=lambda: {
        "primary_tone": "Inspiring & Authentic",
        "emotional_register": "Energetic / Warm",
        "voice_guidelines": "Direct, conversational, respectful of heritage"
    })
    colors: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#0D5C3A",
        "secondary": "#C2A649",
        "accent": "#E65100",
        "background": "#0A0E17"
    })
    typography: Dict[str, str] = field(default_factory=lambda: {
        "heading": "Cabinet Grotesk",
        "body": "Inter",
        "accent": "JetBrains Mono"
    })
    logo_url: Optional[str] = None
    visual_style: str = "Cinematic Warm / Contemporary Heritage"
    motion_style: str = "Dynamic Rhythmic Cuts / Beat-Synced"
    language: str = "es-CL"
    approved_claims: List[str] = field(default_factory=list)
    forbidden_claims: List[str] = field(default_factory=list)
    retention_rules: Dict[str, Any] = field(default_factory=dict)
    aesthetic_learnings: Dict[str, Any] = field(default_factory=dict)
    musical_tempo_learnings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrandProfile":
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class Product:
    product_id: str
    name: str
    description: str = ""
    category: str = ""
    benefits: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    differentiators: List[str] = field(default_factory=list)
    claims: List[str] = field(default_factory=list)
    price_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AudienceProfile:
    audience_id: str
    name: str
    primary_segment: str = ""
    secondary_segment: str = ""
    pain_points: List[str] = field(default_factory=list)
    desires: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    consumption_context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Client:
    id: str
    name: str
    tenant_id: str = "default_tenant"
    company: str = ""
    description: str = ""
    industry: str = ""
    website: str = ""
    socials: Dict[str, str] = field(default_factory=dict)
    brand_dna: BrandProfile = field(default_factory=BrandProfile)
    products: List[Product] = field(default_factory=list)
    audiences: List[AudienceProfile] = field(default_factory=list)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "ACTIVE"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "tenant_id": self.tenant_id,
            "company": self.company,
            "description": self.description,
            "industry": self.industry,
            "website": self.website,
            "socials": self.socials,
            "brand_dna": self.brand_dna.to_dict(),
            "products": [p.to_dict() for p in self.products],
            "audiences": [a.to_dict() for a in self.audiences],
            "assets": self.assets,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Client":
        brand_data = data.get("brand_dna", {})
        brand_dna = BrandProfile.from_dict(brand_data) if isinstance(brand_data, dict) else BrandProfile()
        
        products = [Product(**p) if isinstance(p, dict) else p for p in data.get("products", [])]
        audiences = [AudienceProfile(**a) if isinstance(a, dict) else a for a in data.get("audiences", [])]

        return cls(
            id=data.get("id", f"client_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", "Unnamed Client"),
            tenant_id=data.get("tenant_id", "default_tenant"),
            company=data.get("company", ""),
            description=data.get("description", ""),
            industry=data.get("industry", ""),
            website=data.get("website", ""),
            socials=data.get("socials", {}),
            brand_dna=brand_dna,
            products=products,
            audiences=audiences,
            assets=data.get("assets", []),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            status=data.get("status", "ACTIVE"),
            metadata=data.get("metadata", {})
        )
