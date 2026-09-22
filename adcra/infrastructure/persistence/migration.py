"""
ADCRA v2.1 — Initial Data Migration & Seeding
Migrates legacy single-campaign pilot files (Locos Materos) into structured multi-tenant
storage/clients/locos-materos/ without modifying or breaking existing legacy files.
"""

import os
import json
import logging
from pathlib import Path
from adcra.domain.clients.client import Client, BrandProfile
from adcra.domain.campaigns.campaign import Campaign, CampaignStatus, CampaignContextSnapshot
from adcra.infrastructure.persistence.client_repository import get_client_repository
from adcra.infrastructure.persistence.campaign_repository import get_campaign_repository

logger = logging.getLogger("adcra.persistence.migration")
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def run_legacy_migration() -> None:
    client_repo = get_client_repository()
    camp_repo = get_campaign_repository()

    # Check if locos-materos client is already seeded
    if client_repo.exists("locos-materos"):
        return

    logger.info("Executing legacy data migration for pilot client 'locos-materos'...")
    brand_file = WORKSPACE_ROOT / "campaign" / "memory" / "brand-profile-memory.json"
    brand_data = {}
    if brand_file.is_file():
        try:
            with open(brand_file, "r", encoding="utf-8") as f:
                brand_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not read {brand_file}: {e}")

    # Build BrandProfile
    brand_profile = BrandProfile(
        mission="Revolucionar la experiencia del mate con accesorios de autor y yerba premium.",
        values=["Autenticidad", "Diseño", "Comunidad", "Calidad Artesanal"],
        personality=["Cálido", "Entusiasta", "Urbano", "Tradicional Moderno"],
        colors={
            "primary": "#0D5C3A",
            "secondary": "#C2A649",
            "accent": "#E65100",
            "background": "#0A0E17"
        },
        typography={
            "heading": "Cabinet Grotesk",
            "body": "Inter",
            "accent": "JetBrains Mono"
        },
        language="es-CL",
        retention_rules=brand_data.get("retention_rules", {}),
        aesthetic_learnings=brand_data.get("aesthetic_learnings", {}),
        musical_tempo_learnings=brand_data.get("musical_tempo_learnings", {
            "optimal_bpm": 107.7,
            "last_successful_bpm": 107.7,
            "preferred_tempo_range": [104.0, 112.0]
        }),
        approved_claims=["El mejor mate térmico de Chile", "Diseñado para durar toda la vida"]
    )

    # Build Client
    client = Client(
        id="locos-materos",
        name=brand_data.get("brand_name", "Locos Materos"),
        tenant_id="default_tenant",
        company="Locos Materos SpA",
        description="E-commerce líder en sets de mate térmico y yerbas de selección en Chile.",
        industry="Alimentos y Bebidas / Yerba Mate",
        website="https://locosmateros.cl",
        brand_dna=brand_profile,
        status="ACTIVE",
        metadata={"legacy_migrated": True}
    )
    client_repo.save(client)

    # Build & save Campaign
    campaign = Campaign(
        id="camp_locos_materos_2026",
        client_id="locos-materos",
        tenant_id="default_tenant",
        name="Locos Materos — Lanzamiento Verano 2026",
        objective="Conversión directa e-commerce para sets de mate de autor 9x16",
        status=CampaignStatus.DELIVERED,
        brief={
            "target_channels": ["instagram_reels", "tiktok", "youtube_shorts"],
            "aspect_ratio": "9:16",
            "optimal_bpm": 107.7
        },
        metadata={"legacy_migrated": True}
    )
    camp_repo.save(campaign)

    # Save immutable context snapshot
    snapshot = CampaignContextSnapshot(
        snapshot_id="snap_locos_materos_init",
        campaign_id=campaign.id,
        client_id=client.id,
        tenant_id="default_tenant",
        brand_dna=brand_profile.to_dict(),
        audience_snapshot={"primary": "Jóvenes profesionales 22-38 años amantes del mate y café de especialidad"},
        product_snapshot={"primary_product": "Mate Térmico Autocebante Acero Inox 304"},
        approved_claims_snapshot=brand_profile.approved_claims
    )
    camp_repo.save_snapshot(snapshot)
    logger.info("Legacy migration completed: locos-materos client & campaign persisted successfully.")
