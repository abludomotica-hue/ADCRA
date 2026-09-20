# ADCRA — Campaign Intake Studio
## Documento de Arquitectura de Sistema (CAMPAIGN-INTAKE-ARCHITECTURE)
**Versión:** 1.0.0 | **Estado:** APROBADA PARA IMPLEMENTACIÓN  
**Sistema:** ADCRA (Autonomous Digital Campaign & Creative Production System)  

---

## 1. Visión General y Propósito

El **Campaign Intake Studio** es el subsistema de incorporación, diálogo inteligente y preparación integral de campañas de ADCRA. Transforma requerimientos heterogéneos, activos multimedia no estructurados e intenciones de negocio en un **Campaign Brief formal, validado, enriquecido y ejecutable** sin fricción ni formularios monolíticos.

```
+--------------------------------------------------------------------------------------------------+
|                                    CAMPAIGN INTAKE STUDIO                                        |
+--------------------------------------------------------------------------------------------------+
| ENTRADAS DEL USUARIO / CLIENTE                                                                   |
| [Nuevo Cliente | Cliente Existente] -> Web / Redes -> Assets (Video/Audio/Logo) -> Preferencias |
+--------------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+--------------------------------------------------------------------------------------------------+
| CAPA AGÉNTICA DE ANÁLISIS E INFERENCIA (INTAKE ENGINE)                                           |
| • Website Analyzer: Extracción de tono, paleta, claims y CTA desde URL.                          |
| • Asset Intelligence (FFprobe): Detección de resolución, FPS, códec, orientación y calidad.       |
| • Audio Analyzer: BPM, compases, curva de energía y marcadores de sección (Verse/Chorus/Drop).  |
| • Brand Intelligence: Validación cruzada de claims, colores HEX y prohibiciones.                 |
| • Audience Builder: Segmentación Primaria, Secundaria y Exploratoria (AI Suggestions vs Facts).  |
| • Consistency Auditor: Detección de advertencias (Warnings) y bloqueantes (Blockers).            |
+--------------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+--------------------------------------------------------------------------------------------------+
| ARTEFACTOS GENERADOS Y PERSISTENCIA ESTRUCTURADA                                                 |
| 1. campaign/brief/campaign-brief.json         (Briefing completo normalizado)                    |
| 2. campaign/brief/constraints.json            (Brand Safety y restricciones legales)             |
| 3. campaign/memory/brand-profile-memory.json  (Memoria episódica y aprendizajes de marca)         |
| 4. campaign/assets/asset-inventory.json       (Catálogo técnico de video, imágenes y branding)   |
| 5. campaign/audio/audio-analysis.json         (BPM, beat grid y análisis espectral)              |
| 6. campaign/production/campaign-blueprint.json (Hoja de ruta creativa previa a producción)        |
| 7. campaign/campaign-manifest.json            (Fuente central de verdad y orquestación)          |
+--------------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+--------------------------------------------------------------------------------------------------+
| ACTIVACIÓN DEL PIPELINE DE AGENTES DE PRODUCCIÓN ADCRA (Fases 01 a 22)                           |
| Director -> Copywriting -> Storyboard -> Color -> Fairlight -> Motion -> QC -> Delivery Master   |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Jerarquía del Sistema de Archivos y Almacenamiento

Para soportar múltiples clientes y campañas sin colisiones y manteniendo compatibilidad retrospectiva con la campaña actual (*Locos Materos*), la arquitectura adopta un esquema desacoplado y versionado:

```
campaign/
├── <client_slug>/
│   └── <campaign_slug>/
│       ├── brief/
│       │   ├── campaign-brief.json
│       │   └── constraints.json
│       ├── brand/
│       │   ├── identity.json
│       │   └── palette.json
│       ├── audience/
│       │   └── audience-profile.json
│       ├── strategy/
│       │   └── strategic-brief.json
│       ├── creative/
│       │   ├── creative-copy.json
│       │   └── creative-direction.json
│       ├── audio/
│       │   ├── master-track.wav
│       │   ├── audio-analysis.json
│       │   └── lyric-alignment.json
│       ├── assets/
│       │   ├── video/
│       │   ├── images/
│       │   ├── branding/
│       │   └── references/
│       ├── storyboard/
│       │   └── storyboard.json
│       ├── production/
│       │   ├── tool-selection.json
│       │   └── campaign-blueprint.json
│       ├── editing/
│       │   ├── timeline.json
│       │   ├── edit.edl
│       │   └── edit.xml
│       ├── motion/
│       │   ├── motion-manifest.json
│       │   └── renders/
│       ├── sound/
│       │   └── sound-design-manifest.json
│       ├── color/
│       │   ├── color-grading-manifest.json
│       │   └── luts/
│       ├── qc/
│       │   └── quality-control-report.json
│       ├── renders/
│       ├── exports/
│       ├── reports/
│       │   └── benchmarking-report.json
│       └── campaign-manifest.json
```

---

## 3. Modelo de Comunicación y Servicios Backend (`dashboard_server.py`)

El backend HTTP multihilo existente se extiende con rutas especializadas para el ciclo de vida del intake:

| Método | Endpoint | Propósito |
|---|---|---|
| `GET` | `/api/clients` | Lista clientes registrados en memoria persistente. |
| `GET` | `/api/clients/:id` | Recupera el perfil completo, identidad y campañas previas de un cliente. |
| `POST` | `/api/clients` | Registra un nuevo cliente con su estructura inicial. |
| `GET` | `/api/intake/draft` | Carga el borrador activo con recuperación de sesión (`draft recovery`). |
| `POST` | `/api/intake/draft` | Auto-guardado en tiempo real del progreso por pasos. |
| `POST` | `/api/intake/analyze-url` | Rastreo e inferencia agéntica de identidad, colores y claims desde un sitio web. |
| `POST` | `/api/intake/analyze-asset` | Probing de metadatos técnicos (FFprobe) de video/audio/imágenes subidos. |
| `POST` | `/api/intake/analyze-audio` | Detección de BPM, duración, waveform y energía musical. |
| `POST` | `/api/intake/preflight` | Ejecuta los 10 pre-flight checks y calcula Readiness Score, Warnings y Blockers. |
| `POST` | `/api/intake/blueprint` | Genera el documento visual `Campaign Blueprint` antes de iniciar producción. |
| `POST` | `/api/intake/launch` | Valida compuertas, crea directorios físicos y activa la orquestación de ADCRA. |

---

## 4. Enrutamiento Tecnológico (Tool Router Integration)

El Intake Studio no asigna herramientas arbitrariamente, sino que registra las decisiones en `campaign/production/tool-selection.json` basándose en las necesidades del brief:

1. **HyperFrames:** Motion graphics tipográficos, overlays cinéticos HTML/CSS, reactividad al ritmo musical y bajo consumo GPU.
2. **Remotion:** Video programático en React, parametrización de plantillas y generación masiva de variantes localizadas.
3. **DaVinci Resolve (MCP):** Edición multicapa broadcast, finishing de colorimetría ACEScc / LUTs 3D, mezcla Fairlight y subtítulos conformados.
4. **FFmpeg / FFprobe:** Media probing determinista, normalización EBU R128 (-14 / -12.7 LUFS), transcodificación multi-aspecto (9:16, 1:1, 16:9) y verificación de safe zones.

---

## 5. Garantías de Calidad y No-Regresión

1. **Persistencia Cero-Pérdidas:** Auto-guardado cada vez que un campo cambia (`debounce 500ms`) en `localStorage` y en el servidor vía `/api/intake/draft`.
2. **Diferenciación Epistemológica Estricta:** La UI y el modelo de datos diferencian explícitamente entre:
   - `FACT`: Confirmado directamente por el usuario o archivo físico.
   - `CLIENT_INPUT`: Texto redactado por el cliente.
   - `AI_INFERENCE`: Deducido a partir del sitio web o metraje (requiere confirmación).
   - `AI_RECOMMENDATION`: Propuesta optimizada de la agencia.
   - `UNKNOWN`: Dato faltante no inventado.
3. **Compuerta de Pre-Flight:** Ninguna campaña puede lanzarse con `BLOCKERS` no resueltos (ej. ausencia de audio en video rítmico, falta de logo en campaña de branding o violación de derechos).
