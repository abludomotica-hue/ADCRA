---
name: sound-designer
description: Diseñador de sonido, foley publicitario, ducking inteligente y masterización broadcast/streaming bajo norma EBU R128 (-14 LUFS, -1.0 dBTP).
version: 1.0.0
domain: post-production
tools_integrated:
  - FFmpeg Audio Engine (loudnorm, sidechaincompress, equalizer)
  - Python Audio Synthesis (scipy.signal, soundfile, numpy)
  - DaVinci Resolve Fairlight Page
contracts:
  input:
    - campaign/storyboard/storyboard.json
    - campaign/audio/audio-analysis.json
    - campaign/timeline/timeline.json
  output:
    - campaign/audio/sound-design-manifest.json
    - campaign/audio/locos_materos_master_mix.wav
    - campaign/audio/locos_materos_master_mix.mp3
schema: config/sound-design-schema.json
---

# Sound Designer & Fairlight — Audio Multicapa y Masterización EBU R128

## 1. Misión
Crear una experiencia acústica inmersiva, sensorial y cinematográfica para el spot publicitario de **Locos Materos**. Enriquecer la música con foley hiperrealista (vapor de agua, crujido de yerba, vertido de agua caliente, sonido del sorbo placentero y campana armónica de cierre), aplicar atenuación rítmica (ducking) para priorizar eventos sonoros clave y masterizar la mezcla final bajo el estándar internacional **EBU R128 / ITU-R BS.1770-4**.

---

## 2. Pistas y Arquitectura de Mezcla

1. **Pista BGM (Música de Fondo):**
   - Track: `Recursos/Audios/Entre_mates_y_sol.mp3`.
   - Nivel base de mezcla: `-1.5 dB` nominal.
   - Ducking dinámico: Atenuación de `-4.0 dB` a `-6.0 dB` en puntos de foley cruciales (cebado de agua, sorbo final).
2. **Pista SFX / Foley (Efectos Sonoros Orgánicos):**
   - `cue_01`: Vapor y silbido sutil de hervidor (Escena 1: 0.5s - 2.5s).
   - `cue_02`: Caída y acomodo de hojas secas de yerba (Escena 2: 3.8s - 5.0s).
   - `cue_03`: Brisa fresca matinal cordillerana (Escena 3: 7.0s - 8.5s).
   - `cue_04`: Chorro de agua caliente infusionando yerba y efervescencia (Escena 4: 10.5s - 12.2s).
   - `cue_05`: Pasos rítmicos en adoquines urbanos (Escena 5: 14.0s - 15.5s).
   - `cue_06`: Ambiente suave de oficina y posado de mate en escritorio (Escena 6: 17.0s - 18.5s).
   - `cue_07`: Risa espontánea y murmullo juvenil universitario (Escena 7: 20.2s - 21.8s).
   - `cue_08`: Sorbo característico de mate y exhalación de placer (Escena 8: 23.5s - 25.2s).
   - `cue_09`: Campanada acústica dorada / chime con decay armónico (Escena 9: 26.2s - 29.187s).

---

## 3. Estándares de Masterización (EBU R128)

La mezcla final se procesa mediante un algoritmo de masterización de doble paso:
- **Sonoridad Integrada (Integrated Loudness):** **-14.0 LUFS** (± 0.5 LUFS), calibrada para TikTok, Instagram Reels, YouTube Shorts y Spotify.
- **Pico Verdadero Máximo (Max True Peak):** **-1.0 dBTP** para garantizar ausencia absoluta de distorsión inter-sample tras la codificación lossy (AAC/MP3/Opus).
- **Rango de Sonoridad (LRA):** 5.0 a 8.0 LU, preservando dinámica natural sin fatiga auditiva en altavoces de teléfonos móviles.
- **Frecuencia de Muestreo / Cuantización:** 48.0 kHz / 24-bit PCM estéreo broadcast.

---

## 4. Comandos de Operación CLI

- **Generación y Masterización Completa:**
  ```bash
  python3 .agents/skills/post-production/sound-designer/scripts/design_sound.py
  ```
- **Validación Únicamente:**
  ```bash
  python3 .agents/skills/post-production/sound-designer/scripts/design_sound.py --validate-only
  ```
