# ADCRA — AUDITORÍA TÉCNICA Y ARQUITECTÓNICA v3.0
**Documento:** ADCRA_ARCHITECTURE_AUDIT.md  
**Fecha:** 21 de Septiembre, 2026  
**Sistema:** ADCRA — Creative Operating System & Autonomous Creative Production Platform  
**Objetivo:** Evaluación profunda de la arquitectura actual frente a la arquitectura objetivo de Creative Operating System desacoplado en 5 capas.

---

## 1. Resumen Ejecutivo de la Auditoría

El sistema actual de ADCRA representa una base excepcionalmente sólida y modular:
- **270 pruebas unitarias e integrales pasando al 100%** (159 pruebas de motores backend + 111 pruebas del Intake Studio UI-01 a UI-22).
- **23 habilidades especializadas (`skills`)** organizadas jerárquicamente en `.agents/skills/` con scripts ejecutables y contratos de entrada/salida.
- **20 esquemas formales JSON Schema Draft-07** en `config/` con 100% de cumplimiento bidireccional contra los datos de campaña.
- **Servidor HTTP multi-hilo** (`dashboard_server.py`) con soporte nativo de streaming de video HTTP 206 (Byte-Ranges), endpoints REST para las 22 fases y despacho agéntico.
- **Estudio Web de Campaña** (`web/intake.html`, `web/intake.css`, `web/intake.js`) con Wizard progresivo de 17 pasos, Copy Lab, Storyboard Lab, Aesthetics Studio (Color/Sound/Motion), QC Dashboard, Delivery Center, Historial, Memoria de Cliente, Contratos y Pipeline Release.

No obstante, para evolucionar de un sistema de intake y ensamblaje hacia un **Creative Operating System (COS)** de nivel de agencia autónoma según la especificación v3.0, la arquitectura debe evolucionar desacoplando formalmente sus cinco capas maestras, expandiendo el modelo de datos a un **Campaign Knowledge Graph**, introduciendo el etiquetado epistemológico de fuentes (`CLIENT_INPUT`, `CONFIRMED_FACT`, `AI_INFERENCE`, `AI_RECOMMENDATION`, `UNKNOWN`), y formalizando los contratos de los 21 agentes especializados.

---

## 2. Evaluación de las 5 Capas de la Arquitectura

```text
┌─────────────────────────────────────────────────────────┐
│ 1. ADCRA EXPERIENCE (Creative Operating System)          │
│ Dashboard / Creative Studio / Labs / QC / Delivery     │
└────────────────────────────┬────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│ 2. CAMPAIGN INTELLIGENCE (Campaign Knowledge Graph)     │
│ Brand DNA / Epistemology / Audience / Offer / Insights  │
└────────────────────────────┬────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│ 3. AGENT ORCHESTRATION (21 Specialized Creative Agents) │
│ Director / Strategist / Copy / Story / Sound / QC       │
└────────────────────────────┬────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│ 4. TOOL ROUTER (Agnostic Tool Routing & Fallbacks)      │
│ HyperFrames / Remotion / DaVinci / FFmpeg Matrix        │
└────────────────────────────┬────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────┐
│ 5. MEDIA ENGINE (Deterministic Media Operations)         │
│ Probing / Conformance / Grading / Mixing / Rendering    │
└─────────────────────────────────────────────────────────┘
```

### Capa 1: ADCRA Experience
- **Estado Actual:** Existe un Mission Control Dashboard (`web/index.html`) y un Campaign Intake Studio (`web/intake.html`) con subnavegación Ribbon hacia 10 módulos de estudio.
- **Diagnóstico:** Excelente diseño visual glassmorphic oscuro. Requiere evolucionar de una interfaz de formulario guiado (wizard) a una experiencia unificada de **Creative Studio** con navegación global simplificada (`HOME`, `CAMPAIGNS`, `CLIENTS`, `ASSETS`, `INTELLIGENCE`, `TOOLS`, `ANALYTICS`, `SETTINGS`), Command Palette (`Ctrl+K`), y vista ejecutiva para Directores Creativos.

### Capa 2: Campaign Intelligence (Knowledge Graph)
- **Estado Actual:** El estado se gestiona mediante `draft-session.json`, `campaign-manifest.json`, `campaign-blueprint.json` y `brand-profile-memory.json`.
- **Diagnóstico:** Los campos actuales almacenan valores sin clasificar formalmente la fuente del dato. La arquitectura debe adoptar el modelo **Campaign Knowledge Graph** donde cada nodo posea metadatos epistemológicos: `source` (`CLIENT_INPUT`, `CONFIRMED_FACT`, `AI_INFERENCE`, `AI_RECOMMENDATION`, `UNKNOWN`), `confidence` (`HIGH`, `MEDIUM`, `LOW`), `last_updated`, `approved` y `requires_confirmation`.

### Capa 3: Agent Orchestration
- **Estado Actual:** 7 agentes modelados en telemetría (`campaign-director`, `copywriter`, `beat-editor`, `motion-graphics`, `colorist`, `sound-designer`, `qc-evaluator`) más scripts deterministas en skills.
- **Diagnóstico:** La especificación v3.0 define 21 roles agénticos especializados. La orquestación debe mantener el principio: *agentes para razonamiento, código/scripts para determinismo*. Se formalizarán contratos de agente (`INPUT`, `PROCESS`, `OUTPUT`, `TOOLS`, `CONSTRAINTS`, `FAILURE_MODES`, `HANDOFF`) en `docs/agents/`.

### Capa 4: Tool Router
- **Estado Actual:** Existe `config/tool-router.json` y la skill `.agents/skills/tools/tool-router/` con 14 rutas mapeadas y soporte de fallback (ej. si HyperFrames no está disponible, enrutar a Remotion o FFmpeg).
- **Diagnóstico:** La matriz de enrutamiento es sólida y funcional. Requiere formalizarse en `config/tool-routing.json` con políticas dinámicas de salud de herramientas (`CONNECTED`, `SIMULATION_MODE`, `FALLBACK_ACTIVE`).

### Capa 5: Media Engine
- **Estado Actual:** FFmpeg y FFprobe instalados en `/usr/bin/`; DaVinci Resolve 21.1 instalado en `/opt/resolve/` con API de scripting `fusionscript.so`; Remotion composition en `campaign/remotion/`; HyperFrames templates y renders en `campaign/motion-graphics/`.
- **Diagnóstico:** Completamente operativo. La composición final 9:16 y las 5 variantes sociales se generan con precisión matemática de sampleado a 24 fps, EBU R128 (-14 LUFS) y safe zones verificadas.

---

## 3. Matriz de Componentes: Qué Evolucionar vs. Qué NO Reemplazar

| Componente | Estado Actual | Decisión | Justificación |
| :--- | :--- | :--- | :--- |
| **Pipeline de Pruebas (270 tests)** | 100% pasando | **PRESERVAR / AMPLIAR** | Garantiza cero regresiones. Ningún cambio debe romper las 270 pruebas existentes. |
| **Servidor `dashboard_server.py`** | HTTP 206, REST endpoints | **EVOLUCIONAR** | Mantener arquitectura multi-hilo, añadir endpoints para Knowledge Graph, Command Palette y Client Memory expandida. |
| **Estudio Web `intake.html/css/js`** | 10 vistas funcionales | **EVOLUCIONAR** | Mantener diseño glassmorphic y componentes existentes, incorporar Command Palette (`Ctrl+K`), epistemología de fuentes y Creative Director View. |
| **Motor de Audio `analyze_audio.py`** | 107.7 BPM, 118 beats | **EVOLUCIONAR** | Añadir detección explícita de secciones musicales (`INTRO`, `VERSE`, `CHORUS`, `CLIMAX`, `OUTRO`) vinculadas al storyboard. |
| **Motor de Copy `generate_copy.py`** | 5 variantes por escena | **EVOLUCIONAR** | Incorporar regla de economía verbal ("si eliminar el texto no reduce el impacto, eliminarlo") y opción `NO_TEXT`. |
| **Motor de Storyboard `build_storyboard.py`** | 9 escenas proporcionales | **EVOLUCIONAR** | Añadir campos de `Camera Style`, `Lighting`, `Tool Selected`, `Rationale` y curva de arco dramático (`Story Arc`). |
| **Tricameral QC `evaluate_quality.py`** | Score 100%, 4 pilares | **PRESERVAR / EVOLUCIONAR** | Expandir auditoría para detallar explícitamente las tres cámaras (Technical, Creative, Brand) con evidencia estructurada. |
| **Memoria de Campaña `memory_manager.py`** | Memoria episódica Locos Materos | **EVOLUCIONAR** | Integrar separación rigurosa entre hechos (`facts`), observaciones (`observations`), hipótesis y aprendizajes (`learnings`). |

---

## 4. Deuda Técnica y Oportunidades de Optimización

1. **Rutas Simbólicas y Permisos:** El workspace `/home/ablutech/Documentos/davinci resolve` es un enlace simbólico a `/data/usuario/Documentos/davinci resolve`. Toda manipulación de archivos debe utilizar el sistema estándar de python/shell respetando la ruta canónica.
2. **Dependencias de Audio:** `librosa` no está en el entorno global de python, pero `scipy.signal` y `soundfile` están completamente operativos y ejecutan el análisis de tempo a 107.7 BPM con latencia sub-segundo. Se preserva este enfoque determinista de alta velocidad.
3. **DaVinci Resolve GUI vs. Headless:** En entornos Linux sin sesión de display X11 activa, DaVinci Resolve requiere variables `QT_QPA_PLATFORM=offscreen` o ejecución de scripts mediante `fusionscript.so`. ADCRA ya contempla fallback automático a `ffmpeg-media-engine`, lo cual cumple estrictamente el estándar de confiabilidad.
4. **Esquemas JSON Centralizados:** Se consolidarán los 20 esquemas bajo `schemas/` manteniendo compatibilidad hacia atrás con `config/`.
