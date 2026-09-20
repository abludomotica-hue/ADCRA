---
name: storyboard-engine
description: Motor de dirección creativa y diseño de storyboard para ADCRA. Traduce el concepto estratégico, el análisis musical, la lírica y el inventario de metraje en un storyboard escena por escena rigurosamente validado contra config/storyboard-schema.json con justificación estratégica obligatoria.
---

# Storyboard Engine — Dirección Creativa y Storyboarding

El **Storyboard Engine** es el arquitecto narrativo y visual de la campaña en ADCRA. Transforma la visión conceptual y los activos multimedia analizados en una pauta temporal milimétrica escena por escena, asegurando coherencia dramática, resonancia emocional y sincronización rítmica perfecta.

---

## 1. Principios de Diseño Narrativo

1. **Arco Dramático Progresivo:**  
   La historia debe fluir orgánicamente a través de una progresión emocional clara (en *Locos Materos*: Soledad matutina -> Ritual íntimo -> Identidad territorial -> Movimiento urbano -> Trabajo y esfuerzo -> Juventud y estudio -> Gratificación sensorial -> Comunidad y celebración final).
2. **Sincronización Rítmica con Downbeats:**  
   Los puntos de corte visual no son arbitrarios: coinciden con transientes musicales y compases (downbeats) identificados por `audio-analysis`.
3. **Justificación Estratégica Obligatoria (`rationale`):**  
   Cada escena debe incluir una justificación escrita detallando por qué fue diseñada de esa forma, qué función cumple en el embudo publicitario y cómo aporta al valor de la marca.
4. **Respeto a Reglas de Producto:**  
   El mate debe ser auténtico, con yerba visible, bombilla realista y vapor natural. El logotipo de la marca solo se incorpora en packshot final (`hero_packshot`).
5. **Asignación de Motor Técnico (`tool`):**  
   Cada escena declara explícitamente el motor asignado conforme a `config/tool-router.json` (ej: `DaVinci Resolve` para montaje cinematográfico multicapa).

---

## 2. Validación de Esquema (`config/storyboard-schema.json`)

El archivo generado `campaign/storyboard/storyboard.json` DEBE ser validado obligatoriamente contra el esquema formal JSON Schema Draft-07. Cada escena exige:
- `scene_id` (formato `scene_01`, `scene_02`, ...)
- `start`, `end`, `duration` (numéricos continuos)
- `audio_segment` (`beat_start`, `beat_end`, `energy_level`, `musical_cue`)
- `lyric_reference`
- `visual`, `camera`, `lighting`, `emotion`, `copy`
- `typography` (`font_family`, `size`, `color`, `alignment`)
- `animation`, `transition` (`type`, `duration_seconds`)
- `brand_visibility` (`none`, `subtle`, `product_in_use`, `explicit_logo`, `hero_packshot`)
- `asset_ids` (lista de identificadores de clips)
- `tool` (`DaVinci Resolve`, `Remotion`, `HyperFrames`, `FFmpeg`)
- `rationale` (justificación estratégica)

---

## 3. Scripts e Interfaz CLI

- `scripts/build_storyboard.py`:
  - Lee `campaign/campaign-manifest.json`, `campaign/audio/audio-analysis.json`, `campaign/audio/lyric-alignment.json` y `campaign/assets/asset-inventory.json`.
  - Construye la estructura completa escena por escena.
  - Valida el documento resultante contra `config/storyboard-schema.json`.
  - Guarda el resultado en `campaign/storyboard/storyboard.json`.
