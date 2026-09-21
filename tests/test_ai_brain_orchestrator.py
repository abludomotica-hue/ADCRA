"""
Unit and Integration Tests for Intent Engine, Plan Engine & Agent Orchestrator
"""

import unittest
from adcra.ai.intent import get_intent_engine
from adcra.ai.planner import get_plan_engine
from adcra.ai.orchestrator import get_agent_orchestrator
from adcra.ai.types import AgentState


class TestAIBrainOrchestrator(unittest.TestCase):
    def setUp(self):
        self.intent_engine = get_intent_engine()
        self.plan_engine = get_plan_engine()
        self.orchestrator = get_agent_orchestrator()

    def test_intent_engine_parsing(self):
        # 1. Quick action trigger
        intent_quick = self.intent_engine.parse_intent("create_concept")
        self.assertEqual(intent_quick.intent_type, "CREATIVE_CONCEPT")

        # 2. Natural language instruction
        intent_nl = self.intent_engine.parse_intent("Crea 5 versiones de copy para TikTok con tono juvenil")
        self.assertEqual(intent_nl.intent_type, "COPY_GENERATE")
        self.assertEqual(intent_nl.platform, "Tiktok")
        self.assertEqual(intent_nl.count, 5)
        self.assertEqual(intent_nl.tone, "Juvenil & Dinámico")

    def test_plan_engine_task_graph(self):
        plan = self.plan_engine.create_plan_for_intent("CREATIVE_CONCEPT")
        self.assertGreater(len(plan.steps), 2)
        step_ids = [s.step_id for s in plan.steps]
        self.assertIn("step_load_brand_dna", step_ids)
        self.assertIn("step_generate_territories", step_ids)

    def test_orchestrator_end_to_end_creative_concept(self):
        result = self.orchestrator.run_intent(
            intent_input="Crear una campaña para Locos Materos enfocada en jóvenes y con un tono más auténtico",
            campaign_id="camp_locos_materos_2026"
        )
        self.assertEqual(result.status, AgentState.COMPLETED)
        self.assertIsNotNone(result.run_id)
        self.assertGreater(result.total_tokens, 0)
        self.assertGreater(result.total_cost, 0.0)
        self.assertIn("territories", result.outputs)
        self.assertIn("brand_dna", result.outputs)


if __name__ == "__main__":
    unittest.main()
