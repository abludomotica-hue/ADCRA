#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-13: Agent Activity & Live Telemetry
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (agent-telemetry-grid, agent-telemetry-card,
   agent-avatar-icon, agent-name, agent-status-pill, agent-role-desc, agent-task-text).
2. Lógica de telemetría de agentes en web/intake.js (renderStep16_Automation, bindStep16_Events,
   fetchAgentsTelemetry, integración de despacho en Step 17).
3. Endpoint de telemetría en vivo GET /api/intake/agents/status (los 7 agentes especializados de ADCRA:
   Director, Copywriter, Beat Editor, Motion Graphics, Color, Sound, QC).
4. Endpoint de despacho agéntico POST /api/intake/agents/dispatch y persistencia en campaign/agent-telemetry.json.
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


class TestPhaseUI13AgentActivity(unittest.TestCase):
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

    def test_01_agents_css_classes(self):
        """01. Valida estilos de Telemetría de Agentes en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".agent-telemetry-grid",
            ".agent-telemetry-card",
            ".agent-avatar-icon",
            ".agent-name",
            ".agent-status-pill",
            ".agent-role-desc",
            ".agent-task-text"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_agents_js_logic(self):
        """02. Valida métodos de telemetría y despacho en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep16_Automation()",
            "bindStep16_Events()",
            "fetchAgentsTelemetry()",
            "btnRefreshAgents",
            "/api/intake/agents/status",
            "/api/intake/agents/dispatch"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_api_agents_status_endpoint(self):
        """03. Valida endpoint GET /api/intake/agents/status con los 7 agentes de ADCRA."""
        url = f"{self.base_url}/api/intake/agents/status"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))

        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertEqual(res.get("ecosystem_status"), "ONLINE")
        self.assertEqual(res.get("active_agents_count"), 7)

        agent_ids = [ag.get("id") for ag in res.get("agents", [])]
        expected_7 = [
            "campaign-director",
            "copywriting-engine",
            "beat-synced-editor",
            "motion-graphics",
            "color-grading",
            "sound-designer",
            "quality-control"
        ]
        for eid in expected_7:
            self.assertIn(eid, agent_ids, f"Falta agente {eid} en status")

    def test_04_api_agents_dispatch_endpoint(self):
        """04. Valida endpoint POST /api/intake/agents/dispatch y persistencia en disco."""
        url = f"{self.base_url}/api/intake/agents/dispatch"
        payload = {
            "campaign_id": "test-campaign-adcra-001",
            "mode": "AUTONOMOUS_APPROVALS"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))

        self.assertEqual(res.get("status"), "SUCCESS")
        disp = res.get("dispatch", {})
        self.assertEqual(disp.get("campaign_id"), "test-campaign-adcra-001")
        self.assertEqual(disp.get("status"), "DISPATCHED")
        self.assertEqual(len(disp.get("agents_dispatched", [])), 7)

        # Verificar persistencia en campaign/agent-telemetry.json
        telemetry_path = os.path.join(WORKSPACE_ROOT, "campaign", "agent-telemetry.json")
        self.assertTrue(os.path.exists(telemetry_path), "Falta campaign/agent-telemetry.json")
        with open(telemetry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("campaign_id"), "test-campaign-adcra-001")


if __name__ == "__main__":
    unittest.main()
