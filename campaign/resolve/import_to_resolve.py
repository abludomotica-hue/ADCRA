#!/usr/bin/env python3
# ADCRA — DaVinci Resolve Live Automation Script
# Este script se ejecuta para conectar con DaVinci Resolve en ejecución e importar el proyecto.

import sys
import os
from pathlib import Path

# Añadir módulos de Resolve
sys.path.append("/opt/resolve/Developer/Scripting/Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = "/opt/resolve/libs/Fusion/fusionscript.so"

try:
    import DaVinciResolveScript as dvr
except ImportError as e:
    print(f"[ERROR] No se pudo cargar DaVinciResolveScript: {e}", file=sys.stderr)
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

project_name = "Locos_Materos_2026_Campaign"
project = pm.LoadProject(project_name)
if not project:
    project = pm.CreateProject(project_name)
    print(f"[CREATED] Nuevo proyecto creado: {project_name}")
else:
    print(f"[LOADED] Proyecto existente cargado: {project_name}")

# Configurar resolución de timeline vertical (720x1280 @ 24fps)
project.SetSetting("timelineResolutionWidth", "720")
project.SetSetting("timelineResolutionHeight", "1280")
project.SetSetting("timelineFrameRate", "24.0")

mp = project.GetMediaPool()
root_folder = mp.GetRootFolder()

# Crear Bins jerárquicos
bins = ["01_Footage", "02_Audio", "03_Motion_Graphics", "04_Timelines"]
created_bins = {}
for b_name in bins:
    sub_folder = mp.AddSubFolder(root_folder, b_name)
    created_bins[b_name] = sub_folder
    print(f" - Bin creado: {b_name}")

# Importar clips a sus respectivos Bins
clips_data = [{"clip_name": "Escena 01 Ya est\u00e1 sonando el hervidor.mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 01 Ya est\u00e1 sonando el hervidor.mp4", "media_type": "video", "scene_id": "scene_01"}, {"clip_name": "Escena 02 Macro de yerba y bombilla.mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 02 Macro de yerba y bombilla.mp4", "media_type": "video", "scene_id": "scene_02"}, {"clip_name": "Escena 03 El sol asoma en la cordillera.mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 03 El sol asoma en la cordillera.mp4", "media_type": "video", "scene_id": "scene_03"}, {"clip_name": "Escena 04 Cebando arranca todo Chile.mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 04 Cebando arranca todo Chile.mp4", "media_type": "video", "scene_id": "scene_04"}, {"clip_name": "Escena 05 Caminando por el barrio..mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 05 Caminando por el barrio..mp4", "media_type": "video", "scene_id": "scene_05"}, {"clip_name": "Escena 06 Transici\u00f3n trabajohogar..mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 06 Transici\u00f3n trabajohogar..mp4", "media_type": "video", "scene_id": "scene_06"}, {"clip_name": "Escena 07 Estudiantes en la universidad..mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 07 Estudiantes en la universidad..mp4", "media_type": "video", "scene_id": "scene_07"}, {"clip_name": "Escena 08 Primer plano de mate y sorbo..mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 08 Primer plano de mate y sorbo..mp4", "media_type": "video", "scene_id": "scene_08"}, {"clip_name": "Escena 09 D\u00f3nde est\u00e1s t\u00fa.mp4", "bin": "01_Footage", "file_path": "Recursos/videos/Escena 09 D\u00f3nde est\u00e1s t\u00fa.mp4", "media_type": "video", "scene_id": "scene_09"}, {"clip_name": "Entre_mates_y_sol.mp3", "bin": "02_Audio", "file_path": "Recursos/Audios/Entre_mates_y_sol.mp3", "media_type": "audio", "scene_id": "all"}, {"clip_name": "overlay_scene_01.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_01.png", "media_type": "graphic", "scene_id": "scene_01"}, {"clip_name": "overlay_scene_02.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_02.png", "media_type": "graphic", "scene_id": "scene_02"}, {"clip_name": "overlay_scene_03.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_03.png", "media_type": "graphic", "scene_id": "scene_03"}, {"clip_name": "overlay_scene_04.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_04.png", "media_type": "graphic", "scene_id": "scene_04"}, {"clip_name": "overlay_scene_05.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_05.png", "media_type": "graphic", "scene_id": "scene_05"}, {"clip_name": "overlay_scene_06.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_06.png", "media_type": "graphic", "scene_id": "scene_06"}, {"clip_name": "overlay_scene_07.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_07.png", "media_type": "graphic", "scene_id": "scene_07"}, {"clip_name": "overlay_scene_08.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_08.png", "media_type": "graphic", "scene_id": "scene_08"}, {"clip_name": "overlay_scene_09.png", "bin": "03_Motion_Graphics", "file_path": "campaign/motion-graphics/renders/overlay_scene_09.png", "media_type": "graphic", "scene_id": "scene_09"}]
for c in clips_data:
    target_bin = created_bins.get(c["bin"], root_folder)
    mp.SetCurrentFolder(target_bin)
    f_path = str((Path("/data/usuario/Documentos/davinci resolve") / c["file_path"]).resolve())
    if os.path.exists(f_path):
        mp.ImportMedia([f_path])
        print(f"   + [{c['bin']}] Importado: {c['clip_name']}")

# Importar Timeline desde FCP7 XML
xml_path = str((Path("/data/usuario/Documentos/davinci resolve") / "campaign/timeline/locos_materos_edit.xml").resolve())
if os.path.exists(xml_path):
    mp.SetCurrentFolder(created_bins.get("04_Timelines", root_folder))
    timeline = mp.ImportTimelineFromFile(xml_path)
    if timeline:
        print(f"[SUCCESS] Timeline '{manifest['timelines'][0]['timeline_name']}' importada exitosamente.")
    else:
        print(f"[WARN] No se pudo crear timeline desde XML automáticamente. Importar manualmente desde: {xml_path}")

print("[DONE] Estructuración y conformación en DaVinci Resolve completada.")
