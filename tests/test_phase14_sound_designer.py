#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 14: Sound Designer & Fairlight
Valida la arquitectura de diseño sonoro, mezcla y masterización EBU R128,
conformidad formal con config/sound-design-schema.json, foley procedural para 9 escenas,
ducking adaptativo, tracks de Fairlight y generación física de audio master (WAV 24b/48k y MP3 320k).
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de sound designer a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "sound-designer" / "scripts"))

from design_sound import build_audio_master, validate_sound_manifest

class TestPhase14SoundDesigner(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de sound-designer"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "sound-designer" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: sound-designer", content)
        self.assertIn("domain: post-production", content)
        self.assertIn("EBU R128", content)
        self.assertIn("-14.0 LUFS", content)
        self.assertIn("-1.0 dBTP", content)
        self.assertIn("Fairlight", content)
        self.assertIn("sound-design-schema.json", content)

    def test_02_schema_contract_and_manifest_validity(self):
        """Valida que campaign/audio/sound-design-manifest.json cumpla con config/sound-design-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "audio" / "sound-design-manifest.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró sound-design-manifest.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "sound-design-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/sound-design-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data.get("campaign_id"), "camp_locos_materos_2026")

    def test_03_loudness_compliance_standards(self):
        """Verifica la conformidad estricta con estándares de sonoridad EBU R128 (-14 LUFS, -1 dBTP)"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "audio" / "sound-design-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        loudness = data["loudness_compliance"]
        self.assertIn("EBU R128", loudness["standard"])
        self.assertEqual(loudness["target_integrated_lufs"], -14.0)
        self.assertEqual(loudness["target_true_peak_dbtp"], -1.0)

        # Tolerancia streaming permitida (-14.0 +/- 2.0 LUFS)
        self.assertGreaterEqual(loudness["measured_integrated_lufs"], -16.0)
        self.assertLessEqual(loudness["measured_integrated_lufs"], -12.0)

        # True Peak ceiling no debe exceder -0.9 dBTP para prevenir clipping inter-sample
        self.assertLessEqual(loudness["measured_true_peak_dbtp"], -0.9)
        self.assertGreater(loudness["loudness_range_lu"], 0.0)

    def test_04_audio_format_and_foley_cues_structure(self):
        """Verifica el formato de audio broadcast y los 9 eventos foley sincronizados"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "audio" / "sound-design-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        audio_format = data["audio_format"]
        self.assertEqual(audio_format["sample_rate_hz"], 48000)
        self.assertEqual(audio_format["bit_depth"], 24)
        self.assertEqual(audio_format["channels"], 2)
        self.assertAlmostEqual(audio_format["duration_seconds"], 29.167, places=1)

        foley_track = data["tracks"]["sfx_foley_track"]
        self.assertEqual(foley_track["total_cues"], 9)
        self.assertEqual(len(foley_track["cues"]), 9)

        for i, cue in enumerate(foley_track["cues"], 1):
            self.assertTrue(cue["cue_id"].startswith(f"cue_{i:02d}"))
            self.assertEqual(cue["scene_id"], f"scene_{i:02d}")
            self.assertIn("name", cue)
            self.assertGreater(cue["duration_seconds"], 0)
            self.assertLess(cue["gain_db"], 0)
            self.assertLess(cue["ducking_trigger_db"], 0)
            self.assertTrue(len(cue["description"]) > 5)

    def test_05_master_audio_files_exist_and_valid(self):
        """Verifica que los archivos master WAV y MP3 existan físicamente con formato válido"""
        wav_file = WORKSPACE_ROOT / "campaign" / "audio" / "locos_materos_master_mix.wav"
        mp3_file = WORKSPACE_ROOT / "campaign" / "audio" / "locos_materos_master_mix.mp3"

        self.assertTrue(wav_file.is_file(), f"Falta {wav_file}")
        self.assertTrue(mp3_file.is_file(), f"Falta {mp3_file}")

        # Verificar peso físico (> 1 MB para WAV de 29s a 24-bit 48kHz estéreo)
        wav_size = wav_file.stat().st_size
        self.assertGreater(wav_size, 1024 * 1024, f"WAV master muy pequeño: {wav_size} bytes")

        # Verificar peso MP3 (> 500 KB a 320 kbps)
        mp3_size = mp3_file.stat().st_size
        self.assertGreater(mp3_size, 500 * 1024, f"MP3 master muy pequeño: {mp3_size} bytes")

        # Verificar ffprobe de audio master
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,channels",
            "-of", "json",
            str(wav_file)
        ]
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        info = json.loads(p.stdout)
        stream = info["streams"][0]
        self.assertEqual(int(stream["sample_rate"]), 48000)
        self.assertEqual(int(stream["channels"]), 2)

    def test_06_fairlight_track_layout_and_ducking(self):
        """Verifica la configuración de pistas de audio, ducking adaptativo y outputs"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "audio" / "sound-design-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        bgm = data["tracks"]["bgm_track"]
        self.assertEqual(bgm["ducking_events_count"], 9)
        self.assertEqual(bgm["base_level_db"], -1.5)
        self.assertIn("Entre_mates_y_sol.mp3", bgm["file_path"])

        sfx = data["tracks"]["sfx_foley_track"]
        self.assertEqual(sfx["total_cues"], 9)

        outputs = data["master_outputs"]
        self.assertTrue(outputs["wav_master_path"].endswith(".wav"))
        self.assertTrue(outputs["mp3_delivery_path"].endswith(".mp3"))

    def test_07_cli_execution_and_validate_only(self):
        """Verifica que el script CLI pueda ejecutarse con flag --validate-only"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "sound-designer" / "scripts" / "design_sound.py"
        cmd = [sys.executable, str(script_path), "--validate-only"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"Fallo CLI validate-only: {p.stderr}")
        self.assertIn("cumple 100% con config/sound-design-schema.json", p.stdout)

if __name__ == "__main__":
    unittest.main()
