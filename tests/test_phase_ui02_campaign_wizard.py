#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-02: Campaign Wizard & Step Engine
Campaign Intake Studio (ADCRA)

Verifica:
1. Elementos estructurales del Wizard en web/intake.html (navegación, guardado rápido, atajos).
2. Clases CSS de animación y componentes del Wizard en web/intake.css.
3. Métodos y arquitectura del motor de avance en web/intake.js (goToStep, autosave, recuperación de sesión).
4. Persistencia y recuperación íntegra de sesión mediante /api/intake/draft (POST y GET roundtrip).
5. Verificación de archivo de respaldo en disco campaign/draft-session.json.
6. Coherencia en la evaluación cualitativa de los 17 pasos.
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

class TestPhaseUI02CampaignWizard(unittest.TestCase):

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

    def test_01_wizard_dom_elements(self):
        """01. Valida controles esenciales del Campaign Wizard en intake.html."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="btnStepPrev"', html, "Falta botón Anterior en Footer")
        self.assertIn('id="btnStepNext"', html, "Falta botón Siguiente en Footer")
        self.assertIn('id="btnQuickSaveDraft"', html, "Falta botón de Guardado Rápido en Footer")
        self.assertIn('id="stepContentArea"', html, "Falta contenedor dinámico de pasos")
        self.assertIn('id="footerStepIndicator"', html, "Falta indicador contextual en el Footer")
        self.assertIn('keyboard-hint-pill', html, "Falta píldora informativa de atajos de teclado")

    def test_02_wizard_css_transitions_and_components(self):
        """02. Valida transiciones y estilos de componentes del Wizard en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".step-transition-enter", css, "Falta clase de transición de entrada")
        self.assertIn(".step-transition-active", css, "Falta clase de transición activa")
        self.assertIn(".chip-group", css, "Falta estilo de grupo de chips interactivos")
        self.assertIn(".color-picker-grid", css, "Falta grid de selectores de color")
        self.assertIn(".waveform-box", css, "Falta estilo del visor de onda de audio")
        self.assertIn(".blueprint-card", css, "Falta estilo de la ficha técnica Blueprint")

    def test_03_wizard_js_structure_and_contracts(self):
        """03. Valida métodos del motor CampaignWizard en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected_methods = [
            "init()",
            "setupEventListeners()",
            "setupKeyboardShortcuts()",
            "goToStep(stepNumber)",
            "scheduleAutosave()",
            "saveDraft(",
            "loadDraft()",
            "evaluateAllStepStatuses()",
            "renderActiveStep()",
            "renderStep01_Client()",
            "renderStep08_Audio()",
            "renderStep17_Readiness()"
        ]
        for m in expected_methods:
            self.assertIn(m, js, f"Falta el método o firma '{m}' en intake.js")

    def test_04_api_draft_roundtrip_save_and_recovery(self):
        """04. Valida persistencia y restauración fiel de borrador vía /api/intake/draft."""
        sample_draft_payload = {
            "clientMode": "NEW_CLIENT",
            "activeStep": 4,
            "draft": {
                "client": {
                    "brand_name": "Test Brand Wizard",
                    "industry": "Software & AI",
                    "business_type": "startup",
                    "website_url": "https://testbrand.ai",
                    "description": "Plataforma de prueba para Intake Studio",
                    "social_channels": {"instagram": "@testbrand", "tiktok": "@testbrand"}
                },
                "objective": {
                    "primary": "CONVERSION",
                    "desired_outcome": "visitar_sitio"
                },
                "brand": {
                    "claim": "Innovación sin límites",
                    "primary_color": "#10B981",
                    "secondary_color": "#D4AF37"
                },
                "audio": {
                    "filename": "track_test_128bpm.mp3",
                    "bpm": 128
                }
            },
            "updated_at": "2026-09-20T12:00:00Z"
        }

        # 1. Guardar vía POST
        post_url = f"{self.base_url}/api/intake/draft"
        post_data = json.dumps(sample_draft_payload).encode("utf-8")
        req = urllib.request.Request(post_url, data=post_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res_json = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res_json.get("status"), "SUCCESS")

        # 2. Recuperar vía GET
        get_url = f"{self.base_url}/api/intake/draft"
        with urllib.request.urlopen(get_url) as resp:
            self.assertEqual(resp.status, 200)
            get_json = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(get_json.get("status"), "SUCCESS")
            saved_draft = get_json.get("draft")
            self.assertIsNotNone(saved_draft, "El borrador devuelto no debe ser nulo")
            self.assertEqual(saved_draft.get("activeStep"), 4)
            self.assertEqual(saved_draft.get("draft", {}).get("client", {}).get("brand_name"), "Test Brand Wizard")
            self.assertEqual(saved_draft.get("draft", {}).get("audio", {}).get("bpm"), 128)

    def test_05_draft_session_file_persistence(self):
        """05. Valida que el archivo físico campaign/draft-session.json persista en disco."""
        draft_file = os.path.join(WORKSPACE_ROOT, "campaign", "draft-session.json")
        self.assertTrue(os.path.exists(draft_file), "campaign/draft-session.json no fue creado en disco")

        with open(draft_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("draft", data)
        self.assertEqual(data["draft"]["client"]["brand_name"], "Test Brand Wizard")

    def test_06_seventeen_steps_declared_in_js(self):
        """06. Valida que los 17 pasos canónicos estén rigurosamente modelados en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        for step_id in range(1, 18):
            self.assertIn(f"id: {step_id},", js, f"El paso {step_id} no está declarado en intake.js")

if __name__ == "__main__":
    unittest.main()
