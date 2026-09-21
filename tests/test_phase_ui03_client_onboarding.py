#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-03: Client Onboarding
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (.clients-grid, .client-card, .client-memory-banner, .inference-preview-card).
2. Lógica agéntica en web/intake.js (fetchExistingClients, loadClientFromMemory, inferencia y aceptación de datos).
3. Endpoint REST POST /api/intake/analyze-url (rastreo e inferencia semántica de marca, colores y claims).
4. Endpoint REST GET /api/intake/clients (listado de marcas registradas y perfiles de memoria episódica).
5. Integridad de memoria histórica de Locos Materos (reglas de retención, paleta, BPM óptimo 107.7 y Quality Score 100.0).
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

class TestPhaseUI03ClientOnboarding(unittest.TestCase):

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

    def test_01_client_onboarding_css_classes(self):
        """01. Valida estilos de onboarding de clientes y tarjetas de inferencia en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".clients-grid", css, "Falta .clients-grid en intake.css")
        self.assertIn(".client-card", css, "Falta .client-card en intake.css")
        self.assertIn(".client-memory-banner", css, "Falta .client-memory-banner en intake.css")
        self.assertIn(".memory-pill", css, "Falta .memory-pill en intake.css")
        self.assertIn(".inference-preview-card", css, "Falta .inference-preview-card en intake.css")
        self.assertIn(".inference-badge-ai", css, "Falta .inference-badge-ai en intake.css")

    def test_02_client_onboarding_js_logic(self):
        """02. Valida métodos de onboarding agéntico en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "fetchExistingClients()",
            "loadClientFromMemory(",
            "renderStep01_Client()",
            "bindStep01_Events()",
            "inferredAnalysis",
            "selectedClientId",
            "btnAnalyzeWeb",
            "btnAcceptInference"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_api_analyze_url_success_and_inference(self):
        """03. Valida el endpoint POST /api/intake/analyze-url con extracción semántica."""
        url = f"{self.base_url}/api/intake/analyze-url"
        payload = json.dumps({"url": "https://locosmateros.cl"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res.get("status"), "SUCCESS")
            analysis = res.get("analysis", {})
            self.assertEqual(analysis.get("brand_name"), "Locos Materos")
            self.assertEqual(analysis.get("colors", {}).get("primary"), "#0D5C3A")
            self.assertEqual(analysis.get("epistemology"), "AI_INFERENCE")
            self.assertGreaterEqual(analysis.get("confidence", 0), 0.90)

    def test_04_api_analyze_url_error_handling(self):
        """04. Valida manejo de errores en POST /api/intake/analyze-url (URL vacía)."""
        url = f"{self.base_url}/api/intake/analyze-url"
        payload = json.dumps({"url": ""}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 400)
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)
            res = json.loads(e.read().decode("utf-8"))
            self.assertEqual(res.get("status"), "ERROR")

    def test_05_api_clients_endpoint_data_integrity(self):
        """05. Valida que GET /api/intake/clients devuelva clientes registrados con memoria."""
        url = f"{self.base_url}/api/intake/clients"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            clients = data.get("clients", [])
            self.assertGreaterEqual(len(clients), 1)

            locos = next((c for c in clients if c["id"] == "locos-materos"), None)
            self.assertIsNotNone(locos, "No se encontró el cliente 'locos-materos'")
            self.assertTrue(locos.get("has_memory"))
            mem = locos.get("memory", {})
            self.assertEqual(mem.get("brand_name"), "Locos Materos")
            self.assertIn("aesthetic_learnings", mem)
            self.assertIn("musical_tempo_learnings", mem)
            self.assertIn("retention_rules", mem)
            self.assertEqual(mem.get("musical_tempo_learnings", {}).get("last_successful_bpm"), 107.7)

    def test_06_memory_retention_rules_broadcast(self):
        """06. Valida fidelidad broadcast de reglas de retención aprendidas."""
        memory_path = os.path.join(WORKSPACE_ROOT, "campaign", "memory", "brand-profile-memory.json")
        self.assertTrue(os.path.exists(memory_path), "Falta brand-profile-memory.json")

        with open(memory_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rules = data.get("retention_rules", {}).get("mandatory_rules", [])
        self.assertTrue(any("mate" in r.lower() for r in rules), "Falta regla de consistencia de mate")
        self.assertTrue(any("9:16" in r for r in rules), "Falta regla de safe zones 9:16")
        self.assertTrue(any("09" in r for r in rules), "Falta regla de packshot en escena 09")

if __name__ == "__main__":
    unittest.main()
