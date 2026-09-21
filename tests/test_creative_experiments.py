"""
Unit tests for ADCRA AI Brain — Creative Variant Generator & Experiment Lab
"""

import unittest
from adcra.ai.experiments import (
    get_creative_experiment_engine, HookType, PacingType, CTAType, ExperimentMatrix
)


class TestCreativeExperimentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = get_creative_experiment_engine()

    def test_get_matrix_structure(self):
        matrix = self.engine.get_matrix()
        self.assertIsInstance(matrix, ExperimentMatrix)
        self.assertEqual(len(matrix.variants), 4)
        self.assertIn(matrix.active_variant_id, [v.variant_id for v in matrix.variants])

    def test_variants_have_complete_creative_contracts(self):
        matrix = self.engine.get_matrix()
        hook_types = {v.hook_type for v in matrix.variants}
        self.assertIn(HookType.INTRIGUE_QUESTION, hook_types)
        self.assertIn(HookType.IDENTITY_CHALLENGE, hook_types)
        self.assertIn(HookType.SHOCKING_PROOF, hook_types)
        self.assertIn(HookType.SENSORY_DISRUPTION, hook_types)

        for v in matrix.variants:
            self.assertGreater(len(v.hook_copy), 5)
            self.assertGreater(len(v.cta_copy), 5)
            self.assertGreater(len(v.hypothesis), 10)
            self.assertGreater(v.bpm, 80)
            self.assertIn("wps", v.verbal_economy)

    def test_select_active_variant(self):
        result = self.engine.select_active_variant("var_hook_b_challenge")
        self.assertTrue(result["success"])
        self.assertEqual(result["active_variant"]["variant_id"], "var_hook_b_challenge")

        matrix = self.engine.get_matrix()
        self.assertEqual(matrix.active_variant_id, "var_hook_b_challenge")

        # Restaurar al control por defecto
        self.engine.select_active_variant("var_hook_a_intrigue")


if __name__ == "__main__":
    unittest.main()
