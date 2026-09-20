#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 3: Tool Discovery + Tool Router
Valida la detección en tiempo real de hardware y software, la resolución
de herramientas primarias, la activación de alternativas declaradas (fallback),
el manejo de herramientas no disponibles y la cobertura de la matriz de enrutamiento.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar scripts de herramientas a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "tools" / "tool-discovery" / "scripts"))
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "tools" / "tool-router" / "scripts"))

from discover_tools import discover_all_tools, is_tool_available
from route_tool import route_need, audit_all_routes, load_router_matrix

class TestPhase3ToolRouter(unittest.TestCase):

    def test_01_tool_skills_exist(self):
        """Verifica la existencia y formato de SKILL.md en tool-discovery y tool-router"""
        disc_skill = WORKSPACE_ROOT / ".agents" / "skills" / "tools" / "tool-discovery" / "SKILL.md"
        router_skill = WORKSPACE_ROOT / ".agents" / "skills" / "tools" / "tool-router" / "SKILL.md"

        self.assertTrue(disc_skill.is_file(), f"Falta {disc_skill}")
        self.assertTrue(router_skill.is_file(), f"Falta {router_skill}")

        disc_content = disc_skill.read_text(encoding="utf-8")
        router_content = router_skill.read_text(encoding="utf-8")

        self.assertIn("name: tool-discovery", disc_content)
        self.assertIn("name: tool-router", router_content)
        self.assertIn("ROUTED_PRIMARY", router_content)
        self.assertIn("ROUTED_FALLBACK", router_content)

    def test_02_tool_discovery_hardware(self):
        """Verifica que el descubridor detecte correctamente la GPU y OpenCL"""
        data = discover_all_tools()
        self.assertIn("hardware", data)
        self.assertIn("gpu", data["hardware"])
        gpu = data["hardware"]["gpu"]

        self.assertTrue(gpu["available"], "La GPU NVIDIA debe detectarse como disponible")
        self.assertIn("GTX 750 Ti", gpu["name"])
        self.assertTrue(gpu["opencl_ready"], "OpenCL debe estar listo y funcional")

    def test_03_tool_discovery_installed_runtimes(self):
        """Verifica que los runtimes instalados (Node, Python, Resolve, FFmpeg) se reporten operativos"""
        data = discover_all_tools()
        tools = data.get("tools", {})

        self.assertTrue(tools["DaVinci Resolve"]["installed"])
        self.assertTrue(tools["DaVinci Resolve"]["operational"])
        self.assertEqual(tools["DaVinci Resolve"]["gpu_mode"], "OpenCL")

        self.assertTrue(tools["Node.js"]["installed"])
        self.assertTrue(tools["Python"]["installed"])
        self.assertTrue(tools["npm"]["installed"])
        self.assertTrue(tools["npx"]["installed"])
        self.assertTrue(tools["FFmpeg"]["installed"])
        self.assertTrue(tools["FFprobe"]["installed"])

    def test_04_route_primary_tools(self):
        """Verifica el enrutamiento exitoso hacia herramientas primarias instaladas"""
        needs_for_resolve = [
            "Timeline profesional",
            "Color grading",
            "Fairlight/audio",
            "Fusion",
            "Conversión técnica",
            "Media probing",
            "QC técnico"
        ]
        for need in needs_for_resolve:
            res = route_need(need)
            self.assertEqual(res["status"], "ROUTED_PRIMARY", f"Fallo al enrutar {need}")
            self.assertFalse(res["is_fallback"])
            if need in ["Timeline profesional", "Color grading", "Fusion"]:
                self.assertTrue(res["requires_gpu"])

    def test_05_route_fallback_resolution(self):
        """Verifica que si la herramienta primaria falta pero hay alternativa, se active el fallback determinista"""
        simulated_cache = {
            "tools": {
                "FFprobe": {"installed": False, "operational": False},
                "DaVinci Resolve": {"installed": True, "operational": True, "gpu_mode": "OpenCL"},
                "HyperFrames": {"installed": False, "operational": False},
                "Remotion": {"installed": True, "operational": True}
            }
        }
        # 1. Simulación FFprobe caído -> fallback a DaVinci Resolve
        res_probing = route_need("Media probing", discovery_cache=simulated_cache)
        self.assertEqual(res_probing["status"], "ROUTED_FALLBACK")
        self.assertEqual(res_probing["selected_tool"], "DaVinci Resolve")
        self.assertTrue(res_probing["is_fallback"])
        self.assertIn("[FALLBACK]", res_probing["decision_rationale"])

        # 2. Simulación HyperFrames caído -> fallback a Remotion
        res_motion = route_need("HTML motion graphics", discovery_cache=simulated_cache)
        self.assertEqual(res_motion["status"], "ROUTED_FALLBACK")
        self.assertEqual(res_motion["selected_tool"], "Remotion")
        self.assertTrue(res_motion["is_fallback"])

    def test_06_route_unavailable_needs(self):
        """Verifica el manejo de necesidades donde ni primaria ni alternativa están disponibles"""
        simulated_cache = {
            "tools": {
                "Remotion": {"installed": False, "operational": False},
                "HyperFrames": {"installed": False, "operational": False}
            }
        }
        res_react = route_need("Video programático React", discovery_cache=simulated_cache)
        self.assertEqual(res_react["status"], "UNAVAILABLE")
        self.assertIsNone(res_react["selected_tool"])
        self.assertIn("Se requiere instalar", res_react["resolution_action"])

    def test_07_route_unknown_need(self):
        """Verifica que una necesidad inexistente retorne NOT_FOUND sin romper la ejecución"""
        res_unknown = route_need("Necesidad Inventada Inexistente 12345")
        self.assertEqual(res_unknown["status"], "NOT_FOUND")
        self.assertIn("error", res_unknown)

    def test_08_audit_routes_coverage(self):
        """Verifica que la auditoría de rutas cubra las 14 necesidades declaradas en config/tool-router.json"""
        matrix = load_router_matrix()
        total_declared = len(matrix.get("routes", []))
        self.assertEqual(total_declared, 14, "Deben existir exactamente 14 rutas declaradas")

        audit = audit_all_routes()
        self.assertEqual(len(audit), 14)

        statuses = {item["status"] for item in audit}
        self.assertIn("ROUTED_PRIMARY", statuses)

        # Con cache simulado donde hay herramientas no disponibles:
        simulated_unavail = {
            "tools": {
                "HyperFrames": {"installed": False, "operational": False},
                "Remotion": {"installed": False, "operational": False},
                "DaVinci Resolve": {"installed": False, "operational": False},
                "FFmpeg": {"installed": False, "operational": False},
                "FFprobe": {"installed": False, "operational": False}
            }
        }
        sim_unavail_audit = audit_all_routes(discovery_cache=simulated_unavail)
        sim_unavail_statuses = {item["status"] for item in sim_unavail_audit}
        self.assertIn("UNAVAILABLE", sim_unavail_statuses)

        # Con cache simulado donde hay fallbacks:
        simulated_cache = {
            "tools": {
                "HyperFrames": {"installed": False, "operational": False},
                "Remotion": {"installed": True, "operational": True},
                "DaVinci Resolve": {"installed": True, "operational": True},
                "FFmpeg": {"installed": True, "operational": True},
                "FFprobe": {"installed": True, "operational": True}
            }
        }
        sim_audit = audit_all_routes(discovery_cache=simulated_cache)
        sim_statuses = {item["status"] for item in sim_audit}
        self.assertIn("ROUTED_FALLBACK", sim_statuses)

    def test_09_cli_execution(self):
        """Verifica que los comandos CLI de route_tool.py y discover_tools.py ejecuten con exit code 0"""
        cmd_disc = ["python3", str(WORKSPACE_ROOT / ".agents" / "skills" / "tools" / "tool-discovery" / "scripts" / "discover_tools.py"), "--json"]
        p_disc = subprocess.run(cmd_disc, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_disc.returncode, 0)
        parsed_disc = json.loads(p_disc.stdout)
        self.assertIn("hardware", parsed_disc)

        cmd_route = ["python3", str(WORKSPACE_ROOT / ".agents" / "skills" / "tools" / "tool-router" / "scripts" / "route_tool.py"), "--need", "Color grading", "--json"]
        p_route = subprocess.run(cmd_route, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_route.returncode, 0)
        parsed_route = json.loads(p_route.stdout)
        self.assertEqual(parsed_route["selected_tool"], "DaVinci Resolve")

if __name__ == "__main__":
    unittest.main(verbosity=2)
