#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 10: Programmatic Video Engine (Remotion Orchestrator)
Valida la estructura de composición React programática, el manifiesto de composición,
la matriz de variantes parametrizables (A/B testing, bumpers), sincronía de secuencias
y renderizado de fotogramas clave con Remotion CLI.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema
from PIL import Image

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "remotion-orchestrator" / "scripts"))

from remotion_orchestrator import build_composition_data, validate_remotion_manifest

class TestPhase10RemotionOrchestrator(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones de SKILL.md en remotion-orchestrator"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "remotion-orchestrator" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: remotion-orchestrator", content)
        self.assertIn("domain: production", content)
        self.assertIn("Remotion CLI", content)
        self.assertIn("LocosMaterosCommercial", content)
        self.assertIn("remotion-composition-schema.json", content)

    def test_02_schema_contract_and_manifest_validity(self):
        """Valida que campaign/remotion/composition-manifest.json cumpla rigurosamente con config/remotion-composition-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "remotion" / "composition-manifest.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró composition-manifest.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_path = WORKSPACE_ROOT / "config" / "remotion-composition-schema.json"
        self.assertTrue(schema_path.is_file(), "No se encontró remotion-composition-schema.json")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal Draft-07 sin excepciones
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertEqual(data["composition_id"], "LocosMaterosCommercial")
        self.assertEqual(data["format"]["width"], 720)
        self.assertEqual(data["format"]["height"], 1280)
        self.assertEqual(data["format"]["fps"], 24.0)
        self.assertEqual(data["format"]["duration_in_frames"], 700)

    def test_03_react_project_structure(self):
        """Verifica la presencia e integridad de los componentes React de Remotion"""
        remotion_dir = WORKSPACE_ROOT / "campaign" / "remotion"

        for fname in ["index.jsx", "Root.jsx", "Main.jsx", "props.json"]:
            file_path = remotion_dir / fname
            self.assertTrue(file_path.is_file(), f"Falta archivo React: {file_path}")

        root_content = (remotion_dir / "Root.jsx").read_text(encoding="utf-8")
        self.assertIn("LocosMaterosCommercial", root_content)
        self.assertIn("<Composition", root_content)

        main_content = (remotion_dir / "Main.jsx").read_text(encoding="utf-8")
        self.assertIn("Sequence", main_content)
        self.assertIn("useCurrentFrame", main_content)
        self.assertIn("interpolate", main_content)
        self.assertIn("¿Dónde estás tú?", main_content)

    def test_04_parametric_variants_matrix(self):
        """Verifica la matriz de 4 variantes parametrizadas en variants.json"""
        variants_file = WORKSPACE_ROOT / "campaign" / "remotion" / "variants.json"
        self.assertTrue(variants_file.is_file(), "No se encontró variants.json")

        with open(variants_file, "r", encoding="utf-8") as f:
            variants = json.load(f)

        self.assertEqual(len(variants), 4)
        variant_ids = {v["variant_id"] for v in variants}
        expected_ids = {"master_30s_emocional", "variant_publicitaria", "variant_conversacional", "bumper_15s"}
        self.assertEqual(variant_ids, expected_ids)

        for v in variants:
            self.assertIn("name", v)
            self.assertIn("target_audience", v)
            self.assertIn("props_override", v)
            self.assertIn("output_file", v)

    def test_05_scenes_sequence_synchronization(self):
        """Verifica que las 9 escenas estén sincronizadas secuencialmente en frames sin saltos ni huecos"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "remotion" / "composition-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenes = data["scenes"]
        self.assertEqual(len(scenes), 9)

        expected_frame = 0
        for sc in scenes:
            self.assertEqual(sc["start_frame"], expected_frame,
                msg=f"Discontinuidad en {sc['scene_id']}: {sc['start_frame']} != esperado {expected_frame}")
            self.assertGreater(sc["duration_frames"], 0)
            expected_frame += sc["duration_frames"]

        self.assertEqual(expected_frame, data["format"]["duration_in_frames"])

    def test_06_rendered_still_frame_specs(self):
        """Verifica que el fotograma clave renderizado exista con resolución 720x1280"""
        still_file = WORKSPACE_ROOT / "campaign" / "remotion" / "renders" / "still_frame_650.png"
        self.assertTrue(still_file.is_file(), f"Falta fotograma renderizado: {still_file}")

        with Image.open(still_file) as img:
            self.assertEqual(img.size, (720, 1280))
            self.assertIn(img.mode, ["RGB", "RGBA"])

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI y el flag --validate-only"""
        cmd_gen = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "remotion-orchestrator" / "scripts" / "remotion_orchestrator.py"),
            "--output", "campaign/remotion/test_cli_manifest.json"
        ]
        p_gen = subprocess.run(cmd_gen, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_gen.returncode, 0, f"CLI error: {p_gen.stderr}")

        cmd_val = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "remotion-orchestrator" / "scripts" / "remotion_orchestrator.py"),
            "--output", "campaign/remotion/test_cli_manifest.json",
            "--validate-only"
        ]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_val.returncode, 0)
        self.assertIn("[VALID]", p_val.stdout)

        test_out = WORKSPACE_ROOT / "campaign" / "remotion" / "test_cli_manifest.json"
        if test_out.is_file():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
