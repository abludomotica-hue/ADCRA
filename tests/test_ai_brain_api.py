"""
Integration Tests for Server AI Brain REST API Endpoints
"""

import unittest
import json
import urllib.request
import urllib.error


class TestAIBrainServerAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8080"

    def _get(self, path):
        try:
            with urllib.request.urlopen(f"{self.BASE_URL}{path}", timeout=3) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.URLError:
            self.skipTest("Dashboard server not responding on localhost:8080")

    def _post(self, path, payload):
        try:
            req = urllib.request.Request(
                f"{self.BASE_URL}{path}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.URLError:
            self.skipTest("Dashboard server not responding on localhost:8080")

    def test_endpoint_ai_health(self):
        status, data = self._get("/api/ai/health")
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "OPERATIONAL")
        self.assertIn("connected_providers", data)

    def test_endpoint_ai_providers(self):
        status, data = self._get("/api/ai/providers")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_endpoint_ai_models(self):
        status, data = self._get("/api/ai/models")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_endpoint_ai_brains(self):
        status, data = self._get("/api/ai/brains")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_endpoint_ai_tools(self):
        status, data = self._get("/api/ai/tools")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_endpoint_ai_usage(self):
        status, data = self._get("/api/ai/usage")
        self.assertEqual(status, 200)
        self.assertIn("total_cost_usd", data)
        self.assertIn("total_tokens", data)

    def test_endpoint_ai_intent_execute(self):
        status, data = self._post("/api/ai/intent/execute", {
            "prompt": "Generar copy creativo para Locos Materos",
            "campaign_id": "camp_locos_materos_2026"
        })
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "COMPLETED")
        self.assertIn("outputs", data)

    def test_endpoint_ai_verbal_economy_current(self):
        status, data = self._get("/api/ai/verbal-economy/current")
        self.assertEqual(status, 200)
        self.assertIn("overall_wps", data)
        self.assertIn("scenes_analysis", data)
        self.assertTrue(data.get("passed_qc"))

    def test_endpoint_ai_hardware_probe(self):
        status, data = self._get("/api/ai/hardware/probe")
        self.assertEqual(status, 200)
        self.assertIn("selected_engine", data)
        self.assertIn("gpu", data)
        self.assertIn("ffmpeg_installed", data)

    def test_endpoint_ai_experiments_get_and_select(self):
        status, data = self._get("/api/ai/experiments")
        self.assertEqual(status, 200)
        self.assertIn("variants", data)
        self.assertEqual(len(data["variants"]), 4)

        # Probar selección de variante
        status_post, data_post = self._post("/api/ai/experiments/select-variant", {
            "variant_id": "var_hook_a_intrigue"
        })
        self.assertEqual(status_post, 200)
        self.assertTrue(data_post.get("success"))
        self.assertEqual(data_post.get("active_variant", {}).get("variant_id"), "var_hook_a_intrigue")


if __name__ == "__main__":
    unittest.main()
