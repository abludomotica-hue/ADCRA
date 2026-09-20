---
name: remotion-orchestrator
description: Motor de video programático en React con Remotion para la composición procedural, parametrización por props y generación de variantes masivas de video en ADCRA.
version: 1.0.0
domain: production
tools_integrated:
  - Remotion CLI (@remotion/cli)
  - React 19 / Node.js
  - FFmpeg
contracts:
  input:
    - campaign/storyboard/storyboard.json
    - campaign/creative/creative-copy.json
    - campaign/audio/audio-analysis.json
    - campaign/motion-graphics/motion-manifest.json
  output:
    - campaign/remotion/composition-manifest.json
    - campaign/remotion/props.json
    - campaign/remotion/variants.json
    - campaign/remotion/renders/*.png
schema: config/remotion-composition-schema.json
---

# Remotion Orchestrator — Programmatic Video Engine

## 1. Misión
El módulo `remotion-orchestrator` dota a ADCRA de capacidades de video programático puro mediante React y Remotion. Permite transformar el storyboard, el audio y los textos publicitarios en un grafo de componentes React determinista, completamente parametrizable a través de `props` JSON para A/B testing y generación masiva de variantes de campaña.

---

## 2. Arquitectura de Composición React

Una composición Remotion en ADCRA sigue el siguiente diseño modular:
- **`Root.jsx`:** Define la composición maestra `<Composition id="LocosMaterosCommercial" ... />`, especificando resolución (720x1280), frame rate (24.0 fps), duración en frames (700 frames ≈ 29.187s) y sus `defaultProps`.
- **`Main.jsx`:** Componente principal que orquesta:
  1. **Secuencias de Video (`<Sequence>` + `<Video>` / `<Img>`):** Mapeo de los 9 clips audiovisuales de `Recursos/videos/` con transiciones de corte o disolución.
  2. **Pista de Audio Sincronizada (`<Audio>`):** Inserción del track oficial `Entre_mates_y_sol.mp3`.
  3. **Overlays Tipográficos Dinámicos:** Animaciones de texto basadas en `spring()` e `interpolate()` sincronizadas con los frames clave de cada escena.
  4. **Safe Zones Enforcement:** Delimitación visual para no obstruir elementos en TikTok / Instagram Reels.
  5. **Hero Packshot:** Tarjeta final animada con logo vectorial, claim corporativo y badge CTA web.

---

## 3. Matriz de Variantes Paramétricas

El motor genera automáticamente 4 variantes de campaña a partir de una única plantilla base:
1. **`master_30s_emocional`:** Versión oficial completa de 29.187s orientada al público general con énfasis en la pausa cotidiana y el ritual.
2. **`variant_publicitaria`:** Versión optimizada con copys comerciales orientados a conversión, destacando la marca *Locos Materos* en cada llamado.
3. **`variant_conversacional`:** Versión enfocada en lenguaje espontáneo, cercanía y naturalidad cotidiana.
4. **`bumper_15s`:** Versión condensada de 15 segundos (360 frames) diseñada para pauta de pre-roll y retención rápida, culminando en packshot directo.

---

## 4. Comandos y Operaciones CLI

- **Inspección de Composiciones:**
  ```bash
  NODE_PATH=/data/nodejs/lib/node_modules remotion compositions campaign/remotion/index.jsx
  ```
- **Generación y Validación de Manifiesto:**
  ```bash
  python3 .agents/skills/production/remotion-orchestrator/scripts/remotion_orchestrator.py --validate-only
  ```
- **Renderizado de Fotograma Clave (Still):**
  ```bash
  python3 .agents/skills/production/remotion-orchestrator/scripts/remotion_orchestrator.py --render-still 650
  ```
