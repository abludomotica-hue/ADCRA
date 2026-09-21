import unittest
import os
import json
import hashlib
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI18DeliveryCenter(unittest.TestCase):
    """Test suite para la Fase UI-18: Delivery Center (Emisión & Descarga Multi-Plataforma)."""

    def test_01_delivery_css_classes(self):
        """01. Valida que los estilos de Delivery Center estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".delivery-workspace",
            ".master-hero-card",
            ".master-video-player-container",
            ".master-video-element",
            ".deliverables-grid",
            ".deliverable-card",
            ".deliverable-header",
            ".sha256-hash-pill"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_delivery_js_logic(self):
        """02. Valida métodos de Delivery Center en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderDeliveryCenterView",
            "displayDeliveryCenterUI",
            "verifyDeliverableHash"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_delivery_package_get_api(self):
        """03. Valida endpoint GET /api/intake/delivery-package."""
        url = "http://localhost:8080/api/intake/delivery-package"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            pkg = data.get("package", {})
            self.assertEqual(pkg.get("campaign_id"), "camp_locos_materos_2026")
            self.assertEqual(len(pkg.get("variants", [])), 5)
            self.assertIn("master_video", pkg)

    def test_04_delivery_verify_hash_api(self):
        """04. Valida endpoint POST /api/intake/delivery/verify-hash con SHA-256 real."""
        url = "http://localhost:8080/api/intake/delivery/verify-hash"
        payload = {
            "file_path": "campaign/deliverables/masters/locos_materos_master_9x16.mp4"
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
            self.assertTrue(data.get("verified"))
            self.assertGreater(data.get("size_bytes", 0), 1000000)

            # Verifica contra cálculo local
            local_path = os.path.join(WORKSPACE_ROOT, payload["file_path"])
            hasher = hashlib.sha256()
            with open(local_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            self.assertEqual(data.get("calculated_sha256"), hasher.hexdigest())

    def test_05_delivery_physical_files_exist(self):
        """05. Valida que los masters y entregables existan físicamente en el sistema de archivos."""
        files = [
            "campaign/deliverables/masters/locos_materos_master_9x16.mp4",
            "campaign/deliverables/exports/locos_materos_tiktok_9x16.mp4",
            "campaign/deliverables/exports/locos_materos_instagram_reels_9x16.mp4",
            "campaign/deliverables/exports/locos_materos_youtube_shorts_9x16.mp4",
            "campaign/deliverables/exports/locos_materos_feed_square_1x1.mp4",
            "campaign/deliverables/exports/locos_materos_youtube_widescreen_16x9.mp4",
            "campaign/deliverables/masters/FICHA_TECNICA.md"
        ]
        for f in files:
            p = os.path.join(WORKSPACE_ROOT, f)
            self.assertTrue(os.path.exists(p), f"El archivo físico {f} debe existir")

if __name__ == "__main__":
    unittest.main()
