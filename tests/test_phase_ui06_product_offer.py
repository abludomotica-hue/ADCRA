#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-06: Product + Offer
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (product-manager-bar, anti-hallucination-card,
   claim-chip, offer-mode-selector, offer-type-grid, branding-puro-banner).
2. Lógica del Product Intelligence Studio (Multi-Producto, SKU, precios, escudo anti-alucinación
   con beneficios verificados y afirmaciones prohibidas).
3. Lógica del Commercial Offer Studio (Modo Dual: Oferta Comercial vs Branding Puro, 6 tipos de oferta,
   badging de urgencia en Motion Graphics y letra chica legal).
4. Persistencia integral de productos y ofertas vía /api/intake/draft.
5. Evaluación cualitativa de diagnósticos (COMPLETE, READY, MISSING) para Pasos 05 y 06.
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


class TestPhaseUI06ProductOffer(unittest.TestCase):
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

    def test_01_product_offer_css_classes(self):
        """01. Valida estilos del Product & Offer Studio en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".product-manager-bar",
            ".product-tab-btn",
            ".anti-hallucination-card",
            ".anti-hallucination-title",
            ".anti-hallucination-badge",
            ".claim-chip.verified",
            ".claim-chip.forbidden",
            ".offer-mode-selector",
            ".offer-mode-card",
            ".offer-type-grid",
            ".offer-type-card",
            ".branding-puro-banner"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_product_intelligence_js_logic(self):
        """02. Valida métodos del Product Intelligence Studio en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep05_Product()",
            "bindStep05_Events()",
            "product-manager-bar",
            "btnAddProduct",
            "inpProdName",
            "inpProdSku",
            "selProdCategory",
            "inpProdRegularPrice",
            "inpProdOfferPrice",
            "anti-hallucination-card",
            "STRICT REASONING GUARD",
            "verified_benefits",
            "forbidden_claims",
            "btnAddBenefit",
            "btnAddClaim"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_commercial_offer_and_branding_puro_js_logic(self):
        """03. Valida oferta comercial, 6 tipos de oferta y Branding Puro en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep06_Offer()",
            "bindStep06_Events()",
            "offer-mode-selector",
            "BRANDING_PURO",
            "COMMERCIAL",
            "DISCOUNT_PERCENT",
            "DISCOUNT_AMOUNT",
            "BUNDLE_COMBO",
            "FREE_SHIPPING",
            "SPECIAL_GIFT",
            "LIMITED_EDITION",
            "branding-puro-banner",
            "inpOfferTitle",
            "inpCouponCode",
            "selUrgencyBadge"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_04_product_offer_data_persistence(self):
        """04. Valida persistencia y round-trip de productos y oferta vía /api/intake/draft."""
        payload = {
            "clientMode": "EXISTING_CLIENT",
            "activeStep": 5,
            "draft": {
                "client": {"brand_name": "Locos Materos"},
                "products": [
                    {
                        "id": "prod-1",
                        "sku": "LM-TRM-01",
                        "name": "Termo Acero Inox 1L Edición Patagónica",
                        "category": "Termos & Botellas",
                        "regular_price": 38990,
                        "offer_price": 29990,
                        "currency": "CLP",
                        "description": "Aislación al vacío multicapa con pico cebador de alta precisión.",
                        "verified_benefits": [
                            "Mantiene agua caliente por más de 24 horas",
                            "Acero inoxidable quirúrgico 304",
                            "Libre de BPA certificado"
                        ],
                        "forbidden_claims": [
                            "Cura problemas digestivos",
                            "El termo más barato de Chile"
                        ],
                        "specs": "Capacidad 1L, peso 540g, color verde mate"
                    },
                    {
                        "id": "prod-2",
                        "sku": "LM-MAT-02",
                        "name": "Mate Torpedo Uruguayo con Virola de Alpaca",
                        "category": "Mates & Bombillas",
                        "regular_price": 24990,
                        "offer_price": 19990,
                        "currency": "CLP",
                        "description": "Calabaza gruesa brasilera forrada en cuero vacuno legítimo.",
                        "verified_benefits": [
                            "Cuero legítimo cosido a mano",
                            "Virola de alpaca cincelada"
                        ],
                        "forbidden_claims": [
                            "Indestructible de por vida"
                        ],
                        "specs": "Base de 4 patas reforzadas"
                    }
                ],
                "offer": {
                    "is_branding_only": False,
                    "offer_type": "BUNDLE_COMBO",
                    "offer_title": "Pack Ritual Matero: Termo + Mate Torpedo con 25% OFF",
                    "discount_percentage": 25,
                    "coupon_code": "RITUAL25",
                    "valid_until": "Hasta agotar 150 unidades",
                    "urgency_badge": "ÚLTIMAS 48 HORAS",
                    "terms_conditions": "Válido para compras en territorio nacional. Despacho express disponible."
                }
            },
            "updated_at": "2026-09-20T13:10:00Z"
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
        prods = data.get("products", [])
        offer = data.get("offer", {})

        # Validaciones de producto
        self.assertEqual(len(prods), 2)
        p1 = prods[0]
        self.assertEqual(p1.get("sku"), "LM-TRM-01")
        self.assertEqual(p1.get("regular_price"), 38990)
        self.assertEqual(p1.get("offer_price"), 29990)
        self.assertIn("Mantiene agua caliente por más de 24 horas", p1.get("verified_benefits", []))
        self.assertIn("Cura problemas digestivos", p1.get("forbidden_claims", []))

        # Validaciones de oferta
        self.assertFalse(offer.get("is_branding_only"))
        self.assertEqual(offer.get("offer_type"), "BUNDLE_COMBO")
        self.assertEqual(offer.get("coupon_code"), "RITUAL25")
        self.assertEqual(offer.get("urgency_badge"), "ÚLTIMAS 48 HORAS")

    def test_05_diagnostic_evaluation_rules_step05_and_step06(self):
        """05. Valida reglas diagnósticas en evaluateAllStepStatuses para Pasos 05 y 06."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        # Step 5 evaluation
        self.assertIn("primaryProd.verified_benefits.length > 0", js)
        self.assertIn("this.updateStepStatus(5, 'COMPLETE')", js)
        self.assertIn("this.updateStepStatus(5, 'MISSING')", js)

        # Step 6 evaluation
        self.assertIn("this.draft.offer.is_branding_only", js)
        self.assertIn("this.updateStepStatus(6, 'COMPLETE')", js)


if __name__ == "__main__":
    unittest.main()
