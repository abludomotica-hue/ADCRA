import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI17QCDashboard(unittest.TestCase):
    """Test suite para la Fase UI-17: QC Dashboard (Auditoría Tricameral & Legal)."""

    def test_01_qc_css_classes(self):
        """01. Valida que los estilos de QC Dashboard estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".qc-dashboard-workspace",
            ".qc-score-hero",
            ".qc-score-badge-circle",
            ".qc-score-number",
            ".qc-metrics-row",
            ".qc-metric-item",
            ".qc-pillars-grid",
            ".qc-pillar-card",
            ".qc-pillar-header",
            ".qc-checks-list",
            ".qc-check-item"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_qc_js_logic(self):
        """02. Valida métodos de QC Dashboard en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderQCDashboardView",
            "displayQCDashboardUI",
            "overrideQCCheck",
            "reEvaluateQCAudits"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_qc_get_report_api(self):
        """03. Valida endpoint GET /api/intake/qc-report con los 4 pilares de auditoría."""
        url = "http://localhost:8080/api/intake/qc-report"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            rep = data.get("report", {})
            self.assertGreaterEqual(rep.get("overall_score", 0), 90.0)
            audits = rep.get("audits", {})
            self.assertIn("technical_audit", audits)
            self.assertIn("creative_audit", audits)
            self.assertIn("brand_audit", audits)
            self.assertIn("legal_audit", audits)

    def test_04_qc_override_api(self):
        """04. Valida endpoint POST /api/intake/qc-report/override y persistencia en disco."""
        url = "http://localhost:8080/api/intake/qc-report/override"
        payload = {
            "check_id": "tech_01_resolution_9_16",
            "reason": "Resolución validada en control de calidad para vertical 9:16",
            "reviewer": "Director Técnico"
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

        # Verifica en disco
        qc_path = os.path.join(WORKSPACE_ROOT, "campaign", "reports", "quality-control-report.json")
        with open(qc_path, "r", encoding="utf-8") as f:
            qc_disk = json.load(f)
        tech_checks = qc_disk.get("audits", {}).get("technical_audit", {}).get("checks", [])
        chk = next((c for c in tech_checks if c.get("check_id") == "tech_01_resolution_9_16"), None)
        self.assertIsNotNone(chk)
        self.assertTrue(chk.get("overridden"))
        self.assertEqual(chk.get("overridden_by"), "Director Técnico")

    def test_05_qc_reevaluate_api(self):
        """05. Valida endpoint POST /api/intake/qc-report/re-evaluate."""
        url = "http://localhost:8080/api/intake/qc-report/re-evaluate"
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
            self.assertIn("report", data)
            self.assertEqual(data.get("report", {}).get("certification_status"), "APPROVED")

if __name__ == "__main__":
    unittest.main()
