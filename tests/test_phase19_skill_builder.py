#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 19: Skill Architect & Meta-Learning
Valida el motor de introspección del ecosistema, síntesis dinámica de habilidades,
conformidad formal con config/skill-builder-schema.json, verificación sintáctica AST,
gobernanza del ciclo de vida (DRAFT -> SYNTHESIZED -> VALIDATED -> ACTIVE) y ejecución CLI.
"""

import os
import sys
import ast
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script de skill-builder a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "meta" / "skill-builder" / "scripts"))

from skill_synthesizer import (
    introspect_ecosystem,
    validate_registry,
    validate_python_syntax,
    synthesize_skill,
    build_full_registry,
    ALLOWED_DOMAINS,
    PROTECTED_BASE_SKILLS,
)

class TestPhase19SkillBuilder(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y especificaciones del SKILL.md de skill-builder"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "meta" / "skill-builder" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: skill-builder", content)
        self.assertIn("domain: meta", content)
        self.assertIn("config/skill-builder-schema.json", content)
        self.assertIn("Taxonomía de los 9 Dominios", content)
        self.assertIn("Ciclo de Vida de una Habilidad Sintetizada", content)
        self.assertIn("SYNTHESIZED", content)
        self.assertIn("VALIDATED", content)
        self.assertIn("ACTIVE", content)

    def test_02_schema_contract_and_registry_validity(self):
        """Valida que campaign/meta/synthesized-skills-registry.json cumpla con config/skill-builder-schema.json"""
        registry_file = WORKSPACE_ROOT / "campaign" / "meta" / "synthesized-skills-registry.json"
        self.assertTrue(registry_file.is_file(), "No se encontró synthesized-skills-registry.json")

        with open(registry_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_file = WORKSPACE_ROOT / "config" / "skill-builder-schema.json"
        self.assertTrue(schema_file.is_file(), "No se encontró config/skill-builder-schema.json")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal JSON Schema Draft-07
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertIn("ecosystem_introspection", data)
        self.assertIn("synthesized_skills", data)
        self.assertIn("meta_learning_policies", data)
        self.assertEqual(data["meta_learning_policies"]["max_synthetic_skills_per_domain"], 5)
        self.assertTrue(data["meta_learning_policies"]["require_automated_tests"])

    def test_03_ecosystem_introspection(self):
        """Verifica la introspección exhaustiva de los 9 dominios y todas las habilidades base"""
        intro = introspect_ecosystem(WORKSPACE_ROOT)
        self.assertGreaterEqual(intro["total_skills_discovered"], 19)
        
        # Verificar que los 9 dominios estén representados
        for domain in ALLOWED_DOMAINS:
            self.assertIn(domain, intro["domains_discovered"], f"Dominio {domain} no encontrado en introspección")

        # Verificar habilidades base clave descubiertas
        discovered_names = {s["skill_name"] for s in intro["discovered_skills"]}
        for base in ["campaign-director", "storyboard-engine", "creative-copy-engine", 
                     "color-grading", "qc-evaluator", "iteration-engine", "skill-builder"]:
            self.assertIn(base, discovered_names, f"Habilidad base {base} no descubierta")

    def test_04_dynamic_skill_synthesis(self):
        """Verifica la síntesis programática y control de errores en creación de habilidades"""
        # Síntesis en modo dry-run
        record = synthesize_skill(
            skill_name="custom-metric-tracker",
            domain="analysis",
            description="Tracker de métricas analíticas personalizadas.",
            purpose="Calcula coeficientes de retención y métricas de drop-off.",
            version="1.0.0",
            dry_run=True,
            workspace_root=WORKSPACE_ROOT,
        )

        self.assertEqual(record["skill_name"], "custom-metric-tracker")
        self.assertEqual(record["domain"], "analysis")
        self.assertEqual(record["status"], "ACTIVE")
        self.assertEqual(len(record["files_generated"]), 2)
        self.assertEqual(record["validation_report"]["syntax_valid"], True)

        # Validación de rechazo de dominios no permitidos
        with self.assertRaises(ValueError):
            synthesize_skill(
                skill_name="bad-skill",
                domain="invalid_domain_xyz",
                description="desc",
                purpose="purpose",
                dry_run=True,
                workspace_root=WORKSPACE_ROOT,
            )

        # Validación de rechazo de nombres no slug
        with self.assertRaises(ValueError):
            synthesize_skill(
                skill_name="Bad_Name_With_Caps!",
                domain="meta",
                description="desc",
                purpose="purpose",
                dry_run=True,
                workspace_root=WORKSPACE_ROOT,
            )

    def test_05_synthesized_code_syntax_and_ast_validity(self):
        """Verifica que el código generado sea compilable mediante el módulo ast y que el skill demostrativo sea válido"""
        # Probar función de validación de sintaxis con código válido
        valid_code = "def hello():\n    return 'world'\n"
        ok, msg = validate_python_syntax(valid_code)
        self.assertTrue(ok)

        # Probar con código sintácticamente inválido
        invalid_code = "def hello(:\n    return 'world'\n"
        bad_ok, bad_msg = validate_python_syntax(invalid_code)
        self.assertFalse(bad_ok)
        self.assertIn("SyntaxError", bad_msg)

        # Probar el script real de telemetry-monitor generado
        telemetry_script = WORKSPACE_ROOT / ".agents" / "skills" / "meta" / "telemetry-monitor" / "scripts" / "telemetry_collector.py"
        self.assertTrue(telemetry_script.is_file(), f"Falta {telemetry_script}")
        script_content = telemetry_script.read_text(encoding="utf-8")
        parsed = ast.parse(script_content)
        self.assertIsInstance(parsed, ast.Module)

    def test_06_lifecycle_transitions_and_governance(self):
        """Verifica la trazabilidad formal de estados en el ciclo de vida del skill sintetizado"""
        registry_file = WORKSPACE_ROOT / "campaign" / "meta" / "synthesized-skills-registry.json"
        with open(registry_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertGreaterEqual(len(data["synthesized_skills"]), 1)
        demo = data["synthesized_skills"][0]
        self.assertEqual(demo["skill_name"], "telemetry-monitor")
        self.assertEqual(demo["domain"], "meta")
        self.assertEqual(demo["status"], "ACTIVE")

        # Verificar progresión de estados
        statuses = [step["to_status"] for step in demo["lifecycle_history"]]
        self.assertEqual(statuses, ["DRAFT", "SYNTHESIZED", "VALIDATED", "ACTIVE"])
        for step in demo["lifecycle_history"]:
            self.assertTrue(len(step["reason"]) > 5, "Falta razón descriptiva en transición")

        # Verificar reporte de validación
        self.assertTrue(demo["validation_report"]["schema_valid"])
        self.assertTrue(demo["validation_report"]["syntax_valid"])
        self.assertTrue(demo["validation_report"]["tests_passed"])

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI con --validate-only y --introspect"""
        script_path = WORKSPACE_ROOT / ".agents" / "skills" / "meta" / "skill-builder" / "scripts" / "skill_synthesizer.py"
        
        # 1. Probar --validate-only
        cmd_validate = [sys.executable, str(script_path), "--validate-only"]
        p_val = subprocess.run(cmd_validate, capture_output=True, text=True)
        self.assertEqual(p_val.returncode, 0, f"Fallo CLI validate-only: {p_val.stderr}")
        self.assertIn("cumple 100% con config/skill-builder-schema.json", p_val.stdout)

        # 2. Probar --introspect
        cmd_intro = [sys.executable, str(script_path), "--introspect"]
        p_intro = subprocess.run(cmd_intro, capture_output=True, text=True)
        self.assertEqual(p_intro.returncode, 0, f"Fallo CLI introspect: {p_intro.stderr}")
        intro_data = json.loads(p_intro.stdout)
        self.assertIn("total_skills_discovered", intro_data)
        self.assertGreaterEqual(intro_data["total_skills_discovered"], 19)

if __name__ == "__main__":
    unittest.main()
