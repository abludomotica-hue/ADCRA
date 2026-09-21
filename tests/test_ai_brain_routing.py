"""
Unit Tests for Model Registry, Model Router, Cost Ledger & Budget Engine
"""

import unittest
from adcra.ai.models import get_model_registry, ModelRegistry
from adcra.ai.router import get_model_router, ModelRouter
from adcra.ai.cost import AICostLedger, BudgetEngine
from adcra.ai.types import (
    AIRequest, AIMessage, TaskType, RoutingMode, BudgetStatus
)


class TestAIBrainRoutingAndCost(unittest.TestCase):
    def setUp(self):
        self.registry = get_model_registry()
        self.router = get_model_router()

    def test_model_registry_discovery(self):
        models = self.registry.list_models()
        self.assertGreater(len(models), 0)
        # Verificar que se cargan modelos con sus pricing y capacidades
        sample = models[0]
        self.assertIn("model_id", sample)
        self.assertIn("capabilities", sample)
        self.assertIn("cost_per_million_input", sample)

    def test_model_router_auto_mode(self):
        req = AIRequest(
            request_id="test_route_strategy",
            task_type=TaskType.CAMPAIGN_STRATEGY,
            messages=[AIMessage(role="user", content="Plan campaign strategy")]
        )
        provider_id, model_id, fallbacks = self.router.route(req, mode=RoutingMode.AUTO)
        self.assertIsNotNone(provider_id)
        self.assertIsNotNone(model_id)

    def test_model_router_cost_optimized_mode(self):
        req = AIRequest(
            request_id="test_route_copy",
            task_type=TaskType.COPY_GENERATE,
            messages=[AIMessage(role="user", content="Fast short copy")]
        )
        provider_id, model_id, _ = self.router.route(req, mode=RoutingMode.COST_OPTIMIZED)
        self.assertIsNotNone(model_id)

    def test_cost_ledger_recording_and_summary(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        ledger = AICostLedger(ledger_file=temp_path)
        ledger.record_usage(
            tenant_id="test_tenant",
            campaign_id="test_camp",
            agent_id="Creative Director",
            task="creative.concept",
            provider_id="mock",
            model_id="mock-creative-flash",
            input_tokens=100,
            output_tokens=200,
            cached_tokens=0,
            cost_usd=0.00015
        )

        summary = ledger.get_summary(campaign_id="test_camp", tenant_id="test_tenant")
        self.assertEqual(summary["total_calls"], 1)
        self.assertEqual(summary["total_tokens"], 300)
        self.assertGreater(summary["total_cost_usd"], 0.0)
        self.assertIn("creative.concept", summary["by_task"])

    def test_budget_engine_limits(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        ledger = AICostLedger(ledger_file=temp_path)
        budget = BudgetEngine(cost_ledger=ledger, max_cost_per_request=0.50, max_cost_per_campaign=10.00)

        # 1. Normal request
        status, _ = budget.check_budget("camp_1", estimated_cost=0.05)
        self.assertEqual(status, BudgetStatus.NORMAL)

        # 2. Blocked by single request limit
        status_blocked, msg = budget.check_budget("camp_1", estimated_cost=1.50)
        self.assertEqual(status_blocked, BudgetStatus.BLOCKED)
        self.assertIn("exceeds max per-request limit", msg)


if __name__ == "__main__":
    unittest.main()
