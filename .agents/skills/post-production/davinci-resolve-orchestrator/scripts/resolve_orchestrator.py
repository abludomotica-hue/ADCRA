#!/usr/bin/env python3
"""
ADCRA — DaVinci Resolve Orchestrator
Integra el pipeline de ADCRA con la Scripting API de DaVinci Resolve 21.1 en Linux,
conforma la estructura del Media Pool, vincula secuencias XML/EDL y prepara la automatización de render.
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
import jsonschema

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

# Configurar rutas de scripting de DaVinci Resolve en Linux
RESOLVE_SCRIPT_MODULES = "/opt/resolve/Developer/Scripting/Modules"
RESOLVE_SCRIPT_LIB = "/opt/resolve/libs/Fusion/fusionscript.so"
if RESOLVE_SCRIPT_MODULES not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_MODULES)
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB

def check_resolve_environment() -> tuple[bool, bool, object]:
    fusionscript_loaded = False
    resolve_app = None
    resolve_binary_exists = os.path.isfile("/opt/resolve/bin/resolve")

    try:
        import DaVinciResolveScript as dvr
        fusionscript_loaded = True
        resolve_app = dvr.scriptapp("Resolve")
    except Exception:
        pass

    return resolve_binary_exists, fusionscript_loaded, resolve_app

def generate_resolve_script(resolve_dir: Path, manifest: dict):
    resolve_dir.mkdir(parents=True, exist_ok=True)

    py_script = f"""#!/usr/bin/env python3
# ADCRA — DaVinci Resolve Live Automation Script
# Este script se ejecuta para conectar con DaVinci Resolve en ejecución e importar el proyecto.

import sys
import os
from pathlib import Path

# Añadir módulos de Resolve
sys.path.append("{RESOLVE_SCRIPT_MODULES}")
os.environ["RESOLVE_SCRIPT_LIB"] = "{RESOLVE_SCRIPT_LIB}"

try:
    import DaVinciResolveScript as dvr
except ImportError as e:
    print(f"[ERROR] No se pudo cargar DaVinciResolveScript: {{e}}", file=sys.stderr)
    sys.exit(1)

resolve = dvr.scriptapp("Resolve")
if not resolve:
    print("[ERROR] DaVinci Resolve no está en ejecución. Abra DaVinci Resolve e intente nuevamente.", file=sys.stderr)
    sys.exit(2)

print("[CONNECTED] Conectado exitosamente a DaVinci Resolve API.")
pm = resolve.GetProjectManager()
if not pm:
    print("[ERROR] No se pudo obtener ProjectManager.", file=sys.stderr)
    sys.exit(3)

project_name = "{manifest['project_name']}"
project = pm.LoadProject(project_name)
if not project:
    project = pm.CreateProject(project_name)
    print(f"[CREATED] Nuevo proyecto creado: {{project_name}}")
else:
    print(f"[LOADED] Proyecto existente cargado: {{project_name}}")

# Configurar resolución de timeline vertical (720x1280 @ 24fps)
project.SetSetting("timelineResolutionWidth", "{manifest['timeline_settings']['width']}")
project.SetSetting("timelineResolutionHeight", "{manifest['timeline_settings']['height']}")
project.SetSetting("timelineFrameRate", "{manifest['timeline_settings']['frame_rate']}")

mp = project.GetMediaPool()
root_folder = mp.GetRootFolder()

# Crear Bins jerárquicos
bins = {json.dumps(manifest['media_pool_structure']['bins'])}
created_bins = {{}}
for b_name in bins:
    sub_folder = mp.AddSubFolder(root_folder, b_name)
    created_bins[b_name] = sub_folder
    print(f" - Bin creado: {{b_name}}")

# Importar clips a sus respectivos Bins
clips_data = {json.dumps(manifest['media_pool_structure']['clips_registered'])}
for c in clips_data:
    target_bin = created_bins.get(c["bin"], root_folder)
    mp.SetCurrentFolder(target_bin)
    f_path = str((Path("{WORKSPACE_ROOT}") / c["file_path"]).resolve())
    if os.path.exists(f_path):
        mp.ImportMedia([f_path])
        print(f"   + [{{c['bin']}}] Importado: {{c['clip_name']}}")

# Importar Timeline desde FCP7 XML
xml_path = str((Path("{WORKSPACE_ROOT}") / "{manifest['timelines'][0]['source_xml']}").resolve())
if os.path.exists(xml_path):
    mp.SetCurrentFolder(created_bins.get("04_Timelines", root_folder))
    timeline = mp.ImportTimelineFromFile(xml_path)
    if timeline:
        print(f"[SUCCESS] Timeline '{{manifest['timelines'][0]['timeline_name']}}' importada exitosamente.")
    else:
        print(f"[WARN] No se pudo crear timeline desde XML automáticamente. Importar manualmente desde: {{xml_path}}")

print("[DONE] Estructuración y conformación en DaVinci Resolve completada.")
"""
    (resolve_dir / "import_to_resolve.py").write_text(py_script, encoding="utf-8")
    (resolve_dir / "import_to_resolve.py").chmod(0o755)

    sh_script = f"""#!/usr/bin/env bash
# ADCRA — Setup DaVinci Resolve Project Launcher
set -e
export RESOLVE_SCRIPT_API="{RESOLVE_SCRIPT_MODULES}"
export RESOLVE_SCRIPT_LIB="{RESOLVE_SCRIPT_LIB}"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API"

python3 "{resolve_dir / 'import_to_resolve.py'}"
"""
    (resolve_dir / "setup_project.sh").write_text(sh_script, encoding="utf-8")
    (resolve_dir / "setup_project.sh").chmod(0o755)

def build_resolve_manifest() -> dict:
    timeline_path = WORKSPACE_ROOT / "campaign" / "timeline" / "timeline.json"
    asset_path = WORKSPACE_ROOT / "campaign" / "assets" / "asset-inventory.json"
    motion_path = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "motion-manifest.json"

    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)
    with open(asset_path, "r", encoding="utf-8") as f:
        asset_data = json.load(f)
    with open(motion_path, "r", encoding="utf-8") as f:
        motion_data = json.load(f)

    res_binary, fusionscript_ok, resolve_app = check_resolve_environment()

    # Clips para Media Pool
    clips_registered = []

    # 1. Video Footage -> Bin 01_Footage
    for v in asset_data.get("video_assets", []):
        clips_registered.append({
            "clip_name": v["filename"],
            "bin": "01_Footage",
            "file_path": v["relative_path"],
            "media_type": "video",
            "scene_id": v.get("cinematography", {}).get("scene_id", "unknown")
        })

    # 2. Audio Master -> Bin 02_Audio
    clips_registered.append({
        "clip_name": "Entre_mates_y_sol.mp3",
        "bin": "02_Audio",
        "file_path": "Recursos/Audios/Entre_mates_y_sol.mp3",
        "media_type": "audio",
        "scene_id": "all"
    })

    # 3. Motion Graphics Overlays -> Bin 03_Motion_Graphics
    for ov in motion_data.get("overlays", []):
        clips_registered.append({
            "clip_name": Path(ov["output_asset_path"]).name,
            "bin": "03_Motion_Graphics",
            "file_path": ov["output_asset_path"],
            "media_type": "graphic",
            "scene_id": ov["scene_id"]
        })

    mode = "live_api" if resolve_app is not None else "conformed_project_package"

    manifest = {
        "campaign_id": "camp_locos_materos_2026",
        "project_name": "Locos_Materos_2026_Campaign",
        "timeline_settings": {
            "width": 720,
            "height": 1280,
            "frame_rate": 24.0,
            "color_science_mode": "DaVinci YRGB",
            "working_color_space": "Rec.709 / Gamma 2.4"
        },
        "media_pool_structure": {
            "bins": [
                "01_Footage",
                "02_Audio",
                "03_Motion_Graphics",
                "04_Timelines"
            ],
            "clips_registered": clips_registered
        },
        "timelines": [
            {
                "timeline_name": "LocosMateros_BeatSynced_Master",
                "source_xml": "campaign/timeline/locos_materos_edit.xml",
                "source_edl": "campaign/timeline/locos_materos_edit.edl",
                "tracks_count": {
                    "video": 2,
                    "audio": 1
                }
            }
        ],
        "render_settings": {
            "target_format": "QuickTime",
            "video_codec": "H264",
            "audio_codec": "AAC",
            "bitrate_kbps": 12000,
            "render_preset": "ADCRA Vertical 9:16 Master"
        },
        "execution_status": {
            "mode": mode,
            "resolve_binary": "/opt/resolve/bin/resolve" if res_binary else "not_found",
            "fusionscript_loaded": fusionscript_ok,
            "validation_status": "passed"
        }
    }
    return manifest

def validate_resolve_manifest(manifest: dict):
    schema_path = WORKSPACE_ROOT / "config" / "resolve-integration-schema.json"
    if not schema_path.is_file():
        raise FileNotFoundError(f"Esquema no encontrado: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=manifest, schema=schema)

def main():
    parser = argparse.ArgumentParser(description="ADCRA DaVinci Resolve Orchestrator CLI")
    parser.add_argument("--output", "-o", default="campaign/resolve/resolve-project-manifest.json", help="Ruta de salida JSON")
    parser.add_argument("--validate-only", action="store_true", help="Solo valida el manifiesto existente")
    args = parser.parse_args()

    out_file = WORKSPACE_ROOT / args.output
    resolve_dir = WORKSPACE_ROOT / "campaign" / "resolve"

    if args.validate_only:
        if not out_file.is_file():
            print(f"[ERROR] Archivo no encontrado: {out_file}", file=sys.stderr)
            sys.exit(1)
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        validate_resolve_manifest(data)
        print(f"[VALID] El manifiesto {out_file} cumple 100% con config/resolve-integration-schema.json")
        return

    print("[RESOLVE] Conformando proyecto DaVinci Resolve, Bins y Timeline XML...")
    manifest = build_resolve_manifest()

    try:
        validate_resolve_manifest(manifest)
        print("[SUCCESS] Manifiesto de Resolve validado contra config/resolve-integration-schema.json")
    except jsonschema.ValidationError as e:
        print(f"[ERROR] Validación fallida del manifiesto: {e.message}", file=sys.stderr)
        sys.exit(2)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    generate_resolve_script(resolve_dir, manifest)

    print(f"[SAVED] Manifiesto guardado en: {out_file}")
    print(f"[SAVED] Script de automatización: {resolve_dir / 'import_to_resolve.py'}")
    print(f"[SAVED] Launcher bash: {resolve_dir / 'setup_project.sh'}")
    print(f" - Modo de Ejecución: {manifest['execution_status']['mode']}")
    print(f" - Módulo FusionScript: {'Operativo' if manifest['execution_status']['fusionscript_loaded'] else 'No disponible'}")
    print(f" - Bins Registrados: {len(manifest['media_pool_structure']['bins'])}")
    print(f" - Clips en Media Pool: {len(manifest['media_pool_structure']['clips_registered'])}")

if __name__ == "__main__":
    main()
