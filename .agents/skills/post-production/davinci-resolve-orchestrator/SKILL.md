---
name: davinci-resolve-orchestrator
description: Orquestador de integración con DaVinci Resolve para creación de proyectos, conformación de Media Pool, estructuración de timelines XML/EDL y configuración de render en GPU OpenCL.
version: 1.0.0
domain: post-production
tools_integrated:
  - DaVinci Resolve 21.1 (Linux x86_64)
  - DaVinciResolveScript Python Module
  - Blackmagic Fusion API (fusionscript.so)
contracts:
  input:
    - campaign/timeline/timeline.json
    - campaign/timeline/locos_materos_edit.xml
    - campaign/timeline/locos_materos_edit.edl
    - campaign/assets/asset-inventory.json
  output:
    - campaign/resolve/resolve-project-manifest.json
    - campaign/resolve/import_to_resolve.py
    - campaign/resolve/setup_project.sh
schema: config/resolve-integration-schema.json
---

# DaVinci Resolve Orchestrator — Integración Profesional de Postproducción

## 1. Misión
Integrar el pipeline autónomo de ADCRA con el motor de postproducción cinematográfica de **DaVinci Resolve 21.1**. Provee control programático sobre la creación de proyectos, estructuración jerárquica del Media Pool en carpetas temáticas (Bins), importación automatizada de secuencias XML/EDL sincronizadas al beat y configuración de renderizado en GPU NVIDIA GeForce GTX 750 Ti con aceleración OpenCL.

---

## 2. Configuración del Entorno de Scripting en Linux

DaVinci Resolve expone su API de automatización en Python a través de la biblioteca nativa `fusionscript.so`.

- **Módulo Python:** `/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py`
- **Biblioteca Dinámica:** `/opt/resolve/libs/Fusion/fusionscript.so`
- **Variables de Entorno Clave:**
  ```bash
  export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
  export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
  export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
  ```
- **Wrapper de Ejecución GPU Offload:**
  ```bash
  /opt/resolve/bin/resolve
  # Ejecuta con __NV_PRIME_RENDER_OFFLOAD=1 y __GLX_VENDOR_LIBRARY_NAME=nvidia
  ```

---

## 3. Estructura Jerárquica del Media Pool

Para garantizar el orden profesional exigido por estándares de postproducción, el orquestador organiza los activos en 4 Bins principales:
1. `01_Footage`: Los 9 clips de video brutos en resolución 720x1280 (9:16) a 24 fps.
2. `02_Audio`: Pistas sonoras maestras (`Entre_mates_y_sol.mp3`).
3. `03_Motion_Graphics`: Overlays cinéticos transparentes RGBA exportados en la Fase 9.
4. `04_Timelines`: Secuencia principal conformada (`LocosMateros_BeatSynced_Master`).

---

## 4. Modos de Operación

1. **Modo Live API:**
   Cuando DaVinci Resolve se encuentra abierto en el servidor X11, el script interactúa directamente con la instancia en memoria mediante `bmd.scriptapp('Resolve')`, creando el proyecto, importando los Bins y cargando el timeline XML de forma transparente.
2. **Modo Conformed Project Package (Headless / Offline):**
   Garantiza el 100% de reproducibilidad y determinismo. Empaqueta el manifiesto formal `resolve-project-manifest.json`, verifica la integridad de los medios y genera el script de importación con un clic `import_to_resolve.py` para su ejecución inmediata por el operador o en render automatizado.

---

## 5. Comandos de Operación CLI

- **Generación y Validación del Proyecto Resolve:**
  ```bash
  python3 .agents/skills/post-production/davinci-resolve-orchestrator/scripts/resolve_orchestrator.py
  ```
- **Validación Únicamente:**
  ```bash
  python3 .agents/skills/post-production/davinci-resolve-orchestrator/scripts/resolve_orchestrator.py --validate-only
  ```
