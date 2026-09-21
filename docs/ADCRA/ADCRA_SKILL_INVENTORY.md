# ADCRA — INVENTARIO DE HABILIDADES (SKILLS) v3.0
**Documento:** ADCRA_SKILL_INVENTORY.md  
**Fecha:** 21 de Septiembre, 2026  
**Sistema:** ADCRA (Autonomous Digital Campaign & Creative Production System)  

---

## 1. Inventario Consolidado de las 23 Habilidades en `.agents/skills/`

| Dominio | Nombre de Habilidad | Script Principal | Entradas Principales | Salidas Principales | Esquema de Validación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **strategy** | `campaign-director` | `ingest_brief.py`, `lifecycle_manager.py` | Brief en Markdown / JSON | `campaign/campaign-manifest.json` | `campaign-schema.json` |
| **analysis** | `audio-analysis` | `analyze_audio.py` | Archivo de audio (MP3/WAV) | `campaign/audio/audio-analysis.json` | Contrato JSON interno |
| **analysis** | `lyric-intelligence` | `align_lyrics.py` | Audio + Letra de canción | `campaign/audio/lyric-alignment.json` | Contrato JSON interno |
| **analysis** | `video-analysis` | `analyze_footage.py` | Carpeta de metraje de video | `campaign/assets/asset-inventory.json`| Contrato JSON interno |
| **creative** | `creative-copy-engine` | `generate_copy.py` | Brief + Storyboard + Letra | `campaign/creative/creative-copy.json`| `creative-copy-schema.json` |
| **creative** | `storyboard-engine` | `build_storyboard.py` | Audio analysis + Versos + Clips | `campaign/storyboard/storyboard.json`| `storyboard-schema.json` |
| **production** | `beat-sync-editor` | `build_beat_edit.py` | Storyboard + Beats musicales | `locos_materos_edit.edl`, `.xml` | `timeline-schema.json` |
| **production** | `hyperframes-orchestrator`| `generate_motion_graphics.py`| Copy + Storyboard + Timing | `campaign/motion-graphics/` | `motion-graphics-schema.json` |
| **production** | `remotion-orchestrator` | `remotion_orchestrator.py` | Props + Assets + Overlays | `campaign/remotion/` | `remotion-composition-schema.json` |
| **production** | `campaign-production-master`| `produce_final_commercial.py`| Video clips + Mix + Overlays | `locos_materos_master_9x16.mp4` | Contrato broadcast 9:16 |
| **production** | `social-formatter` | `format_social_deliverables.py`| Master 9:16 + Perfiles | 5 variantes exportadas | `social-formatter-schema.json` |
| **production** | `iteration-engine` | `iteration_orchestrator.py` | Reporte QC + Desvíos | `iteration-history.json` | `iteration-engine-schema.json` |
| **production** | `pilot-orchestrator` | `pilot_runner.py` | Flujo end-to-end piloto | `pilot-run-report.json` | `pilot-campaign-schema.json` |
| **post-production**| `color-grading` | `generate_color_grade.py` | Brand colors + Clips | 3 LUTs .cube + Manifest | `color-grading-schema.json` |
| **post-production**| `sound-designer` | `design_sound.py` | Pista música + Foley track | `locos_materos_master_mix.wav` | `sound-design-schema.json` |
| **post-production**| `davinci-resolve-orchestrator`| `resolve_orchestrator.py` | EDL/XML + Media Pool | `import_to_resolve.py` | `resolve-integration-schema.json` |
| **quality-control**| `qc-evaluator` | `evaluate_quality.py` | Master + Reportes + Manifiesto | `quality-control-report.json` | `quality-control-schema.json` |
| **memory** | `campaign-memory` | `memory_manager.py` | Campaña finalizada + QC | `brand-profile-memory.json` | `campaign-memory-schema.json` |
| **meta** | `skill-builder` | `skill_synthesizer.py` | Requerimiento no cubierto | Nueva skill validada en `.agents/` | `skill-builder-schema.json` |
| **meta** | `telemetry-monitor` | `telemetry_collector.py` | Eventos de agentes y servidor | `campaign/agent-telemetry.json` | Contrato JSON interno |
| **tools** | `tool-discovery` | `discover_tools.py` | Entorno Linux / comandos | `config/tool-inventory.json` | Contrato JSON interno |
| **tools** | `tool-router` | `route_tool.py` | Necesidad técnica audiovisual | Decisión de herramienta y fallback | `tool-router.json` |
| **tools** | `benchmarking-engine` | `run_benchmarks.py` | 8 motores algorítmicos | `benchmarking-report.json` | `benchmarking-schema.json` |

---

## 2. Mapa de Dependencias y Flujo de Datos entre Habilidades

```text
[strategy/campaign-director]
           │
           ├────────────────────────┬────────────────────────┐
           ↓                        ↓                        ↓
[analysis/audio-analysis]  [analysis/lyric-intel]  [analysis/video-analysis]
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    ↓
                       [creative/storyboard-engine]
                                    │
                                    ↓
                       [creative/creative-copy-engine]
                                    │
           ┌────────────────────────┼────────────────────────┐
           ↓                        ↓                        ↓
[post-prod/color-grading] [production/beat-sync-editor] [post-prod/sound-designer]
           │                        │                        │
           ├────────────────────────┴────────────────────────┤
           ↓                                                 ↓
[production/hyperframes-orchestrator]           [production/remotion-orchestrator]
           │                                                 │
           └────────────────────────┬────────────────────────┘
                                    ↓
                 [production/campaign-production-master]
                                    │
                                    ↓
                       [quality-control/qc-evaluator]
                                    │
                     ┌──────────────┴──────────────┐
                     ↓                             ↓
          [FAILED / ITERATE]                  [APPROVED]
                     ↓                             ↓
        [production/iteration-engine]   [production/social-formatter]
                                                   │
                                                   ↓
                                        [memory/campaign-memory]
```
