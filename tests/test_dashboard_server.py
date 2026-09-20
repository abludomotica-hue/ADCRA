#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — ADCRA Mission Control Web Dashboard
Verifica la existencia y estructura de los activos web (HTML/CSS/JS),
los endpoints REST del servidor HTTP, el streaming con byte-ranges (HTTP 206)
y la integración con el CLI 'adcra dashboard'.
"""

import os
import sys
import json
import time
import socket
import threading
import urllib.request
import urllib.error
import subprocess
import unittest

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, WORKSPACE_ROOT)

import dashboard_server

def get_free_port():
    """Encuentra un puerto TCP libre efímero para pruebas."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class TestDashboardServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_port = get_free_port()
        cls.server_address = ('127.0.0.1', cls.test_port)
        cls.httpd = dashboard_server.ThreadedHTTPServer(cls.server_address, dashboard_server.DashboardRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.test_port}"
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_01_web_assets_exist(self):
        """01. Verifica que los archivos estáticos web (HTML, CSS, JS) existan y contengan marcas clave."""
        web_dir = os.path.join(WORKSPACE_ROOT, "web")
        html_path = os.path.join(web_dir, "index.html")
        css_path = os.path.join(web_dir, "index.css")
        js_path = os.path.join(web_dir, "app.js")

        self.assertTrue(os.path.exists(html_path), "Falta web/index.html")
        self.assertTrue(os.path.exists(css_path), "Falta web/index.css")
        self.assertTrue(os.path.exists(js_path), "Falta web/app.js")

        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("ADCRA Mission Control", html)
        self.assertIn("videoViewport", html)
        self.assertIn("mainVideoPlayer", html)
        self.assertIn("safeZoneOverlay", html)

        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("--color-mate-green", css)
        self.assertIn("--color-yerba-gold", css)
        self.assertIn("backdrop-filter", css)

    def test_02_server_routes_status_and_health(self):
        """02. Verifica que /api/status y /api/health respondan HTTP 200 con JSON válido."""
        # Test /api/status
        req_status = urllib.request.Request(f"{self.base_url}/api/status")
        with urllib.request.urlopen(req_status, timeout=5) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertEqual(data.get("system"), "ADCRA")
            self.assertEqual(data.get("total_phases"), 22)
            self.assertEqual(data.get("completed_phases"), 22)
            self.assertEqual(data.get("completion_percentage"), 100.0)

        # Test /api/health
        req_health = urllib.request.Request(f"{self.base_url}/api/health")
        with urllib.request.urlopen(req_health, timeout=5) as res:
            self.assertEqual(res.status, 200)
            health = json.loads(res.read().decode("utf-8"))
            self.assertEqual(health.get("status"), "HEALTHY")
            self.assertGreater(health.get("cpu_cores"), 0)

    def test_03_server_routes_deliver_and_benchmark(self):
        """03. Verifica los endpoints /api/deliver y /api/benchmark."""
        req_deliv = urllib.request.Request(f"{self.base_url}/api/deliver")
        with urllib.request.urlopen(req_deliv, timeout=5) as res:
            self.assertEqual(res.status, 200)
            pkg = json.loads(res.read().decode("utf-8"))
            self.assertEqual(pkg.get("campaign_id"), "camp_locos_materos_2026")
            self.assertEqual(pkg.get("broadcast_certification", {}).get("status"), "APPROVED")
            self.assertEqual(len(pkg.get("variants", [])), 5)

        req_bench = urllib.request.Request(f"{self.base_url}/api/benchmark")
        with urllib.request.urlopen(req_bench, timeout=5) as res:
            self.assertEqual(res.status, 200)
            bench = json.loads(res.read().decode("utf-8"))
            self.assertIn(bench.get("performance_rating"), ["EXCELLENT", "GOOD"])
            self.assertGreaterEqual(len(bench.get("engine_benchmarks", [])), 8)

    def test_04_server_routes_introspect(self):
        """04. Verifica el endpoint /api/introspect y el catálogo de 23 habilidades."""
        req = urllib.request.Request(f"{self.base_url}/api/introspect")
        with urllib.request.urlopen(req, timeout=5) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertGreaterEqual(data.get("total_skills"), 20)
            self.assertTrue(any(s["name"] == "campaign-production-master" for s in data["skills"]))

    def test_05_server_route_artifact_and_security(self):
        """05. Verifica que /api/artifact sirva JSONs de campaña de forma segura y bloquee path traversal."""
        # Ruta válida
        req = urllib.request.Request(f"{self.base_url}/api/artifact?path=campaign/campaign-manifest.json")
        with urllib.request.urlopen(req, timeout=5) as res:
            self.assertEqual(res.status, 200)
            art = json.loads(res.read().decode("utf-8"))
            self.assertEqual(art.get("type"), "json")
            self.assertIn("campaign_id", art.get("content", {}))

        # Path traversal malicioso
        req_bad = urllib.request.Request(f"{self.base_url}/api/artifact?path=../../etc/passwd")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req_bad, timeout=5)
        self.assertEqual(ctx.exception.code, 404)

    def test_06_video_streaming_range_request_http_206(self):
        """06. Verifica el streaming de video con HTTP 206 Partial Content y encabezados Accept-Ranges."""
        video_url = f"{self.base_url}/campaign/deliverables/masters/locos_materos_master_9x16.mp4"
        req = urllib.request.Request(video_url, headers={"Range": "bytes=0-1023"})
        
        with urllib.request.urlopen(req, timeout=5) as res:
            self.assertEqual(res.status, 206)
            self.assertEqual(res.headers.get("Accept-Ranges"), "bytes")
            self.assertIn("bytes 0-1023/", res.headers.get("Content-Range"))
            self.assertEqual(int(res.headers.get("Content-Length")), 1024)
            data = res.read()
            self.assertEqual(len(data), 1024)

    def test_07_cli_dashboard_integration(self):
        """07. Valida que el CLI 'adcra' exponga el comando 'dashboard'."""
        cli_path = os.path.join(WORKSPACE_ROOT, "bin/adcra")
        res = subprocess.run([cli_path, "--help"], stdout=subprocess.PIPE, text=True, timeout=5)
        self.assertEqual(res.returncode, 0)
        self.assertIn("dashboard", res.stdout)

if __name__ == "__main__":
    unittest.main()
