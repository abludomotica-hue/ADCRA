#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 16: Quality Control Engineer
Valida el motor de auditoría tricameral (Técnica, Creativa y de Marca),
conformidad formal con config/quality-control-schema.json, evaluación integral de especificaciones,
puntuación ponderada de calidad y certificación formal de entrega (APPROVED).
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de qc-evaluator a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "quality-control" / "qc-evaluator" / "scripts"))

from evaluate_quality import run_tricameral_audit, validate_qc_report

class TestPhase16QualityControl(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de qc-evaluator"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "quality-control" / "qc-evaluator" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: qc-evaluator", content)
        self.assertIn("domain: quality-control", content)
        self.assertIn("Auditoría Técnica", content)
        self.assertIn("Auditoría Creativa", content)
        self.assertIn("Auditoría de Marca", content)
        self.assertIn("720x1280", content)
        self.assertIn("EBU R128", content)
        self.assertIn("#0D5C3A", content)
        self.assertIn("quality-control-schema.json", content)

    def test_02_schema_contract_and_report_validity(self):
        """Valida que campaign/reports/quality-control-report.json cumpla con config/quality-control-schema.json"""
        report_file = WORKSPACE_ROOT / "campaign" / "reports" / "quality-control-report.json"
        self.assertTrue(report_file.is_file(), "No se encontró quality-control-report.json")

        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "quality-control-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/quality-control-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data.get("campaign_id"), "camp_locos_materos_2026")
        self.assertIn(data["certification_status"], ["APPROVED", "NEEDS_REVISION", "REJECTED"])

    def test_03_technical_audit_verification(self):
        """Verifica que la auditoría técnica certifique resolución, framerate, EBU R128 y archivos NLE"""
        report_file = WORKSPACE_ROOT / "campaign" / "reports" / "quality-control-report.json"
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        tech = data["audits"]["technical_audit"]
        self.assertEqual(tech["score"], 100.0)
        self.assertEqual(tech["status"], "PASSED")
        self.assertGreaterEqual(len(tech["checks"]), 4)

        check_ids = [c["check_id"] for c in tech["checks"]]
        self.assertIn("tech_01_resolution_9_16", check_ids)
        self.assertIn("tech_02_framerate_duration", check_ids)
        self.assertIn("tech_03_ebu_r128_loudness", check_ids)
        self.assertIn("tech_04_timeline_conformance", check_ids)
        self.assertIn("tech_05_master_audio_assets", check_ids)

        for c in tech["checks"]:
            self.assertTrue(c["passed"], f"Fallo en check técnico: {c['check_id']}")

    def test_04_creative_audit_verification(self):
        """Verifica que la auditoría creativa certifique sincronía de cortes, narrativa y motion graphics"""
        report_file = WORKSPACE_ROOT / "campaign" / "reports" / "quality-control-report.json"
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        creative = data["audits"]["creative_audit"]
        self.assertEqual(creative["score"], 100.0)
        self.assertEqual(creative["status"], "PASSED")
        self.assertGreaterEqual(len(creative["checks"]), 3)

        check_ids = [c["check_id"] for c in creative["checks"]]
        self.assertIn("creat_01_beat_sync_cuts", check_ids)
        self.assertIn("creat_02_narrative_progression", check_ids)
        self.assertIn("creat_03_motion_graphics_overlays", check_ids)
        self.assertIn("creat_04_safe_zones_adherence", check_ids)

        for c in creative["checks"]:
            self.assertTrue(c["passed"], f"Fallo en check creativo: {c['check_id']}")

    def test_05_brand_audit_verification(self):
        """Verifica que la auditoría de marca certifique paleta oficial, calidez, claim y packshot"""
        report_file = WORKSPACE_ROOT / "campaign" / "reports" / "quality-control-report.json"
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        brand = data["audits"]["brand_audit"]
        self.assertEqual(brand["score"], 100.0)
        self.assertEqual(brand["status"], "PASSED")
        self.assertGreaterEqual(len(brand["checks"]), 3)

        check_ids = [c["check_id"] for c in brand["checks"]]
        self.assertIn("brand_01_color_palette_harmony", check_ids)
        self.assertIn("brand_02_cinematic_warmth_look", check_ids)
        self.assertIn("brand_03_official_campaign_claim", check_ids)
        self.assertIn("brand_04_packshot_hero_closing", check_ids)

        for c in brand["checks"]:
            self.assertTrue(c["passed"], f"Fallo en check de marca: {c['check_id']}")

    def test_06_overall_score_and_certification_decision(self):
        """Verifica la ponderación tricameral matemática y la certificación definitiva APPROVED"""
        report_file = WORKSPACE_ROOT / "campaign" / "reports" / "quality-control-report.json"
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        tech_score = data["audits"]["technical_audit"]["score"]
        creative_score = data["audits"]["creative_audit"]["score"]
        brand_score = data["audits"]["brand_audit"]["score"]

        expected_weighted = round(tech_score * 0.35 + creative_score * 0.35 + brand_score * 0.30, 1)
        self.assertEqual(data["overall_score"], expected_weighted)
        self.assertGreaterEqual(data["overall_score"], 90.0)
        self.assertEqual(data["certification_status"], "APPROVED")

    def test_07_cli_execution_and_validate_only(self):
        """Verifica que el script CLI pueda ejecutarse con flag --validate-only"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "quality-control" / "qc-evaluator" / "scripts" / "evaluate_quality.py"
        cmd = [sys.executable, str(script_path), "--validate-only"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"Fallo CLI validate-only: {p.stderr}")
        self.assertIn("cumple 100% con config/quality-control-schema.json", p.stdout)

if __name__ == "__main__":
    unittest.main()
