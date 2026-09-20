---
name: beat-sync-editor
description: Editor de montaje sincronizado al beat musical con precisión de cuadro, alineación a transientes y exportación universal de timelines (EDL CMX 3600, FCP7 XML, JSON Timeline).
version: 1.0.0
domain: production
tools_integrated:
  - Python Timeline Engine
  - CMX 3600 EDL Generator
  - FCP7 XML Generator
  - FFmpeg
contracts:
  input:
    - campaign/storyboard/storyboard.json
    - campaign/audio/audio-analysis.json
    - campaign/assets/asset-inventory.json
    - campaign/motion-graphics/motion-manifest.json
  output:
    - campaign/timeline/timeline.json
    - campaign/timeline/locos_materos_edit.edl
    - campaign/timeline/locos_materos_edit.xml
    - campaign/timeline/ffmpeg_assembly.sh
schema: config/timeline-schema.json
---

# Beat-Synced Editor — Montaje Rítmico y Timelines Universales

## 1. Misión
Garantizar la sincronización milimétrica entre la estructura narrativa visual y el pulso musical del spot publicitario. Cada corte debe ocurrir en un downbeat (primer tiempo de compás) o transiente rítmico musical con una tolerancia de desfase inferior a 42 ms (menos de un fotograma a 24 fps).

---

## 2. Reglas de Sincronización Rítmica

1. **Alineación a Downbeats (Compás 4/4):**
   - Con un tempo detectado de **107.7 BPM**, cada compás musical dura aproximadamente **2.228 segundos**.
   - Los cortes de escena se fijan en múltiplos de compás o semicompas musicales, asegurando resolución rítmica natural.
2. **Matemática de Timecode a 24.0 fps:**
   - La duración total de 29.187s equivale exactamente a **700 fotogramas** (00:00:29:04).
   - Los puntos de entrada (`In`) y salida (`Out`) se calculan en enteros absolutos sin redondeos acumulativos.
3. **Estructura Multicapa:**
   - **Video Track 1 (V1):** Metraje bruto de cámara (`Recursos/videos/`).
   - **Video Track 2 (V2):** Overlays transparentes de cinética tipográfica (`campaign/motion-graphics/renders/`).
   - **Audio Track 1 (A1):** Pista musical master estéreo (`Recursos/Audios/Entre_mates_y_sol.mp3`).

---

## 3. Formatos de Intercambio Soportados

1. **CMX 3600 EDL (`.edl`):**
   Estándar de la industria para conformado en salas de montaje y postproducción cinematográfica. Formato Non-Drop Frame (24 fps).
2. **FCP7 XML (`.xml`):**
   Esquema Apple XML v4 / DaVinci Resolve Timeline Import, preservando tracks multicapa, nombres de clips, timecodes fuente y marcadores de beat.
3. **JSON Master Timeline (`timeline.json`):**
   Representación canónica de datos para automatizaciones headless con FFmpeg, Remotion o DaVinci Resolve Scripting API.
4. **Script de Ensamblaje FFmpeg (`ffmpeg_assembly.sh`):**
   Pipeline de conformado rápido para previsualización offline sin depender de GUI.

---

## 4. Comandos de Operación CLI

- **Generación y Validación Completa:**
  ```bash
  python3 .agents/skills/production/beat-sync-editor/scripts/build_beat_edit.py
  ```
- **Validación Únicamente:**
  ```bash
  python3 .agents/skills/production/beat-sync-editor/scripts/build_beat_edit.py --validate-only
  ```
