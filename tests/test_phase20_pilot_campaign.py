#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 20: Campaña Piloto Completa (Pilot Run E2E)
Valida la orquestación unificada de los 12 estadios del pipeline,
conformidad formal con config/pilot-campaign-schema.json, verificación broadcast,
integridad cruzada de artefactos, métricas de calidad y ejecución CLI.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de pilot-orchestrator a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "pilot-orchestrator" / "scripts"))

from pilot_runner import run_pilot_pipeline, validate_pilot_manifest

class TestPhase20PilotCampaign(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de pilot-orchestrator"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "pilot-orchestrator" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: pilot-orchestrator", content)
        self.assertIn("domain: production", content)
        self.assertIn("config/pilot-campaign-schema.json", content)
        self.assertIn("Cadena Unificada de Producción E2E", content)
        self.assertIn("Matriz de Verificación de Integridad Cruzada", content)
        self.assertIn("EBU R128", content)
        self.assertIn("Quality Control", content)

    def test_02_schema_contract_and_manifest_validity(self):
        """Valida que campaign/pilot/pilot-campaign-manifest.json cumpla con config/pilot-campaign-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "pilot" / "pilot-campaign-manifest.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró pilot-campaign-manifest.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "pilot-campaign-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/pilot-campaign-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["final_status"], "COMPLETED")
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertTrue(data["pilot_id"].startswith("pilot_"))

    def test_03_pipeline_stages_completeness(self):
        """Verifica que los 12 estadios del pipeline se hayan ejecutado satisfactoriamente"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "pilot" / "pilot-campaign-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        stages = data["pipeline_stages"]
        self.assertEqual(len(stages), 12, "Deben existir exactamente 12 estadios en el pipeline")

        expected_stages = [
            "stage_01_strategy",
            "stage_02_audio_intelligence",
            "stage_03_video_intelligence",
            "stage_04_creative_copy",
            "stage_05_storyboard",
            "stage_06_assembly_and_timeline",
            "stage_07_color_grading",
            "stage_08_sound_design",
            "stage_09_social_formatting",
            "stage_10_quality_control",
            "stage_11_iteration_control",
            "stage_12_memory_and_telemetry"
        ]

        stage_ids = [s["stage_id"] for s in stages]
        for exp in expected_stages:
            self.assertIn(exp, stage_ids, f"Falta el estadio {exp} en el pipeline")

        for s in stages:
            self.assertEqual(s["status"], "SUCCESS", f"Estadio {s['stage_id']} no concluyó en SUCCESS")
            self.assertGreater(s["execution_time_ms"], 0)
            self.assertGreater(len(s["artifacts_verified"]), 0)

    def test_04_e2e_technical_and_broadcast_metrics(self):
        """Verifica las métricas técnicas globales del montaje y sonido broadcast"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "pilot" / "pilot-campaign-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        metrics = data["e2e_metrics"]
        self.assertAlmostEqual(metrics["duration_seconds"], 29.187, places=2)
        self.assertEqual(metrics["resolution"], "720x1280")
        self.assertEqual(metrics["fps"], 24.0)
        self.assertEqual(metrics["total_scenes"], 9)
        self.assertAlmostEqual(metrics["loudness_lufs"], -12.7, places=1)
        self.assertEqual(metrics["quality_score"], 100.0)
        self.assertLessEqual(metrics["iterations_count"], 3)

    def test_05_e2e_creative_and_brand_coherence(self):
        """Verifica que los entregables y masters existan físicamente en disco"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "pilot" / "pilot-campaign-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        deliverables = data["deliverables_summary"]
        self.assertGreaterEqual(deliverables["social_formats_count"], 5)

        # Verificar existencia física de masters en disco
        wav_path = WORKSPACE_ROOT / deliverables["audio_master_wav"]
        mp3_path = WORKSPACE_ROOT / deliverables["audio_master_mp3"]
        edl_path = WORKSPACE_ROOT / deliverables["timeline_edl"]
        xml_path = WORKSPACE_ROOT / deliverables["timeline_xml"]
        color_path = WORKSPACE_ROOT / deliverables["color_manifest"]

        self.assertTrue(wav_path.is_file(), f"Falta master WAV: {wav_path}")
        self.assertTrue(mp3_path.is_file(), f"Falta master MP3: {mp3_path}")
        self.assertTrue(edl_path.is_file(), f"Falta timeline EDL: {edl_path}")
        self.assertTrue(xml_path.is_file(), f"Falta timeline XML: {xml_path}")
        self.assertTrue(color_path.is_file(), f"Falta color manifest: {color_path}")

    def test_06_e2e_qc_and_iteration_invariants(self):
        """Verifica el veredicto de QC, invariantes de parada y actualización del manifiesto maestro"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "pilot" / "pilot-campaign-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cert = data["quality_certification"]
        self.assertEqual(cert["verdict"], "APPROVED")
        self.assertEqual(cert["technical_score"], 100.0)
        self.assertEqual(cert["creative_score"], 100.0)
        self.assertEqual(cert["brand_score"], 100.0)

        # Verificar actualización del manifiesto maestro campaign-manifest.json
        camp_manifest_file = WORKSPACE_ROOT / "campaign" / "campaign-manifest.json"
        with open(camp_manifest_file, "r", encoding="utf-8") as f:
            camp_data = json.load(f)

        self.assertEqual(camp_data["workflow_status"]["current_phase"], "FASE 20 — PILOT RUN COMPLETE")
        self.assertTrue(camp_data["workflow_status"]["is_approved"])
        self.assertLessEqual(camp_data["workflow_status"]["iteration_count"], 3)

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI de pilot_runner.py con --validate-only y --json"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "pilot-orchestrator" / "scripts" / "pilot_runner.py"

        # 1. Probar --validate-only
        cmd_val = [sys.executable, str(script_path), "--validate-only"]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True)
        self.assertEqual(p_val.returncode, 0, f"Fallo CLI validate-only: {p_val.stderr}")
        self.assertIn("cumple 100% con config/pilot-campaign-schema.json", p_val.stdout)

        # 2. Probar --json
        cmd_json = [sys.executable, str(script_path), "--json"]
        p_json = subprocess.run(cmd_json, capture_output=True, text=True)
        self.assertEqual(p_json.returncode, 0, f"Fallo CLI json: {p_json.stderr}")
        report_data = json.loads(p_json.stdout)
        self.assertTrue(report_data["ready_for_production"])
        self.assertEqual(report_data["certification_verdict"], "APPROVED")
        self.assertEqual(report_data["quality_score"], 100.0)

if __name__ == "__main__":
    unittest.main()
