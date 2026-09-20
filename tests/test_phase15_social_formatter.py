#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 15: Social Media Formatter
Valida la especificación técnica de plataformas sociales (TikTok, Reels, Shorts, Feed 1:1, 16:9),
conformidad formal con config/social-formatter-schema.json, cálculo de Safe Zones móviles,
generación física de guías visuales PNG semitransparentes y comandos FFmpeg de adaptación multi-ratio.
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

# Agregar script de social-formatter a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "social-formatter" / "scripts"))

from format_social_deliverables import build_social_manifest, validate_social_manifest

class TestPhase15SocialFormatter(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de social-formatter"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "social-formatter" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: social-formatter", content)
        self.assertIn("domain: production", content)
        self.assertIn("TikTok", content)
        self.assertIn("Instagram Reels", content)
        self.assertIn("YouTube Shorts", content)
        self.assertIn("Safe Zones", content)
        self.assertIn("#0D5C3A", content)
        self.assertIn("social-formatter-schema.json", content)

    def test_02_schema_contract_and_manifest_validity(self):
        """Valida que campaign/deliverables/social-format-manifest.json cumpla con config/social-formatter-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "social-format-manifest.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró social-format-manifest.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "social-formatter-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/social-formatter-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data.get("campaign_id"), "camp_locos_materos_2026")
        self.assertEqual(data["master_format"]["aspect_ratio"], "9:16")

    def test_03_platform_presets_and_ratios(self):
        """Verifica los perfiles de plataforma y resoluciones estándar móviles y widescreen"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "social-format-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        platforms = {p["platform_id"]: p for p in data["platforms"]}
        self.assertGreaterEqual(len(platforms), 5)
        self.assertIn("tiktok_9_16", platforms)
        self.assertIn("instagram_reels_9_16", platforms)
        self.assertIn("youtube_shorts_9_16", platforms)
        self.assertIn("meta_feed_1_1", platforms)
        self.assertIn("youtube_widescreen_16_9", platforms)

        # Verificar dimensiones
        self.assertEqual(platforms["tiktok_9_16"]["target_resolution"], {"width": 720, "height": 1280})
        self.assertEqual(platforms["meta_feed_1_1"]["target_resolution"], {"width": 1080, "height": 1080})
        self.assertEqual(platforms["youtube_widescreen_16_9"]["target_resolution"], {"width": 1920, "height": 1080})

    def test_04_safe_zones_margins_and_ui_protection(self):
        """Verifica que las Safe Zones y zonas de oclusión UI eviten la superposición de controles nativos"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "social-format-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for platform in data["platforms"]:
            safe = platform["safe_zone"]
            self.assertGreaterEqual(safe["top_px"], 50)
            self.assertGreaterEqual(safe["bottom_px"], 50)
            self.assertGreaterEqual(safe["left_px"], 40)
            self.assertGreaterEqual(safe["right_px"], 50)

            # Verificar bounding boxes de oclusiones UI
            for zone in platform.get("ui_occlusion_zones", []):
                bb = zone["bounding_box"]
                self.assertGreaterEqual(bb["x"], 0)
                self.assertGreaterEqual(bb["y"], 0)
                self.assertGreater(bb["width"], 0)
                self.assertGreater(bb["height"], 0)

    def test_05_overlay_guides_generated_and_valid(self):
        """Verifica que las guías visuales PNG semitransparentes existan y tengan canales RGBA válidos"""
        guides_dir = WORKSPACE_ROOT / "campaign" / "deliverables" / "guides"
        self.assertTrue(guides_dir.is_dir(), f"No existe {guides_dir}")

        expected_guides = [
            ("tiktok_9_16_safe_zone.png", (720, 1280)),
            ("instagram_reels_9_16_safe_zone.png", (720, 1280)),
            ("youtube_shorts_9_16_safe_zone.png", (720, 1280)),
            ("meta_feed_1_1_safe_zone.png", (1080, 1080)),
            ("youtube_widescreen_16_9_safe_zone.png", (1920, 1080)),
        ]

        for filename, (expected_w, expected_h) in expected_guides:
            guide_file = guides_dir / filename
            self.assertTrue(guide_file.is_file(), f"Falta guía visual: {guide_file}")
            self.assertGreater(guide_file.stat().st_size, 5000, f"Guía corrupta o vacía: {guide_file}")

            # Abrir con PIL y verificar modo RGBA y resolución
            with Image.open(guide_file) as im:
                self.assertEqual(im.size, (expected_w, expected_h))
                self.assertEqual(im.mode, "RGBA")

    def test_06_adaptation_strategies_and_ffmpeg_commands(self):
        """Verifica las estrategias de adaptación de ratios y comandos FFmpeg asociados"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "social-format-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        strategies = data["adaptation_strategies"]
        self.assertEqual(strategies["square_1_1"]["brand_fill_color"], "#0D5C3A")
        self.assertIn("blurred_background", strategies["widescreen_16_9"]["method"])

        deliverables = data["deliverables"]
        self.assertGreaterEqual(len(deliverables), 5)
        for d in deliverables:
            self.assertTrue(d["deliverable_id"].startswith("deliv_"))
            self.assertIn("ffmpeg -y -i", d["ffmpeg_command"])
            self.assertIn("libx264", d["ffmpeg_command"])
            self.assertTrue(d["guide_overlay_path"].endswith(".png"))

    def test_07_cli_execution_and_validate_only(self):
        """Verifica que el script CLI pueda ejecutarse con flag --validate-only"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "social-formatter" / "scripts" / "format_social_deliverables.py"
        cmd = [sys.executable, str(script_path), "--validate-only"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"Fallo CLI validate-only: {p.stderr}")
        self.assertIn("cumple 100% con config/social-formatter-schema.json", p.stdout)

if __name__ == "__main__":
    unittest.main()
