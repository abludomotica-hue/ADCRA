#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-12: Campaign Blueprint Studio
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (blueprint-card, blueprint-actions-bar,
   blueprint-tag-pill, blueprint-grid, blueprint-item).
2. Lógica del Campaign Blueprint Studio en web/intake.js (generateCampaignBlueprint,
   btnGenerateBlueprint, btnApproveBlueprint, btnExportBlueprint).
3. Endpoints REST de compilación y recuperación de blueprint:
   - POST /api/intake/blueprint/generate (compilación técnica, hash de campaña, status APPROVED)
   - GET /api/intake/blueprint (recuperación de ficha técnica ejecutiva)
4. Persistencia física en disco de campaign/campaign-blueprint.json con contrato de datos válido.
"""

import os
import sys
import json
import socket
import threading
import urllib.request
import urllib.error
import unittest

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, WORKSPACE_ROOT)

import dashboard_server

def get_free_port():
    """Encuentra un puerto TCP libre efímero para pruebas."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


class TestPhaseUI12CampaignBlueprint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_port = get_free_port()
        cls.server_address = ('127.0.0.1', cls.test_port)
        cls.httpd = dashboard_server.ThreadedHTTPServer(cls.server_address, dashboard_server.DashboardRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.test_port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.server_thread.join(timeout=2.0)

    def test_01_blueprint_css_classes(self):
        """01. Valida estilos de Campaign Blueprint en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".blueprint-card",
            ".blueprint-header",
            ".blueprint-title",
            ".blueprint-grid",
            ".blueprint-item",
            ".blueprint-actions-bar",
            ".blueprint-tag-pill"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_blueprint_js_logic(self):
        """02. Valida métodos del Blueprint Studio en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "generateCampaignBlueprint()",
            "campaignBlueprint",
            "btnGenerateBlueprint",
            "btnApproveBlueprint",
            "btnExportBlueprint",
            "/api/intake/blueprint/generate"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_api_blueprint_generate_and_get(self):
        """03. Valida endpoints POST /api/intake/blueprint/generate y GET /api/intake/blueprint."""
        gen_url = f"{self.base_url}/api/intake/blueprint/generate"
        get_url = f"{self.base_url}/api/intake/blueprint"

        draft_payload = {
            "client": {"brand_name": "Locos Materos"},
            "objective": {"primary": "CONVERSION", "secondary": ["RETENCION"]},
            "audience": {"primary": {"demographics": {"location": "Chile"}}},
            "brand": {"primary_color": "#2C1B14", "color_temperature_target_kelvin": 5200},
            "creative": {
                "director_treatment": "WARM_LIFESTYLE",
                "key_takeaway": "El ritual matero que nos une con calidez",
                "target_emotions": ["NOSTALGIA", "CONFIANZA"]
            },
            "audio": {
                "filename": "locos_materos_track.mp3",
                "bpm": 107.7,
                "musical_key": "Am (La menor)",
                "cut_interval_seconds": 2.22
            },
            "duration": {"target_seconds": 30},
            "offer": {"is_branding_only": False, "offer_title": "30% OFF en Termos"}
        }

        # Generar Blueprint
        req = urllib.request.Request(gen_url, data=json.dumps(draft_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res.get("status"), "SUCCESS")
            bp = res.get("blueprint", {})
            self.assertEqual(bp.get("status"), "APPROVED")
            self.assertEqual(bp.get("executive_summary", {}).get("brand_name"), "Locos Materos")
            self.assertEqual(bp.get("audio_intelligence", {}).get("bpm"), 107.7)
            self.assertEqual(bp.get("deliverables_matrix", {}).get("aspect_ratio"), "9:16")

        # Recuperar Blueprint
        with urllib.request.urlopen(get_url) as resp:
            self.assertEqual(resp.status, 200)
            res_get = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res_get.get("status"), "SUCCESS")
            bp_recovered = res_get.get("blueprint", {})
            self.assertEqual(bp_recovered.get("executive_summary", {}).get("brand_name"), "Locos Materos")

    def test_04_blueprint_physical_file_persistence(self):
        """04. Valida persistencia física en disco de campaign/campaign-blueprint.json."""
        bp_path = os.path.join(WORKSPACE_ROOT, "campaign", "campaign-blueprint.json")
        self.assertTrue(os.path.exists(bp_path), "No existe campaign/campaign-blueprint.json")

        with open(bp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("schema_version"), "1.0.0")
        self.assertIn("campaign_id", data)
        self.assertIn("executive_summary", data)
        self.assertIn("cinematography_and_color", data)
        self.assertIn("audio_intelligence", data)
        self.assertIn("deliverables_matrix", data)


if __name__ == "__main__":
    unittest.main()
