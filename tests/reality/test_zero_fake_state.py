import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import adcra.ai as ai
from adcra.ai.types import ProviderStatus, CostConfidence
from adcra.infrastructure.secrets.secret_store import LocalSecureSecretStore, get_secret_provider
from adcra.infrastructure.persistence.client_repository import ClientRepository
from adcra.infrastructure.persistence.campaign_repository import CampaignRepository
from adcra.infrastructure.persistence.run_repository import RunRepository
from adcra.infrastructure.events.event_bus import EventBus
from adcra.api.routes.provider_routes import handle_providers_request
from adcra.api.routes.client_routes import handle_clients_request
from adcra.api.routes.run_routes import handle_runs_request


class TestZeroFakeState(unittest.TestCase):
    """
    ADCRA v2.1 Reality Verification Suite.
    Enforces the Core System Directive:
    NO DATA MAY BE PRESENTED AS REAL UNLESS IT IS BACKED BY REAL SYSTEM STATE.
    Zero hallucinated/fake state allowed.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.secret_store = LocalSecureSecretStore(storage_dir=Path(self.temp_dir) / "secrets")
        self.client_repo = ClientRepository(base_dir=os.path.join(self.temp_dir, "clients"))
        self.campaign_repo = CampaignRepository(base_dir=os.path.join(self.temp_dir, "clients"))
        self.run_repo = RunRepository(base_dir=os.path.join(self.temp_dir, "runs"))
        self.event_bus = EventBus()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unconfigured_real_providers_report_not_configured(self):
        """Unconfigured real providers must report configured=False, connected=False, NOT_CONFIGURED."""
        gw = ai.get_ai_gateway()
        # Ensure clean environment for external keys
        with patch.dict(os.environ, {}, clear=True):
            providers = gw.list_providers()
            for p in providers:
                pid = p["provider_id"]
                if pid == "mock":
                    self.assertEqual(p["execution_mode"], "SIMULATION")
                    self.assertEqual(p["status"], "HEALTHY")
                else:
                    self.assertEqual(p["execution_mode"], "REAL")
                    self.assertFalse(p["configured"], f"Provider {pid} must not be configured without a key")
                    self.assertFalse(p["connected"], f"Provider {pid} must not be connected without a key")
                    self.assertEqual(p["status"], "NOT_CONFIGURED")
                    self.assertEqual(p["models_count"], 0)

    def test_mock_provider_strictly_labeled_as_simulation(self):
        """Mock provider must never masquerade as a real production provider."""
        gw = ai.get_ai_gateway()
        mock_adapter = gw.get_adapter("mock")
        config_status = mock_adapter.validate_configuration()
        self.assertEqual(config_status.get("execution_mode"), "SIMULATION")
        self.assertEqual(config_status.get("provider_type"), "MOCK")

        test_res = mock_adapter.test_connection()
        self.assertEqual(test_res.get("execution_mode"), "SIMULATION")
        self.assertEqual(test_res.get("provider_type"), "MOCK")

    def test_empty_client_repository_reports_zero_clients(self):
        """When no clients are stored, repository must return empty list, not fake fallback."""
        clients = self.client_repo.list_all()
        self.assertEqual(len(clients), 0)
        self.assertEqual(clients, [])

    def test_empty_run_repository_reports_zero_runs(self):
        """When no runs exist, repository must return empty list, not mock data."""
        runs = self.run_repo.list_all()
        self.assertEqual(len(runs), 0)
        self.assertEqual(runs, [])

    def test_secret_redaction_in_provider_api(self):
        """API keys must never be leaked through provider endpoints or events."""
        raw_key = "sk-proj-supersecretkey1234567890abcdef"
        self.secret_store.set_secret("OPENAI_API_KEY", raw_key)
        masked = self.secret_store.get_masked_secret("OPENAI_API_KEY")
        self.assertTrue(masked.startswith("sk-") or masked.startswith("***"))
        self.assertNotIn("supersecretkey", masked)

        # Verify event bus redacts secrets from payloads
        captured_events = []
        self.event_bus.subscribe("test.secret", lambda e: captured_events.append(e))
        self.event_bus.publish(
            event_type="test.secret",
            source="Test",
            payload={"api_key": raw_key, "token": "secret_tok_999", "provider": "openai"}
        )
        self.assertEqual(len(captured_events), 1)
        event_payload = captured_events[0].payload
        self.assertNotEqual(event_payload["api_key"], raw_key)
        self.assertEqual(event_payload["api_key"], "[REDACTED]")
        self.assertEqual(event_payload["token"], "[REDACTED]")
        self.assertEqual(event_payload["provider"], "openai")

    def test_provider_routes_never_expose_raw_keys(self):
        """GET /api/ai/providers must never return unmasked api keys."""
        status_code, body = handle_providers_request("GET", "/api/ai/providers")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)
        for p in body:
            self.assertNotIn("api_key", p)
            if p.get("masked_key"):
                self.assertFalse("supersecret" in p["masked_key"])


if __name__ == "__main__":
    unittest.main()
