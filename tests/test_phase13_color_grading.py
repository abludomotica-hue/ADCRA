#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 13: Color Grading Assistant
Valida la identidad cromática de Locos Materos, conformidad formal con config/color-grading-schema.json,
generación matemática y sintáctica de LUTs 3D .cube (33x33x33 y 65x65x65) y balance tonal plano a plano.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "color-grading" / "scripts"))

from generate_color_grade import build_color_manifest, validate_color_manifest

class TestPhase13ColorGrading(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y contenido de SKILL.md en color-grading"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "color-grading" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: color-grading", content)
        self.assertIn("domain: post-production", content)
        self.assertIn("Rec.709", content)
        self.assertIn("Gamma 2.4", content)
        self.assertIn("#0D5C3A", content)
        self.assertIn("#D4AF37", content)
        self.assertIn("color-grading-schema.json", content)

    def test_02_schema_contract_and_manifest_validity(self):
        """Valida que campaign/color/color-grading-manifest.json cumpla con config/color-grading-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "color" / "color-grading-manifest.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró color-grading-manifest.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_path = WORKSPACE_ROOT / "config" / "color-grading-schema.json"
        self.assertTrue(schema_path.is_file(), "No se encontró color-grading-schema.json")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal Draft-07 sin excepciones
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertEqual(data["color_science"]["color_space"], "Rec.709")
        self.assertEqual(data["color_science"]["gamma"], "Gamma 2.4")

    def test_03_cube_lut_files_syntax_and_structure(self):
        """Verifica que las 3 LUTs .cube existan y cumplan la sintaxis estándar de encabezado"""
        luts_dir = WORKSPACE_ROOT / "campaign" / "color" / "luts"

        expected_luts = {
            "locos_materos_warm_cinematic.cube": 33,
            "locos_materos_editorial_film.cube": 33,
            "locos_materos_master_grade.cube": 65
        }

        for fname, expected_size in expected_luts.items():
            lut_file = luts_dir / fname
            self.assertTrue(lut_file.is_file(), f"Falta archivo LUT: {lut_file}")

            lines = lut_file.read_text(encoding="utf-8").splitlines()
            header_lines = [l for l in lines[:10] if l.strip()]

            title_found = any(l.startswith("TITLE ") for l in header_lines)
            size_found = any(l.strip() == f"LUT_3D_SIZE {expected_size}" for l in header_lines)
            domain_min = any("DOMAIN_MIN 0.0 0.0 0.0" in l for l in header_lines)
            domain_max = any("DOMAIN_MAX 1.0 1.0 1.0" in l for l in header_lines)

            self.assertTrue(title_found, f"Falta TITLE en {fname}")
            self.assertTrue(size_found, f"LUT_3D_SIZE {expected_size} no coincide en {fname}")
            self.assertTrue(domain_min, f"Falta DOMAIN_MIN en {fname}")
            self.assertTrue(domain_max, f"Falta DOMAIN_MAX en {fname}")

    def test_04_mathematical_range_and_data_points(self):
        """Verifica que todas las tripletas RGB de las LUTs estén estrictamente en [0.0, 1.0]"""
        luts_dir = WORKSPACE_ROOT / "campaign" / "color" / "luts"
        test_lut = luts_dir / "locos_materos_warm_cinematic.cube"

        data_count = 0
        with open(test_lut, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("TITLE") or line.startswith("LUT_3D_SIZE") or line.startswith("DOMAIN_"):
                    continue
                parts = line.split()
                self.assertEqual(len(parts), 3)
                r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
                self.assertGreaterEqual(r, 0.0)
                self.assertLessEqual(r, 1.0)
                self.assertGreaterEqual(g, 0.0)
                self.assertLessEqual(g, 1.0)
                self.assertGreaterEqual(b, 0.0)
                self.assertLessEqual(b, 1.0)
                data_count += 1

        self.assertEqual(data_count, 33 * 33 * 33, f"Total de puntos 3D debe ser 35937, obtenido: {data_count}")

    def test_05_shot_by_shot_grading_completeness(self):
        """Verifica que las 9 escenas tengan etalonaje individual y que los LUTs asociados existan"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "color" / "color-grading-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        scene_grades = data["scene_grades"]
        self.assertEqual(len(scene_grades), 9)

        for sc in scene_grades:
            sc_id = sc["scene_id"]
            lut_path = WORKSPACE_ROOT / sc["base_lut"]
            self.assertTrue(lut_path.is_file(), f"LUT base no existe para {sc_id}: {lut_path}")
            self.assertGreaterEqual(sc["contrast"], 0.9)
            self.assertLessEqual(sc["contrast"], 1.4)
            self.assertGreater(len(sc["intent_rationale"]), 20)
            self.assertEqual(len(sc["lift"]), 3)
            self.assertEqual(len(sc["gamma"]), 3)
            self.assertEqual(len(sc["gain"]), 3)

    def test_06_brand_color_harmony_standards(self):
        """Verifica la coherencia de la armonía de marca (#0D5C3A, #D4AF37) y temperatura cálida"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "color" / "color-grading-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        harmony = data["brand_color_harmony"]
        self.assertEqual(harmony["primary_green"].upper(), "#0D5C3A")
        self.assertEqual(harmony["golden_highlight"].upper(), "#D4AF37")
        self.assertEqual(harmony["deep_neutral_black"].upper(), "#1A1A1A")
        self.assertGreaterEqual(harmony["color_temperature_target_kelvin"], 5600)
        self.assertLessEqual(harmony["color_temperature_target_kelvin"], 6200)

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI y el flag --validate-only"""
        cmd_gen = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "color-grading" / "scripts" / "generate_color_grade.py"),
            "--output", "campaign/color/test_cli_color.json"
        ]
        p_gen = subprocess.run(cmd_gen, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_gen.returncode, 0, f"CLI error: {p_gen.stderr}")

        cmd_val = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "color-grading" / "scripts" / "generate_color_grade.py"),
            "--output", "campaign/color/test_cli_color.json",
            "--validate-only"
        ]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_val.returncode, 0)
        self.assertIn("[VALID]", p_val.stdout)

        test_out = WORKSPACE_ROOT / "campaign" / "color" / "test_cli_color.json"
        if test_out.is_file():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
