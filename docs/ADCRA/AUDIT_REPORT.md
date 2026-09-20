# ADCRA — Auditoría Integral del Entorno (Fase 0)

**Fecha:** 2026-09-19T02:00:00-03:00  
**Sistema:** ADCRA — Autonomous Digital Campaign & Creative Production System  
**Auditor:** Agente de Ingeniería e Infraestructura ADCRA  
**Estado:** COMPLETADO  

---

## 1. Resumen Ejecutivo

Se ha completado la auditoría exhaustiva del entorno de ejecución, hardware, aceleración gráfica, dependencias multimedia y tooling para la puesta en marcha de **ADCRA (Autonomous Digital Campaign & Creative Production System)**.

### Hallazgos Críticos Principales:
1. **DaVinci Resolve 21.1:** Se encuentra instalado y operativo (`v21.1.0.0017`). Inicialmente sufría congelamientos en la carga del módulo Color debido a la ejecución sobre `Mesa llvmpipe` en sesiones remotas XRDP y falta de permisos en `/dev/dri/renderD128`. Ambos problemas fueron resueltos mediante la asignación al grupo `render`, reglas persistentes de `udev` y un wrapper con `__NV_PRIME_RENDER_OFFLOAD=1` y `__GLX_VENDOR_LIBRARY_NAME=nvidia`.
2. **GPU NVIDIA GeForce GTX 750 Ti (Maxwell GM107):** Cuenta con 4 GB de VRAM y Compute Capability 5.0. DaVinci Resolve 21 no soporta CUDA en arquitecturas inferiores a Pascal (CC 6.0+), por lo que opera obligatoriamente mediante **OpenCL 3.0** (configurado con éxito en `config.dat`).
3. **Runtimes Base:** Se cuenta con **Node.js v24.21.0**, **npm 11.19.0**, **npx 11.19.0** y **Python 3.13.5**.
4. **Brechas de Herramientas Críticas (Gaps):**
   - `ffmpeg` y `ffprobe` no están presentes como binarios CLI (están las librerías `libavcodec61`, disponibles en los repositorios oficiales de Debian trixie).
   - `remotion` y `hyperframes` no están instalados aún en el workspace.
   - `davinci-resolve-mcp` no está clonado ni registrado como servidor MCP.
   - Herramientas de análisis de audio y visión (`whisper`, `opencv`, `sox`, `librosa`) no están instaladas en Python.

---

## 2. Inspección del Workspace y Estructura Existente

- **Ruta real:** `/data/usuario/Documentos/davinci resolve`
- **Ruta simbólica:** `/home/ablutech/Documentos/davinci resolve`
- **Contenido previo:** Archivo de instalación `DaVinci_Resolve_21.1_Linux.zip` (4.09 GB).
- **Estructura `.agents/skills` y `.agent/skills`:** Inexistente (se creará de acuerdo a la arquitectura modular en la Fase 1).
- **`AGENTS.md`:** Inexistente en el workspace.

---

## 3. Runtimes y Gestores de Paquetes

| Runtime / Herramienta | Versión | Ruta | Estado | Método de Detección |
| :--- | :--- | :--- | :--- | :--- |
| **Node.js** | v24.21.0 | `/data/nodejs/bin/node` | **DISPONIBLE** | `node -v` |
| **npm** | 11.19.0 | `/data/nodejs/bin/npm` | **DISPONIBLE** | `npm -v` |
| **npx** | 11.19.0 | `/data/nodejs/bin/npx` | **DISPONIBLE** | `npx -v` |
| **pnpm** | No disponible | — | NO INSTALADO | `which pnpm` |
| **bun** | No disponible | — | NO INSTALADO | `which bun` |
| **Python** | 3.13.5 | `/usr/bin/python3` | **DISPONIBLE** | `python3 --version` |
| **pip** | 25.1.1 | `/usr/bin/pip3` | **DISPONIBLE** | `pip3 --version` |
| **uv** | No disponible | — | NO INSTALADO | `which uv` |

---

## 4. Hardware Gráfico y Aceleración

### 4.1. GPU Principal
- **Modelo:** NVIDIA Corporation GM107 [GeForce GTX 750 Ti] (rev a2)
- **VRAM Total:** 4096 MiB (4 GB GDDR5)
- **Versión del Driver:** `550.163.01`
- **Versión CUDA Driver API:** `12.4`
- **Compute Capability:** `5.0`
- **Compilador CUDA (`nvcc`):** No instalado

### 4.2. Capacidades de Cómputo y Video
- **OpenCL:** Plataforma `NVIDIA CUDA`, dispositivo `GeForce GTX 750 Ti`, OpenCL 3.0. Funcionamiento verificado con creación de contextos y `cl_khr_gl_sharing`.
- **OpenGL:** 4.6.0 NVIDIA 550.163.01 bajo PRIME Render Offload.
- **NVDEC / NVENC:** El silicio GM107 posee codificador H.264 de primera generación. DaVinci Resolve 21 no soporta decodificación por hardware en Maxwell ni las versiones modernas de NvEncodeAPI. El procesamiento se realiza vía CPU/OpenCL.
- **Limitación crítica documentada:** DaVinci Resolve debe mantenerse configurado en `Local.GPU.Mode = OpenCL` para evitar diálogos de error de CUDA.

---

## 5. Motores y Herramientas de Edición Audiovisual

### 5.1. DaVinci Resolve
- **Versión:** `21.1.0.0017 (Linux/Clang x86_64)`
- **Ubicación del ejecutable:** `/opt/resolve/bin/resolve` (wrapper bash que inyecta `__NV_PRIME_RENDER_OFFLOAD=1` y `__GLX_VENDOR_LIBRARY_NAME=nvidia`) -> binario real `/opt/resolve/bin/resolve.bin`.
- **Scripting API:** Módulo Python `DaVinciResolveScript.py` y librería `fusionscript.so` presentes en `/opt/resolve/Developer/Scripting/Modules/` y `/opt/resolve/libs/Fusion/`.
- **Estado operativo:** Totalmente funcional. Abre directamente en el Organizador de Proyectos (*Project Manager*).

### 5.2. DaVinci Resolve MCP
- **Estado:** NO INSTALADO.
- **Objetivo:** Integrar el servidor MCP de Samuel Gursky (`https://github.com/samuelgursky/davinci-resolve-mcp`) para permitir que las Skills de ADCRA controlen timelines, Media Pool, Color y Fairlight de forma autónoma con verificación formal de respuestas.

### 5.3. Remotion
- **Estado:** NO INSTALADO.
- **Capacidad esperada:** Motor de video programático en React para composiciones masivas, variantes y renderizado por lotes.
- **Viabilidad:** 100% compatible gracias a la presencia de Node.js v24 y npm 11.

### 5.4. HyperFrames
- **Estado:** NO INSTALADO.
- **Capacidad esperada:** Motion graphics HTML, flujos music-to-video y animaciones CSS/JS de alta fidelidad.
- **Fuente de referencia:** `https://github.com/heygen-com/hyperframes`.
- **Viabilidad:** 100% compatible mediante Node.js/npx.

---

## 6. Herramientas CLI Multimedia y Análisis

| Herramienta | Estado | Disponible en Repositorios | Propósito en ADCRA |
| :--- | :--- | :--- | :--- |
| **FFmpeg** | NO INSTALADO | Sí (`7:7.1.5` en Debian Trixie) | Conformado técnico, render headless, extracción de audio/frames |
| **FFprobe** | NO INSTALADO | Sí (incluido con ffmpeg) | Media probing, análisis de FPS, duración y códecs |
| **ImageMagick** | NO INSTALADO (solo infraestructura común) | Sí (`8:7.1.1.43`) | Procesamiento y ajuste de assets gráficos estáticos |
| **SoX** | NO INSTALADO | Sí (`14.4.2`) | Procesamiento y análisis rápido de espectro sonoro |
| **MediaInfo** | NO INSTALADO | Sí (`25.04`) | Extracción de metadatos exhaustivos para el Quality Control |
| **Blender** | NO INSTALADO | Sí (vía apt) | Motion graphics 3D y elementos volumétricos |

---

## 7. Modelos Locales e Inteligencia Artificial

- **Whisper (STT / Letra de canciones / Timing de voz):** No instalado. Requiere instalación de `openai-whisper` en un virtualenv Python o uso del binario standalone `whisper.cpp`.
- **OpenCV (`cv2`):** No instalado. Esencial para análisis de estabilidad, cortes de plano y colorimetría en la Fase 8.
- **ComfyUI:** No instalado. Dada la memoria VRAM disponible (4 GB), la generación intensiva de video por difusión local presentará restricciones de memoria; se priorizará composición procedural, Motion Graphics y assets pre-existentes o remotos.

---

## 8. Conectividad y Almacenamiento

- **Conectividad a Internet:** Activa y verificada (GitHub y registros npm accesibles por HTTP/2).
- **Espacio en Disco:**
  - Partición raíz (`/`): 61 GB disponibles.
  - Partición de datos y workspace (`/data`): 34 GB disponibles.
- **Seguridad:** No se detectaron secretos, tokens ni variables privadas expuestas en logs o repositorios.

---

## 9. Inventario Detallado de Herramientas

El inventario estructurado formal con estados, limitaciones, dependencias y niveles de confianza ha sido generado y validado en:
`config/tool-inventory.json`

---

## 10. Conclusión y Preparación para la Fase 1

El entorno cuenta con los runtimes centrales necesarios (Node.js 24 y Python 3.13) y DaVinci Resolve 21.1 acelerado por hardware y estabilizado. 

Antes de iniciar la producción en fases avanzadas, se requerirá la instalación de utilidades de conformado (`ffmpeg`, `ffprobe`) y la inicialización de los orquestadores. La Fase 0 queda completada sin bloqueos críticos pendientes.
