"""
Unit Tests for AI Brain Foundation Layer:
AIProviderGateway, MockAIProvider, normalized AIRequest/AIResponse,
and structured output validation.
"""

import unittest
from adcra.ai.gateway import AIProviderGateway, get_ai_gateway
from adcra.ai.adapters.mock_adapter import MockAIProvider
from adcra.ai.types import (
    AIRequest, AIMessage, TaskType, ModelCapability, CostEstimate
)


class TestAIBrainFoundation(unittest.TestCase):
    def setUp(self):
        self.gateway = AIProviderGateway()
        self.mock_provider = MockAIProvider()
        self.gateway.register_adapter(self.mock_provider)
        self.gateway.set_default_provider("mock")

    def test_gateway_registration_and_retrieval(self):
        self.assertTrue(self.gateway.has_adapter("mock"))
        adapter = self.gateway.get_adapter("mock")
        self.assertEqual(adapter.provider_id, "mock")
        providers = self.gateway.list_providers()
        self.assertGreaterEqual(len(providers), 1)
        self.assertTrue(providers[0]["connected"])

    def test_mock_provider_models_and_capabilities(self):
        models = self.mock_provider.list_models()
        self.assertGreaterEqual(len(models), 2)
        m_ids = [m["model_id"] for m in models]
        self.assertIn("mock-reasoning-pro", m_ids)
        self.assertIn("mock-creative-flash", m_ids)

        caps = self.mock_provider.get_model_capabilities("mock-reasoning-pro")
        self.assertTrue(caps.get(ModelCapability.REASONING.value))
        self.assertTrue(caps.get(ModelCapability.TOOL_CALLING.value))

    def test_cost_estimation(self):
        req = AIRequest(
            request_id="test_req_cost",
            messages=[AIMessage(role="user", content="Test cost estimation message length")]
        )
        est = self.mock_provider.estimate_cost(req, "mock-creative-flash")
        self.assertIsInstance(est, CostEstimate)
        self.assertGreater(est.estimated_input_tokens, 0)
        self.assertGreater(est.estimated_output_tokens, 0)
        self.assertGreater(est.estimated_cost_usd, 0.0)

    def test_execute_creative_concept_structured_output(self):
        req = AIRequest(
            request_id="test_req_concept",
            task_type=TaskType.CREATIVE_CONCEPT,
            messages=[AIMessage(role="user", content="Crear 3 territorios de campaña")]
        )
        response = self.gateway.execute(req)
        self.assertEqual(response.provider_id, "mock")
        self.assertIsNotNone(response.structured_data)
        self.assertIn("territories", response.structured_data)
        self.assertEqual(len(response.structured_data["territories"]), 3)
        self.assertGreater(response.usage["input_tokens"], 0)
        self.assertGreater(response.usage["output_tokens"], 0)

    def test_execute_stream(self):
        req = AIRequest(
            request_id="test_req_stream",
            task_type=TaskType.COPY_GENERATE,
            messages=[AIMessage(role="user", content="Generar copy")]
        )
        events = list(self.mock_provider.stream(req))
        self.assertGreater(len(events), 1)
        event_types = [e.event_type for e in events]
        self.assertIn("content_chunk", event_types)
        self.assertIn("completed", event_types)

    def test_error_simulation_and_fallback(self):
        # Configurar fallo temporal en mock
        self.mock_provider.set_force_failure(True, count=1)
        req = AIRequest(
            request_id="test_req_fail",
            messages=[AIMessage(role="user", content="Fail check")]
        )
        with self.assertRaises(RuntimeError):
            self.gateway.execute(req)


if __name__ == "__main__":
    unittest.main()
