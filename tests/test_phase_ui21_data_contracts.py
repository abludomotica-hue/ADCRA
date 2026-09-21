import unittest
import os
import json
import urllib.request
import urllib.parse

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhaseUI21DataContracts(unittest.TestCase):
    """Test suite para la Fase UI-21: Data Contracts Auditor Studio (Gobernanza JSON Schema)."""

    def test_01_contracts_css_classes(self):
        """01. Valida que los estilos de Data Contracts estén en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        self.assertTrue(os.path.exists(css_path), "intake.css debe existir")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".contracts-container",
            ".contracts-summary-banner",
            ".contracts-grid",
            ".contract-card",
            ".contract-card.status-valid",
            ".contract-meta-row"
        ]

        for cls in required_classes:
            self.assertIn(cls, css, f"La clase {cls} debe estar definida en intake.css")

    def test_02_contracts_html_and_js(self):
        """02. Valida estructura HTML de studioSubnav y métodos de Contracts Studio en intake.js."""
        html_path = os.path.join(WORKSPACE_ROOT, "web", "intake.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="tabContracts"', html, "tabContracts debe existir en studioSubnav")
        self.assertIn('data-view="contracts"', html, "tabContracts debe tener data-view='contracts'")

        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        required_methods = [
            "renderDataContractsView",
            "displayDataContractsUI"
        ]

        for method in required_methods:
            self.assertIn(method, js, f"El método {method} debe estar definido en intake.js")

    def test_03_contracts_status_api(self):
        """03. Valida endpoint GET /api/intake/contracts/status con los 10 esquemas formales."""
        url = "http://localhost:8080/api/intake/contracts/status"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertTrue(data.get("all_valid"), f"Todos los contratos deben ser válidos: {data}")
            self.assertEqual(data.get("total_contracts"), 10)
            self.assertEqual(data.get("passed_contracts"), 10)
            self.assertEqual(data.get("validation_rate"), "100.0%")
            contracts = data.get("contracts", [])
            self.assertEqual(len(contracts), 10)
            for c in contracts:
                self.assertTrue(c.get("valid"), f"Contrato {c.get('name')} debe ser válido")
                self.assertEqual(len(c.get("errors", [])), 0)

    def test_04_validate_contract_endpoint_valid_payload(self):
        """04. Valida endpoint POST /api/intake/validate-contract con payload válido de storyboard."""
        url = "http://localhost:8080/api/intake/validate-contract"
        # Cargar storyboard real que sabemos que es válido
        storyboard_path = os.path.join(WORKSPACE_ROOT, "campaign", "storyboard", "storyboard.json")
        with open(storyboard_path, "r", encoding="utf-8") as f:
            real_sb = json.load(f)

        payload = {
            "schema_name": "storyboard-schema.json",
            "payload": real_sb
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertTrue(data.get("valid"))
            self.assertEqual(len(data.get("errors", [])), 0)

    def test_05_validate_contract_endpoint_invalid_payload(self):
        """05. Valida endpoint POST /api/intake/validate-contract detectando violaciones de esquema."""
        url = "http://localhost:8080/api/intake/validate-contract"
        payload = {
            "schema_name": "storyboard-schema.json",
            "payload": {
                "campaign_id": "invalid_sb",
                "scenes": []  # Falta target_total_duration_sec, scene_count minItems, etc.
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "SUCCESS")
            self.assertFalse(data.get("valid"))
            self.assertGreater(len(data.get("errors", [])), 0)

if __name__ == "__main__":
    unittest.main()
