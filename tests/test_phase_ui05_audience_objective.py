#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-05: Audience + Objective
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (objective-category-group, audience-tabs-nav, epistemology-pill, chip-pill).
2. Lógica de Objetivos Canónicos (14 metas de negocio) y Resultados Deseados en web/intake.js.
3. Audience Builder Tripartito (Primaria, Secundaria, Exploratoria) con epistemología FACT vs AI_SUGGESTION.
4. Persistencia integral de objetivos y audiencias en /api/intake/draft.
5. Evaluación cualitativa de diagnósticos (COMPLETE vs MISSING) para Pasos 02 y 03.
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestPhaseUI05AudienceObjective(unittest.TestCase):
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

    def test_01_audience_objective_css_classes(self):
        """01. Valida estilos de Objetivos y Audiencia en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required_classes = [
            ".objective-category-group",
            ".objective-category-title",
            ".audience-tabs-nav",
            ".audience-tab-btn",
            ".epistemology-pill",
            ".epistemology-ai",
            ".epistemology-fact",
            ".chip-pill"
        ]
        for c in required_classes:
            self.assertIn(c, css, f"Falta {c} en intake.css")

    def test_02_step02_canonical_objectives(self):
        """02. Valida los 14 objetivos canónicos y outcomes en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        canonical_14 = [
            'AWARENESS', 'BRANDING', 'RETENCION', 'COMUNIDAD',
            'CONVERSION', 'VENTAS', 'LEADS', 'TRAFICO', 'REMARKETING',
            'LANZAMIENTO', 'ENGAGEMENT', 'EDUCACION', 'EVENTO', 'TEMPORADA'
        ]
        for obj in canonical_14:
            self.assertIn(f"id: '{obj}'", js, f"Falta objetivo canónico {obj} en web/intake.js")

        self.assertIn("renderStep02_Objective()", js)
        self.assertIn("bindStep02_Events()", js)
        self.assertIn("selDesiredOutcome", js)
        self.assertIn("inpOutcomeNote", js)

    def test_03_step03_tripartite_audience(self):
        """03. Valida Audience Builder Tripartito y epistemología en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep03_Audience()",
            "bindStep03_Events()",
            "audience-tabs-nav",
            'data-tab="primary"',
            'data-tab="secondary"',
            'data-tab="exploratory"',
            "inpAudienceAgeMin",
            "inpAudienceAgeMax",
            "epistemology-pill",
            "AI_SUGGESTION",
            "FACT"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_04_audience_objective_persistence(self):
        """04. Valida persistencia y round-trip de objetivos y audiencia tripartita."""
        payload = {
            "clientMode": "EXISTING_CLIENT",
            "activeStep": 3,
            "draft": {
                "client": {"brand_name": "Locos Materos"},
                "objective": {
                    "primary": "CONVERSION",
                    "secondary": ["RETENCION", "ENGAGEMENT"],
                    "desired_outcome": "comprar",
                    "custom_outcome_note": "Incentivar compra de nuevo termo térmico 1L"
                },
                "audience": {
                    "primary": {
                        "demographics": {
                            "age_range": [22, 38],
                            "location": "Santiago y Valparaíso, Chile",
                            "language": "es",
                            "gender": "todos",
                            "occupation": "Estudiantes y Profesionales jóvenes"
                        },
                        "psychographics": {
                            "interests": ["yerba mate", "estudio nocturno", "vida al aire libre"],
                            "needs": ["mantener agua caliente más de 12 hrs"],
                            "motivations": ["compartir ritual", "sabor auténtico"],
                            "objections": ["precio percibido", "tiempo de despacho"]
                        },
                        "digital_behavior": {
                            "primary_platforms": ["INSTAGRAM", "TIKTOK"],
                            "peak_hours": "18:00 - 22:00"
                        },
                        "is_ai_suggested": False
                    },
                    "secondary": {
                        "demographics": {
                            "age_range": [39, 60],
                            "location": "Todo Chile",
                            "language": "es",
                            "gender": "todos",
                            "occupation": "Adultos tradicionales del mate"
                        },
                        "psychographics": {
                            "interests": ["costumbres", "familia", "descanso"],
                            "needs": ["durabilidad"],
                            "motivations": ["calidad noble"],
                            "objections": ["compra online"]
                        },
                        "digital_behavior": {
                            "primary_platforms": ["FACEBOOK", "YOUTUBE"]
                        },
                        "is_ai_suggested": True
                    },
                    "exploratory": {
                        "demographics": {
                            "age_range": [18, 25],
                            "location": "Latinoamérica",
                            "language": "es",
                            "gender": "todos",
                            "occupation": "Gamers y Creadores de contenido"
                        },
                        "psychographics": {
                            "interests": ["gaming", "streaming", "energía natural"],
                            "needs": ["foco prolongado sin bajón"]
                        },
                        "digital_behavior": {
                            "primary_platforms": ["TWITCH", "TIKTOK"]
                        },
                        "is_ai_suggested": True
                    }
                }
            },
            "updated_at": "2026-09-20T12:45:00Z"
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
        obj = data.get("objective", {})
        aud = data.get("audience", {})

        self.assertEqual(obj.get("primary"), "CONVERSION")
        self.assertIn("RETENCION", obj.get("secondary", []))
        self.assertEqual(obj.get("desired_outcome"), "comprar")
        self.assertEqual(aud.get("primary", {}).get("demographics", {}).get("location"), "Santiago y Valparaíso, Chile")
        self.assertEqual(aud.get("primary", {}).get("demographics", {}).get("age_range"), [22, 38])
        self.assertFalse(aud.get("primary", {}).get("is_ai_suggested"))
        self.assertTrue(aud.get("secondary", {}).get("is_ai_suggested"))
        self.assertTrue(aud.get("exploratory", {}).get("is_ai_suggested"))

    def test_05_diagnostic_evaluation_rules(self):
        """05. Valida reglas diagnósticas en evaluateAllStepStatuses."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        # Step 2 logic: if (this.draft.objective.primary) -> COMPLETE else MISSING
        self.assertIn("this.draft.objective.primary", js)
        self.assertIn("this.updateStepStatus(2, 'COMPLETE')", js)
        self.assertIn("this.updateStepStatus(2, 'MISSING')", js)

        # Step 3 logic: if (this.draft.audience.primary.location) -> COMPLETE
        self.assertIn("this.draft.audience.primary.location", js)
        self.assertIn("this.updateStepStatus(3, 'COMPLETE')", js)


if __name__ == "__main__":
    unittest.main()
