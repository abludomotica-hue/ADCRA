#!/usr/bin/env python3
"""
ADCRA — Test Suite para FASE 12: DaVinci Resolve Integration
Valida la integración con la Scripting API de DaVinci Resolve 21.1 en Linux,
conformidad del manifiesto de proyecto con config/resolve-integration-schema.json,
presencia de la biblioteca fusionscript.so, estructura jerárquica del Media Pool
y scripts de automatización de importación de timeline XML/EDL.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Agregar script a sys.path
sys.path.insert(0, str(WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "davinci-resolve-orchestrator" / "scripts"))

from resolve_orchestrator import build_resolve_manifest, validate_resolve_manifest, check_resolve_environment

class TestPhase12DaVinciResolve(unittest.TestCase):

    def test_01_skill_definition_exists(self):
        """Verifica la existencia y contenido de SKILL.md en davinci-resolve-orchestrator"""
        skill_file = WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "davinci-resolve-orchestrator" / "SKILL.md"
        self.assertTrue(skill_file.is_file(), f"Falta {skill_file}")

        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: davinci-resolve-orchestrator", content)
        self.assertIn("domain: post-production", content)
        self.assertIn("DaVinci Resolve 21.1", content)
        self.assertIn("fusionscript.so", content)
        self.assertIn("resolve-integration-schema.json", content)

    def test_02_schema_contract_and_manifest_validity(self):
        """Valida que campaign/resolve/resolve-project-manifest.json cumpla con config/resolve-integration-schema.json"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "resolve" / "resolve-project-manifest.json"
        self.assertTrue(manifest_file.is_file(), "No se encontró resolve-project-manifest.json")

        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_path = WORKSPACE_ROOT / "config" / "resolve-integration-schema.json"
        self.assertTrue(schema_path.is_file(), "No se encontró resolve-integration-schema.json")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validación formal Draft-07 sin excepciones
        jsonschema.validate(instance=data, schema=schema)
        self.assertEqual(data["campaign_id"], "camp_locos_materos_2026")
        self.assertEqual(data["project_name"], "Locos_Materos_2026_Campaign")
        self.assertEqual(data["timeline_settings"]["width"], 720)
        self.assertEqual(data["timeline_settings"]["height"], 1280)
        self.assertEqual(data["timeline_settings"]["frame_rate"], 24.0)

    def test_03_fusionscript_library_and_python_module(self):
        """Verifica que los binarios nativos de scripting de Resolve existan y se importen correctamente"""
        fusionscript_so = Path("/opt/resolve/libs/Fusion/fusionscript.so")
        self.assertTrue(fusionscript_so.is_file(), f"Falta fusionscript.so en {fusionscript_so}")

        dvr_script = Path("/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py")
        self.assertTrue(dvr_script.is_file(), f"Falta DaVinciResolveScript.py en {dvr_script}")

        res_bin, fusionscript_ok, _ = check_resolve_environment()
        self.assertTrue(res_bin, "El ejecutable de Resolve no existe en /opt/resolve/bin/resolve")
        self.assertTrue(fusionscript_ok, "No se pudo cargar fusionscript en Python")

    def test_04_media_pool_bins_and_clips_existence(self):
        """Verifica la jerarquía de 4 Bins y que todos los 19 clips registrados existan en disco"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "resolve" / "resolve-project-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected_bins = ["01_Footage", "02_Audio", "03_Motion_Graphics", "04_Timelines"]
        self.assertEqual(data["media_pool_structure"]["bins"], expected_bins)

        clips = data["media_pool_structure"]["clips_registered"]
        self.assertEqual(len(clips), 19, "Deben existir 19 clips (9 video + 1 audio + 9 overlays)")

        for c in clips:
            c_path = WORKSPACE_ROOT / c["file_path"]
            self.assertTrue(c_path.is_file(), f"El archivo de clip no existe: {c_path}")
            self.assertIn(c["bin"], expected_bins)

    def test_05_timeline_and_render_settings(self):
        """Verifica la vinculación de fuentes de timeline (XML, EDL) y configuración de render"""
        manifest_file = WORKSPACE_ROOT / "campaign" / "resolve" / "resolve-project-manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        tl_entry = data["timelines"][0]
        self.assertEqual(tl_entry["timeline_name"], "LocosMateros_BeatSynced_Master")

        xml_path = WORKSPACE_ROOT / tl_entry["source_xml"]
        self.assertTrue(xml_path.is_file(), f"Falta archivo XML: {xml_path}")

        edl_path = WORKSPACE_ROOT / tl_entry["source_edl"]
        self.assertTrue(edl_path.is_file(), f"Falta archivo EDL: {edl_path}")

        rs = data["render_settings"]
        self.assertEqual(rs["target_format"], "QuickTime")
        self.assertEqual(rs["video_codec"], "H264")
        self.assertEqual(rs["bitrate_kbps"], 12000)

    def test_06_automation_scripts_exist_and_executable(self):
        """Verifica que los scripts de automatización e importación existan y sean ejecutables"""
        resolve_dir = WORKSPACE_ROOT / "campaign" / "resolve"

        py_script = resolve_dir / "import_to_resolve.py"
        self.assertTrue(py_script.is_file())
        self.assertTrue(os.access(py_script, os.X_OK))

        content_py = py_script.read_text(encoding="utf-8")
        self.assertIn("DaVinciResolveScript", content_py)
        self.assertIn("CreateProject", content_py)
        self.assertIn("AddSubFolder", content_py)
        self.assertIn("ImportTimelineFromFile", content_py)

        sh_script = resolve_dir / "setup_project.sh"
        self.assertTrue(sh_script.is_file())
        self.assertTrue(os.access(sh_script, os.X_OK))

    def test_07_cli_execution_and_validate_flag(self):
        """Verifica la ejecución CLI y el flag --validate-only"""
        cmd_gen = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "davinci-resolve-orchestrator" / "scripts" / "resolve_orchestrator.py"),
            "--output", "campaign/resolve/test_cli_manifest.json"
        ]
        p_gen = subprocess.run(cmd_gen, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_gen.returncode, 0, f"CLI error: {p_gen.stderr}")

        cmd_val = [
            "python3",
            str(WORKSPACE_ROOT / ".agents" / "skills" / "post-production" / "davinci-resolve-orchestrator" / "scripts" / "resolve_orchestrator.py"),
            "--output", "campaign/resolve/test_cli_manifest.json",
            "--validate-only"
        ]
        p_val = subprocess.run(cmd_val, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
        self.assertEqual(p_val.returncode, 0)
        self.assertIn("[VALID]", p_val.stdout)

        test_out = WORKSPACE_ROOT / "campaign" / "resolve" / "test_cli_manifest.json"
        if test_out.is_file():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main(verbosity=2)
