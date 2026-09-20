#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 21: Campaña Real Locos Materos (Final Commercial Production)
Valida la producción física del comercial audiovisual, renderizado del master 9:16,
generación de las 5 variantes multiformato, conformidad formal con config/commercial-delivery-schema.json,
integridad de checksums SHA-256 y ficha técnica broadcast.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de campaign-production-master a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "campaign-production-master" / "scripts"))

from produce_final_commercial import generate_delivery_package, validate_delivery_manifest, compute_sha256

class TestPhase21CommercialProduction(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de campaign-production-master"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "campaign-production-master" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: campaign-production-master", content)
        self.assertIn("domain: production", content)
        self.assertIn("config/commercial-delivery-schema.json", content)
        self.assertIn("Pipeline de Composición Multicapa", content)
        self.assertIn("Especificaciones de Entrega Broadcast", content)
        self.assertIn("EBU R128", content)

    def test_02_schema_contract_and_delivery_manifest(self):
        """Valida que commercial-delivery-package.json cumpla con config/commercial-delivery-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "masters" / "commercial-delivery-package.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró commercial-delivery-package.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "commercial-delivery-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/commercial-delivery-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertTrue(data["delivery_id"].startswith("deliv_"))
        self.assertEqual(data["broadcast_certification"]["status"], "APPROVED")
        self.assertEqual(data["broadcast_certification"]["qc_score"], 100.0)

    def test_03_master_video_existence_and_specs(self):
        """Verifica que el master oficial locos_materos_master_9x16.mp4 exista y cumpla especificaciones"""
        master_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "masters" / "locos_materos_master_9x16.mp4"
        self.assertTrue(master_file.is_file(), f"Falta {master_file}")

        # Tamaño mayor a 5 MB
        self.assertGreater(master_file.stat().st_size, 5 * 1024 * 1024)

        with open(WORKSPACE_ROOT / "campaign" / "deliverables" / "masters" / "commercial-delivery-package.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        v_spec = data["master_video"]
        self.assertEqual(v_spec["resolution"], "720x1280")
        self.assertEqual(v_spec["aspect_ratio"], "9:16")
        self.assertEqual(v_spec["fps"], 24.0)
        self.assertEqual(v_spec["video_codec"], "h264")
        self.assertEqual(len(v_spec["sha256"]), 64)

        # Comprobar recálculo de hash
        calculated_hash = compute_sha256(master_file)
        self.assertEqual(calculated_hash, v_spec["sha256"])

    def test_04_multiformat_exports_completeness(self):
        """Verifica la existencia y parámetros de las 5 variantes de exportación para redes sociales"""
        exports_dir = WORKSPACE_ROOT / "campaign" / "deliverables" / "exports"
        self.assertTrue(exports_dir.is_dir(), f"Falta {exports_dir}")

        expected_files = [
            "locos_materos_tiktok_9x16.mp4",
            "locos_materos_instagram_reels_9x16.mp4",
            "locos_materos_youtube_shorts_9x16.mp4",
            "locos_materos_feed_square_1x1.mp4",
            "locos_materos_youtube_widescreen_16x9.mp4"
        ]

        for fname in expected_files:
            target = exports_dir / fname
            self.assertTrue(target.is_file(), f"Falta archivo exportado {fname}")
            self.assertGreater(target.stat().st_size, 1024 * 1024, f"Archivo {fname} demasiado pequeño")

        with open(WORKSPACE_ROOT / "campaign" / "deliverables" / "masters" / "commercial-delivery-package.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        variants = data["variants"]
        self.assertEqual(len(variants), 5)
        platforms = [v["platform"] for v in variants]
        self.assertIn("tiktok", platforms)
        self.assertIn("instagram_reels", platforms)
        self.assertIn("youtube_shorts", platforms)
        self.assertIn("meta_feed_1x1", platforms)
        self.assertIn("youtube_widescreen_16x9", platforms)

    def test_05_audio_and_overlay_blending_integrity(self):
        """Verifica la integridad de masters de audio y existencia de overlays compositados"""
        with open(WORKSPACE_ROOT / "campaign" / "deliverables" / "masters" / "commercial-delivery-package.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        a_spec = data["master_audio"]
        self.assertEqual(a_spec["sample_rate_hz"], 48000)
        self.assertEqual(a_spec["loudness_lufs"], -12.7)
        self.assertEqual(a_spec["true_peak_dbtp"], -1.0)

        wav_path = WORKSPACE_ROOT / a_spec["file_path_wav"]
        mp3_path = WORKSPACE_ROOT / a_spec["file_path_mp3"]
        self.assertTrue(wav_path.is_file(), f"Falta {wav_path}")
        self.assertTrue(mp3_path.is_file(), f"Falta {mp3_path}")

        # Verificar los 9 overlays gráficos
        renders_dir = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "renders"
        for i in range(1, 10):
            overlay_file = renders_dir / f"overlay_scene_{i:02d}.png"
            self.assertTrue(overlay_file.is_file(), f"Falta {overlay_file}")

    def test_06_broadcast_compliance_and_ficha_tecnica(self):
        """Verifica la existencia y contenido exhaustivo de la ficha técnica broadcast"""
        ficha_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "masters" / "FICHA_TECNICA.md"
        self.assertTrue(ficha_file.is_file(), f"Falta {ficha_file}")

        content = ficha_file.read_text(encoding="utf-8")
        self.assertIn("FICHA TÉCNICA Y CERTIFICADO DE ENTREGA BROADCAST", content)
        self.assertIn("Locos Materos", content)
        self.assertIn("¿Dónde estás tú? Está tu mate", content)
        self.assertIn("APPROVED", content)
        self.assertIn("100.0/100.0", content)
        self.assertIn("-12.7 LUFS", content)
        self.assertIn("720x1280", content)
        self.assertIn("TikTok", content)
        self.assertIn("Instagram Reels", content)

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI de produce_final_commercial.py con --validate-only y --json"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "campaign-production-master" / "scripts" / "produce_final_commercial.py"

        # 1. Probar --validate-only
        cmd_val = [sys.executable, str(script_path), "--validate-only"]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True)
        self.assertEqual(p_val.returncode, 0, f"Fallo CLI validate-only: {p_val.stderr}")
        self.assertIn("cumple 100% con config/commercial-delivery-schema.json", p_val.stdout)

        # 2. Probar --json
        cmd_json = [sys.executable, str(script_path), "--json"]
        p_json = subprocess.run(cmd_json, capture_output=True, text=True)
        self.assertEqual(p_json.returncode, 0, f"Fallo CLI json: {p_json.stderr}")
        pkg_data = json.loads(p_json.stdout)
        self.assertEqual(pkg_data["broadcast_certification"]["status"], "APPROVED")
        self.assertEqual(pkg_data["broadcast_certification"]["qc_score"], 100.0)

if __name__ == "__main__":
    unittest.main()
