#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 2: Campaign Director
Valida la definición de la habilidad, la ingesta formal del brief, la taxonomía epistemológica,
las transiciones de ciclo de vida y el límite estricto de 3 iteraciones automáticas.
"""

import os
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

class TestPhase2CampaignDirector(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y completitud de SKILL.md de Campaign Director"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "strategy" / "campaign-director" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta el archivo {skill_file}")
        
        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: campaign-director", content)
        self.assertIn("USER_REQUIREMENT", content)
        self.assertIn("CLIENT_REQUIREMENT", content)
        self.assertIn("CREATIVE_RECOMMENDATION", content)
        self.assertIn("TECHNICAL_REQUIREMENT", content)
        self.assertIn("AGENT_ASSUMPTION", content)
        self.assertIn("HALT_FOR_USER_REVIEW", content)
        self.assertIn("iteration_count", content)

    def test_02_ingest_real_brief_and_validate_schema(self):
        """Ejecuta ingest_brief.py sobre el brief real de Locos Materos y valida contra campaign-schema.json"""
        brief_file = WORKSPACE_ROOT / "Recursos" / "CAMPAÑA LOCOS MATEROS.md"
        self.assertTrue(brief_file.is_file(), "El brief de Recursos/ no existe")

        manifest_output = WORKSPACE_ROOT / "campaign" / "test_campaign_manifest.json"
        
        cmd = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "strategy" / "campaign-director" / "scripts" / "ingest_brief.py"),
            "--brief", str(brief_file),
            "--output", str(manifest_output.relative_to(WORKSPACE_ROOT)),
            "--campaign-id", "camp_locos_materos_test"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(result.returncode, 0, f"ingest_brief.py falló: {result.stderr}")
        self.assertTrue(manifest_output.is_file(), "No se generó el manifiesto")

        # Validar contra esquema oficial
        with open(manifest_output, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        schema_path = WORKSPACE_ROOT / "config" / "campaign-schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            
        jsonschema.validate(instance=manifest, schema=schema)
        self.assertEqual(manifest["client"]["name"], "Locos Materos")
        self.assertEqual(manifest["strategic_brief"]["objective"], "awareness")

    def test_03_epistemological_taxonomy_coverage(self):
        """Comprueba que todos los 5 tipos de requisitos estén presentes en el manifiesto parseado"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "campaign-manifest.json"
        self.assertTrue(manifest_file.is_file())

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        reqs = manifest["strategic_brief"]["requirements"]
        present_types = {r["type"] for r in reqs}

        expected_types = {
            "USER_REQUIREMENT",
            "CLIENT_REQUIREMENT",
            "CREATIVE_RECOMMENDATION",
            "TECHNICAL_REQUIREMENT",
            "AGENT_ASSUMPTION"
        }
        self.assertTrue(expected_types.issubset(present_types), f"Tipos faltantes: {expected_types - present_types}")

    def test_04_deliverable_specifications(self):
        """Verifica que los entregables cumplan con formato vertical 9:16 y 30 FPS"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "campaign-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        deliverables = manifest.get("deliverables", [])
        self.assertGreater(len(deliverables), 0)
        deliv = deliverables[0]
        self.assertEqual(deliv["aspect_ratio"], "9:16")
        self.assertEqual(deliv["resolution"]["width"], 1080)
        self.assertEqual(deliv["resolution"]["height"], 1920)
        self.assertEqual(deliv["fps"], 30.0)

    def test_05_lifecycle_transitions_and_iteration_limit(self):
        """Verifica la máquina de estados, transiciones y el corte estricto al 3er intento de iteración"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "strategy" / "campaign-director" / "scripts" / "lifecycle_manager.py"
        test_manifest_path = WORKSPACE_ROOT / "campaign" / "temp_lifecycle_test.json"
        
        # Copiar manifiesto base para prueba aislada
        base_manifest_path = WORKSPACE_ROOT / "campaign" / "campaign-manifest.json"
        with open(base_manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["workflow_status"]["iteration_count"] = 0
        data["workflow_status"]["current_phase"] = "BRIEF_INGESTION"
        data["workflow_status"]["is_approved"] = False
        with open(test_manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        rel_test_manifest = str(test_manifest_path.relative_to(WORKSPACE_ROOT))

        # 1. Transición válida
        res = subprocess.run([
            "python3", str(script_path),
            "--manifest", rel_test_manifest,
            "transition", "--to", "STRATEGIC_ALIGNMENT"
        ], capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(res.returncode, 0)
        with open(test_manifest_path, "r", encoding="utf-8") as f:
            updated = json.load(f)
        self.assertEqual(updated["workflow_status"]["current_phase"], "STRATEGIC_ALIGNMENT")

        # 2. Transición inválida debe fallar
        res_invalid = subprocess.run([
            "python3", str(script_path),
            "--manifest", rel_test_manifest,
            "transition", "--to", "INVALID_PHASE_NAME"
        ], capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertNotEqual(res_invalid.returncode, 0)

        # 3. Iteración 1
        res_it1 = subprocess.run([
            "python3", str(script_path),
            "--manifest", rel_test_manifest,
            "iterate", "--reason", "Ajuste rítmico en corte de escena 3"
        ], capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(res_it1.returncode, 0)
        with open(test_manifest_path, "r", encoding="utf-8") as f:
            it1_data = json.load(f)
        self.assertEqual(it1_data["workflow_status"]["iteration_count"], 1)
        self.assertEqual(it1_data["workflow_status"]["current_phase"], "ITERATION_ENGINE")

        # 4. Iteración 2
        subprocess.run([
            "python3", str(script_path),
            "--manifest", rel_test_manifest,
            "iterate", "--reason", "Corrección de contraste en color grading"
        ], cwd=str(WORKSPACE_ROOT))
        with open(test_manifest_path, "r", encoding="utf-8") as f:
            it2_data = json.load(f)
        self.assertEqual(it2_data["workflow_status"]["iteration_count"], 2)

        # 5. Iteración 3 (Máximo permitido)
        subprocess.run([
            "python3", str(script_path),
            "--manifest", rel_test_manifest,
            "iterate", "--reason", "Rebalanceo de safe zone para logo"
        ], cwd=str(WORKSPACE_ROOT))
        with open(test_manifest_path, "r", encoding="utf-8") as f:
            it3_data = json.load(f)
        self.assertEqual(it3_data["workflow_status"]["iteration_count"], 3)
        self.assertEqual(it3_data["workflow_status"]["current_phase"], "ITERATION_ENGINE")

        # 6. Iteración 4 (DEBE DETENERSE EN HALT_FOR_USER_REVIEW)
        res_it4 = subprocess.run([
            "python3", str(script_path),
            "--manifest", rel_test_manifest,
            "iterate", "--reason", "Intento de 4ta iteración automática"
        ], capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertIn("[HALT]", res_it4.stdout)
        with open(test_manifest_path, "r", encoding="utf-8") as f:
            it4_data = json.load(f)
        self.assertEqual(it4_data["workflow_status"]["iteration_count"], 3)
        self.assertEqual(it4_data["workflow_status"]["current_phase"], "HALT_FOR_USER_REVIEW")

        # 7. Aprobación
        subprocess.run([
            "python3", str(script_path),
            "--manifest", rel_test_manifest,
            "approve"
        ], cwd=str(WORKSPACE_ROOT))
        with open(test_manifest_path, "r", encoding="utf-8") as f:
            approved_data = json.load(f)
        self.assertTrue(approved_data["workflow_status"]["is_approved"])
        self.assertEqual(approved_data["workflow_status"]["current_phase"], "DELIVERY")

        # Limpiar archivo temporal de prueba
        if test_manifest_path.is_file():
            test_manifest_path.unlink()
        temp_manifest2 = WORKSPACE_ROOT / "campaign" / "test_campaign_manifest.json"
        if temp_manifest2.is_file():
            temp_manifest2.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
