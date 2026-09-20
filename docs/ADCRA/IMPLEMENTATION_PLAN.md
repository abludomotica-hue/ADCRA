# ADCRA — Plan Maestro de Implementación por Fases

Este documento define la hoja de ruta estricta de 23 fases (Fase 0 a Fase 22) para la construcción, verificación y puesta en producción de ADCRA.

---

## Regla de Oro de Ejecución
Cada fase es atómica y secuencial:
1. Inspección de estado actual.
2. Implementación exclusiva del alcance de la fase.
3. Pruebas y validación demostrable con tests.
4. Documentación y actualización en `PROJECT_STATE.md`.
5. Validación y pase a la siguiente fase únicamente tras verificación y confirmación.

---

## Tabla de Fases y Entregables

| Fase | Título | Entregables Principales | Estado |
| :--- | :--- | :--- | :--- |
| **Fase 0** | **Auditoría del Entorno** | `docs/ADCRA/AUDIT_REPORT.md`, `config/tool-inventory.json` | **COMPLETADA** |
| **Fase 1** | **Arquitectura Base** | Estructura `.agents/skills/`, esquemas JSON, contratos, `ARCHITECTURE.md`, `DECISION_LOG.md` | **COMPLETADA** |
| **Fase 2** | **Campaign Director** | `.agents/skills/strategy/campaign-director/SKILL.md`, `scripts/ingest_brief.py`, `lifecycle_manager.py`, `campaign-manifest.json` | **COMPLETADA** |
| **Fase 3** | **Tool Discovery & Router** | `.agents/skills/tools/tool-discovery/`, `.agents/skills/tools/tool-router/`, `route_tool.py` | **COMPLETADA** |
| **Fase 4** | **Music / Audio Analysis** | `.agents/skills/analysis/audio-analysis/`, `analyze_audio.py`, `campaign/audio/audio-analysis.json` | **COMPLETADA** |
| **Fase 5** | **Lyric / Audio Intelligence** | `.agents/skills/analysis/lyric-intelligence/`, `align_lyrics.py`, `campaign/audio/lyric-alignment.json` | **COMPLETADA** |
| **Fase 6** | **Video / Footage Analysis** | `.agents/skills/analysis/video-analysis/`, `analyze_footage.py`, `campaign/assets/asset-inventory.json` | **COMPLETADA** |
| **Fase 7** | **Creative Director & Storyteller** | `.agents/skills/creative/storyboard-engine/`, `build_storyboard.py`, `campaign/storyboard/storyboard.json` | **COMPLETADA** |
| **Fase 8** | **Copywriting Engine** | `.agents/skills/creative/creative-copy-engine/`, 5 variantes obligatorias y selección justificada | **COMPLETADA** |
| **Fase 9** | **Motion Graphics Designer** | `.agents/skills/production/hyperframes-orchestrator/`, cinética tipográfica, layout HTML/CSS | **COMPLETADA** |
| **Fase 10**| **Programmatic Video Engine** | `.agents/skills/production/remotion-orchestrator/`, React video, parametrización por props | **COMPLETADA** |
| **Fase 11**| **Beat-Synced Editor** | `.agents/skills/production/beat-sync-editor/`, cortes alineados a transientes musicales | **COMPLETADA** |
| **Fase 12**| **DaVinci Resolve Integration** | `.agents/skills/post-production/davinci-resolve-orchestrator/`, scripting timeline, OpenCL | **COMPLETADA** |
| **Fase 13**| **Color Grading Assistant** | `.agents/skills/post-production/color-grading/`, balances cromáticos, LUTs, look cinematográfico | **COMPLETADA** |
| **Fase 14**| **Sound Designer & Fairlight** | `.agents/skills/post-production/sound-designer/`, ecualización, ducking, masterización audio | **COMPLETADA** |
| **Fase 15**| **Social Media Formatter** | `.agents/skills/production/social-formatter/`, safe zones, 9:16 vertical, multi-plataforma | **COMPLETADA** |
| **Fase 16**| **Quality Control Engineer** | `.agents/skills/quality-control/`, evaluación tricameral (Técnico, Creativo, Marca) | **COMPLETADA** |
| **Fase 17**| **Campaign Memory System** | `.agents/skills/memory/campaign-memory/`, persistencia de aprendizajes y perfiles de marca | **COMPLETADA** |
| **Fase 18**| **Feedback & Iteration Engine** | `.agents/skills/production/iteration-engine/`, bucle cerrado con tope de 3 iteraciones | **COMPLETADA** |
| **Fase 19**| **Skill Architect & Meta-Learning** | `.agents/skills/meta/skill-builder/`, auto-mejora y generación dinámica de habilidades | **COMPLETADA** |
| **Fase 20**| **Campaña Piloto Completa** | Ejecución end-to-end de prueba con renderizado y validación de pipeline | **COMPLETADA** |
| **Fase 21**| **Campaña Real Locos Materos** | Producción integral del comercial audiovisual *"¿Dónde estás tú? Está tu mate"* | **COMPLETADA** |
| **Fase 22**| **Hardening, Benchmarking & Release**| Optimización de tiempos, perfiles de consumo y manual final de operación | COMPLETADA |

---

## Criterios de Aceptación de la Fase 7 (Cumplidos)
1. `.agents/skills/creative/storyboard-engine/` con `SKILL.md` y script operacional `build_storyboard.py`.
2. Estructuración de 9 escenas contiguas de 0.0s a 29.187s perfectamente sincronizadas con los downbeats musicales.
3. Integración de metadatos de audio, lírica, clasificación cinematográfica, tipografía y movimiento.
4. Cumplimiento de la exigencia obligatoria de justificación estratégica profunda (`rationale`) en cada escena.
5. Validación formal sin errores de `campaign/storyboard/storyboard.json` contra `config/storyboard-schema.json`.
6. 7 pruebas unitarias automatizadas en `tests/test_phase7_storyboard_engine.py` aprobadas al 100%.

## Criterios de Aceptación de la Fase 8 (Cumplidos)
1. `.agents/skills/creative/creative-copy-engine/` con `SKILL.md` y script operacional `generate_copy.py`.
2. Generación obligatoria de las 5 variantes por escena: `emocional`, `publicitaria`, `conversacional`, `minimalista`, `identidad_de_marca`.
3. Puntuaciones cuantitativas normalizadas y conteo de palabras rigurosamente asignados.
4. Justificación estratégica profunda (`selection_rationale`) documentando por qué la opción elegida supera a las otras cuatro.
5. Validación formal sin errores de `campaign/creative/creative-copy.json` contra `config/creative-copy-schema.json`.
6. 7 pruebas unitarias automatizadas en `tests/test_phase8_copywriting_engine.py` aprobadas al 100% (54 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 9 (Cumplidos)
1. `.agents/skills/production/hyperframes-orchestrator/` con `SKILL.md` y script operacional `generate_motion_graphics.py`.
2. Contrato formal `config/motion-graphics-schema.json` estructurado bajo JSON Schema Draft-07.
3. Generación de 9 plantillas HTML5/CSS3 con cinética tipográfica y keyframes (`fade_in_word_by_word`, `slide_up_reveal`, `lower_third_pill`, `kinetic_stomp`, `hero_packshot_reveal`).
4. Aplicación de paleta oficial de *Locos Materos* (#0D5C3A, #D4AF37, #FFFFFF, #1A1A1A) y safe zones verticales 9:16 (Top 120px, Bottom 200px, Sides 40px).
5. Renderizado headless de overlays transparentes RGBA 720x1280 en `campaign/motion-graphics/renders/`.
6. 7 pruebas unitarias automatizadas en `tests/test_phase9_motion_graphics.py` aprobadas al 100% (61 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 10 (Cumplidos)
1. `.agents/skills/production/remotion-orchestrator/` con `SKILL.md` y script operacional `remotion_orchestrator.py`.
2. Contrato formal `config/remotion-composition-schema.json` estructurado bajo JSON Schema Draft-07.
3. Componentes React de Remotion (`index.jsx`, `Root.jsx`, `Main.jsx`) completamente funcionales y parametrizables vía `props.json`.
4. Matriz de 4 variantes publicitarias parametrizadas (`master_30s_emocional`, `variant_publicitaria`, `variant_conversacional`, `bumper_15s`).
5. Sincronía secuencial de 9 escenas (700 frames @ 24fps = 29.167s).
6. Renderizado exitoso de fotograma clave still HD (720x1280) con Remotion CLI en headless mode.
7. 7 pruebas unitarias automatizadas en `tests/test_phase10_remotion_orchestrator.py` aprobadas al 100% (68 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 11 (Cumplidos)
1. `.agents/skills/production/beat-sync-editor/` con `SKILL.md` y script operacional `build_beat_edit.py`.
2. Contrato formal `config/timeline-schema.json` estructurado bajo JSON Schema Draft-07.
3. Representación canónica multicapa en `campaign/timeline/timeline.json` con 700 frames contiguos a 24 fps.
4. Exportación estándar de EDL CMX 3600 (`locos_materos_edit.edl`) con timecode Non-Drop Frame.
5. Exportación estándar de FCP7 XML (`locos_materos_edit.xml`) compatible con DaVinci Resolve.
6. Script de ensamblaje automatizado FFmpeg (`ffmpeg_assembly.sh`).
7. 7 pruebas unitarias automatizadas en `tests/test_phase11_beat_synced_editor.py` aprobadas al 100% (75 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 12 (Cumplidos)
1. `.agents/skills/post-production/davinci-resolve-orchestrator/` con `SKILL.md` y script operacional `resolve_orchestrator.py`.
2. Contrato formal `config/resolve-integration-schema.json` estructurado bajo JSON Schema Draft-07.
3. Integración con la Scripting API de DaVinci Resolve 21.1 en Linux (`fusionscript.so` y `DaVinciResolveScript.py`).
4. Estructuración jerárquica del Media Pool en 4 Bins (`01_Footage`, `02_Audio`, `03_Motion_Graphics`, `04_Timelines`) con 19 clips registrados y verificados en disco.
5. Vinculación y conformación de la timeline `LocosMateros_BeatSynced_Master` desde FCP7 XML y CMX 3600 EDL.
6. Generación de scripts de automatización e importación (`import_to_resolve.py` y `setup_project.sh`).
7. 7 pruebas unitarias automatizadas en `tests/test_phase12_davinci_resolve.py` aprobadas al 100% (82 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 13 (Cumplidos)
1. `.agents/skills/post-production/color-grading/` con `SKILL.md` y script operacional `generate_color_grade.py`.
2. Contrato formal `config/color-grading-schema.json` estructurado bajo JSON Schema Draft-07.
3. Definición de la identidad visual de *Locos Materos* (#0D5C3A verde mate, #D4AF37 dorado yerba, 5900K temperatura objetivo).
4. Generación matemática de 3 LUTs 3D estándar en formato `.cube` (`locos_materos_warm_cinematic.cube` 33x33x33, `locos_materos_editorial_film.cube` 33x33x33, `locos_materos_master_grade.cube` 65x65x65).
5. Asignación de etalonaje plano a plano para las 9 escenas con lift, gamma, gain, contraste y rationale visual en `campaign/color/color-grading-manifest.json`.
6. 7 pruebas unitarias automatizadas en `tests/test_phase13_color_grading.py` aprobadas al 100% (89 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 14 (Cumplidos)
1. `.agents/skills/post-production/sound-designer/` con `SKILL.md` y script operacional `design_sound.py`.
2. Contrato formal `config/sound-design-schema.json` estructurado bajo JSON Schema Draft-07.
3. Síntesis procedural de 9 eventos de foley publicitario (pava humeando, crujido de yerba, vertido de agua caliente, burbujeo, choque de mates, sorbo, etc.) a 48 kHz / 24-bit.
4. Mezcla multicapa con ducking adaptativo sobre el BGM (`Entre_mates_y_sol.mp3`).
5. Masterización con normalización estricta EBU R128 / ITU-R BS.1770-4 (-14.0 LUFS para streaming social, -1.0 dBTP ceiling).
6. Exportación de masters en `campaign/audio/locos_materos_master_mix.wav` (PCM 24-bit 48kHz estéreo) y `locos_materos_master_mix.mp3` (320 kbps).
7. 7 pruebas unitarias automatizadas en `tests/test_phase14_sound_designer.py` aprobadas al 100% (96 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 15 (Cumplidos)
1. `.agents/skills/production/social-formatter/` con `SKILL.md` y script operacional `format_social_deliverables.py`.
2. Contrato formal `config/social-formatter-schema.json` estructurado bajo JSON Schema Draft-07.
3. Definición precisa de especificaciones para 5 destinos (TikTok, Instagram Reels, YouTube Shorts, Meta Feed Square 1:1, YouTube Widescreen 16:9).
4. Delimitación de Safe Zones y zonas de oclusión UI móvil (evitando superposición con buscador superior, botones laterales de acción y pie de foto/audio).
5. Generación de 5 guías visuales en formato PNG RGBA semitransparente en `campaign/deliverables/guides/`.
6. Estrategias multi-ratio definidas (passthrough 9:16, pillarbox institucional `#0D5C3A` para 1:1, fondo desenfocado `boxblur` para 16:9) con comandos ejecutables FFmpeg.
7. 7 pruebas unitarias automatizadas en `tests/test_phase15_social_formatter.py` aprobadas al 100% (103 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 16 (Cumplidos)
1. `.agents/skills/quality-control/qc-evaluator/` con `SKILL.md` y script operacional `evaluate_quality.py`.
2. Contrato formal `config/quality-control-schema.json` estructurado bajo JSON Schema Draft-07.
3. Evaluación tricameral automatizada y exhaustiva:
   - **Auditoría Técnica (35%):** Resolución 720x1280 (9:16), 24.0 fps / 700 cuadros (29.167s), normalización EBU R128 (-12.7 LUFS, -1.0 dBTP), conformación CMX 3600 EDL / FCP7 XML e integridad de activos master.
   - **Auditoría Creativa (35%):** Sincronía rítmica a 107.7 BPM, progresión narrativa con justificación estratégica en 9 escenas, overlays motion graphics 720x1280 y safe zones móviles.
   - **Auditoría de Marca (30%):** Paleta institucional (#0D5C3A, #D4AF37), temperatura cinematográfica ~5900K, presencia del claim rector *"¿Dónde estás tú? Está tu mate"* y cierre hero packshot.
4. Generación y validación formal de `campaign/reports/quality-control-report.json`.
5. Puntuación ponderada alcanzada de 100.0/100.0 con dictamen final de certificación `APPROVED`.
6. 7 pruebas unitarias automatizadas en `tests/test_phase16_quality_control.py` aprobadas al 100% (110 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 17 (Cumplidos)
1. `.agents/skills/memory/campaign-memory/` con `SKILL.md` y script operacional `memory_manager.py`.
2. Contrato formal `config/campaign-memory-schema.json` estructurado bajo JSON Schema Draft-07.
3. Consolidación de aprendizajes estéticos (#0D5C3A verde mate, #D4AF37 dorado yerba, #1A1A1A, temperatura 5900K, 3 LUTs 3D).
4. Registro de parámetros musicales y rítmicos óptimos (107.7 BPM, compás 4/4, duración promedio 3.24s por escena, sincronización a downbeats).
5. Formalización del perfil de audiencia (demografía, psicografía y contexto geográfico de Santiago de Chile) y catálogo de reglas de retención obligatorias y prohibiciones.
6. Generación de la base de memoria acumulada en `campaign/memory/brand-profile-memory.json` e interfaz de consulta semántica (`--query`).
7. 7 pruebas unitarias automatizadas en `tests/test_phase17_campaign_memory.py` aprobadas al 100% (117 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 18 (Cumplidos)
1. `.agents/skills/production/iteration-engine/` con `SKILL.md` y script operacional `iteration_orchestrator.py`.
2. Contrato formal `config/iteration-engine-schema.json` estructurado bajo JSON Schema Draft-07.
3. Implementación estricta de ciclo cerrado con límite infranqueable de 3 iteraciones (`max_allowed_iterations = 3`).
4. Capacidad de resolución autónoma de desvíos detectados por el motor de QC y convergencia certificada a `APPROVED`.
5. Protocolo de escalamiento a operador humano (`ESCALATED_TO_HUMAN`) en caso de agotamiento de 3 iteraciones sin convergencia.
6. Registro histórico auditable en `campaign/reports/iteration-history.json` con soporte de simulación de feedback (`--simulate-feedback`).
7. 7 pruebas unitarias automatizadas en `tests/test_phase18_iteration_engine.py` aprobadas al 100% (124 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 19 (Cumplidos)
1. `.agents/skills/meta/skill-builder/` con `SKILL.md` y motor operacional `skill_synthesizer.py`.
2. Contrato formal `config/skill-builder-schema.json` estructurado bajo JSON Schema Draft-07.
3. Introspección exhaustiva del ecosistema descubriendo las 19 habilidades instaladas y verificando cobertura en los 9 dominios arquitectónicos.
4. Síntesis dinámica de nuevas habilidades con verificación sintáctica mediante el árbol de sintaxis abstracta de Python (`ast.parse`).
5. Gestión gobernada del ciclo de vida (`DRAFT` -> `SYNTHESIZED` -> `VALIDATED` -> `ACTIVE` -> `DEPRECATED`) y protección contra sobreescritura de habilidades base.
6. Síntesis, despliegue y certificación del skill modular demostrativo `telemetry-monitor` y persistencia en `campaign/meta/synthesized-skills-registry.json`.
7. 7 pruebas unitarias automatizadas en `tests/test_phase19_skill_builder.py` aprobadas al 100% (131 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 20 (Cumplidos)
1. `.agents/skills/production/pilot-orchestrator/` con `SKILL.md` y motor operacional `pilot_runner.py`.
2. Contrato formal `config/pilot-campaign-schema.json` estructurado bajo JSON Schema Draft-07.
3. Orquestación end-to-end de los 12 estadios del pipeline (Estrategia, Audio, Video, Copywriting, Storyboard, Timeline, Color, Sound, Safe Zones, QC, Iteración, Memoria y Telemetría) completados al 100% con estado `SUCCESS`.
4. Conformación y verificación física de entregables y masters en disco (`locos_materos_master_mix.wav/mp3`, `locos_materos_edit.edl/xml`, `color-grading-manifest.json`).
5. Parámetros broadcast certificados: duración 29.187s, resolución 720x1280 9:16, 24.0 fps, sonoridad -12.7 LUFS (EBU R128), 9 escenas continuas y 5 canales formateados.
6. Aprobación tricameral (Técnico 100%, Creativo 100%, Marca 100%) con veredicto `APPROVED`, Quality Score 100.0/100.0 y tope de iteraciones $\le 3$.
7. 7 pruebas unitarias automatizadas en `tests/test_phase20_pilot_campaign.py` aprobadas al 100% (138 pruebas acumuladas en el sistema).

## Criterios de Aceptación de la Fase 21 (Cumplidos)
1. `.agents/skills/production/campaign-production-master/` con `SKILL.md` y motor operacional `produce_final_commercial.py`.
2. Contrato formal `config/commercial-delivery-schema.json` estructurado bajo JSON Schema Draft-07.
3. Renderizado y ensamblado del master audiovisual vertical 9:16 (`locos_materos_master_9x16.mp4` a 720x1280, 24.0 fps progresivo, H.264, 29.21s) con composición de los 9 overlays tipográficos de HyperFrames y mezcla sonora Fairlight a -12.7 LUFS.
4. Generación de las 5 variantes multiformato para redes sociales en `campaign/deliverables/exports/` (TikTok, Instagram Reels, YouTube Shorts, Feed Square 1:1 con marco institucional `#0D5C3A`, y YouTube Widescreen 16:9 con fondo cinemático `boxblur`).
5. Emisión y cálculo de checksums de integridad SHA-256 para cada activo del paquete en `campaign/deliverables/masters/commercial-delivery-package.json`.
6. Generación de la ficha técnica broadcast oficial y certificado de entrega en `campaign/deliverables/masters/FICHA_TECNICA.md`.
7. 7 pruebas unitarias automatizadas en `tests/test_phase21_commercial_production.py` aprobadas al 100% (145 pruebas acumuladas en el sistema).
## Criterios de Aceptación de la Fase 22 (Cumplidos)
1. `.agents/skills/tools/benchmarking-engine/` con `SKILL.md` y motor de micro-benchmarks `run_benchmarks.py`.
2. Contrato formal `config/benchmarking-schema.json` estructurado bajo JSON Schema Draft-07.
3. Evaluación y medición precisa de latencia, throughput y memoria sobre los 8 motores algorítmicos de ADCRA (Audio, Storyboard, Color, Fairlight, Remotion, QC, Delivery, Meta-Learning).
4. Emisión y certificación del informe de rendimiento en `campaign/reports/benchmarking-report.json` con calificación `EXCELLENT` y dictamen `PRODUCTION_READY`.
5. Interfaz de línea de comandos unificada `adcra_cli.py` y ejecutable `bin/adcra` con soporte exhaustivo para `status`, `benchmark`, `produce`, `deliver`, `introspect`, `test`, `version` y flag `--json`.
6. Manual de Operaciones integral y guía de despliegue industrial en `docs/ADCRA/OPERATIONS_MANUAL.md` cubriendo arquitectura, comandos, configuración de OpenCL/GPU en Linux, SLAs de broadcast y resolución de incidencias.
7. 7 pruebas unitarias automatizadas en `tests/test_phase22_hardening_and_release.py` aprobadas al 100% (152 pruebas acumuladas en todo el sistema ADCRA sin regresiones).
