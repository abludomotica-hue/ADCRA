import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI20ClientMemory(unittest.TestCase):
    """Test suite para la Fase UI-20: Client Memory Studio (Aprendizajes Continuos)."""

    def test_01_memory_css_classes(self):
        """01. Valida que los estilos de Client Memory estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".memory-container",
            ".memory-brand-banner",
            ".memory-grid",
            ".memory-card",
            ".palette-swatches",
            ".swatch-chip"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_memory_html_and_js(self):
        """02. Valida estructura HTML de studioSubnav y métodos de Memory Studio en intake.js."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="tabMemory"', html, "tabMemory debe existir en studioSubnav")
        self.assertIn('data-view="memory"', html, "tabMemory debe tener data-view='memory'")

        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderClientMemoryView",
            "displayClientMemoryUI"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_memory_get_api(self):
        """03. Valida endpoint GET /api/intake/memory con la memoria de Locos Materos."""
        url = "http://localhost:8080/api/intake/memory"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertEqual(data.get("brand_id"), "locos_materos")
            self.assertEqual(data.get("brand_name"), "Locos Materos")

            mem = data.get("memory", {})
            self.assertIn("aesthetic_learnings", mem)
            self.assertIn("musical_tempo_learnings", mem)
            mus = mem.get("musical_tempo_learnings", {})
            self.assertEqual(mus.get("last_successful_bpm"), 107.7)

    def test_04_memory_apply_to_draft_api(self):
        """04. Valida endpoint POST /api/intake/memory/apply-to-draft y actualización de sesión."""
        url = "http://localhost:8080/api/intake/memory/apply-to-draft"
        req = urllib.request.Request(
            url,
            data=json.dumps({}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertIn("applied_fields", data)

            draft_path = os.path.join(WORKSPACE_ROOT, "campaign", "draft-session.json")
            with open(draft_path, "r", encoding="utf-8") as f:
                draft = json.load(f)
            self.assertTrue(draft.get("memory_applied"))

    def test_05_memory_update_api(self):
        """05. Valida endpoint POST /api/intake/memory/update para persistir aprendizajes continuos."""
        url = "http://localhost:8080/api/intake/memory/update"
        payload = {
            "new_learning_note": "Test Note UI-20: Iluminación cálida con tonos ambarinos."
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
            mem = data.get("memory", {})
            self.assertIn("historical_learnings", mem)
            last_item = mem["historical_learnings"][-1]
            self.assertEqual(last_item.get("note"), payload["new_learning_note"])

if __name__ == "__main__":
    unittest.main()
