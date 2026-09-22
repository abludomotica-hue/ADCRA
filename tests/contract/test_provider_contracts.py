import unittest
import adcra.ai as ai
from adcra.ai.types import (
    AIRequest,
    AIMessage,
    AIResponse,
    AIProviderError,
    CostEstimate,
    CostConfidence
)


class TestProviderContracts(unittest.TestCase):
    """
    ADCRA v2.1 Provider Contract Specification Tests.
    Guarantees that all provider adapters satisfy the strict AIProviderAdapter interface contract.
    """

    def setUp(self):
        self.gw = ai.get_ai_gateway()
        self.provider_ids = ["mock", "openai", "gemini", "anthropic", "openrouter"]

    def test_all_expected_providers_registered(self):
        """Verify all 5 core provider adapters are registered."""
        for pid in self.provider_ids:
            self.assertTrue(self.gw.has_adapter(pid), f"Missing expected adapter for '{pid}'")

    def test_provider_adapters_interface_compliance(self):
        """Verify every adapter implements the full lifecycle interface."""
        contract_methods = [
            "initialize",
            "validate_configuration",
            "test_connection",
            "list_models",
            "discover_models",
            "generate",
            "stream",
            "estimate_cost",
        ]
        for pid in self.provider_ids:
            adapter = self.gw.get_adapter(pid)
            self.assertIsNotNone(adapter.provider_id)
            self.assertIsNotNone(adapter.name)
            for m in contract_methods:
                self.assertTrue(
                    hasattr(adapter, m) and callable(getattr(adapter, m)),
                    f"Adapter '{pid}' does not implement required contract method '{m}'"
                )

    def test_adapter_initialization(self):
        """Verify initialize() succeeds on all adapters."""
        for pid in self.provider_ids:
            adapter = self.gw.get_adapter(pid)
            res = adapter.initialize()
            self.assertTrue(res, f"Adapter '{pid}' initialize() failed")

    def test_validate_configuration_structure(self):
        """Verify validate_configuration returns standardized schema."""
        for pid in self.provider_ids:
            adapter = self.gw.get_adapter(pid)
            res = adapter.validate_configuration()
            self.assertIsInstance(res, dict)
            self.assertIn("provider", res)
            self.assertIn("configured", res)
            self.assertIn("connected", res)
            self.assertIn("status", res)

    def test_list_models_structure(self):
        """Verify list_models returns standardized list of model descriptors."""
        for pid in self.provider_ids:
            adapter = self.gw.get_adapter(pid)
            models = adapter.list_models()
            self.assertIsInstance(models, list)
            for m in models:
                self.assertTrue("model_id" in m or "id" in m, f"Model descriptor in {pid} missing id")
                self.assertIn("name", m)

    def test_cost_estimation_contract(self):
        """Verify estimate_cost returns CostEstimate object."""
        req = AIRequest(
            request_id="req_contract_cost",
            messages=[AIMessage(role="user", content="Produce 3 campaign headline options.")]
        )
        for pid in self.provider_ids:
            adapter = self.gw.get_adapter(pid)
            models = adapter.list_models()
            model_id = (models[0].get("model_id") or models[0].get("id")) if models else "default"
            est = adapter.estimate_cost(req, model_id)
            self.assertIsInstance(est, CostEstimate)
            self.assertGreaterEqual(est.estimated_cost_usd, 0.0)
            self.assertIn(est.confidence, [CostConfidence.KNOWN_COST, CostConfidence.ESTIMATED_COST, CostConfidence.UNKNOWN_COST])

    def test_mock_adapter_generate_lifecycle(self):
        """Verify mock adapter generate succeeds in simulation mode."""
        adapter = self.gw.get_adapter("mock")
        req = AIRequest(
            request_id="req_contract_gen",
            messages=[AIMessage(role="user", content="Test creative concept")]
        )
        resp = adapter.generate(req)
        self.assertIsInstance(resp, AIResponse)
        self.assertTrue(len(resp.content) > 0)
        self.assertIn("SIMULATION", resp.usage.get("execution_mode", ""))
        self.assertEqual(resp.provider_id, "mock")

    def test_unconfigured_real_adapters_fail_gracefully_on_generate(self):
        """Unconfigured adapters must raise AIProviderError, not uncaught system crashes."""
        req = AIRequest(
            request_id="req_contract_unconf",
            messages=[AIMessage(role="user", content="Real prompt without API key")]
        )
        for pid in ["openai", "gemini", "anthropic", "openrouter"]:
            adapter = self.gw.get_adapter(pid)
            # If not configured, generate must raise AIProviderError
            config = adapter.validate_configuration()
            if not config.get("configured"):
                with self.assertRaises(AIProviderError):
                    adapter.generate(req)


if __name__ == "__main__":
    unittest.main()
