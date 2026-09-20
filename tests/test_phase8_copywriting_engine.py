#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 8: Copywriting Engine
Valida la generación obligatoria de 5 variantes de copy por escena,
la conformidad estricta con config/creative-copy-schema.json, métricas cuantitativas,
la justificación estratégica de selección y el hilo narrativo unificado.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de copy engine a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "creative-copy-engine" / "scripts"))

from generate_copy import generate_creative_copy, validate_creative_copy

class TestPhase8CopywritingEngine(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y contenido de SKILL.md en creative-copy-engine"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "creative-copy-engine" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: creative-copy-engine", content)
        self.assertIn("emocional", content)
        self.assertIn("publicitaria", content)
        self.assertIn("conversacional", content)
        self.assertIn("minimalista", content)
        self.assertIn("identidad_de_marca", content)
        self.assertIn("creative-copy-schema.json", content)

    def test_02_copy_file_contract_and_schema(self):
        """Valida que campaign/creative/creative-copy.json cumpla rigurosamente con config/creative-copy-schema.json"""
        copy_file = WORKSPACE_ROOT / "campaign" / "creative" / "creative-copy.json"
        self.assertTrue(copy_file.is_file(), "No se encontró el archivo creative-copy.json")

        with open(copy_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_path = WORKSPACE_ROOT / "config" / "creative-copy-schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07 sin excepciones
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertTrue(len(data["overall_narrative_thread"]) > 20)

    def test_03_all_scenes_have_five_mandatory_variants(self):
        """Verifica que las 9 escenas posean exactamente las 5 variantes requeridas"""
        copy_file = WORKSPACE_ROOT / "campaign" / "creative" / "creative-copy.json"
        with open(copy_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenes = data["scene_copies"]
        self.assertEqual(len(scenes), 9)

        mandatory_variants = {"emocional", "publicitaria", "conversacional", "minimalista", "identidad_de_marca"}

        for s in scenes:
            scene_id = s["scene_id"]
            alts = s["alternatives"]
            self.assertEqual(set(alts.keys()), mandatory_variants, f"Variantes incompletas en {scene_id}")
            for v_name, v_data in alts.items():
                self.assertIn("text", v_data, f"Falta text en {scene_id} -> {v_name}")
                self.assertTrue(len(v_data["text"].strip()) > 0)

    def test_04_quantitative_metrics_and_ranges(self):
        """Verifica que las métricas cuantitativas estén presentes y dentro de sus rangos válidos"""
        copy_file = WORKSPACE_ROOT / "campaign" / "creative" / "creative-copy.json"
        with open(copy_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data["scene_copies"]:
            alts = s["alternatives"]
            # Emocional (emotional_impact_score 0-10)
            self.assertGreaterEqual(alts["emocional"]["emotional_impact_score"], 0.0)
            self.assertLessEqual(alts["emocional"]["emotional_impact_score"], 10.0)
            # Publicitaria (call_to_action_score 0-10)
            self.assertGreaterEqual(alts["publicitaria"]["call_to_action_score"], 0.0)
            self.assertLessEqual(alts["publicitaria"]["call_to_action_score"], 10.0)
            # Conversacional (naturalness_score 0-10)
            self.assertGreaterEqual(alts["conversacional"]["naturalness_score"], 0.0)
            self.assertLessEqual(alts["conversacional"]["naturalness_score"], 10.0)
            # Minimalista (word_count >= 1)
            self.assertGreaterEqual(alts["minimalista"]["word_count"], 1)
            # Identidad de marca (brand_alignment_score 0-10)
            self.assertGreaterEqual(alts["identidad_de_marca"]["brand_alignment_score"], 0.0)
            self.assertLessEqual(alts["identidad_de_marca"]["brand_alignment_score"], 10.0)

    def test_05_selection_and_rationale_depth(self):
        """Verifica que la variante seleccionada coincida con una alternativa y tenga rationale profundo"""
        copy_file = WORKSPACE_ROOT / "campaign" / "creative" / "creative-copy.json"
        with open(copy_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        valid_variants = {"emocional", "publicitaria", "conversacional", "minimalista", "identidad_de_marca"}

        for s in data["scene_copies"]:
            scene_id = s["scene_id"]
            selected_var = s["selected_variant"]
            self.assertIn(selected_var, valid_variants, f"Variante seleccionada no válida en {scene_id}")

            # Coincidencia con el texto de la variante
            expected_text = s["alternatives"][selected_var]["text"]
            self.assertEqual(s["selected_text"], expected_text, f"Texto no coincide en {scene_id}")

            # Rationale profundo
            self.assertIn("selection_rationale", s)
            rationale = s["selection_rationale"].strip()
            self.assertGreater(len(rationale), 30, f"Rationale insuficiente en {scene_id}: '{rationale}'")

    def test_06_context_inputs_presence(self):
        """Verifica que los inputs contextuales requeridos estén completos por escena"""
        copy_file = WORKSPACE_ROOT / "campaign" / "creative" / "creative-copy.json"
        with open(copy_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_ctx = ["visual_description", "music_cue", "lyric_reference", "emotion_target", "objective", "brand_tone"]
        for s in data["scene_copies"]:
            ctx = s["context_inputs"]
            for field in required_ctx:
                self.assertIn(field, ctx, f"Falta contexto '{field}' en {s['scene_id']}")
                self.assertTrue(len(ctx[field].strip()) > 0)

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI y el flag --validate-only"""
        cmd_gen = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "creative-copy-engine" / "scripts" / "generate_copy.py"),
            "--output", "campaign/creative/test_cli_copy.json"
        ]
        p_gen = subprocess.run(cmd_gen, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_gen.returncode, 0, f"CLI error: {p_gen.stderr}")

        cmd_val = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "creative" / "creative-copy-engine" / "scripts" / "generate_copy.py"),
            "--output", "campaign/creative/test_cli_copy.json",
            "--validate-only"
        ]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_val.returncode, 0)
        self.assertIn("[VALID]", p_val.stdout)

        test_out = WORKSPACE_ROOT / "campaign" / "creative" / "test_cli_copy.json"
        if test_out.is_file():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
