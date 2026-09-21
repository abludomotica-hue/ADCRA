import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI16ColorSoundMotion(unittest.TestCase):
    """Test suite para la Fase UI-16: Color / Sound / Motion Labs (Aprobación Estética No Destructiva)."""

    def test_01_aesthetics_css_classes(self):
        """01. Valida que los estilos de Color, Sound y Motion Labs estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".aesthetics-workspace",
            ".aesthetics-subtabs",
            ".aesthetics-subtab-btn",
            ".luts-grid",
            ".lut-card",
            ".fairlight-hud",
            ".loudness-meter-box",
            ".loudness-meter-bar",
            ".safezone-visualizer-container",
            ".safezone-phone-frame",
            ".safezone-guide-top",
            ".safezone-guide-bottom"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_aesthetics_js_logic(self):
        """02. Valida métodos de Aesthetics Lab en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderAestheticsLabView",
            "displayAestheticsUI",
            "approveAestheticsColor",
            "confirmAestheticsAudioMaster",
            "approveAestheticsMotionSafezone"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_aesthetics_get_api(self):
        """03. Valida endpoint GET /api/intake/aesthetics."""
        url = "http://localhost:8080/api/intake/aesthetics"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertIn("color", data)
            self.assertIn("audio", data)
            self.assertIn("motion", data)
            self.assertTrue(len(data.get("color", {}).get("luts_registered", [])) >= 3)

    def test_04_aesthetics_color_approve_api(self):
        """04. Valida endpoint POST /api/intake/aesthetics/color/approve y persistencia en disco."""
        url = "http://localhost:8080/api/intake/aesthetics/color/approve"
        payload = {
            "lut_name": "locos_materos_warm_cinematic"
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
            self.assertEqual(data.get("selected_lut"), "locos_materos_warm_cinematic")

        # Verifica en disco
        color_path = os.path.join(WORKSPACE_ROOT, "campaign", "color", "color-grading-manifest.json")
        with open(color_path, "r", encoding="utf-8") as f:
            c = json.load(f)
        self.assertEqual(c.get("selected_lut"), "locos_materos_warm_cinematic")
        self.assertEqual(c.get("approval_status"), "APPROVED")

    def test_05_aesthetics_audio_master_api(self):
        """05. Valida endpoint POST /api/intake/aesthetics/audio/master y persistencia en disco."""
        url = "http://localhost:8080/api/intake/aesthetics/audio/master"
        payload = {
            "target_integrated_lufs": -14.0
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
            self.assertEqual(data.get("loudness_compliance", {}).get("target_integrated_lufs"), -14.0)

        # Verifica en disco
        audio_path = os.path.join(WORKSPACE_ROOT, "campaign", "audio", "sound-design-manifest.json")
        with open(audio_path, "r", encoding="utf-8") as f:
            a = json.load(f)
        self.assertEqual(a.get("loudness_compliance", {}).get("target_integrated_lufs"), -14.0)
        self.assertTrue(a.get("loudness_compliance", {}).get("mastering_approved"))

    def test_06_aesthetics_motion_safezone_api(self):
        """06. Valida endpoint POST /api/intake/aesthetics/motion/safezone y persistencia en disco."""
        url = "http://localhost:8080/api/intake/aesthetics/motion/safezone"
        payload = {
            "safe_zones": {
                "top_px": 120,
                "bottom_px": 200,
                "left_px": 40,
                "right_px": 40
            }
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
            self.assertTrue(data.get("template_approved"))

        # Verifica en disco
        motion_path = os.path.join(WORKSPACE_ROOT, "campaign", "motion-graphics", "motion-manifest.json")
        with open(motion_path, "r", encoding="utf-8") as f:
            m = json.load(f)
        self.assertTrue(m.get("template_approved"))
        self.assertEqual(m.get("safe_zones", {}).get("bottom_px"), 200)

if __name__ == "__main__":
    unittest.main()
