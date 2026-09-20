#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 5: Lyric & Audio Intelligence
Valida la definición de la habilidad, la alineación rítmica y fonética de versos,
la continuidad temporal sin solapamientos ni huecos, la presencia de metraje
en disco y la cobertura de categorías semánticas.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de lyric intelligence a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "lyric-intelligence" / "scripts"))

from align_lyrics import build_lyric_alignment, load_audio_analysis

class TestPhase5LyricIntelligence(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y formato de SKILL.md en lyric-intelligence"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "lyric-intelligence" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: lyric-intelligence", content)
        self.assertIn("RITUAL_START", content)
        self.assertIn("BRAND_CORE", content)
        self.assertIn("lyric-alignment.json", content)

    def test_02_lyric_alignment_file_contract(self):
        """Verifica la validez y contrato formal del archivo campaign/audio/lyric-alignment.json"""
        align_file = WORKSPACE_ROOT / "campaign" / "audio" / "lyric-alignment.json"
        self.assertTrue(align_file.is_file(), "El archivo lyric-alignment.json no existe")

        with open(align_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = [
            "song_title",
            "audio_reference",
            "target_duration_seconds",
            "total_scenes",
            "thematic_arc",
            "thematic_categories_present",
            "alignment"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Clave faltante: {key}")

        self.assertEqual(data["total_scenes"], 9)
        self.assertEqual(len(data["alignment"]), 9)

    def test_03_thematic_categories_completeness(self):
        """Verifica que las categorías semánticas abarquen las dimensiones del brief"""
        align_file = WORKSPACE_ROOT / "campaign" / "audio" / "lyric-alignment.json"
        with open(align_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cats = set(data["thematic_categories_present"])
        expected_cats = {
            "RITUAL_START",
            "SENSORY_CLOSENESS",
            "NATURAL_IDENTITY",
            "COMMUNITY_MOVEMENT",
            "WORK_AND_STUDY",
            "BRAND_CORE"
        }
        self.assertEqual(cats, expected_cats)

    def test_04_temporal_continuity_and_no_gaps(self):
        """Verifica que los segmentos de las 9 escenas sean estrictamente continuos sin huecos ni solapes"""
        align_file = WORKSPACE_ROOT / "campaign" / "audio" / "lyric-alignment.json"
        with open(align_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenes = data["alignment"]
        prev_end = 0.0

        for i, s in enumerate(scenes):
            seg = s["timeline_segment"]
            self.assertAlmostEqual(seg["start"], prev_end, delta=0.01,
                msg=f"Discontinuidad en escena {s['scene_number']}: inicio {seg['start']} != fin previo {prev_end}")
            self.assertGreater(seg["end"], seg["start"], f"Duración no positiva en escena {s['scene_number']}")
            self.assertAlmostEqual(seg["duration"], seg["end"] - seg["start"], delta=0.01)
            prev_end = seg["end"]

        self.assertAlmostEqual(prev_end, data["target_duration_seconds"], delta=0.05)

    def test_05_video_asset_mapping_integrity(self):
        """Verifica que todos los archivos de video asignados a las escenas existan físicamente en Recursos/videos/"""
        align_file = WORKSPACE_ROOT / "campaign" / "audio" / "lyric-alignment.json"
        with open(align_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data["alignment"]:
            v = s["video_asset"]
            self.assertTrue(v["exists_on_disk"], f"El activo asignado no existe: {v['filename']}")
            full_path = WORKSPACE_ROOT / v["relative_path"]
            self.assertTrue(full_path.is_file(), f"Archivo no encontrado en ruta completa: {full_path}")
            self.assertGreater(full_path.stat().st_size, 100000, f"El archivo {v['filename']} parece corrupto o vacío")

    def test_06_word_timings_and_keywords(self):
        """Verifica que cada frase tenga palabras clave y timestamps de palabras ordenados"""
        align_file = WORKSPACE_ROOT / "campaign" / "audio" / "lyric-alignment.json"
        with open(align_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for s in data["alignment"]:
            self.assertGreater(len(s["keywords"]), 0, f"Escena {s['scene_number']} sin keywords")
            words = s["word_timings"]
            self.assertGreater(len(words), 0)
            prev_time = 0.0
            for w in words:
                self.assertIn("word", w)
                self.assertIn("approx_timestamp", w)
                self.assertGreaterEqual(w["approx_timestamp"], prev_time)
                prev_time = w["approx_timestamp"]

    def test_07_cli_execution(self):
        """Verifica la ejecución CLI de align_lyrics.py"""
        cmd = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "lyric-intelligence" / "scripts" / "align_lyrics.py"),
            "--output", "campaign/audio/test_cli_lyric_alignment.json"
        ]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p.returncode, 0, f"Fallo CLI: {p.stderr}")

        test_out = WORKSPACE_ROOT / "campaign" / "audio" / "test_cli_lyric_alignment.json"
        self.assertTrue(test_out.is_file())
        test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
