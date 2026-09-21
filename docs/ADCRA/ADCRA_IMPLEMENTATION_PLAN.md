# ADCRA — PLAN MAESTRO DE TRANSFORMACIÓN & IMPLEMENTACIÓN v3.0
**Documento:** ADCRA_IMPLEMENTATION_PLAN.md  
**Fecha:** 21 de Septiembre, 2026  
**Sistema:** ADCRA — Creative Operating System (COS)  
**Versión Objetivo:** `v3.0.0-creative-os`  

---

## 1. Visión y Objetivos de la Transformación

Transformar ADCRA de una herramienta de preparación audiovisual a un **Creative Operating System (COS)** profesional que:
1. Permite diseñar, producir, evaluar, iterar y entregar campañas publicitarias digitales completas.
2. Desacopla formalmente las 5 capas maestras (Experience, Campaign Intelligence, Agent Orchestration, Tool Router, Media Engine).
3. Implementa el **Campaign Knowledge Graph** con epistemología de fuentes (`CLIENT_INPUT`, `CONFIRMED_FACT`, `AI_INFERENCE`, `AI_RECOMMENDATION`, `UNKNOWN`) y control de confianza.
4. Soporta los dos flujos de trabajo clave: **Nuevo Cliente** (onboarding progresivo) y **Cliente Existente** (precarga de memoria episódica, "¿Qué cambió para esta campaña?").
5. Integra la navegación global de Creative OS (`HOME`, `CAMPAIGNS`, `CLIENTS`, `ASSETS`, `INTELLIGENCE`, `TOOLS`, `ANALYTICS`, `SETTINGS`) y la Command Palette (`Ctrl+K`).
6. Mantiene el principio de **EVOLUCIONAR antes que REEMPLAZAR**, garantizando que las 270 pruebas automatizadas continúen pasando al 100% de éxito en cada hito.

---

## 2. Hoja de Ruta de Implementación en 25 Fases

```text
FASE 0: Auditoría Completa del Entorno y Línea Base (Completada en documentos de auditoría)
FASE 1: Arquitectura de 5 Capas y Desacoplamiento Formal
FASE 2: Campaign Knowledge Graph & Clasificación Epistemológica de Fuentes
FASE 3: Client Memory & Brand DNA Engine
FASE 4: Campaign Intake Progresivo (Nuevo Cliente vs. Cliente Existente)
FASE 5: Readiness Engine con Bloqueantes, Advertencias y Reglas Dinámicas
FASE 6: Asset Intelligence, Clasificación de Planos y Rights Management
FASE 7: Audio Intelligence & Sincronización Estructural Audio → Story
FASE 8: Creative Director & Concept Generator con Ponderación de Ajuste
FASE 9: Copy Lab & Regla de Economía Verbal (5 alternativas + opción NO_TEXT)
FASE 10: Storyboard Lab & Curva de Arco Narrativo
FASE 11: Tool Router con Matriz Funcional y Gestión de Salud
FASE 12: HyperFrames Orchestration (Motion Graphics & Overlays)
FASE 13: Remotion Orchestration (Composición Programática y Variantes)
FASE 14: DaVinci Resolve Orchestration (Conformación, Color y Fairlight)
FASE 15: Production Engine & Máquina de Estados Finita
FASE 16: Tricameral QC (Technical, Creative, Brand) con Evidencia Detallada
FASE 17: Closed-Loop Iteration Engine con Límite de 3 Ciclos y Puerta Humana
FASE 18: Multiformat Delivery Center (9:16, 4:5, 1:1, 16:9 con SHA-256)
FASE 19: Campaign Episodic Memory & Continuous Learning Loop
FASE 20: Post-Mortem Engine (`campaign-postmortem.md`)
FASE 21: Creative OS UI Polish & Command Palette (`Ctrl+K`)
FASE 22: Testing Integral & Verificación de Cero Regresiones (270+ tests)
FASE 23: Performance & Optimización de Caching basado en Hashes
FASE 24: Security, Secret Isolation & Path Sanitization
FASE 25: End-to-End Test (Campaña Sintética Demo + Campaña Real Locos Materos)
```

---

## 3. Plan Detallado de Fases Iniciales (Hitos Clave)

### Hito 1: Infraestructura de Datos y Contratos (Fases 1 a 3)
- **Archivos Nuevos / Modificados:**
  - `schemas/campaign-knowledge-graph.schema.json`
  - `config/campaign-schema.json` (ampliado con metadatos de fuentes)
  - `campaign/campaign-knowledge-graph.json`
  - `.agents/skills/strategy/campaign-director/scripts/knowledge_graph_manager.py`
- **Criterios de Aceptación:**
  - Validación formal de todos los esquemas contra datos de campaña.
  - Clasificación de cada campo con `source`, `confidence`, `requires_confirmation`.

### Hito 2: Inteligencia de Campaña, Audio y Copy (Fases 4 a 10)
- **Archivos Nuevos / Modificados:**
  - `.agents/skills/analysis/audio-analysis/scripts/analyze_audio.py` (secciones Intro, Verse, Chorus, Climax, Outro)
  - `.agents/skills/creative/creative-copy-engine/scripts/generate_copy.py` (alternativa `NO_TEXT` y justificación de economía verbal)
  - `.agents/skills/creative/storyboard-engine/scripts/build_storyboard.py` (atributos de cámara, iluminación y arco dramático)
  - `web/intake.js` & `web/intake.css` (visualización de fuentes y badges de confianza)
- **Criterios de Aceptación:**
  - Enlace determinista entre picos de energía de audio y cortes del storyboard.
  - Copys concisos con conteo estricto de caracteres y cálculo de tiempo en off.

### Hito 3: Tool Router, Producción y QC Tricameral (Fases 11 a 18)
- **Archivos Nuevos / Modificados:**
  - `config/tool-routing.json` (matriz funcional y políticas de fallback)
  - `.agents/skills/tools/tool-router/scripts/route_tool.py` (diagnóstico de salud `CONNECTED`, `FALLBACK_ACTIVE`)
  - `.agents/skills/quality-control/qc-evaluator/scripts/evaluate_quality.py` (cámaras Técnica, Creativa y de Marca con evidencias)
  - `.agents/skills/production/iteration-engine/scripts/iteration_orchestrator.py`
- **Criterios de Aceptación:**
  - Tolerancia a fallos: si una herramienta externa no responde, el sistema conmuta a su fallback automático.
  - Reporte QC con 100% de trazabilidad de evidencia.

### Hito 4: Experiencia Creative OS, Command Palette y Release (Fases 19 a 25)
- **Archivos Nuevos / Modificados:**
  - `web/intake.html`, `web/intake.js`, `web/intake.css`
  - Command Palette (`Ctrl+K` modal con búsqueda rápida de acciones y pantallas)
  - `campaign/reports/campaign-postmortem.md`
  - Suites de pruebas automáticas en `tests/`
- **Criterios de Aceptación:**
  - Experiencia editorial y cinemática de alto nivel ("Creative Operating System").
  - 100% de pruebas pasando sin regresiones.
