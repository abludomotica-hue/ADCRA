import shutil
"""
ADCRA v2.1 — Client Persistence Repository
Manages durable JSON storage for Clients under storage/clients/<client_id>/
Enforces multi-tenant isolation and data integrity.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from adcra.domain.clients.client import Client, BrandProfile

logger = logging.getLogger("adcra.persistence.client")
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


class ClientRepository:
    def __init__(self, base_dir: Optional[Path] = None):
        self._dir = Path(base_dir) if base_dir else (WORKSPACE_ROOT / "storage" / "clients")
        self._dir.mkdir(parents=True, exist_ok=True)

    def _client_path(self, client_id: str) -> Path:
        return self._dir / client_id / "client.json"

    def save(self, client: Client) -> Client:
        client_dir = self._dir / client.id
        client_dir.mkdir(parents=True, exist_ok=True)
        
        # Save client.json
        client_file = client_dir / "client.json"
        with open(client_file, "w", encoding="utf-8") as f:
            json.dump(client.to_dict(), f, indent=2, ensure_ascii=False)
            
        # Save dedicated brand_dna.json
        brand_file = client_dir / "brand_dna.json"
        with open(brand_file, "w", encoding="utf-8") as f:
            json.dump(client.brand_dna.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Saved client '{client.id}' ({client.name}) to {client_dir}")
        return client

    def get(self, client_id: str, tenant_id: Optional[str] = None) -> Optional[Client]:
        path = self._client_path(client_id)
        if not path.is_file():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            client = Client.from_dict(data)
            if tenant_id and client.tenant_id != tenant_id:
                return None
            return client
        except Exception as e:
            logger.error(f"Error reading client {client_id}: {e}")
            return None

    def list(self, tenant_id: Optional[str] = None) -> List[Client]:
        clients = []
        if not self._dir.is_dir():
            return clients
            
        for entry in self._dir.iterdir():
            if entry.is_dir():
                c_file = entry / "client.json"
                if c_file.is_file():
                    try:
                        with open(c_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        client = Client.from_dict(data)
                        if tenant_id and client.tenant_id != tenant_id:
                            continue
                        clients.append(client)
                    except Exception as e:
                        logger.warning(f"Skipping invalid client file in {entry}: {e}")
        return sorted(clients, key=lambda c: c.created_at, reverse=True)

    def delete(self, client_id: str, tenant_id: Optional[str] = None) -> bool:
        client = self.get(client_id, tenant_id=tenant_id)
        if not client:
            return False
        client_dir = self._dir / client_id
        if client_dir.is_dir():
            # Delete files safely
            for f in client_dir.glob("*"):
                if f.is_file():
                    f.unlink()
            try:
                shutil.rmtree(client_dir, ignore_errors=True)
                return True
            except Exception as e:
                logger.warning(f"Could not remove directory {client_dir}: {e}")
                return True
        return False

    def exists(self, client_id: str) -> bool:
        return self._client_path(client_id).is_file()


_GLOBAL_CLIENT_REPO: Optional[ClientRepository] = None

def get_client_repository() -> ClientRepository:
    global _GLOBAL_CLIENT_REPO
    if _GLOBAL_CLIENT_REPO is None:
        _GLOBAL_CLIENT_REPO = ClientRepository()
    return _GLOBAL_CLIENT_REPO

ClientRepository.list_all = ClientRepository.list
