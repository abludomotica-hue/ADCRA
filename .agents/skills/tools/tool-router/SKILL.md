---
name: tool-router
description: Enrutador dinámico de herramientas y motores audiovisuales para ADCRA. Asigna la herramienta óptima según la necesidad técnica y creativa (motion graphics, timeline, color grading, Fairlight, transcodificación, QC) con resolución de alternativas y fallbacks.
---

# Tool Router — Enrutador Dinámico de Herramientas

El **Tool Router** es el componente de despacho técnico de ADCRA. Su responsabilidad es mapear cada requerimiento operativo de una campaña o escena hacia el motor de render, edición o análisis adecuado, garantizando redundancia y continuidad operativa mediante políticas de fallback documentadas en `config/tool-router.json`.

---

## 1. Matriz de Mapeo de Necesidades

| Necesidad Creativa / Técnica | Herramienta Primaria | Alternativa Declarada | Criterio de Selección | Requiere GPU |
| :--- | :--- | :--- | :--- | :---: |
| **HTML motion graphics** | HyperFrames | Remotion | Animaciones basadas en web y timeline ligero | No |
| **Motion graphics** | HyperFrames | Remotion | Motion design vectorial/HTML optimizado | No |
| **Video programático React**| Remotion | HyperFrames | Árbol de componentes React con props tipadas | No |
| **Variantes masivas** | Remotion | HyperFrames | Batch rendering parametrizado con datasets JSON | No |
| **Beat-synced composition** | HyperFrames | Remotion | Workflow `/music-to-video` alineado a BPM | No |
| **Timeline profesional** | DaVinci Resolve | FFmpeg | Edición multicapa broadcast y multipista | Sí |
| **Color grading** | DaVinci Resolve | *(Ninguna)* | Estándar de industria (Color Wheels, LUTs, Scopes) | Sí |
| **Fairlight/audio** | DaVinci Resolve | FFmpeg | Mezcla multipista, EQ y masterización broadcast | No |
| **Fusion** | DaVinci Resolve | *(Ninguna)* | Compositing por nodos, keying y tracking avanzado | Sí |
| **Conversión técnica** | FFmpeg | *(Ninguna)* | Transcodificación determinista y rápida | No |
| **Media probing** | FFprobe | DaVinci Resolve | Extracción instantánea de metadatos de streams | No |
| **QC técnico** | FFprobe/FFmpeg | DaVinci Resolve | Detección de black frames, silencio y conformance | No |
| **Render HTML** | HyperFrames | *(Ninguna)* | Renderizado headless de escenas web interactivas | No |
| **Render React** | Remotion | *(Ninguna)* | Renderizado headless React con multi-threading | No |

---

## 2. Política de Evaluación y Fallback

1. **Consulta del Estado:**  
   El enrutador consulta en tiempo de ejecución a `tool-discovery` para conocer la disponibilidad real de la herramienta primaria.
2. **Despacho Primario:**  
   Si la herramienta primaria está instalada y operativa, se selecciona con estado `ROUTED_PRIMARY`.
3. **Activación de Alternativa (Fallback):**  
   Si la herramienta primaria no se encuentra instalada o falla tras verificación:
   - Se evalúa si existe una `alternativa` declarada en `config/tool-router.json`.
   - Si la alternativa está disponible, se despacha con estado `ROUTED_FALLBACK` y se registra una advertencia en el log de ejecución.
4. **Alerta de Indisponibilidad (`UNAVAILABLE`):**  
   Si ni la herramienta primaria ni su alternativa están disponibles, el enrutador emite una excepción estructurada detallando los comandos de instalación requeridos para desbloquear la necesidad.

---

## 3. Scripts e Interfaz CLI

- `scripts/route_tool.py`:
  - `route(need: str) -> dict`: Función invocable desde Python por otras habilidades (Director, Storyboard, Producción).
  - `--need "<nombre_necesidad>"`: Enruta una necesidad específica desde terminal.
  - `--list-routes`: Muestra la matriz completa de enrutamiento.
  - `--audit-routes`: Audita las 14 rutas contra el estado real del sistema y reporta cuántas pueden resolverse de inmediato y cuáles requieren dependencias.
