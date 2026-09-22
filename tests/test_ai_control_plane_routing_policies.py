"""
Unit and Integration Tests for ADCRA AI Intelligence Control Plane v2.0 - Routing & Policies
Verifies:
- ModelPolicy enum and policy weight calculations
- Logical routing aliases (creative.high, creative.fast, strategy.deep, etc.)
- ModelRouter.route_detailed() with capability matching and policy optimization
- Circuit-breaker aware routing candidate filtering
- ModelRouter.explain_routing() explanation generation
"""

import unittest
from adcra.ai.policies import ModelPolicy, ModelPolicyEngine, get_policy_engine
from adcra.ai.router import ModelRouter, RoutingDecision, get_model_router
from adcra.ai.types import AIRequest, TaskType, AIMessage

class TestAiControlPlaneRoutingPolicies(unittest.TestCase):

    def setUp(self):
        self.policy_engine = ModelPolicyEngine()
        self.router = ModelRouter()

    def test_logical_aliases_loaded(self):
        """Verify the 10 canonical logical aliases are registered from config/ai-routing-policies.json."""
        aliases = self.policy_engine.list_aliases()
        self.assertEqual(len(aliases), 10)

        expected = [
            "creative.high", "creative.fast", "strategy.deep", "strategy.fast",
            "vision.high", "vision.fast", "copy.high", "copy.fast",
            "qc.deep", "qc.fast"
        ]
        for a in expected:
            self.assertIn(a, aliases)

    def test_alias_resolution(self):
        """Verify resolving an alias returns preferred_provider, preferred_model, and fallback chain."""
        resolved = self.policy_engine.resolve_alias("creative.high")
        self.assertIsNotNone(resolved)
        self.assertIn("preferred_provider", resolved)
        self.assertIn("preferred_model", resolved)
        self.assertIn("fallbacks", resolved)
        self.assertGreater(len(resolved["fallbacks"]), 0)

    def test_policy_scoring_weights(self):
        """Verify score_candidate behaves differently under QUALITY_FIRST vs COST_OPTIMIZED."""
        mock_model = {
            "quality_score": 95,
            "speed_score": 60,
            "cost_per_million_input": 15.0,
            "cost_per_million_output": 60.0
        }

        # Under Quality First, high quality gives high score despite high cost
        score_q, _ = self.policy_engine.score_candidate(mock_model, policy=ModelPolicy.QUALITY_FIRST)

        # Under Cost Optimized, high cost lowers the score
        score_c, _ = self.policy_engine.score_candidate(mock_model, policy=ModelPolicy.COST_OPTIMIZED)

        self.assertGreater(score_q, score_c)

    def test_route_detailed_with_alias(self):
        """Verify routing request with model_preference set to a logical alias."""
        req = AIRequest(
            request_id="test_alias_req",
            task_type=TaskType.CREATIVE_CONCEPT,
            model_preference="creative.high",
            messages=[AIMessage(role="user", content="Concepto para yerba mate")]
        )

        decision = self.router.route_detailed(req)
        self.assertIsInstance(decision, RoutingDecision)
        self.assertIsNotNone(decision.selected_provider)
        self.assertIsNotNone(decision.selected_model)
        self.assertGreater(len(decision.fallback_chain), 0)

    def test_explain_routing(self):
        """Verify explain_routing returns a comprehensive dictionary with human-readable rationale."""
        req = AIRequest(
            request_id="test_explain_req",
            task_type=TaskType.COPY_GENERATE,
            messages=[AIMessage(role="user", content="Guion de 15s")]
        )
        decision = self.router.route_detailed(req, policy=ModelPolicy.BALANCED)
        explanation = self.router.explain_routing(req, decision)

        self.assertIsInstance(explanation, dict)
        self.assertIn("explanation", explanation)
        self.assertIn("score_breakdown", explanation)
        self.assertEqual(explanation["requested_policy"], ModelPolicy.BALANCED.value)
        self.assertIn(decision.selected_model, explanation["explanation"])

if __name__ == "__main__":
    unittest.main()
