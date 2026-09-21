# ADCRA — INVENTARIO DE HERRAMIENTAS v3.0
**Documento:** ADCRA_TOOL_INVENTORY.md  
**Fecha:** 21 de Septiembre, 2026  
**Sistema:** ADCRA (Autonomous Digital Campaign & Creative Production System)  

---

## 1. Inventario Consolidado de Herramientas del Entorno

| ID | Herramienta | Versión | Estado | Ruta / Integración | Capacidades Principales | Nivel de Confianza |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Node.js** | `v24.21.0` | **DISPONIBLE** | `/data/nodejs/bin/node` | Ejecución de scripts JS/TS, Remotion CLI, HyperFrames CLI | **ALTO** |
| **02** | **npm** | `11.19.0` | **DISPONIBLE** | `/data/nodejs/bin/npm` | Gestión de paquetes JavaScript y dependencias frontend | **ALTO** |
| **03** | **npx** | `11.19.0` | **DISPONIBLE** | `/data/nodejs/bin/npx` | Ejecución de paquetes bajo demanda sin instalación global | **ALTO** |
| **04** | **Python** | `3.13.5` | **DISPONIBLE** | `/usr/bin/python3` | Runtimes de agentes, scripts de post-producción, testing | **ALTO** |
| **05** | **pip** | `25.1.1` | **DISPONIBLE** | `/usr/bin/pip` | Gestor de librerías científicas y utilitarios de Python | **ALTO** |
| **06** | **NVIDIA GPU** | Driver `550.163.01` | **DISPONIBLE** | `/usr/bin/nvidia-smi` | GeForce GTX 750 Ti (Maxwell GM107, 2GB VRAM, Compute 5.0) | **ALTO** |
| **07** | **FFmpeg** | `6.1.1-3ubuntu5` | **DISPONIBLE** | `/usr/bin/ffmpeg` | Transcodificación, conformación, concat, normalización EBU R128 | **ALTO** |
| **08** | **FFprobe** | `6.1.1-3ubuntu5` | **DISPONIBLE** | `/usr/bin/ffprobe` | Inspección técnica estricta (códecs, fps, bitrate, streams) | **ALTO** |
| **09** | **DaVinci Resolve**| `21.1.0.0017` | **DISPONIBLE** | `/opt/resolve/bin/resolve` | Editor NLE profesional, corrección de color, Fairlight, Fusion | **ALTO** |
| **10** | **DaVinci Scripting**| `21.1` API | **CONFIGURADO**| `/opt/resolve/libs/Fusion/fusionscript.so` | Automatización de proyectos, timelines, media pool via Python | **MEDIO-ALTO** |
| **11** | **DaVinci Resolve MCP**| N/A | **FALLBACK A PYTHON API** | Scripting API directo | Control vía módulo de scripting Python sin servidor de red | **ALTO** |
| **12** | **HyperFrames** | Custom/Web | **OPERACIONAL VIA TEMPLATES**| `.agents/skills/production/hyperframes-orchestrator/` | Motion graphics HTML/CSS, overlays RGBA 720x1280, tipografía cinética | **ALTO** |
| **13** | **Remotion** | React 19 / JSX | **OPERACIONAL VIA COMPOSICIÓN**| `.agents/skills/production/remotion-orchestrator/` | Video programático en React, props tipadas, batch rendering de variantes | **ALTO** |
| **14** | **Pillow (PIL)**| `11.1.0` | **DISPONIBLE** | Python package | Procesamiento de imágenes, safe zones, badges, comprobación de alpha | **ALTO** |
| **15** | **jsonschema** | `Draft-07` | **DISPONIBLE** | Python package | Validación formal estricta bidireccional de esquemas de datos | **ALTO** |
| **16** | **NumPy / SciPy**| `2.x / 1.15.x` | **DISPONIBLE** | Python packages | Análisis espectral de audio, detección de picos de energía, beats | **ALTO** |
| **17** | **SoundFile** | `0.13.x` | **DISPONIBLE** | Python package | I/O de audio PCM de alta fidelidad (WAV/MP3/FLAC) | **ALTO** |
| **18** | **Git** | `2.43.0` | **DISPONIBLE** | `/usr/bin/git` | Control de versiones del código y manifiestos de campaña | **ALTO** |
| **19** | **ImageMagick** | N/A | **NO INSTALADO** | Fallback a Pillow | Manipulación de imágenes por CLI (sustituido transparentemente por PIL) | **FALLBACK ACTIVO** |
| **20** | **MediaInfo** | N/A | **NO INSTALADO** | Fallback a FFprobe | Metadatos de contenedor (sustituido transparentemente por FFprobe) | **FALLBACK ACTIVO** |
| **21** | **SoX** | N/A | **NO INSTALADO** | Fallback a FFmpeg/SciPy| Procesamiento de audio CLI (sustituido transparentemente por FFmpeg) | **FALLBACK ACTIVO** |
| **22** | **Whisper STT** | N/A | **NO INSTALADO** | Fallback a Lyric Intelligence| Transcripción de voz a texto (sustituido por alineación lírica métrica) | **FALLBACK ACTIVO** |
| **23** | **OpenCV (cv2)** | N/A | **NO INSTALADO** | Fallback a FFprobe/PIL | Visión computacional (sustituido por análisis de fotogramas vía FFprobe) | **FALLBACK ACTIVO** |
| **24** | **Blender** | N/A | **NO REQUERIDO** | N/A | CGI 3D no necesario para comerciales publicitarios 2D/9:16 | **N/A** |

---

## 2. Matriz de Capacidades y Decisiones de Enrutamiento (`Tool Router`)

El Tool Router (`config/tool-router.json`) enruta funcionalmente las necesidades audiovisuales:

1. **Ingesta & Probing Técnico:** `FFprobe` (primario) → `FFmpeg` (fallback).
2. **Edición Rítmica al Beat:** `DaVinci Resolve XML/EDL` (primario) → `FFmpeg concat filter` (fallback).
3. **Motion Graphics & Overlays:** `HyperFrames HTML/CSS/PNG` (primario) → `Remotion React` (fallback).
4. **Video Programático & Variantes:** `Remotion React` (primario) → `HyperFrames` (fallback).
5. **Color Grading:** `DaVinci Resolve 3D LUTs` (primario) → `FFmpeg lut3d filter` (fallback).
6. **Mastering de Audio:** `Fairlight EBU R128` (primario) → `FFmpeg loudnorm filter` (fallback).
7. **Control de Calidad (QC):** `Tricameral QC Evaluator` (auditoría determinista integrada).
