# ADCRA — Registro de Decisiones de Arquitectura (ADR)

**Sistema:** ADCRA — Autonomous Digital Campaign & Creative Production System  
**Última Actualización:** 2026-09-19T02:20:00-03:00  

---

## Índice de Decisiones
1. [ADR-001: Arquitectura Modular Basada en Habilidades (Skills-First Architecture)](#adr-001-arquitectura-modular-basada-en-habilidades)
2. [ADR-002: Taxonomía Epistemológica Estricta de Requisitos](#adr-002-taxonomía-epistemológica-estricta-de-requisitos)
3. [ADR-003: Selección de Motor Gráfico y Fallback en Tool Router](#adr-003-selección-de-motor-gráfico-y-fallback-en-tool-router)
4. [ADR-004: Modelo de Copywriting Multivariante (5 Enfoques Obligatorios)](#adr-004-modelo-de-copywriting-multivariante)
5. [ADR-005: Control de Calidad en 3 Niveles y Límite de Iteraciones](#adr-005-control-de-calidad-en-3-niveles-y-límite-de-iteraciones)
6. [ADR-006: Jerarquía de Almacenamiento y Protección de Medios Originales](#adr-006-jerarquía-de-almacenamiento-y-protección-de-medios-originales)

---

## ADR-001: Arquitectura Modular Basada en Habilidades
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  ADCRA requiere coordinar múltiples disciplinas profesionales (estrategia, dirección creativa, copywriting, edición, post-producción, audio, control de calidad, memoria) sin incurrir en código monolítico rígido.
- **Decisión:**  
  Implementar la arquitectura dividida en 9 dominios funcionales bajo `.agents/skills/`:
  - `strategy/`: Dirección de campaña y alineación de brief.
  - `creative/`: Concepto, storyboard y copy publicitario.
  - `analysis/`: Análisis musical, ritmo y segmentación de video.
  - `production/`: Generación de escenas, beat-sync y layout de video.
  - `tools/`: Descubrimiento de herramientas y enrutador dinámico.
  - `post-production/`: DaVinci Resolve, grading, Fairlight y conformación técnica.
  - `quality-control/`: QC técnico, creativo y de marca.
  - `memory/`: Sistema de persistencia y aprendizaje de campañas.
  - `meta/`: Orquestación y evolución de Skills.
- **Consecuencias:**  
  Desacoplamiento total, contratos explícitos vía JSON Schema, capacidad de probar y auditar cada habilidad de forma aislada.

---

## ADR-002: Taxonomía Epistemológica Estricta de Requisitos
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  En sistemas de producción asistidos por IA suele presentarse ambigüedad entre lo que el cliente exige, lo que el usuario instruye, lo que la creatividad propone y las asunciones técnicas del modelo.
- **Decisión:**  
  Todo requisito, restricción o directriz en briefs, manifests y storyboards debe categorizarse obligatoriamente bajo una de cinco etiquetas:
  1. `USER_REQUIREMENT`: Instrucción directa y vinculante del operador del sistema.
  2. `CLIENT_REQUIREMENT`: Restricción o directriz explícita del cliente o marca (ej: colores, logo, claims legales).
  3. `CREATIVE_RECOMMENDATION`: Propuesta estética u operativa sujeta a revisión.
  4. `TECHNICAL_REQUIREMENT`: Restricción impuesta por hardware, contenedores, formatos o APIs (ej: GPU OpenCL, 1080x1920, 30fps).
  5. `AGENT_ASSUMPTION`: Hipótesis generada por el agente ante vacíos de información; requiere validación explícita.
- **Consecuencias:**  
  Trazabilidad completa, eliminación de falsas atribuciones de requisitos del cliente y transparencia en la toma de decisiones.

---

## ADR-003: Selección de Motor Gráfico y Fallback en Tool Router
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  El entorno auditado cuenta con una GPU NVIDIA GeForce GTX 750 Ti (Maxwell GM107, Compute Capability 5.0, 4GB VRAM) y un runtime moderno de Node.js v24.21.0. DaVinci Resolve 21 no soporta CUDA en Compute Capability < 6.0, pero opera estable bajo OpenCL 3.0.
- **Decisión:**  
  - DaVinci Resolve se fija permanentemente en modo `OpenCL` con PRIME render offload para tareas de timeline multicapa, corrección de color profesional y entrega broadcast.
  - HyperFrames es la herramienta primaria para motion graphics basados en HTML/CSS/JS y alineación rítmica (`/music-to-video`).
  - Remotion es la herramienta primaria para renderizado programático React y generación de variantes masivas parametrizadas.
  - FFmpeg y FFprobe actúan como motor determinista para transcodificación técnica, cambio de contenedores, media probing y verificación de conformance de QC.
- **Consecuencias:**  
  Eliminación de cuelgues de GPU, máximo aprovechamiento de la aceleración por hardware y redundancia funcional mediante la matriz de fallback en `config/tool-router.json`.

---

## ADR-004: Modelo de Copywriting Multivariante (5 Enfoques Obligatorios)
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  El texto en pantalla de un anuncio no debe ser una transcripción literal de la música ni un texto plano generado sin alternativas estratégicas.
- **Decisión:**  
  Cada escena del storyboard debe generar obligatoriamente 5 variantes de copy evaluadas numéricamente:
  1. `emocional`: Conexión afectiva y empatía con la vivencia del usuario.
  2. `publicitaria`: Enfoque persuasivo orientado a beneficio y llamada a la acción.
  3. `conversacional`: Lenguaje cercano, cotidiano y natural.
  4. `minimalista`: Síntesis extrema (1-3 palabras de alto impacto).
  5. `identidad_de_marca`: Resonancia directa con el tagline y valores corporativos.  
  El sistema debe justificar por escrito la variante seleccionada en función del arco narrativo.
- **Consecuencias:**  
  Riqueza creativa comparable a una agencia humana, opciones inmediatas para pruebas A/B y coherencia narrativa escena a escena.

---

## ADR-005: Control de Calidad en 3 Niveles y Límite de Iteraciones
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  Un pipeline autónomo puede degradar la calidad o entrar en bucles infinitos de corrección si no existen umbrales claros y límites de parada.
- **Decisión:**  
  - Se establecen 3 compuertas de evaluación independientes:
    1. **QC Técnico:** Duración exacta (delta < 0.1s), ausencia de black frames o frames congelados accidentales, integridad de audio sin clipping ni silencios involuntarios.
    2. **QC Creativo:** Sincronización con el beat, fluidez de cortes, legibilidad tipográfica y equilibrio de composición visual.
    3. **QC de Marca:** Presencia y posición del logo, cumplimiento de paleta cromática, consistencia de tono y verificación de ausencia de claims no autorizados.
  - El motor de iteración tiene un límite estricto de **3 ciclos automáticos**. Si un entregable no alcanza estado `APPROVED` en el tercer ciclo, el sistema se detiene y escala a revisión del usuario (`HALT_FOR_USER_REVIEW`).
- **Consecuencias:**  
  Garantía de salida broadcast, protección contra bucles infinitos y gobierno humano en casos límite.

---

## ADR-006: Jerarquía de Almacenamiento y Protección de Medios Originales
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  Durante la manipulación intensiva de clips de video, pistas de audio y renders intermedios existe riesgo de sobrescritura accidental de metraje original.
- **Decisión:**  
  Los activos de medios deben aislarse estrictamente en la siguiente estructura de directorios:
  - `assets/source/`: Activos crudos originales del cliente (solo lectura).
  - `assets/working/`: Archivos de trabajo intermedios, proxies y secuencias temporales.
  - `assets/preview/`: Renders comprimidos de baja resolución para evaluación rápida y QC visual.
  - `assets/master/`: Master final de alta fidelidad sin compresión destructiva.
  - `assets/export/`: Versiones optimizadas por plataforma (9:16 Reels/TikTok, 16:9 YouTube, 1:1 Feed).
  Queda prohibido sobrescribir o eliminar archivos en `assets/source/`.
- **Consecuencias:**  
  Integridad absoluta de los activos originales y reproducibilidad completa del pipeline.

---

## ADR-007: Meta-Learning, Gobernanza y Síntesis Dinámica de Habilidades
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  A medida que las necesidades de producción evolucionan (nuevas plataformas sociales, formatos de renderizado específicos, monitoreo de telemetría), el sistema ADCRA no debe depender de intervenciones manuales en su estructura de agentes para adquirir capacidades modulares. Sin embargo, la auto-modificación no gobernada puede inducir inestabilidad, errores de sintaxis o sobreescritura accidental de habilidades fundacionales.
- **Decisión:**  
  1. Se implementa el módulo `skill-builder` en el noveno dominio (`.agents/skills/meta/`) para introspección y síntesis dinámica.
  2. Las 18 habilidades fundacionales (Fases 1-18) se declaran inmutables y protegidas contra colisiones de nombres o reescritura.
  3. Todo código Python generado dinámicamente debe validarse mediante el compilador AST de Python (`ast.parse`) previo a su persistencia en disco.
  4. Todo nuevo skill debe atravesar un ciclo de vida estrictamente gobernado: `DRAFT` -> `SYNTHESIZED` -> `VALIDATED` -> `ACTIVE` -> `DEPRECATED`, con registro auditable y validación formal contra `config/skill-builder-schema.json`.
  5. Los scripts sintetizados deben implementar obligatoriamente el flag `--validate-only`.
- **Consecuencias:**  
  Capacidad de auto-evolución y extensión modular del sistema de agentes con máximas garantías de integridad arquitectónica, prevención de regresiones y trazabilidad completa.

---

## ADR-008: Orquestación End-to-End y Validación de Campaña Piloto Unificada
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  Tras la construcción de las 19 habilidades especializadas en sus 9 dominios arquitectónicos, se requiere un mecanismo de orquestación global que valide el pipeline de principio a fin antes de la producción masiva o renderizado intensivo final, garantizando que no existan inconsistencias de formato, metadatos truncados o pérdidas de trazabilidad entre etapas.
- **Decisión:**  
  1. Se implementa el orquestador unificado `pilot-orchestrator` en `.agents/skills/production/pilot-orchestrator/`.
  2. La campaña piloto debe recorrer formalmente los 12 estadios del pipeline: Estrategia, Inteligencia de Audio, Inteligencia de Video, Copywriting, Storyboard, Ensamblado de Timelines, Color Grading, Sound Design, Formateador Social, Control de Calidad, Iteración y Memoria/Telemetría.
  3. Cada estadio debe registrar su tiempo de ejecución, artefactos físicos auditados y estado `SUCCESS`.
  4. La emisión del manifiesto formal `campaign/pilot/pilot-campaign-manifest.json` está condicionada a un Quality Score $\ge 90.0$ (alcanzando 100.0/100.0), veredicto `APPROVED` y estricto respeto del tope de 3 iteraciones.
- **Consecuencias:**  
  Validación empírica total de la arquitectura ADCRA como agencia autónoma unificada, desacoplamiento modular preservado y vía despejada para la Fase 21 (Campaña Real de Locos Materos).

---

## ADR-009: Arquitectura de Renderizado Master y Entrega Multiformato
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  La entrega final de una campaña audiovisual publicitaria requiere la emisión de un master de máxima resolución y la transcodificación sin pérdidas perceptuales a múltiples plataformas sociales, garantizando que el diseño tipográfico y de safe zones se preserve sin cortes ni distorsiones.
- **Decisión:**  
  1. Se implementa la habilidad terminal `campaign-production-master` en `.agents/skills/production/campaign-production-master/`.
  2. El master oficial (`locos_materos_master_9x16.mp4`) se compone concatenando el metraje recortado al compás musical (29.21s, 700 frames a 24 fps), superponiendo los overlays cinéticos de HyperFrames (01 a 09) en composición alpha RGBA y multiplexando el audio master Fairlight PCM a AAC 320 kbps (48 kHz).
  3. A partir del master, se derivan 5 formatos estandarizados:
     - TikTok, Instagram Reels y YouTube Shorts (9:16 vertical 720x1280 nativo).
     - Meta Feed Square 1:1 (720x720) mediante pillarbox con color institucional verde mate `#0D5C3A`.
     - YouTube Widescreen 16:9 (1280x720) mediante composición de fondo desenfocado cinemático (`boxblur=20:5`).
  4. Cada archivo emitido cuenta con su hash SHA-256 registrado en `commercial-delivery-package.json`, validado bajo el esquema formal `config/commercial-delivery-schema.json`.
  5. Se emite un documento legible `FICHA_TECNICA.md` con las especificaciones broadcast para agencias y canales de televisión o pauta digital.
- **Consecuencias:**  
  Entrega broadcast profesional completa, compatibilidad 100% con todos los canales modernos de pauta y trazabilidad criptográfica de todos los entregables.
---

## ADR-010: Hardening, Benchmarking Architecture & Release CLI
- **Estado:** ACEPTADA
- **Fecha:** 2026-09-19
- **Contexto:**  
  Tras completar la producción broadcast de la campaña *Locos Materos*, el sistema ADCRA requiere una fase final de endurecimiento técnico (hardening), profiling algorítmico de latencias por motor, certificación de SLAs de rendimiento y unificación operativa mediante un punto de entrada CLI único que permita operar la agencia autónoma tanto por usuarios humanos como por sistemas de orquestación continua (CI/CD / Kubernetes).
- **Decisión:**  
  1. Se implementa el motor `benchmarking-engine` en `.agents/skills/tools/benchmarking-engine/` para ejecutar micro-benchmarks y telemetría de hardware (CPU, RAM, GPU OpenCL/CUDA) sobre los 8 motores algorítmicos del sistema.
  2. Se define el contrato formal `config/benchmarking-schema.json` (JSON Schema Draft-07) para auditar latencia media, percentil 95 (P95), consumo de memoria y throughput (ops/sec).
  3. Se establece una compuerta de rendimiento con umbral máximo de latencia por motor (< 500 ms) y tiempo total de benchmark (< 30s), asignando una calificación global `EXCELLENT` si todos los motores operan en estado `OPTIMAL` (< 100 ms).
  4. Se crea la interfaz de línea de comandos unificada `adcra_cli.py` y su ejecutable `bin/adcra` con subcomandos estandarizados: `version`, `status`, `benchmark`, `produce`, `deliver`, `introspect`, `test` y soporte para `--json`.
  5. Se documenta la arquitectura completa y procedimientos de soporte en `docs/ADCRA/OPERATIONS_MANUAL.md`, incluyendo dependencias de DaVinci Resolve en Linux y modo de fallback headless.
- **Consecuencias:**  
  Cierre arquitectónico de la Fase 22 y del sistema ADCRA completo (v1.0.0-gold). Trazabilidad total de rendimiento, cero dependencias manuales para la inspección y producción, y certificación final como sistema de grado industrial listo para emisión broadcast.
