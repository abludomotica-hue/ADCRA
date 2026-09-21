#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-11: Campaign Readiness Pre-Flight Studio
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (readiness-cert-card, readiness-score-circle,
   readiness-cert-seal, readiness-counters-grid, readiness-issue-item, quick-jump-btn).
2. Lógica de auditoría pre-flight en web/intake.js (getPreflightAuditReport, renderStep17_Readiness,
   resolución inmediata de blockers mediante quick-jumps).
3. Endpoint de auditoría pre-flight POST /api/intake/preflight-audit (evaluación multicámara,
   readiness score 0-100%, semáforo de blockers/warnings y certificación broadcast).
4. Bloqueo de seguridad de producción: deshabilitación imperativa del botón de lanzamiento si
   existen bloqueantes críticos pendientes de resolución.
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


class TestPhaseUI11CampaignReadiness(unittest.TestCase):
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

    def test_01_readiness_css_classes(self):
        """01. Valida estilos de Campaign Readiness en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".readiness-cert-card",
            ".readiness-score-box",
            ".readiness-score-circle",
            ".readiness-cert-seal",
            ".readiness-counters-grid",
            ".readiness-counter-card",
            ".readiness-issues-list",
            ".readiness-issue-item",
            ".quick-jump-btn"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_readiness_js_logic(self):
        """02. Valida métodos del Pre-Flight Studio en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "getPreflightAuditReport()",
            "renderStep17_Readiness()",
            "bindStep17_Events()",
            "readiness-cert-card",
            "readiness-score-circle",
            "btnRunPreflightAudit",
            "btnLaunchProduction",
            "data-jump-to-step",
            "/api/intake/preflight-audit"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_api_preflight_audit_endpoint(self):
        """03. Valida endpoint POST /api/intake/preflight-audit con borrador completo vs vacío."""
        url = f"{self.base_url}/api/intake/preflight-audit"

        # Borrador Certificado (Completo)
        complete_draft = {
            "client": {"brand_name": "Locos Materos"},
            "objective": {"primary": "CONVERSION"},
            "audience": {"primary": {"demographics": {"location": "Chile"}}},
            "brand": {"claim": "El ritual matero que nos une"},
            "products": [{"name": "Termo 1L", "verified_benefits": ["24h calor"]}],
            "audio": {"filename": "locos_track.mp3", "bpm": 107.7},
            "assets": [{"orientation": "vertical", "aspect_ratio": "9:16"}]
        }
        req = urllib.request.Request(url, data=json.dumps(complete_draft).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res.get("status"), "SUCCESS")
            self.assertTrue(res.get("is_ready"))
            self.assertEqual(res.get("blockers_count"), 0)
            self.assertGreaterEqual(res.get("readiness_score"), 90)
            self.assertEqual(res.get("certification"), "CERTIFICADO PRE-FLIGHT ADCRA")

        # Borrador con Bloqueantes (Vacío)
        empty_draft = {}
        req2 = urllib.request.Request(url, data=json.dumps(empty_draft).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req2) as resp:
            self.assertEqual(resp.status, 200)
            res2 = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res2.get("status"), "SUCCESS")
            self.assertFalse(res2.get("is_ready"))
            self.assertGreater(res2.get("blockers_count"), 0)
            self.assertEqual(res2.get("certification"), "REVISIÓN REQUERIDA (BLOQUEADO)")

    def test_04_production_launch_security_lock(self):
        """04. Valida bloqueo de botón de lanzamiento cuando existen bloqueantes."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("!report.isReady", js)
        self.assertIn("Producción Bloqueada", js)
        self.assertIn("No puedes iniciar producción con bloqueantes activos", js)


if __name__ == "__main__":
    unittest.main()
