#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-01: Design System + Layout Base
Campaign Intake Studio (ADCRA)

Verifica:
1. Existencia e integridad estructural de web/intake.html, web/intake.css, web/intake.js.
2. Las 3 zonas conceptuales espaciales:
   - Zona 1: CAMPAIGN PROGRESS (#sidebarProgress) con los 17 pasos secuenciales y estados cualitativos.
   - Zona 2: MAIN WORKSPACE (#mainWorkspace).
   - Zona 3: AI CAMPAIGN ASSISTANT (#aiAssistantBar + #diagnosticDrawer).
3. Selector de modo: NUEVO CLIENTE vs CLIENTE EXISTENTE.
4. Estados cualitativos: COMPLETE, READY, NEEDS REVIEW, MISSING, OPTIONAL.
5. Servidor HTTP: Rutas /intake, /intake.html, /intake.css, /intake.js, /api/intake/clients, /api/intake/draft.
6. Enlace de retorno e integración en Mission Control Dashboard (web/index.html).
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

class TestPhaseUI01LayoutBase(unittest.TestCase):

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

    def test_01_assets_exist_and_integrity(self):
        """01. Valida existencia y tamaño no nulo de activos de Intake Studio."""
        web_dir = os.path.join(WORKSPACE_ROOT, "web")
        for filename in ["intake.html", "intake.css", "intake.js"]:
            path = os.path.join(web_dir, filename)
            self.assertTrue(os.path.exists(path), f"Archivo no encontrado: {path}")
            self.assertGreater(os.path.getsize(path), 500, f"Archivo {filename} es demasiado pequeño")

    def test_02_three_conceptual_zones(self):
        """02. Valida la presencia de las tres zonas conceptuales del Layout Base."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Zona 1: CAMPAIGN PROGRESS
        self.assertIn('id="sidebarProgress"', html, "Falta Zona 1: #sidebarProgress")
        self.assertTrue("campaign-progress" in html or "sidebar-progress" in html, "Falta clase de progreso")

        # Zona 2: MAIN WORKSPACE
        self.assertIn('id="mainWorkspace"', html, "Falta Zona 2: #mainWorkspace")
        self.assertIn('class="main-workspace"', html, "Falta clase de main workspace")

        # Zona 3: AI CAMPAIGN ASSISTANT
        self.assertIn('id="aiAssistantBar"', html, "Falta Zona 3: #aiAssistantBar")
        self.assertIn('id="diagnosticDrawer"', html, "Falta panel diagnóstico de AI Campaign Assistant")

    def test_03_seventeen_steps_defined(self):
        """03. Valida que los 17 pasos canónicos de Intake Studio estén declarados en la UI."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        steps = [
            "01", "Cliente",
            "02", "Objetivo",
            "03", "Audiencia",
            "04", "Marca",
            "05", "Producto",
            "06", "Oferta",
            "07", "Creatividad",
            "08", "Audio",
            "09", "Assets",
            "10", "Referencias",
            "11", "Canales",
            "12", "Duración",
            "13", "CTA",
            "14", "Restricciones",
            "15", "Presupuesto",
            "16", "Automatización",
            "17", "Aprobación"
        ]
        for term in steps:
            self.assertIn(term, html, f"Falta el paso o etiqueta '{term}' en intake.html")

    def test_04_qualitative_statuses_in_css(self):
        """04. Valida que CSS defina estilos para todos los estados cualitativos canónicos."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        # COMPLETE, READY, NEEDS REVIEW, MISSING, OPTIONAL
        required_classes = [
            "badge-complete",
            "badge-ready",
            "badge-needs_review",
            "badge-missing",
            "badge-optional"
        ]
        for cls_name in required_classes:
            self.assertIn(cls_name, css, f"Falta estilo para estado cualitativo '{cls_name}' en intake.css")

    def test_05_client_mode_selector_and_navigation(self):
        """05. Valida el selector de modo (Nuevo vs Existente) y botones de navegación."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="clientModeSelector"', html, "Falta selector de modo de cliente")
        self.assertIn('data-mode="NEW_CLIENT"', html, "Falta opción NEW_CLIENT")
        self.assertIn('data-mode="EXISTING_CLIENT"', html, "Falta opción EXISTING_CLIENT")
        self.assertIn('href="/"', html, "Falta enlace de retorno a Mission Control")
        self.assertIn('id="autosaveBadge"', html, "Falta badge de autosave")

    def test_06_http_routes_intake_and_assets(self):
        """06. Valida que el servidor HTTP sirva /intake, /intake.html y recursos estáticos con 200 OK."""
        # /intake
        req = urllib.request.Request(f"{self.base_url}/intake")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/html", resp.headers.get("Content-Type"))
            content = resp.read().decode("utf-8")
            self.assertIn("Campaign Intake Studio", content)

        # /intake.html
        req2 = urllib.request.Request(f"{self.base_url}/intake.html")
        with urllib.request.urlopen(req2) as resp:
            self.assertEqual(resp.status, 200)

        # /intake.css
        req_css = urllib.request.Request(f"{self.base_url}/intake.css")
        with urllib.request.urlopen(req_css) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/css", resp.headers.get("Content-Type"))

        # /intake.js
        req_js = urllib.request.Request(f"{self.base_url}/intake.js")
        with urllib.request.urlopen(req_js) as resp:
            self.assertEqual(resp.status, 200)

    def test_07_api_intake_endpoints(self):
        """07. Valida los endpoints REST /api/intake/clients y /api/intake/draft (GET y POST)."""
        # GET /api/intake/clients
        req_clients = urllib.request.Request(f"{self.base_url}/api/intake/clients")
        with urllib.request.urlopen(req_clients) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            clients = data.get("clients", [])
            self.assertIsInstance(clients, list)
            client_ids = [c.get("id") for c in clients]
            self.assertIn("locos-materos", client_ids, "Debe incluir a Locos Materos como cliente existente con memoria")

        # POST /api/intake/draft
        payload = {
            "mode": "NEW_CLIENT",
            "client_name": "Test Client Agency",
            "current_step": 1,
            "timestamp": "2026-09-20T00:00:00Z"
        }
        post_data = json.dumps(payload).encode("utf-8")
        req_post = urllib.request.Request(
            f"{self.base_url}/api/intake/draft",
            data=post_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_post) as resp:
            self.assertEqual(resp.status, 200)
            res_json = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res_json.get("status"), "SUCCESS")

        # GET /api/intake/draft
        req_draft = urllib.request.Request(f"{self.base_url}/api/intake/draft")
        with urllib.request.urlopen(req_draft) as resp:
            self.assertEqual(resp.status, 200)
            draft_res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(draft_res.get("status"), "SUCCESS")
            saved_draft = draft_res.get("draft")
            self.assertIsNotNone(saved_draft)
            self.assertEqual(saved_draft.get("client_name"), "Test Client Agency")

    def test_08_mission_control_intake_integration(self):
        """08. Valida que el Dashboard Mission Control (web/index.html) vincule a /intake."""
        index_path = os.path.join(WORKSPACE_ROOT, "web", "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            index_html = f.read()
        self.assertIn('href="/intake"', index_html, "web/index.html debe tener un enlace a /intake")
        self.assertIn('btnGoToIntake', index_html, "Falta el ID btnGoToIntake en el botón de index.html")

if __name__ == "__main__":
    unittest.main()
