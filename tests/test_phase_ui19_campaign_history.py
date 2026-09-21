import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI19CampaignHistory(unittest.TestCase):
    """Test suite para la Fase UI-19: Campaign History & Iteration Studio."""

    def test_01_history_css_classes(self):
        """01. Valida que los estilos de History Studio e Iteration Track estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".history-container",
            ".history-summary-bar",
            ".history-stat-group",
            ".iteration-track",
            ".iteration-cycle-card",
            ".snapshots-grid",
            ".snapshot-card"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_history_html_and_js(self):
        """02. Valida estructura HTML de studioSubnav y métodos de History Studio en intake.js."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="tabHistory"', html, "tabHistory debe existir en studioSubnav")
        self.assertIn('data-view="history"', html, "tabHistory debe tener data-view='history'")

        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderCampaignHistoryView",
            "displayCampaignHistoryUI"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_history_get_api(self):
        """03. Valida endpoint GET /api/intake/history."""
        url = "http://localhost:8080/api/intake/history"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertIn("campaign", data)
            self.assertIn("iterations", data)
            self.assertIn("snapshots", data)
            self.assertGreaterEqual(len(data.get("snapshots", [])), 1)

            iter_data = data.get("iterations", {})
            self.assertEqual(iter_data.get("max_allowed_iterations"), 3)
            self.assertIn("iteration_log", iter_data)

    def test_04_history_restore_api(self):
        """04. Valida endpoint POST /api/intake/history/restore y persistencia en sesión activa."""
        url = "http://localhost:8080/api/intake/history/restore"
        payload = {
            "snapshot_id": "snap_v1_0_0_brief"
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
            self.assertEqual(data.get("restored_id"), "snap_v1_0_0_brief")
            self.assertIn("Snapshot snap_v1_0_0_brief restaurado", data.get("message", ""))

            # Valida archivo en disco
            draft_path = os.path.join(WORKSPACE_ROOT, "campaign", "draft-session.json")
            with open(draft_path, "r", encoding="utf-8") as f:
                draft = json.load(f)
            self.assertEqual(draft.get("restored_from_snapshot"), "snap_v1_0_0_brief")

    def test_05_history_snapshot_api(self):
        """05. Valida endpoint POST /api/intake/history/snapshot para registrar checkpoints."""
        url = "http://localhost:8080/api/intake/history/snapshot"
        payload = {
            "name": "Checkpoint Test UI-19",
            "stage": "Automated Unit Test",
            "author": "Test Runner",
            "quality_score": 100.0,
            "notes": "Validación de checkpoint automático."
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
            snap = data.get("snapshot", {})
            self.assertEqual(snap.get("name"), "Checkpoint Test UI-19")
            self.assertEqual(snap.get("stage"), "Automated Unit Test")
            self.assertTrue(snap.get("snapshot_id", "").startswith("snap_manual_"))

if __name__ == "__main__":
    unittest.main()
