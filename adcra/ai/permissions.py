"""
ADCRA AI Brain — Tool Permission Engine
Evaluates granular security permissions (READ, WRITE, EXECUTE, DELETE, PUBLISH, EXTERNAL, PAID, DESTRUCTIVE)
to ensure safe, tenant-isolated and policy-compliant tool invocations.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from adcra.ai.types import PermissionLevel, RiskLevel

logger = logging.getLogger("adcra.ai.permissions")


class PermissionEngine:
    def __init__(self):
        # Permisos por rol de agente del sistema
        self._role_permissions: Dict[str, Set[PermissionLevel]] = {
            "Creative Director": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE
            },
            "Strategist": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.EXTERNAL
            },
            "Research Analyst": {
                PermissionLevel.READ, PermissionLevel.EXTERNAL
            },
            "Copywriter": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE
            },
            "Audio Analyst": {
                PermissionLevel.READ, PermissionLevel.EXECUTE
            },
            "Visual Director": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE
            },
            "Storyboard Director": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE
            },
            "Motion Designer": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE
            },
            "Production Director": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE
            },
            "QC Director": {
                PermissionLevel.READ, PermissionLevel.EXECUTE
            },
            "Delivery Manager": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE, PermissionLevel.PUBLISH
            },
            "Admin": {
                PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE,
                PermissionLevel.DELETE, PermissionLevel.PUBLISH, PermissionLevel.EXTERNAL,
                PermissionLevel.PAID, PermissionLevel.DESTRUCTIVE
            }
        }

    def check_permissions(
        self,
        agent_role: str,
        required_permissions: List[PermissionLevel],
        tenant_policy: Optional[Dict[str, Any]] = None
    ) -> bool:
        # Si el rol no está explícito, otorgar permisos base seguros READ y EXECUTE si no son de alto riesgo
        granted = self._role_permissions.get(agent_role, {PermissionLevel.READ, PermissionLevel.EXECUTE})
        for req in required_permissions:
            if req not in granted:
                logger.warning(f"Permission denied for role '{agent_role}': missing '{req.value}'")
                return False

        # Comprobar si el tenant bloquea operaciones externas o pagas
        if tenant_policy:
            if PermissionLevel.PAID in required_permissions and not tenant_policy.get("allow_paid_tools", True):
                return False
            if PermissionLevel.EXTERNAL in required_permissions and not tenant_policy.get("allow_external_tools", True):
                return False

        return True

    def is_high_risk(self, tool_permissions: List[PermissionLevel], risk_level: RiskLevel) -> bool:
        high_risk_perms = {
            PermissionLevel.PUBLISH,
            PermissionLevel.DESTRUCTIVE,
            PermissionLevel.DELETE,
            PermissionLevel.PAID
        }
        has_high_perm = any(p in high_risk_perms for p in tool_permissions)
        return has_high_perm or (risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])


_GLOBAL_PERMISSIONS = PermissionEngine()

def get_permission_engine() -> PermissionEngine:
    return _GLOBAL_PERMISSIONS
