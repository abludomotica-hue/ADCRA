#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 7: Creative Director & Storyteller
Valida la generación del storyboard publicitario escena por escena,
la conformidad estricta con config/storyboard-schema.json, la continuidad temporal,
la presencia obligatoria de rationale estratégico y la progresión de visibilidad de marca.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de storyboard engine a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "storyboard-engine" / "scripts"))

from build_storyboard import generate_storyboard, validate_storyboard

class TestPhase7StoryboardEngine(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y formato de SKILL.md en storyboard-engine"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "storyboard-engine" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: storyboard-engine", content)
        self.assertIn("rationale", content)
        self.assertIn("storyboard-schema.json", content)

    def test_02_storyboard_file_contract_and_schema(self):
        """Valida que campaign/storyboard/storyboard.json cumpla rigurosamente con config/storyboard-schema.json"""
        sb_file = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
        self.assertTrue(sb_file.is_file(), "No se encontró el archivo storyboard.json")

        with open(sb_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_path = WORKSPACE_ROOT / "config" / "storyboard-schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07 sin excepciones
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertEqual(data["target_fps"], 24.0)
        self.assertAlmostEqual(data["total_duration_seconds"], 29.187, delta=0.01)

    def test_03_scene_count_and_continuity(self):
        """Verifica que existan exactamente 9 escenas contiguas sin huecos temporales"""
        sb_file = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
        with open(sb_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenes = data["scenes"]
        self.assertEqual(len(scenes), 9)

        prev_end = 0.0
        for s in scenes:
            self.assertAlmostEqual(s["start"], prev_end, delta=0.01,
                msg=f"Discontinuidad en {s['scene_id']}: inicio {s['start']} != fin previo {prev_end}")
            self.assertGreater(s["end"], s["start"])
            self.assertAlmostEqual(s["duration"], s["end"] - s["start"], delta=0.01)
            prev_end = s["end"]

        self.assertAlmostEqual(prev_end, data["total_duration_seconds"], delta=0.01)

    def test_04_mandatory_rationale_per_scene(self):
        """Verifica que cada una de las 9 escenas posea justificación estratégica profunda"""
        sb_file = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
        with open(sb_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data["scenes"]:
            self.assertIn("rationale", s, f"Falta rationale en {s['scene_id']}")
            rationale = s["rationale"].strip()
            self.assertGreater(len(rationale), 40, f"Rationale demasiado breve en {s['scene_id']}: '{rationale}'")

    def test_05_brand_visibility_progression(self):
        """Verifica la progresión lógica de visibilidad de marca (cierre en hero_packshot)"""
        sb_file = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
        with open(sb_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenes = data["scenes"]
        first_scene = scenes[0]
        last_scene = scenes[-1]

        self.assertIn(first_scene["brand_visibility"], ["subtle", "none"])
        self.assertEqual(last_scene["brand_visibility"], "hero_packshot", "La última escena debe ser hero_packshot")

    def test_06_tool_assignment_validity(self):
        """Verifica que el motor asignado a cada escena sea una herramienta autorizada"""
        sb_file = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
        with open(sb_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data["scenes"]:
            self.assertEqual(s["tool"], "DaVinci Resolve")

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI y el flag --validate-only"""
        cmd_build = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "storyboard-engine" / "scripts" / "build_storyboard.py"),
            "--output", "campaign/storyboard/test_cli_storyboard.json"
        ]
        p_build = subprocess.run(cmd_build, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_build.returncode, 0)

        cmd_val = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "storyboard-engine" / "scripts" / "build_storyboard.py"),
            "--output", "campaign/storyboard/test_cli_storyboard.json",
            "--validate-only"
        ]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_val.returncode, 0)
        self.assertIn("[VALID]", p_val.stdout)

        test_out = WORKSPACE_ROOT / "campaign" / "storyboard" / "test_cli_storyboard.json"
        if test_out.is_file():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
