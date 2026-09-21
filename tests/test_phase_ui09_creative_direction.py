#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-09: Creative Direction
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (emotions-matrix-grid, emotion-matrix-card,
   director-treatment-grid, director-card).
2. Lógica del Creative Direction Studio en web/intake.js (12 emociones canónicas, tratamientos
   de dirección cinematográfica, ritmo de edición y conceptos prohibidos).
3. Persistencia integral del perfil creativo en /api/intake/draft.
4. Reglas diagnósticas cualitativas para Paso 07 en evaluateAllStepStatuses.
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


class TestPhaseUI09CreativeDirection(unittest.TestCase):
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

    def test_01_creative_css_classes(self):
        """01. Valida estilos de Dirección Creativa en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".emotions-matrix-grid",
            ".emotion-matrix-card",
            ".emotion-matrix-icon",
            ".emotion-matrix-name",
            ".director-treatment-grid",
            ".director-card",
            ".director-card-title",
            ".director-card-desc"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_creative_js_logic(self):
        """02. Valida las 12 emociones canónicas y tratamientos en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        canonical_12 = [
            "CONFIANZA", "ALEGRIA", "NOSTALGIA", "ENERGIA",
            "TRANQUILIDAD", "CURIOSIDAD", "EXCLUSIVIDAD", "INSPIRACION",
            "URGENCIA", "HUMOR", "EMPATIA", "ORGULLO"
        ]
        for emo in canonical_12:
            self.assertIn(f"id: '{emo}'", js, f"Falta emoción canónica {emo} en web/intake.js")

        treatments = [
            "CINEMATIC_DOCUMENTARY",
            "FAST_PACED_TIKTOK",
            "WARM_LIFESTYLE",
            "ELEGANT_MINIMAL",
            "PRODUCT_HERO_MACRO"
        ]
        for tr in treatments:
            self.assertIn(tr, js, f"Falta tratamiento {tr} en web/intake.js")

        self.assertIn("renderStep07_Creative()", js)
        self.assertIn("bindStep07_Events()", js)
        self.assertIn("inpTakeaway", js)
        self.assertIn("selEditingPacing", js)

    def test_03_creative_data_persistence(self):
        """03. Valida persistencia y round-trip de dirección creativa vía /api/intake/draft."""
        payload = {
            "clientMode": "EXISTING_CLIENT",
            "activeStep": 7,
            "draft": {
                "client": {"brand_name": "Locos Materos"},
                "creative": {
                    "target_emotions": ["NOSTALGIA", "CONFIANZA", "ALEGRIA"],
                    "director_treatment": "WARM_LIFESTYLE",
                    "editing_pacing": "RHYTHMIC",
                    "key_takeaway": "El ritual del mate conecta a las personas con calor y autenticidad",
                    "forbidden_concepts": ["Humor vulgar", "Comparaciones directas de precio", "Lenguaje técnico aburrido"]
                }
            },
            "updated_at": "2026-09-20T14:00:00Z"
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
        creative = data.get("creative", {})

        self.assertEqual(len(creative.get("target_emotions", [])), 3)
        self.assertIn("NOSTALGIA", creative.get("target_emotions", []))
        self.assertEqual(creative.get("director_treatment"), "WARM_LIFESTYLE")
        self.assertEqual(creative.get("editing_pacing"), "RHYTHMIC")
        self.assertIn("ritual del mate conecta", creative.get("key_takeaway", ""))
        self.assertIn("Humor vulgar", creative.get("forbidden_concepts", []))

    def test_04_diagnostic_evaluation_step07(self):
        """04. Valida reglas diagnósticas de Paso 07 en evaluateAllStepStatuses."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("this.draft.creative.target_emotions.length > 0", js)
        self.assertIn("this.draft.creative.key_takeaway", js)
        self.assertIn("this.updateStepStatus(7, 'COMPLETE')", js)
        self.assertIn("this.updateStepStatus(7, 'NEEDS_REVIEW')", js)


if __name__ == "__main__":
    unittest.main()
