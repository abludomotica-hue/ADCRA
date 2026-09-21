import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI15StoryboardLab(unittest.TestCase):
    """Test suite para la Fase UI-15: Storyboard Lab (Timeline & Montaje Dinámico DaVinci)."""

    def test_01_storyboard_css_classes(self):
        """01. Valida que los estilos de Storyboard Lab y Timeline estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".storyboard-workspace",
            ".storyboard-arc-header",
            ".timeline-track-container",
            ".timeline-time-ruler",
            ".timeline-track",
            ".timeline-segment",
            ".scene-storyboard-card",
            ".scene-drag-handle",
            ".energy-pill",
            ".sb-grid-2col",
            ".sb-tech-badge"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_storyboard_js_logic(self):
        """02. Valida métodos de Storyboard Lab en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderStoryboardLabView",
            "displayStoryboardUI",
            "reorderStoryboardScenes",
            "updateStoryboardSceneDuration"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_storyboard_get_api(self):
        """03. Valida endpoint GET /api/intake/storyboard."""
        url = "http://localhost:8080/api/intake/storyboard"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            sb = data.get("storyboard", {})
            self.assertIn("narrative_arc", sb)
            self.assertEqual(len(sb.get("scenes", [])), 9)
            self.assertGreater(sb.get("total_duration_seconds", 0), 25.0)

    def test_04_storyboard_reorder_api(self):
        """04. Valida endpoint POST /api/intake/storyboard/reorder y recálculo secuencial de tiempos."""
        url = "http://localhost:8080/api/intake/storyboard/reorder"
        # Intercambia escena 0 y escena 1
        payload = {
            "source_index": 0,
            "target_index": 1
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            scenes = data.get("storyboard", {}).get("scenes", [])
            # La primera escena debe empezar exactamente en 0.0s
            self.assertEqual(scenes[0].get("start"), 0.0)
            # La segunda escena debe empezar exactamente donde termina la primera
            self.assertEqual(scenes[1].get("start"), scenes[0].get("end"))

        # Restaurar orden original
        payload_restore = {
            "source_index": 0,
            "target_index": 1
        }
        req_res = urllib.request.Request(
            url,
            data=json.dumps(payload_restore).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_res, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            scenes = data.get("storyboard", {}).get("scenes", [])
            self.assertEqual(scenes[0].get("scene_id"), "scene_01")

    def test_05_storyboard_update_scene_api(self):
        """05. Valida endpoint POST /api/intake/storyboard/update-scene y persistencia en disco."""
        url = "http://localhost:8080/api/intake/storyboard/update-scene"
        payload = {
            "scene_id": "scene_01",
            "duration": 3.5,
            "camera": "Plano medio con movimiento orgánico en mano (handheld 35mm)"
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertEqual(data.get("scene", {}).get("duration"), 3.5)

        # Verifica en disco
        sb_path = os.path.join(WORKSPACE_ROOT, "campaign", "storyboard", "storyboard.json")
        with open(sb_path, "r", encoding="utf-8") as f:
            sb_disk = json.load(f)
        sc1 = next((s for s in sb_disk.get("scenes", []) if s.get("scene_id") == "scene_01"), None)
        self.assertIsNotNone(sc1)
        self.assertEqual(sc1.get("duration"), 3.5)

if __name__ == "__main__":
    unittest.main()
