#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 4: Music & Audio Analysis
Valida la extracción precisa de metadatos, estimación de tempo (BPM),
seguimiento de beats, cálculo de curva de energía y segmentación de secciones
tanto en audio sintético controlado como en el audio real de Locos Materos.
"""

import os
import sys
import json
import unittest
import subprocess
import wave
import struct
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar scripts de audio a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "audio-analysis" / "scripts"))

from analyze_audio import analyze_audio_file, probe_audio_metadata

class TestPhase4AudioAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Crear un archivo WAV sintético a 120 BPM (2 beats por segundo) de 4.0 segundos
        cls.synthetic_wav = WORKSPACE_ROOT / "campaign" / "audio" / "synthetic_test_120bpm.wav"
        cls.synthetic_wav.parent.mkdir(parents=True, exist_ok=True)
        
        sr = 22050
        duration = 4.0
        n_samples = int(sr * duration)
        samples = [0.0] * n_samples
        
        # Click cada 0.5 segundos (120 BPM)
        beat_interval = int(sr * 0.5)
        for b in range(0, n_samples, beat_interval):
            for i in range(min(200, n_samples - b)):
                samples[b + i] = 0.8 if (i % 2 == 0) else -0.8

        with wave.open(str(cls.synthetic_wav), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            packed = struct.pack(f"<{n_samples}h", *[int(s * 32767) for s in samples])
            wf.writeframes(packed)

    @classmethod
    def tearDownClass(cls):
        if cls.synthetic_wav.is_file():
            cls.synthetic_wav.unlink()

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y formato de SKILL.md en audio-analysis"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "audio-analysis" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")
        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: audio-analysis", content)
        self.assertIn("BPM", content)
        self.assertIn("energy_curve", content)

    def test_02_synthetic_audio_analysis(self):
        """Prueba el análisis musical sobre un archivo de audio sintético a 120 BPM"""
        res = analyze_audio_file(str(self.synthetic_wav))
        
        # Duración exacta
        self.assertAlmostEqual(res["technical_metadata"]["duration"], 4.0, delta=0.05)
        
        # BPM estimado debe rondar 120 (margen +/- 4 BPM)
        bpm = res["musical_analysis"]["bpm"]
        self.assertGreaterEqual(bpm, 115.0)
        self.assertLessEqual(bpm, 125.0)
        
        # Debe contener beats
        self.assertGreater(len(res["all_beats"]), 4)

    def test_03_real_audio_analysis_locos_materos(self):
        """Prueba el análisis sobre el audio real de Locos Materos (Entre_mates_y_sol.mp3)"""
        real_audio = WORKSPACE_ROOT / "Recursos" / "Audios" / "Entre_mates_y_sol.mp3"
        self.assertTrue(real_audio.is_file(), "No se encontró el audio real en Recursos/Audios/")

        res = analyze_audio_file(str(real_audio))

        # Metadatos técnicos
        meta = res["technical_metadata"]
        self.assertAlmostEqual(meta["duration"], 66.09, delta=0.1)
        self.assertEqual(meta["sample_rate"], 44100)
        self.assertEqual(meta["channels"], 2)

        # Musical
        musical = res["musical_analysis"]
        self.assertAlmostEqual(musical["bpm"], 107.7, delta=5.0)
        self.assertGreater(musical["total_beats_detected"], 90)

        # Curva de energía
        self.assertGreater(len(res["energy_profile"]), 30)
        levels = {w["energy_level"] for w in res["energy_profile"]}
        self.assertIn("low", levels)
        self.assertIn("medium", levels)

        # Secciones
        sections = res["sections"]
        self.assertGreaterEqual(len(sections), 3)
        sec_names = [s["name"] for s in sections]
        self.assertIn("intro", sec_names)
        self.assertIn("verse_1", sec_names)

        # Cortes comerciales
        cuts = res["recommended_commercial_cuts"]
        self.assertEqual(len(cuts), 2)
        cut30 = next(c for c in cuts if c["target_duration_seconds"] == 30)
        self.assertAlmostEqual(cut30["exact_cut_timestamp"], 29.19, delta=1.5)

    def test_04_json_output_contract(self):
        """Verifica que el archivo campaign/audio/audio-analysis.json cumpla con el contrato esperado"""
        output_file = WORKSPACE_ROOT / "campaign" / "audio" / "audio-analysis.json"
        self.assertTrue(output_file.is_file())

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = [
            "audio_file",
            "technical_metadata",
            "musical_analysis",
            "all_beats",
            "all_downbeats",
            "sections",
            "energy_profile",
            "recommended_commercial_cuts"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Clave faltante en contrato JSON: {key}")

    def test_05_cli_execution(self):
        """Verifica la ejecución CLI de analyze_audio.py con --json y archivo de salida"""
        real_audio = WORKSPACE_ROOT / "Recursos" / "Audios" / "Entre_mates_y_sol.mp3"
        cmd = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "analysis" / "audio-analysis" / "scripts" / "analyze_audio.py"),
            "--audio", str(real_audio),
            "--output", "campaign/audio/test_cli_audio_analysis.json"
        ]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p.returncode, 0, f"Error en CLI: {p.stderr}")

        test_out = WORKSPACE_ROOT / "campaign" / "audio" / "test_cli_audio_analysis.json"
        self.assertTrue(test_out.is_file())
        test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
