---
name: tool-discovery
description: Habilidad de descubrimiento e inspección activa de herramientas de renderizado, hardware y software en el entorno ADCRA. Detecta versiones, rutas, estado operativo de GPU y disponibilidad de motores audiovisuales.
---

# Tool Discovery — Detección e Inspección de Herramientas

La habilidad **Tool Discovery** se encarga de explorar, verificar y mantener actualizado el inventario dinámico de herramientas y motores audiovisuales disponibles en la máquina anfitriona.

---

## 1. Responsabilidades Principales

1. **Inspección en Tiempo Real:**  
   Verificar binarios en PATH y rutas estándar (`/opt/resolve/bin/resolve`, `/data/nodejs/bin/`, `/usr/bin/`).
2. **Detección de Aceleración por Hardware:**  
   Comprobar disponibilidad de GPU NVIDIA, librerías OpenCL (`libOpenCL.so.1`) y soporte OpenGL PRIME Render Offload.
3. **Mantenimiento del Inventario:**  
   Sincronizar el estado de ejecución con `config/tool-inventory.json` sin alterar información histórica no reproducible.
4. **Alimentación del Enrutador:**  
   Proporcionar al **Tool Router** un mapa determinista de qué herramientas están realmente operativas y cuáles requieren fallback o instalación.

---

## 2. Herramientas Auditadas

| Herramienta | Método de Detección | Ruta Estándar / Comando |
| :--- | :--- | :--- |
| **DaVinci Resolve** | Binario ejecutable | `/opt/resolve/bin/resolve` |
| **Node.js** | CLI version check | `node -v` (v24.21.0 en `/data/nodejs/bin/node`) |
| **npm / npx** | CLI version check | `npm -v`, `npx -v` |
| **Python** | CLI version check | `python3 --version` |
| **FFmpeg / FFprobe**| Which check | `which ffmpeg`, `which ffprobe` |
| **NVIDIA GPU** | nvidia-smi / ctypes | `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader` |
| **OpenCL** | Ctypes libOpenCL | `clGetPlatformIDs`, `clGetDeviceIDs` |
| **Remotion** | npm list / npx | `npx remotion --version` / `npm list remotion` |
| **HyperFrames** | CLI / node module | `npx hyperframes --version` / local package |

---

## 3. Scripts Asociados

- `scripts/discover_tools.py`:
  - Ejecuta pruebas no invasivas en subprocesos para cada herramienta.
  - Genera un resumen estructurado en JSON con flags: `installed`, `version`, `path`, `operational`, `supports_gpu`.
  - Permite verificar herramientas individuales o el sistema completo.
