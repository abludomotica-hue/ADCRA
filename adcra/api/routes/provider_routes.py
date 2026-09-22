"""
ADCRA v2.1 — AI Provider API Routes
Handles:
GET  /api/ai/providers
POST /api/ai/providers/{provider_id}/configure
POST /api/ai/providers/{provider_id}/test
POST /api/ai/providers/{provider_id}/discover-models
GET  /api/ai/providers/{provider_id}/health
POST /api/ai/providers/{provider_id}/disable
"""

from typing import Dict, Any, Tuple, Optional
import adcra.ai as ai
from adcra.infrastructure.events.event_bus import get_event_bus
from adcra.infrastructure.secrets.secret_store import get_secret_provider


def handle_providers_request(
    method: str,
    path: str,
    body_data: Optional[Dict[str, Any]] = None,
    tenant_id: str = "default_tenant"
) -> Tuple[int, Dict[str, Any]]:
    gw = ai.get_ai_gateway()
    health_mon = ai.get_health_monitor()
    event_bus = get_event_bus()
    secret_prov = get_secret_provider()

    parts = [p for p in path.split("/") if p]
    # ['api', 'ai', 'providers', ...]

    # 1. GET /api/ai/providers
    if method == "GET" and len(parts) == 3:
        providers = gw.list_providers()
        # Add masked secret info to details
        clean_providers = []
        for p in providers:
            pid = p["provider_id"]
            p_copy = dict(p)
            key_name = f"{pid.upper()}_API_KEY"
            p_copy["is_configured"] = p["configured"]
            p_copy["masked_key"] = secret_prov.get_masked_secret(key_name) if pid != "mock" else None
            clean_providers.append(p_copy)

        return 200, clean_providers

    if len(parts) >= 4:
        provider_id = parts[3]
        if not gw.has_adapter(provider_id):
            return 404, {"error": "PROVIDER_NOT_FOUND", "message": f"AI Provider '{provider_id}' is not registered."}

        # 2. POST /api/ai/providers/{provider_id}/configure
        if method == "POST" and len(parts) == 5 and parts[4] == "configure":
            if not body_data:
                return 400, {"error": "BAD_REQUEST", "message": "No credentials provided."}
            test_res = gw.configure_provider(provider_id, body_data)
            event_bus.publish(
                event_type="provider.configured",
                source="ProviderAPI",
                payload={"provider_id": provider_id, "status": test_res.get("status")}
            )
            # Never return keys
            clean_res = dict(test_res)
            clean_res.pop("api_key", None)
            return 200, clean_res

        # 3. POST /api/ai/providers/{provider_id}/test
        if method == "POST" and len(parts) == 5 and parts[4] == "test":
            test_res = gw.test_provider(provider_id)
            if test_res.get("status") in ["DEGRADED", "UNAVAILABLE"]:
                event_bus.publish(
                    event_type="provider.degraded",
                    source="ProviderAPI",
                    payload={"provider_id": provider_id, "details": test_res}
                )
            elif test_res.get("connected"):
                event_bus.publish(
                    event_type="provider.recovered",
                    source="ProviderAPI",
                    payload={"provider_id": provider_id}
                )
            return 200, test_res

        # 4. POST /api/ai/providers/{provider_id}/discover-models
        if method == "POST" and len(parts) == 5 and parts[4] == "discover-models":
            models = gw.discover_models(provider_id)
            return 200, {
                "provider_id": provider_id,
                "total_models": len(models),
                "models": models
            }

        # 5. GET /api/ai/providers/{provider_id}/health
        if method == "GET" and len(parts) == 5 and parts[4] == "health":
            health = health_mon.get_provider_health(provider_id)
            return 200, health

        # 6. POST /api/ai/providers/{provider_id}/disable
        if method == "POST" and len(parts) == 5 and parts[4] == "disable":
            cb = health_mon.get_circuit_breaker(provider_id)
            cb.state = ai.health.CircuitState.OPEN
            return 200, {"status": "DISABLED", "provider_id": provider_id}

    return 404, {"error": "NOT_FOUND", "message": f"No provider route matches {method} {path}"}
