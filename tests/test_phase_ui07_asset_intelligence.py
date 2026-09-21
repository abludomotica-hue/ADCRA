#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-07: Asset Upload + Asset Intelligence
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (assets-dropzone, assets-summary-bar,
   assets-grid, asset-card, asset-badge-res, asset-badge-fps, asset-badge-codec).
2. Lógica del Asset Intelligence Studio en web/intake.js (renderStep09_Assets, bindStep09_Events,
   handleAssetFilesUpload, selector de rol de montaje).
3. Endpoint de probing técnico POST /api/intake/analyze-asset (detección vertical 9:16 vs horizontal 16:9,
   fps, códec, duración y manejo de errores 400).
4. Persistencia integral de assets audiovisuales en /api/intake/draft.
5. Reglas de diagnóstico pre-flight para Paso 09 en evaluateAllStepStatuses.
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


class TestPhaseUI07AssetIntelligence(unittest.TestCase):
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

    def test_01_assets_css_classes(self):
        """01. Valida estilos de Assets & Dropzone en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".assets-dropzone",
            ".assets-summary-bar",
            ".assets-summary-metric",
            ".assets-grid",
            ".asset-card",
            ".asset-badge-res",
            ".asset-badge-fps",
            ".asset-badge-codec",
            ".asset-badge-duration",
            ".asset-role-select"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_assets_js_logic(self):
        """02. Valida métodos del Asset Intelligence Studio en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep09_Assets()",
            "bindStep09_Events()",
            "handleAssetFilesUpload(",
            "assetsDropzone",
            "assetsFileInput",
            "asset-role-select",
            "/api/intake/analyze-asset"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_api_analyze_asset_endpoint(self):
        """03. Valida probing técnico vía POST /api/intake/analyze-asset."""
        url = f"{self.base_url}/api/intake/analyze-asset"

        # Clip Vertical
        vert_payload = {
            "filename": "mate_cebado_reels_vertical_01.mp4",
            "file_size_mb": 28.4,
            "type": "video"
        }
        req = urllib.request.Request(url, data=json.dumps(vert_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res.get("status"), "SUCCESS")
            probe = res.get("probe", {})
            self.assertEqual(probe.get("width"), 1080)
            self.assertEqual(probe.get("height"), 1920)
            self.assertEqual(probe.get("orientation"), "vertical")
            self.assertEqual(probe.get("aspect_ratio"), "9:16")
            self.assertEqual(probe.get("status"), "PROBED_OK")

        # Clip Horizontal
        horiz_payload = {
            "filename": "paisaje_patagonia_horizontal.mp4",
            "file_size_mb": 42.1,
            "type": "video"
        }
        req2 = urllib.request.Request(url, data=json.dumps(horiz_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req2) as resp:
            self.assertEqual(resp.status, 200)
            res2 = json.loads(resp.read().decode("utf-8"))
            probe2 = res2.get("probe", {})
            self.assertEqual(probe2.get("width"), 1920)
            self.assertEqual(probe2.get("height"), 1080)
            self.assertEqual(probe2.get("orientation"), "horizontal")
            self.assertEqual(probe2.get("status"), "WARNING_HORIZONTAL")

        # Error cuando falta filename
        empty_req = urllib.request.Request(url, data=json.dumps({}).encode("utf-8"), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(empty_req) as resp:
                self.fail("Debió retornar HTTP 400")
        except urllib.error.HTTPError as err:
            self.assertEqual(err.code, 400)

    def test_04_asset_data_persistence(self):
        """04. Valida persistencia y round-trip de assets audiovisuales vía /api/intake/draft."""
        payload = {
            "clientMode": "EXISTING_CLIENT",
            "activeStep": 9,
            "draft": {
                "client": {"brand_name": "Locos Materos"},
                "assets": [
                    {
                        "id": "asset-101",
                        "filename": "termo_primer_plano_vertical.mp4",
                        "file_size_mb": 32.5,
                        "type": "video",
                        "role": "HOOK",
                        "width": 1080,
                        "height": 1920,
                        "aspect_ratio": "9:16",
                        "orientation": "vertical",
                        "fps": 29.97,
                        "codec": "h264",
                        "duration_seconds": 15.0,
                        "status": "PROBED_OK"
                    },
                    {
                        "id": "asset-102",
                        "filename": "logo_animado_fondo_transparente.mov",
                        "file_size_mb": 18.2,
                        "type": "video",
                        "role": "OUTRO",
                        "width": 1080,
                        "height": 1920,
                        "aspect_ratio": "9:16",
                        "orientation": "vertical",
                        "fps": 29.97,
                        "codec": "prores",
                        "duration_seconds": 3.0,
                        "status": "PROBED_OK"
                    }
                ]
            },
            "updated_at": "2026-09-20T13:30:00Z"
        }

        # Guardar POST
        url = f"{self.base_url}/api/intake/draft"
        post_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=post_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)

        # Leer GET
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))

        data = res.get("draft", {}).get("draft", {})
        assets = data.get("assets", [])

        self.assertEqual(len(assets), 2)
        self.assertEqual(assets[0].get("filename"), "termo_primer_plano_vertical.mp4")
        self.assertEqual(assets[0].get("role"), "HOOK")
        self.assertEqual(assets[1].get("codec"), "prores")

    def test_05_diagnostic_evaluation_step09(self):
        """05. Valida reglas diagnósticas para Paso 09 en evaluateAllStepStatuses."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("this.draft.assets && this.draft.assets.length > 0", js)
        self.assertIn("hasVertical", js)
        self.assertIn("this.updateStepStatus(9, 'COMPLETE')", js)
        self.assertIn("this.updateStepStatus(9, 'MISSING')", js)


if __name__ == "__main__":
    unittest.main()
