#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 6: Video & Footage Analysis
Valida la definición de la habilidad, la inspección técnica de streams de video
mediante ffprobe, la clasificación cinematográfica (plano, iluminación, movimiento,
presencia de mate) y el catálogo de imágenes y audios.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de video analysis a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "video-analysis" / "scripts"))

from analyze_footage import build_asset_inventory, probe_video_file

class TestPhase6VideoAnalysis(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y formato de SKILL.md en video-analysis"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "video-analysis" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: video-analysis", content)
        self.assertIn("shot_type", content)
        self.assertIn("macro_detail", content)
        self.assertIn("golden_hour_morning", content)

    def test_02_asset_inventory_contract(self):
        """Verifica la existencia y estructura del archivo campaign/assets/asset-inventory.json"""
        inv_file = WORKSPACE_ROOT / "campaign" / "assets" / "asset-inventory.json"
        self.assertTrue(inv_file.is_file(), "No existe el inventario de activos")

        with open(inv_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = ["summary", "video_assets", "image_assets", "audio_assets"]
        for key in required_keys:
            self.assertIn(key, data, f"Clave faltante: {key}")

        summary = data["summary"]
        self.assertEqual(summary["total_video_assets"], 9)
        self.assertEqual(summary["native_video_fps"], 24.0)
        self.assertIn("9:16", summary["native_video_aspect_ratio"])
        self.assertEqual(summary["total_image_assets"], 6)
        self.assertEqual(summary["total_audio_assets"], 1)

    def test_03_video_technical_metrics(self):
        """Verifica los parámetros técnicos exactos de los 9 clips de video"""
        inv_file = WORKSPACE_ROOT / "campaign" / "assets" / "asset-inventory.json"
        with open(inv_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data["video_assets"]), 9)
        for v in data["video_assets"]:
            ts = v["technical_specs"]
            self.assertEqual(ts["width"], 720, f"Ancho incorrecto en {v['filename']}")
            self.assertEqual(ts["height"], 1280, f"Alto incorrecto en {v['filename']}")
            self.assertEqual(ts["aspect_ratio"], "9:16")
            self.assertEqual(ts["fps"], 24.0)
            self.assertEqual(ts["codec"], "h264")
            self.assertGreater(ts["duration_seconds"], 5.0)
            self.assertGreater(ts["file_size_bytes"], 1000000)

    def test_04_cinematographic_classification_coverage(self):
        """Verifica que las categorías de cinematografía e intención estén completas"""
        inv_file = WORKSPACE_ROOT / "campaign" / "assets" / "asset-inventory.json"
        with open(inv_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        shot_types = set()
        lighting_types = set()
        movements = set()
        mate_visible_count = 0

        for v in data["video_assets"]:
            c = v["cinematography"]
            shot_types.add(c["shot_type"])
            lighting_types.add(c["lighting"])
            movements.add(c["camera_movement"])
            if c["mate_visible"]:
                mate_visible_count += 1
            self.assertGreater(len(c["primary_subjects"]), 1)
            self.assertGreater(len(c["emotion_evoked"]), 5)

        # Verificar diversidad requerida por el brief
        self.assertIn("macro_detail", shot_types)
        self.assertIn("wide_establishing", shot_types)
        self.assertIn("medium_shot", shot_types)
        self.assertIn("group_shot", shot_types)
        self.assertIn("close_up", shot_types)

        self.assertIn("golden_hour_morning", lighting_types)
        self.assertIn("warm_natural_window", lighting_types)

        # En 8 de las 9 escenas el mate está presente (excepto la Cordillera paisajística)
        self.assertEqual(mate_visible_count, 8)

    def test_05_image_assets_catalog(self):
        """Verifica la catalogación de imágenes de marca y logotipos"""
        inv_file = WORKSPACE_ROOT / "campaign" / "assets" / "asset-inventory.json"
        with open(inv_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        imgs = data["image_assets"]
        self.assertEqual(len(imgs), 6)

        usages = {img["intended_usage"] for img in imgs}
        self.assertIn("brand_logo", usages)
        self.assertIn("editorial_lifestyle_reference", usages)

    def test_06_cli_execution(self):
        """Verifica la ejecución CLI de analyze_footage.py"""
        cmd = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "video-analysis" / "scripts" / "analyze_footage.py"),
            "--output", "campaign/assets/test_cli_asset_inventory.json"
        ]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p.returncode, 0, f"Fallo CLI: {p.stderr}")

        test_out = WORKSPACE_ROOT / "campaign" / "assets" / "test_cli_asset_inventory.json"
        self.assertTrue(test_out.is_file())
        test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
