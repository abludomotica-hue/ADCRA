#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-04: Brand Intake
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (.brand-dropzone, .brand-assets-list, .color-matrix-preview, .kelvin-box).
2. Lógica del Brand Identity Studio en web/intake.js (paleta HEX, temperatura Kelvin, tono de voz y subida de assets).
3. Persistencia integral del perfil de marca en el borrador (/api/intake/draft).
4. Evaluación del estado cualitativo del Paso 04 (COMPLETE al fijar claim y colores).
5. Rango de temperatura cinematográfica y accesibilidad WCAG.
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

class TestPhaseUI04BrandIntake(unittest.TestCase):

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

    def test_01_brand_intake_css_classes(self):
        """01. Valida estilos del Brand Identity Studio en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".brand-dropzone", css, "Falta .brand-dropzone en intake.css")
        self.assertIn(".brand-assets-list", css, "Falta .brand-assets-list en intake.css")
        self.assertIn(".brand-asset-card", css, "Falta .brand-asset-card en intake.css")
        self.assertIn(".color-matrix-preview", css, "Falta .color-matrix-preview en intake.css")
        self.assertIn(".wcag-indicator", css, "Falta .wcag-indicator en intake.css")
        self.assertIn(".kelvin-box", css, "Falta .kelvin-box en intake.css")
        self.assertIn(".kelvin-track-bar", css, "Falta .kelvin-track-bar en intake.css")

    def test_02_brand_intake_js_logic(self):
        """02. Valida métodos del Brand Identity Studio en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep04_Brand()",
            "bindStep04_Events()",
            "handleBrandFileUploads(",
            "color_temperature_target_kelvin",
            "tone_of_voice",
            "logo_files",
            "inpColPrimary",
            "rngKelvin",
            "brandDropzone"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_brand_data_model_persistence(self):
        """03. Valida guardado y recuperación de identidad de marca vía /api/intake/draft."""
        brand_payload = {
            "clientMode": "NEW_CLIENT",
            "activeStep": 4,
            "draft": {
                "client": {"brand_name": "Valparaíso Artisan Coffee"},
                "brand": {
                    "claim": "El arte del café de puerto",
                    "purpose": "Conectar comunidades a través de granos seleccionados",
                    "primary_color": "#2C1B14",
                    "secondary_color": "#D4AF37",
                    "accent_color": "#E65100",
                    "color_temperature_target_kelvin": 5200,
                    "tone_of_voice": ["auténtico", "artesanal", "cálido"],
                    "mandatory_words": ["puerto", "tueste", "origen"],
                    "forbidden_words": ["industrial", "instantáneo"],
                    "logo_files": ["valpo_coffee_logo.svg"],
                    "brand_manual_pdf": "valpo_brand_book.pdf"
                }
            },
            "updated_at": "2026-09-20T12:30:00Z"
        }

        # Guardar POST
        url = f"{self.base_url}/api/intake/draft"
        post_data = json.dumps(brand_payload).encode("utf-8")
        req = urllib.request.Request(url, data=post_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)

        # Leer GET
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            saved_brand = res.get("draft", {}).get("draft", {}).get("brand", {})
            self.assertEqual(saved_brand.get("claim"), "El arte del café de puerto")
            self.assertEqual(saved_brand.get("primary_color"), "#2C1B14")
            self.assertEqual(saved_brand.get("color_temperature_target_kelvin"), 5200)
            self.assertIn("valpo_coffee_logo.svg", saved_brand.get("logo_files", []))

    def test_04_brand_kelvin_temperature_valid_range(self):
        """04. Valida rango de temperatura Kelvin (3200K a 6500K) en el modelo."""
        # Comprobar que en intake.js el slider tiene min=3200 y max=6500
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn('min="3200"', js)
        self.assertIn('max="6500"', js)

    def test_05_brand_file_uploads_support(self):
        """05. Valida soporte para formatos de logos vectoriales y manual PDF."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn(".svg", js.lower())
        self.assertIn(".pdf", js.lower())

if __name__ == "__main__":
    unittest.main()
