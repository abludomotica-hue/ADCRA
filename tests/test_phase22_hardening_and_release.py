#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — Fase 22: Hardening, Benchmarking & Release CLI
Verifica el schema de benchmarking, la ejecución del motor de benchmarking,
el CLI unificado de ADCRA, el manual de operaciones y la integridad de release del sistema.
"""

import os
import sys
import json
import subprocess
import unittest
import jsonschema

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestPhase22HardeningAndRelease(unittest.TestCase):

    def setUp(self):
        self.schema_path = os.path.join(WORKSPACE_ROOT, "config/benchmarking-schema.json")
        self.report_path = os.path.join(WORKSPACE_ROOT, "campaign/reports/benchmarking-report.json")
        self.cli_script = os.path.join(WORKSPACE_ROOT, "adcra_cli.py")
        self.cli_wrapper = os.path.join(WORKSPACE_ROOT, "bin/adcra")
        self.manual_path = os.path.join(WORKSPACE_ROOT, "docs/ADCRA/OPERATIONS_MANUAL.md")

    def test_01_benchmarking_schema_validity(self):
        """01. Valida que config/benchmarking-schema.json sea un Draft-07 válido."""
        self.assertTrue(os.path.exists(self.schema_path), f"No existe {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        # Validar contra metaschema draft-07
        metaschema = jsonschema.Draft7Validator.META_SCHEMA
        jsonschema.Draft7Validator.check_schema(schema)
        self.assertEqual(schema.get("$schema"), "http://json-schema.org/draft-07/schema#")
        self.assertIn("required", schema)
        self.assertIn("environment_telemetry", schema["properties"])
        self.assertIn("engine_benchmarks", schema["properties"])

    def test_02_benchmarking_engine_execution_and_schema_validation(self):
        """02. Verifica que campaign/reports/benchmarking-report.json cumpla con el schema."""
        self.assertTrue(os.path.exists(self.report_path), f"No existe {self.report_path}")
        with open(self.schema_path, "r", encoding="utf-8") as sf, open(self.report_path, "r", encoding="utf-8") as rf:
            schema = json.load(sf)
            report = json.load(rf)

        # Validación estricta con jsonschema
        jsonschema.validate(instance=report, schema=schema)
        self.assertEqual(report.get("schema_version"), "1.0.0")
        self.assertEqual(report.get("production_readiness", {}).get("status"), "PRODUCTION_READY")
        self.assertTrue(report.get("production_readiness", {}).get("ready_for_release"))

    def test_03_benchmarking_report_thresholds(self):
        """03. Verifica que las métricas de rendimiento y SLAs cumplan los umbrales de producción."""
        with open(self.report_path, "r", encoding="utf-8") as rf:
            report = json.load(rf)

        benchmarks = report.get("engine_benchmarks", [])
        self.assertGreaterEqual(len(benchmarks), 8, "Debe haber al menos 8 motores evaluados")
        
        for b in benchmarks:
            self.assertIn(b.get("status"), ["OPTIMAL", "ACCEPTABLE"], f"Motor {b.get('engine_id')} en estado no conforme")
            self.assertLess(b.get("mean_latency_ms"), 500.0, f"Latencia excesiva en {b.get('engine_id')}")
            self.assertGreater(b.get("throughput_ops_sec"), 1.0)

        rating = report.get("performance_rating")
        self.assertIn(rating, ["EXCELLENT", "GOOD"], f"Rating de rendimiento insuficiente: {rating}")
        
        agg = report.get("aggregate_metrics", {})
        self.assertLess(agg.get("total_benchmark_time_ms"), 30000.0, "Tiempo total de benchmarking excedió 30s")

    def test_04_adcra_cli_status(self):
        """04. Ejecuta 'adcra status --json' y valida 100% de completitud de las 22 fases."""
        self.assertTrue(os.path.exists(self.cli_wrapper), "El wrapper bin/adcra no existe")
        self.assertTrue(os.access(self.cli_wrapper, os.X_OK), "bin/adcra no tiene permisos de ejecución")

        res = subprocess.run(
            [self.cli_wrapper, "--json", "status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        self.assertEqual(res.returncode, 0, f"CLI status falló: {res.stderr}")
        data = json.loads(res.stdout)
        
        self.assertEqual(data.get("total_phases"), 22)
        self.assertEqual(data.get("completed_phases"), 22)
        self.assertEqual(data.get("completion_percentage"), 100.0)
        self.assertEqual(data.get("overall_status"), "PRODUCTION_READY")

    def test_05_adcra_cli_deliver_and_introspect(self):
        """05. Ejecuta 'adcra deliver' e 'introspect' con verificación de salida JSON."""
        # Test deliver
        res_deliv = subprocess.run(
            [self.cli_wrapper, "--json", "deliver"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        self.assertEqual(res_deliv.returncode, 0, f"CLI deliver falló: {res_deliv.stderr}")
        pkg = json.loads(res_deliv.stdout)
        self.assertEqual(pkg.get("campaign_id"), "camp_locos_materos_2026")
        self.assertEqual(pkg.get("broadcast_certification", {}).get("status"), "APPROVED")
        self.assertEqual(len(pkg.get("variants", [])), 5)

        # Test introspect
        res_intro = subprocess.run(
            [self.cli_wrapper, "--json", "introspect"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        self.assertEqual(res_intro.returncode, 0, f"CLI introspect falló: {res_intro.stderr}")
        intro = json.loads(res_intro.stdout)
        self.assertGreaterEqual(intro.get("total_skills"), 20)

    def test_06_operations_manual_completeness(self):
        """06. Valida que docs/ADCRA/OPERATIONS_MANUAL.md exista y contenga secciones críticas."""
        self.assertTrue(os.path.exists(self.manual_path), f"Falta {self.manual_path}")
        with open(self.manual_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_sections = [
            "Visión General de la Arquitectura",
            "Referencia de Comandos CLI",
            "Configuración de Hardware y DaVinci Resolve en Linux",
            "OpenCL",
            "Estándares de Emisión y SLAs Técnicos",
            "Procedimientos de Recuperación y Solución de Problemas",
            "Estado de Certificación y Release"
        ]
        for sec in required_sections:
            self.assertIn(sec, content, f"Sección obligatoria '{sec}' no encontrada en manual")

    def test_07_full_system_release_integrity(self):
        """07. Verifica la integridad global de artefactos y contratos de las 22 fases."""
        core_contracts = [
            "config/campaign-schema.json",
            "config/timeline-schema.json",
            "config/creative-copy-schema.json",
            "config/storyboard-schema.json",
            "config/color-grading-schema.json",
            "config/sound-design-schema.json",
            "config/motion-graphics-schema.json",
            "config/social-formatter-schema.json",
            "config/quality-control-schema.json",
            "config/iteration-engine-schema.json",
            "config/remotion-composition-schema.json",
            "config/campaign-memory-schema.json",
            "config/skill-builder-schema.json",
            "config/pilot-campaign-schema.json",
            "config/commercial-delivery-schema.json",
            "config/benchmarking-schema.json"
        ]
        for contract in core_contracts:
            c_path = os.path.join(WORKSPACE_ROOT, contract)
            self.assertTrue(os.path.exists(c_path), f"Falta contrato crítico: {contract}")

        # Master deliverable file check
        master_file = os.path.join(WORKSPACE_ROOT, "campaign/deliverables/masters/locos_materos_master_9x16.mp4")
        self.assertTrue(os.path.exists(master_file), f"Falta archivo master: {master_file}")
        self.assertGreater(os.path.getsize(master_file), 100_000, "El archivo master debe superar los 100KB")

if __name__ == "__main__":
    unittest.main()
