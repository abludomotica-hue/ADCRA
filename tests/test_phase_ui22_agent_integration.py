import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI22AgentIntegration(unittest.TestCase):
    """Test suite para la Fase UI-22: ADCRA Agent Full Integration & Production Pipeline Certification."""

    def test_01_pipeline_css_classes(self):
        """01. Valida que los estilos de Pipeline y Certificación estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".pipeline-container",
            ".pipeline-hero-banner",
            ".pipeline-agent-grid",
            ".pipeline-agent-card",
            ".pipeline-steps-console",
            ".pipeline-step-item",
            ".cert-badge-gold"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_pipeline_html_and_js(self):
        """02. Valida estructura HTML de studioSubnav y métodos de Pipeline en intake.js."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="tabPipeline"', html, "tabPipeline debe existir en studioSubnav")
        self.assertIn('data-view="pipeline"', html, "tabPipeline debe tener data-view='pipeline'")

        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderPipelineOrchestratorView",
            "displayPipelineOrchestratorUI"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_pipeline_status_api(self):
        """03. Valida endpoint GET /api/intake/pipeline/status con los 9 dominios y 22 fases."""
        url = "http://localhost:8080/api/intake/pipeline/status"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertEqual(data.get("total_phases"), 22)
            self.assertEqual(data.get("certified_phases"), 22)
            self.assertEqual(data.get("status_code"), "FULLY_OPERATIONAL")

            domains = data.get("domains", [])
            self.assertEqual(len(domains), 9)
            domain_ids = [d.get("id") for d in domains]
            expected_domains = [
                "campaign_director", "audio_intelligence", "video_intelligence",
                "creative_copywriter", "storyboard_director", "color_grading_specialist",
                "sound_designer", "motion_animator", "qc_inspector"
            ]
            for ed in expected_domains:
                self.assertIn(ed, domain_ids)

    def test_04_pipeline_execute_full_api(self):
        """04. Valida endpoint POST /api/intake/pipeline/execute-full orquestando el flujo completo."""
        url = "http://localhost:8080/api/intake/pipeline/execute-full"
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
            self.assertEqual(data.get("phases_certified"), 22)
            self.assertEqual(data.get("quality_score"), 100.0)
            self.assertEqual(data.get("certification_badge"), "GOLD_MASTER_COMMERCIAL_RELEASE")
            steps = data.get("steps", [])
            self.assertGreaterEqual(len(steps), 10)
            for s in steps:
                self.assertEqual(s.get("status"), "COMPLETED")

    def test_05_project_manifest_and_certification_consistency(self):
        """05. Valida consistencia integral de artefactos de producción y manifiesto maestro."""
        manifest_path = os.path.join(WORKSPACE_ROOT, "campaign", "campaign-manifest.json")
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest.get("campaign_id"), "camp_locos_materos_2026")
        self.assertIn("strategic_brief", manifest)
        self.assertIn("deliverables", manifest)

        # Verificar que existen los artefactos clave producidos por los agentes
        key_artifacts = [
            "campaign/audio/locos_materos_master_mix.wav",
            "campaign/color/color-grading-manifest.json",
            "campaign/motion-graphics/motion-manifest.json",
            "campaign/remotion/composition-manifest.json",
            "campaign/storyboard/storyboard.json",
            "campaign/reports/quality-control-report.json",
            "campaign/reports/iteration-history.json",
            "campaign/memory/brand-profile-memory.json",
            "campaign/deliverables/masters/locos_materos_master_9x16.mp4",
            "campaign/deliverables/masters/commercial-delivery-package.json"
        ]
        for art in key_artifacts:
            full_art = os.path.join(WORKSPACE_ROOT, art)
            self.assertTrue(os.path.exists(full_art), f"El artefacto integral {art} debe existir")

if __name__ == "__main__":
    unittest.main()
