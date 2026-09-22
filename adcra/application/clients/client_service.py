"""
ADCRA v2.1 — Client Application Service
Implements business use cases for Client lifecycle, Brand DNA management,
and multi-client isolation.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional
from adcra.domain.clients.client import Client, BrandProfile, Product, AudienceProfile
from adcra.infrastructure.persistence.client_repository import get_client_repository

logger = logging.getLogger("adcra.application.client")


class ClientService:
    def __init__(self, repo=None):
        self._repo = repo or get_client_repository()

    def create_client(self, data: Dict[str, Any], tenant_id: str = "default_tenant") -> Client:
        client_name = data.get("name", "").strip()
        if not client_name:
            raise ValueError("Client name cannot be empty.")

        # Generate slug-based or uuid-based id
        client_id = data.get("id")
        if not client_id:
            slug = "".join(c if c.isalnum() else "-" for c in client_name.lower()).strip("-")
            client_id = slug if slug and not self._repo.exists(slug) else f"{slug or 'client'}_{uuid.uuid4().hex[:6]}"

        if self._repo.exists(client_id):
            raise ValueError(f"Client with ID '{client_id}' already exists.")

        brand_data = data.get("brand_dna", {})
        brand_dna = BrandProfile.from_dict(brand_data) if brand_data else BrandProfile()

        client = Client(
            id=client_id,
            name=client_name,
            tenant_id=tenant_id,
            company=data.get("company", ""),
            description=data.get("description", ""),
            industry=data.get("industry", ""),
            website=data.get("website", ""),
            socials=data.get("socials", {}),
            brand_dna=brand_dna,
            status="ACTIVE",
            metadata=data.get("metadata", {})
        )
        return self._repo.save(client)

    def get_client(self, client_id: str, tenant_id: Optional[str] = None) -> Optional[Client]:
        return self._repo.get(client_id, tenant_id=tenant_id)

    def list_clients(self, tenant_id: Optional[str] = None) -> List[Client]:
        return self._repo.list(tenant_id=tenant_id)

    def update_client(self, client_id: str, updates: Dict[str, Any], tenant_id: Optional[str] = None) -> Optional[Client]:
        client = self._repo.get(client_id, tenant_id=tenant_id)
        if not client:
            return None

        if "name" in updates and updates["name"]:
            client.name = updates["name"].strip()
        if "company" in updates:
            client.company = updates["company"]
        if "description" in updates:
            client.description = updates["description"]
        if "industry" in updates:
            client.industry = updates["industry"]
        if "website" in updates:
            client.website = updates["website"]
        if "socials" in updates and isinstance(updates["socials"], dict):
            client.socials = updates["socials"]
        if "status" in updates:
            client.status = updates["status"]
        if "brand_dna" in updates and isinstance(updates["brand_dna"], dict):
            client.brand_dna = BrandProfile.from_dict(updates["brand_dna"])

        return self._repo.save(client)

    def delete_client(self, client_id: str, tenant_id: Optional[str] = None) -> bool:
        return self._repo.delete(client_id, tenant_id=tenant_id)

    def get_brand_dna(self, client_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        client = self._repo.get(client_id, tenant_id=tenant_id)
        return client.brand_dna.to_dict() if client else None

    def update_brand_dna(self, client_id: str, brand_data: Dict[str, Any], tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        client = self._repo.get(client_id, tenant_id=tenant_id)
        if not client:
            return None
        client.brand_dna = BrandProfile.from_dict(brand_data)
        self._repo.save(client)
        return client.brand_dna.to_dict()


_GLOBAL_CLIENT_SERVICE: Optional[ClientService] = None

def get_client_service() -> ClientService:
    global _GLOBAL_CLIENT_SERVICE
    if _GLOBAL_CLIENT_SERVICE is None:
        _GLOBAL_CLIENT_SERVICE = ClientService()
    return _GLOBAL_CLIENT_SERVICE
