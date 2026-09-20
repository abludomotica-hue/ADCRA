#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 11: Beat-Synced Editor
Valida la precisión rítmica de cortes a downbeats musicales,
la conformidad formal con config/timeline-schema.json, la integridad de formatos
universales (EDL CMX 3600, FCP7 XML, FFmpeg script) y la continuidad temporal a 24 fps.
"""

import os
import sys
import json
import unittest
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "beat-sync-editor" / "scripts"))

from build_beat_edit import build_timeline_data, validate_timeline_data, frames_to_tc

class TestPhase11BeatSyncedEditor(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y contenido de SKILL.md en beat-sync-editor"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "beat-sync-editor" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: beat-sync-editor", content)
        self.assertIn("domain: production", content)
        self.assertIn("CMX 3600 EDL", content)
        self.assertIn("FCP7 XML", content)
        self.assertIn("timeline-schema.json", content)

    def test_02_schema_contract_and_timeline_validity(self):
        """Valida que campaign/timeline/timeline.json cumpla con config/timeline-schema.json"""
        timeline_file = WORKSPACE_ROOT / "campaign" / "timeline" / "timeline.json"
        self.assertTrue(timeline_file.is_file(), "No se encontró timeline.json")

        with open(timeline_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_path = WORKSPACE_ROOT / "config" / "timeline-schema.json"
        self.assertTrue(schema_path.is_file(), "No se encontró timeline-schema.json")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal Draft-07 sin excepciones
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertEqual(data["timeline_id"], "timeline_locos_materos_master")
        self.assertEqual(data["timeline_format"]["duration_frames"], 700)
        self.assertEqual(data["timeline_format"]["fps"], 24.0)

    def test_03_edl_cmx3600_structure(self):
        """Verifica la sintaxis estándar y timecodes del archivo CMX 3600 EDL"""
        edl_file = WORKSPACE_ROOT / "campaign" / "timeline" / "locos_materos_edit.edl"
        self.assertTrue(edl_file.is_file(), "No se encontró locos_materos_edit.edl")

        content = edl_file.read_text(encoding="utf-8")
        self.assertIn("TITLE: LOCOS_MATEROS_COMMERCIAL", content)
        self.assertIn("FCM: NON-DROP FRAME", content)

        # Verificar que existan exactamente los eventos 001 a 009
        for i in range(1, 10):
            self.assertIn(f"{i:03d}  AX{i:02d}", content)

        # Verificar inicio en 00:00:00:00 y fin en 00:00:29:04
        self.assertIn("00:00:00:00 00:00:03:12 00:00:00:00 00:00:03:12", content)
        self.assertIn("00:00:29:04", content)

    def test_04_fcp7_xml_structure_and_parsing(self):
        """Valida que el archivo FCP7 XML sea un XML válido y contenga los elementos de DaVinci Resolve"""
        xml_file = WORKSPACE_ROOT / "campaign" / "timeline" / "locos_materos_edit.xml"
        self.assertTrue(xml_file.is_file(), "No se encontró locos_materos_edit.xml")

        tree = ET.parse(xml_file)
        root = tree.getroot()
        self.assertEqual(root.tag, "xmeml")
        self.assertEqual(root.attrib.get("version"), "4")

        seq = root.find(".//sequence")
        self.assertIsNotNone(seq)
        self.assertEqual(seq.find("duration").text, "700")
        self.assertEqual(seq.find(".//timebase").text, "24")

        # Verificar 9 clips en video track y 1 en audio track
        v_clips = seq.findall(".//video/track/clipitem")
        self.assertEqual(len(v_clips), 9)

        a_clips = seq.findall(".//audio/track/clipitem")
        self.assertEqual(len(a_clips), 1)

    def test_05_rhythmic_beat_synchronization(self):
        """Verifica que el desfase promedio a beats musicales sea bajo (<100ms) y haya cortes en downbeats"""
        timeline_file = WORKSPACE_ROOT / "campaign" / "timeline" / "timeline.json"
        with open(timeline_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        metrics = data["sync_metrics"]
        self.assertEqual(metrics["total_cuts"], 9)
        self.assertLess(metrics["average_beat_drift_ms"], 100.0)
        self.assertGreaterEqual(metrics["beat_alignment_rate"], 0.70)
        self.assertGreaterEqual(metrics["downbeat_cuts_count"], 3)

    def test_06_multitrack_integrity(self):
        """Verifica que las pistas V1, V2 y A1 no posean huecos temporales y sumen 700 frames"""
        timeline_file = WORKSPACE_ROOT / "campaign" / "timeline" / "timeline.json"
        with open(timeline_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        v1_clips = data["tracks"]["video_tracks"][0]["clips"]
        v2_clips = data["tracks"]["video_tracks"][1]["clips"]
        self.assertEqual(len(v1_clips), 9)
        self.assertEqual(len(v2_clips), 9)

        prev_end = 0
        for c in v1_clips:
            self.assertEqual(c["record_in_frame"], prev_end)
            self.assertGreater(c["record_out_frame"], c["record_in_frame"])
            prev_end = c["record_out_frame"]
        self.assertEqual(prev_end, 700)

        # Verificar script FFmpeg ejecutable
        sh_file = WORKSPACE_ROOT / "campaign" / "timeline" / "ffmpeg_assembly.sh"
        self.assertTrue(sh_file.is_file())
        self.assertTrue(os.access(sh_file, os.X_OK))

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI y el flag --validate-only"""
        cmd_gen = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "beat-sync-editor" / "scripts" / "build_beat_edit.py"),
            "--output", "campaign/timeline/test_cli_timeline.json"
        ]
        p_gen = subprocess.run(cmd_gen, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_gen.returncode, 0, f"CLI error: {p_gen.stderr}")

        cmd_val = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "beat-sync-editor" / "scripts" / "build_beat_edit.py"),
            "--output", "campaign/timeline/test_cli_timeline.json",
            "--validate-only"
        ]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_val.returncode, 0)
        self.assertIn("[VALID]", p_val.stdout)

        test_out = WORKSPACE_ROOT / "campaign" / "timeline" / "test_cli_timeline.json"
        if test_out.is_file():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
