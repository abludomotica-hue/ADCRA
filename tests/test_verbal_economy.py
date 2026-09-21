"""
Unit tests for ADCRA AI Brain — Verbal Economy & Readability Enforcement Engine
"""

import unittest
from adcra.ai.verbal_economy import (
    get_verbal_economy_engine, VerbalEconomyStatus, VerbalEconomyEngine
)


class TestVerbalEconomyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = get_verbal_economy_engine()

    def test_count_words_spanish_accents(self):
        text = "¡Un buen mate no se apura, se disfruta con amigos al amanecer!"
        words = self.engine.count_words(text)
        self.assertEqual(words, 12)

    def test_rate_thresholds_9_16(self):
        self.assertEqual(self.engine.evaluate_rate(1.8, aspect_ratio="9:16"), VerbalEconomyStatus.OPTIMAL)
        self.assertEqual(self.engine.evaluate_rate(2.5, aspect_ratio="9:16"), VerbalEconomyStatus.ACCEPTABLE)
        self.assertEqual(self.engine.evaluate_rate(3.0, aspect_ratio="9:16"), VerbalEconomyStatus.WARNING)
        self.assertEqual(self.engine.evaluate_rate(3.8, aspect_ratio="9:16"), VerbalEconomyStatus.CRITICAL)

    def test_hook_density_first_3s(self):
        metric_good = self.engine.analyze_scene("hook_1", "Cada día comienza con una pausa.", 3.5, is_hook=True)
        self.assertEqual(metric_good.status, VerbalEconomyStatus.OPTIMAL)
        self.assertIsNone(metric_good.flag)

        metric_bad = self.engine.analyze_scene(
            "hook_bad",
            "Si querés tomar un mate realmente extraordinario tenés que saber que el agua a 78 grados cambia todo",
            3.0,
            is_hook=True
        )
        self.assertIn(metric_bad.status, (VerbalEconomyStatus.WARNING, VerbalEconomyStatus.CRITICAL))
        self.assertIsNotNone(metric_bad.flag)
        self.assertIn("HOOK_DENSITY_HIGH", metric_bad.flag)

    def test_analyze_campaign_storyboard(self):
        scenes = [
            {"scene_id": "scene_01", "copy": "Cada día comienza con una pausa.", "duration": 3.5, "start": 0.0},
            {"scene_id": "scene_02", "copy": "El arte de prepararse para lo bueno.", "duration": 3.3, "start": 3.5},
            {"scene_id": "scene_03", "copy": "La energía de arrancar juntos.", "duration": 3.2, "start": 6.8}
        ]
        report = self.engine.analyze_campaign(scenes, aspect_ratio="9:16", campaign_id="test_camp")
        self.assertEqual(report["campaign_id"], "test_camp")
        self.assertTrue(report["passed_qc"])
        self.assertLess(report["overall_wps"], 2.8)
        self.assertEqual(report["scenes_count"], 3)
        self.assertIn("hook_metric", report)

    def test_critical_copy_overload_fails_qc(self):
        scenes = [
            {"scene_id": "scene_01", "copy": "Palabra " * 25, "duration": 3.0, "start": 0.0}
        ]
        report = self.engine.analyze_campaign(scenes, aspect_ratio="9:16")
        self.assertFalse(report["passed_qc"])
        self.assertEqual(report["status"], VerbalEconomyStatus.CRITICAL.value)
        self.assertGreater(len(report["flags"]), 0)


if __name__ == "__main__":
    unittest.main()
