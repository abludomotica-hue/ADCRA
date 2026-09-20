#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 18: Feedback & Iteration Engine
Valida el orquestador de ciclo cerrado con límite estricto de 3 iteraciones,
conformidad formal con config/iteration-engine-schema.json, resolución autónoma de desvíos,
protocolo de escalamiento a operador humano y convergencia certificada.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de iteration-engine a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "production" / "iteration-engine" / "scripts"))

from iteration_orchestrator import run_iteration_cycle, validate_iteration_log

class TestPhase18IterationEngine(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de iteration-engine"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "iteration-engine" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: iteration-engine", content)
        self.assertIn("domain: production", content)
        self.assertIn("Closed-Loop", content)
        self.assertIn("3 iteraciones", content)
        self.assertIn("ESCALATED_TO_HUMAN", content)
        self.assertIn("iteration-engine-schema.json", content)

    def test_02_schema_contract_and_log_validity(self):
        """Valida que campaign/reports/iteration-history.json cumpla con config/iteration-engine-schema.json"""
        history_file = WORKSPACE_ROOT / "campaign" / "reports" / "iteration-history.json"
        self.assertTrue(history_file.is_file(), "No se encontró iteration-history.json")

        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "iteration-engine-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/iteration-engine-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data.get("campaign_id"), "camp_locos_materos_2026")

    def test_03_strict_iteration_limit(self):
        """Verifica que el límite estricto de iteraciones sea exactamente 3 y no se sobrepase"""
        history_file = WORKSPACE_ROOT / "campaign" / "reports" / "iteration-history.json"
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["max_allowed_iterations"], 3)
        self.assertLessEqual(data["total_iterations_run"], 3)
        self.assertGreaterEqual(data["total_iterations_run"], 1)
        self.assertLessEqual(len(data["iteration_log"]), 3)

    def test_04_closed_loop_convergence_and_tracking(self):
        """Verifica la ejecución del ciclo normal y trazabilidad de scores y acciones"""
        result = run_iteration_cycle()
        self.assertIn(result["final_decision"], ["APPROVED", "NEEDS_REVISION"])
        self.assertLessEqual(result["total_iterations_run"], 3)

        first_it = result["iteration_log"][0]
        self.assertEqual(first_it["iteration_index"], 1)
        self.assertGreaterEqual(first_it["initial_score"], 0.0)
        self.assertGreaterEqual(first_it["post_score"], 90.0)
        self.assertEqual(first_it["post_status"], "APPROVED")

    def test_05_escalation_protocol_on_exhaustion(self):
        """Verifica que si no hay convergencia tras 3 iteraciones, se escale a humano"""
        escalated = run_iteration_cycle(force_escalation=True)
        self.assertEqual(escalated["total_iterations_run"], 3)
        self.assertEqual(escalated["final_decision"], "ESCALATED_TO_HUMAN")
        self.assertEqual(len(escalated["iteration_log"]), 3)
        self.assertEqual(escalated["iteration_log"][-1]["post_status"], "ESCALATED_TO_HUMAN")

        # Validar que cumpla el esquema formal
        validate_iteration_log(escalated)

    def test_06_simulation_feedback_loop(self):
        """Verifica la simulación de ciclo adaptativo multi-paso con retroalimentación guiada"""
        sim = run_iteration_cycle(simulate_feedback=True)
        self.assertEqual(sim["final_decision"], "APPROVED")
        self.assertEqual(sim["total_iterations_run"], 2)

        # Paso 1: desvío inicial
        self.assertEqual(sim["iteration_log"][0]["post_status"], "NEEDS_REVISION")
        # Paso 2: corrección convergente
        self.assertEqual(sim["iteration_log"][1]["post_status"], "APPROVED")
        self.assertEqual(sim["iteration_log"][1]["post_score"], 95.0)

        # Validar esquema
        validate_iteration_log(sim)

    def test_07_cli_execution_and_validate_only(self):
        """Verifica que el script CLI pueda ejecutarse con flag --validate-only"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "production" / "iteration-engine" / "scripts" / "iteration_orchestrator.py"
        cmd = [sys.executable, str(script_path), "--validate-only"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"Fallo CLI validate-only: {p.stderr}")
        self.assertIn("cumple 100% con config/iteration-engine-schema.json", p.stdout)

if __name__ == "__main__":
    unittest.main()
