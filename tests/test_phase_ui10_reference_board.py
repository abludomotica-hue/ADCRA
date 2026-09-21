#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-10: Reference Board
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (references-grid, reference-card,
   aspect-badge, reference-card-note, aspect-chip).
2. Lógica del Reference Board & Moodboard en web/intake.js (renderStep10_References,
   bindStep10_Events, aspects to replicate y notas técnicas).
3. Persistencia integral del board de referencias en /api/intake/draft.
4. Reglas diagnósticas (COMPLETE vs OPTIONAL) para Paso 10 en evaluateAllStepStatuses.
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


class TestPhaseUI10ReferenceBoard(unittest.TestCase):
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

    def test_01_references_css_classes(self):
        """01. Valida estilos de Reference Board en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".references-grid",
            ".reference-card",
            ".reference-card-header",
            ".reference-card-title",
            ".reference-card-url",
            ".reference-aspects-row",
            ".aspect-badge",
            ".reference-card-note",
            ".aspect-chip"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_references_js_logic(self):
        """02. Valida métodos del Reference Board Studio en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep10_References()",
            "bindStep10_Events()",
            "referencesGrid",
            "btnAddReference",
            "inpNewRefUrl",
            "inpNewRefTitle",
            "aspectsChipsGroup"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_references_data_persistence(self):
        """03. Valida persistencia y round-trip de referencias vía /api/intake/draft."""
        payload = {
            "clientMode": "EXISTING_CLIENT",
            "activeStep": 10,
            "draft": {
                "client": {"brand_name": "Locos Materos"},
                "references": [
                    {
                        "id": "ref-01",
                        "url": "https://www.instagram.com/reel/C8XYZ123",
                        "title": "Apertura dinámica con macro zoom",
                        "platform": "INSTAGRAM",
                        "aspects_to_replicate": ["HOOK_PACE", "LIGHTING"],
                        "notes": "Corte veloz en el segundo 2.0 que engancha la atención"
                    },
                    {
                        "id": "ref-02",
                        "url": "https://www.tiktok.com/@yerbamate/video/987654",
                        "title": "Transición de vertido al beat",
                        "platform": "TIKTOK",
                        "aspects_to_replicate": ["EDITING_RHYTHM", "SOUND_DESIGN"],
                        "notes": "Efecto foley de agua hirviendo muy nítido"
                    }
                ]
            },
            "updated_at": "2026-09-20T14:15:00Z"
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
        refs = data.get("references", [])

        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0].get("title"), "Apertura dinámica con macro zoom")
        self.assertIn("HOOK_PACE", refs[0].get("aspects_to_replicate", []))
        self.assertEqual(refs[1].get("platform"), "TIKTOK")

    def test_04_diagnostic_evaluation_step10(self):
        """04. Valida reglas diagnósticas para Paso 10 en evaluateAllStepStatuses."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("this.draft.references && this.draft.references.length > 0", js)
        self.assertIn("this.updateStepStatus(10, 'COMPLETE')", js)
        self.assertIn("this.updateStepStatus(10, 'OPTIONAL')", js)


if __name__ == "__main__":
    unittest.main()
