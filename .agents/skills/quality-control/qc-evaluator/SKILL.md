---
name: qc-evaluator
description: Motor de evaluación y auditoría tricameral de control de calidad publicitario (Técnico, Creativo y de Marca) con cálculo ponderado de Quality Score y certificación formal de entrega.
domain: quality-control
version: 1.0.0
schema: config/quality-control-schema.json
inputs:
  - campaign/campaign-manifest.json
  - campaign/timeline/timeline.json
  - campaign/audio/sound-design-manifest.json
  - campaign/color/color-grading-manifest.json
  - campaign/motion-graphics/motion-manifest.json
  - campaign/deliverables/social-format-manifest.json
outputs:
  - campaign/reports/quality-control-report.json
---

# Quality Control Evaluator Skill

## Propósito
El motor de Control de Calidad Tricameral actúa como la última barrera de defensa antes de la distribución o masterización definitiva de la campaña publicitaria *"¿Dónde estás tú? Está tu mate"* de **Locos Materos**. Evalúa de forma exhaustiva los tres pilares fundamentales de la producción:

1. **Auditoría Técnica:** Rigor formal de especificaciones de video, audio, formatos y presencia de activos físicos.
2. **Auditoría Creativa:** Coherencia de montaje, sincronización rítmica, progresión emocional y legibilidad tipográfica.
3. **Auditoría de Marca:** Adherencia irrestricta a los lineamientos de identidad visual y verbal de *Locos Materos*.

---

## Estructura de la Auditoría Tricameral

### 1. Auditoría Técnica (Ponderación: 35%)
- **Resolución & Aspect Ratio:** 720x1280 píxeles, proporción vertical 9:16.
- **Velocidad de Fotogramas:** 24.0 fps exactos (700 fotogramas continuos en 29.167s).
- **Conformidad de Sonoridad EBU R128:**
  - Sonoridad integrada: `-14.0 ± 2.0 LUFS` (rango streaming social).
  - True Peak ceiling: `≤ -1.0 dBTP` (prevención de clipping inter-muestra).
  - Frecuencia de muestreo: `48,000 Hz` / `24-bit` estéreo.
- **Integridad de Archivos:** Existencia de clips de footage, timeline XML/EDL, master WAV/MP3, LUTs 3D y overlays de motion graphics.

### 2. Auditoría Creativa (Ponderación: 35%)
- **Sincronización Rítmica:** Verificación de que los 9 cortes de escena coincidan con los transientes musicales del análisis rítmico (107.7 BPM).
- **Estructura Narrativa:** Presencia de las 9 etapas dramáticas (Hook cotidiano -> Ritual de preparación -> Momentos de consumo -> Clímax -> Cierre de marca).
- **Legibilidad Tipográfica y Safe Zones:** Validación de que ningún texto publicitario invada las zonas de oclusión UI nativas de TikTok, Reels o Shorts.

### 3. Auditoría de Marca (Ponderación: 30%)
- **Paleta Cromática Oficial:** Uso verificado de Verde Mate (`#0D5C3A`), Dorado Yerba (`#D4AF37`), Blanco Puro (`#FFFFFF`) y Carbón (`#1A1A1A`).
- **Temperatura de Color:** Calidez visual natural consistente con el grading cinematográfico (~5900K).
- **Claim Publicitario:** Presencia explícita del lema rector *"¿Dónde estás tú? Está tu mate"*.
- **Packshot y Logotipo:** Inclusión del logotipo oficial en el remate de escena 09.

---

## Algoritmo de Puntuación y Certificación

$$\text{Overall Score} = (\text{Score}_{\text{técnico}} \times 0.35) + (\text{Score}_{\text{creativo}} \times 0.35) + (\text{Score}_{\text{marca}} \times 0.30)$$

- **APPROVED:** $\text{Overall Score} \ge 90.0$ y ningún fallo técnico crítico.
- **NEEDS_REVISION:** $75.0 \le \text{Overall Score} < 90.0$.
- **REJECTED:** $\text{Overall Score} < 75.0$ o fallo estructural bloqueante.

## Validación Formal
El informe `campaign/reports/quality-control-report.json` se valida contra `config/quality-control-schema.json`.
