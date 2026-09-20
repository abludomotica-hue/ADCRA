#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 9: Motion Graphics Designer (HyperFrames Orchestrator)
Valida la generación de templates HTML5/CSS3 con cinética tipográfica,
conformidad estricta con config/motion-graphics-schema.json, verificación de safe zones,
paleta de marca oficial de Locos Materos y especificaciones de render RGBA 9:16.
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
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "hyperframes-orchestrator" / "scripts"))

from generate_motion_graphics import generate_motion_manifest, validate_motion_manifest

class TestPhase9MotionGraphics(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones en SKILL.md de hyperframes-orchestrator"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "hyperframes-orchestrator" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: hyperframes-orchestrator", content)
        self.assertIn("domain: production", content)
        self.assertIn("#0D5C3A", content)
        self.assertIn("#D4AF37", content)
        self.assertIn("fade_in_word_by_word", content)
        self.assertIn("hero_packshot_reveal", content)
        self.assertIn("motion-graphics-schema.json", content)

    def test_02_schema_contract_and_manifest_validity(self):
        """Valida que campaign/motion-graphics/motion-manifest.json cumpla con config/motion-graphics-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "motion-manifest.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró motion-manifest.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_path = WORKSPACE_ROOT / "config" / "motion-graphics-schema.json"
        self.assertTrue(schema_path.is_file(), "No se encontró motion-graphics-schema.json")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal Draft-07 sin excepciones
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertEqual(data["format"]["aspect_ratio"], "9:16")
        self.assertEqual(data["format"]["width"], 720)
        self.assertEqual(data["format"]["height"], 1280)
        self.assertEqual(data["format"]["fps"], 24.0)

    def test_03_all_scenes_have_overlays_and_timing(self):
        """Verifica que las 9 escenas tengan overlay asignado y correspondencia temporal con storyboard"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "motion-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        overlays = data["overlays"]
        self.assertEqual(len(overlays), 9)

        sb_path = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
        with open(sb_path, "r", encoding="utf-8") as f:
            sb_data = json.load(f)

        sb_scenes = {s["scene_id"]: s for s in sb_data["scenes"]}

        for ov in overlays:
            sc_id = ov["scene_id"]
            self.assertIn(sc_id, sb_scenes)
            self.assertAlmostEqual(ov["start_seconds"], sb_scenes[sc_id]["start"], delta=0.01)
            self.assertAlmostEqual(ov["end_seconds"], sb_scenes[sc_id]["end"], delta=0.01)
            self.assertTrue(len(ov["text_content"]) > 0)
            self.assertEqual(ov["render_status"], "rendered")

    def test_04_brand_palette_and_safe_zones(self):
        """Verifica la fidelidad de la paleta de marca y dimensiones de safe zone"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "motion-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        palette = data["brand_palette"]
        self.assertEqual(palette["primary"].upper(), "#0D5C3A")
        self.assertEqual(palette["accent"].upper(), "#D4AF37")
        self.assertEqual(palette["text_light"].upper(), "#FFFFFF")

        sz = data["safe_zones"]
        self.assertEqual(sz["top_px"], 120)
        self.assertEqual(sz["bottom_px"], 200)
        self.assertEqual(sz["left_px"], 40)
        self.assertEqual(sz["right_px"], 40)

    def test_05_html_templates_exist_and_markup(self):
        """Verifica que los 9 templates HTML existan en disco y contengan marcado válido y keyframes"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "motion-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for ov in data["overlays"]:
            tmpl_path = WORKSPACE_ROOT / ov["html_template_path"]
            self.assertTrue(tmpl_path.is_file(), f"Falta template: {tmpl_path}")

            content = tmpl_path.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("@keyframes", content)
            self.assertIn("720px", content)
            self.assertIn("1280px", content)

        # Verificar escena 9 hero packshot con logo
        scene_9_tmpl = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "templates" / "scene_09.html"
        content_9 = scene_9_tmpl.read_text(encoding="utf-8")
        self.assertIn("data:image/jpeg;base64,", content_9)
        self.assertIn("¿Dónde estás tú?", content_9)
        self.assertIn("www.locosmateros.cl", content_9)

    def test_06_rendered_png_assets_specs(self):
        """Verifica que los 9 overlays PNG renderizados existan y tengan dimensiones exactas 720x1280 RGBA"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "motion-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for ov in data["overlays"]:
            png_path = WORKSPACE_ROOT / ov["output_asset_path"]
            self.assertTrue(png_path.is_file(), f"Falta render PNG: {png_path}")

            with Image.open(png_path) as img:
                self.assertEqual(img.size, (720, 1280), f"Dimensiones erróneas en {png_path}: {img.size}")
                self.assertEqual(img.mode, "RGBA", f"Modo no es RGBA en {png_path}: {img.mode}")

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI con --no-render y el flag --validate-only"""
        cmd_gen = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "hyperframes-orchestrator" / "scripts" / "generate_motion_graphics.py"),
            "--output", "campaign/motion-graphics/test_cli_manifest.json",
            "--no-render"
        ]
        p_gen = subprocess.run(cmd_gen, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_gen.returncode, 0, f"CLI error: {p_gen.stderr}")

        cmd_val = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "hyperframes-orchestrator" / "scripts" / "generate_motion_graphics.py"),
            "--output", "campaign/motion-graphics/test_cli_manifest.json",
            "--validate-only"
        ]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_val.returncode, 0)
        self.assertIn("[VALID]", p_val.stdout)

        test_out = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "test_cli_manifest.json"
        if test_out.is_file():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
