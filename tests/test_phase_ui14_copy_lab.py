import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI14CopyLab(unittest.TestCase):
    """Test suite para la Fase UI-14: Copy Lab (Laboratorio de Copywriting & Narrativa)."""

    def test_01_copylab_css_classes(self):
        """01. Valida que los estilos de Copy Lab y la barra de navegación de estudio estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".studio-subnav",
            ".subnav-tab",
            ".copylab-workspace",
            ".copylab-narrative-header",
            ".copylab-vo-tracker",
            ".scene-copy-card",
            ".variant-card",
            ".variant-score-badge",
            ".char-counter-pill",
            ".vo-timing-badge",
            ".rationale-box",
            ".copylab-cta-banner"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_copylab_html_and_js(self):
        """02. Valida estructura HTML de studioSubnav y métodos de Copy Lab en intake.js."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="studioSubnav"', html, "intake.html debe contener el elemento #studioSubnav")
        self.assertIn('data-view="copylab"', html, "intake.html debe contener tab copylab")

        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "switchStudioView",
            "renderCopyLabView",
            "displayCopyDeckUI",
            "selectCopyVariant",
            "saveCustomCopyText",
            "regenerateSceneCopy"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_copylab_get_api(self):
        """03. Valida endpoint GET /api/intake/copy-lab."""
        url = "http://localhost:8080/api/intake/copy-lab"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            deck = data.get("copy_deck", {})
            self.assertTrue(len(deck.get("scene_copies", [])) >= 9)

    def test_04_copylab_select_api(self):
        """04. Valida endpoint POST /api/intake/copy-lab/select y persistencia en disco."""
        url = "http://localhost:8080/api/intake/copy-lab/select"
        payload = {
            "scene_id": "scene_02",
            "selected_variant": "emocional",
            "selection_rationale": "Prueba unitaria de selección de variante emocional para escena 02"
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
            self.assertEqual(data.get("scene_id"), "scene_02")
            self.assertEqual(data.get("selected_variant"), "emocional")

        # Verifica en disco en creative-copy.json
        disk_path = os.path.join(WORKSPACE_ROOT, "campaign", "creative", "creative-copy.json")
        with open(disk_path, "r", encoding="utf-8") as f:
            deck = json.load(f)
        sc2 = next((s for s in deck.get("scene_copies", []) if s.get("scene_id") == "scene_02"), None)
        self.assertIsNotNone(sc2)
        self.assertEqual(sc2.get("selected_variant"), "emocional")

    def test_05_copylab_regenerate_api(self):
        """05. Valida endpoint POST /api/intake/copy-lab/regenerate."""
        url = "http://localhost:8080/api/intake/copy-lab/regenerate"
        payload = {
            "scene_id": "scene_03",
            "tone": "Auténtico y cercano"
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
            sc = data.get("scene", {})
            self.assertEqual(sc.get("scene_id"), "scene_03")
            self.assertIn("emocional", sc.get("alternatives", {}))
            self.assertIn("conversacional", sc.get("alternatives", {}))

if __name__ == "__main__":
    unittest.main()
