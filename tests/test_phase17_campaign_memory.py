#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 17: Campaign Memory System
Valida la arquitectura de persistencia evolutiva de aprendizajes de marca,
conformidad formal con config/campaign-memory-schema.json, consolidación de métricas estéticas y rítmicas,
reglas de retención publicitaria y la interfaz de consulta semántica cross-campaign.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de memory-manager a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "memory" / "campaign-memory" / "scripts"))

from memory_manager import compile_brand_memory, validate_brand_memory, query_brand_memory

class TestPhase17CampaignMemory(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de campaign-memory"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "memory" / "campaign-memory" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: campaign-memory", content)
        self.assertIn("domain: memory", content)
        self.assertIn("Aesthetic Learnings", content)
        self.assertIn("Musical & Tempo", content)
        self.assertIn("#0D5C3A", content)
        self.assertIn("#D4AF37", content)
        self.assertIn("campaign-memory-schema.json", content)

    def test_02_schema_contract_and_memory_validity(self):
        """Valida que campaign/memory/brand-profile-memory.json cumpla con config/campaign-memory-schema.json"""
        mem_file = WORKSPACE_ROOT / "campaign" / "memory" / "brand-profile-memory.json"
        self.assertTrue(mem_file.is_file(), "No se encontró brand-profile-memory.json")

        with open(mem_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "campaign-memory-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/campaign-memory-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data.get("brand_id"), "locos_materos")
        self.assertEqual(data.get("brand_name"), "Locos Materos")

    def test_03_brand_identity_and_historical_records(self):
        """Verifica los registros históricos de campañas y sus certificaciones"""
        mem_file = WORKSPACE_ROOT / "campaign" / "memory" / "brand-profile-memory.json"
        with open(mem_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        campaigns = data.get("historical_campaigns", [])
        self.assertGreaterEqual(len(campaigns), 1)

        camp = campaigns[0]
        self.assertEqual(camp["campaign_id"], "camp_locos_materos_2026")
        self.assertGreaterEqual(camp["quality_score"], 90.0)
        self.assertEqual(camp["certification_status"], "APPROVED")

    def test_04_aesthetic_and_color_learnings(self):
        """Verifica la persistencia de lineamientos cromáticos y LUTs recomendadas"""
        mem_file = WORKSPACE_ROOT / "campaign" / "memory" / "brand-profile-memory.json"
        with open(mem_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        aes = data["aesthetic_learnings"]
        palette = aes["primary_palette"]
        self.assertEqual(palette["primary_green"], "#0D5C3A")
        self.assertEqual(palette["golden_highlight"], "#D4AF37")
        self.assertEqual(palette["neutral_dark"], "#1A1A1A")

        self.assertEqual(aes["color_temperature_target_kelvin"], 5900)
        self.assertGreaterEqual(len(aes["recommended_luts"]), 3)
        self.assertTrue(any("warm_cinematic" in lut for lut in aes["recommended_luts"]))

    def test_05_musical_tempo_and_rhythm_learnings(self):
        """Verifica los aprendizajes de tempo musical (BPM) y ritmo de montaje"""
        mem_file = WORKSPACE_ROOT / "campaign" / "memory" / "brand-profile-memory.json"
        with open(mem_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        tempo = data["musical_tempo_learnings"]
        self.assertEqual(tempo["optimal_bpm_range"]["min"], 100.0)
        self.assertEqual(tempo["optimal_bpm_range"]["max"], 115.0)
        self.assertAlmostEqual(tempo["last_successful_bpm"], 107.7, places=1)
        self.assertEqual(tempo["meter"], "4/4")

        rhythm = data["editing_rhythm_learnings"]
        self.assertEqual(rhythm["scene_count"], 9)
        self.assertAlmostEqual(rhythm["target_commercial_duration_sec"], 29.167, places=1)
        self.assertGreater(rhythm["average_scene_duration_sec"], 2.5)
        self.assertLess(rhythm["average_scene_duration_sec"], 4.0)

    def test_06_query_interface_and_semantic_lookup(self):
        """Verifica la capacidad de consulta tematica del motor de memoria"""
        mem_file = WORKSPACE_ROOT / "campaign" / "memory" / "brand-profile-memory.json"
        with open(mem_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Consulta de color
        q_color = query_brand_memory(data, "color")
        self.assertEqual(q_color["topic"], "aesthetic_learnings")
        self.assertIn("primary_palette", q_color["data"])

        # Consulta de tempo
        q_tempo = query_brand_memory(data, "tempo")
        self.assertEqual(q_tempo["topic"], "musical_tempo_learnings")
        self.assertIn("last_successful_bpm", q_tempo["data"])

        # Consulta de reglas
        q_rules = query_brand_memory(data, "rules")
        self.assertEqual(q_rules["topic"], "retention_rules")
        self.assertIn("mandatory_rules", q_rules["data"])
        self.assertIn("prohibited_patterns", q_rules["data"])

    def test_07_cli_execution_and_validate_only(self):
        """Verifica que el script CLI pueda ejecutarse con flag --validate-only"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "memory" / "campaign-memory" / "scripts" / "memory_manager.py"
        cmd = [sys.executable, str(script_path), "--validate-only"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"Fallo CLI validate-only: {p.stderr}")
        self.assertIn("cumple 100% con config/campaign-memory-schema.json", p.stdout)

if __name__ == "__main__":
    unittest.main()
