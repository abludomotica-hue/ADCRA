---
name: audio-analysis
description: Motor de inteligencia y análisis de audio para ADCRA. Extrae duración con precisión de muestra, calcula tempo (BPM), rastrea beats y compases, evalúa envolventes de energía y segmenta la estructura musical para sincronización rítmica publicitaria.
---

# Audio Analysis — Inteligencia y Análisis Musical

La habilidad **Audio Analysis** es el oído analítico de ADCRA. Procesa bandas sonoras, canciones comerciales y pistas de voz para desentrañar su estructura temporal, métrica y dinámica, proporcionando las anclas rítmicas necesarias para que el montaje y los cortes visuales sincronicen con precisión milimétrica.

---

## 1. Capacidades Principales

1. **Duración y Metadatos Exactos:**  
   Extracción de duración en segundos (con precisión de microsegundos) y conteo de muestras a través de `ffprobe` y decodificación PCM.
2. **Estimación de Tempo (BPM):**  
   Cálculo de tempo global mediante función de detección de onsets (spectral novelty curve) y autocorrelación temporal periódica.
3. **Seguimiento de Beats y Compases (Bars):**  
   Identificación de instantes exactos de cada pulso musical (beats) y agrupación métrica en compases (generalmente 4/4), permitiendo cortes en el beat 1 (downbeat) o cortes sincopados.
4. **Perfil Dinámico y Curva de Energía:**  
   Cálculo de RMS y flujo espectral por ventana temporal (ej. 100ms) clasificando los segmentos en niveles: `low`, `medium`, `high`, `climax`, `drop`.
5. **Segmentación Estructural:**  
   División de la pista en bloques musicales comprensibles por el director creativo (`intro`, `verse`, `build_up`, `chorus`, `bridge`, `outro`).

---

## 2. Esquema de Salida (`campaign/audio/audio-analysis.json`)

El análisis genera un archivo estructurado con la siguiente especificación:

```json
{
  "audio_file": "Recursos/Audios/Entre_mates_y_sol.mp3",
  "format": "mp3",
  "duration_seconds": 66.089,
  "sample_rate": 44100,
  "channels": 2,
  "bpm": 105.0,
  "time_signature": "4/4",
  "beats_count": 115,
  "beats": [0.42, 0.99, 1.56, 2.13, ...],
  "downbeats": [0.42, 2.70, 4.98, ...],
  "energy_curve": [
    {"start": 0.0, "end": 5.0, "energy_level": "low", "rms": 0.08},
    {"start": 5.0, "end": 15.0, "energy_level": "medium", "rms": 0.22},
    {"start": 15.0, "end": 28.0, "energy_level": "high", "rms": 0.45},
    {"start": 28.0, "end": 35.0, "energy_level": "climax", "rms": 0.58}
  ],
  "sections": [
    {"name": "intro", "start": 0.0, "end": 7.2, "description": "Guitarras acústicas y clima matutino íntimo"},
    {"name": "verse_1", "start": 7.2, "end": 18.5, "description": "Entrada de ritmo suave, desarrollo cotidiano"},
    {"name": "chorus", "start": 18.5, "end": 32.0, "description": "Crescendo y encuentro social"},
    {"name": "outro", "start": 32.0, "end": 66.0, "description": "Desvanecimiento y cierre de marca"}
  ],
  "recommended_commercial_cuts": [
    {"duration": 15, "start": 0.0, "end": 15.0, "target": "Story / Bumper 15s"},
    {"duration": 30, "start": 0.0, "end": 30.0, "target": "Reel / Broadcast 30s"}
  ]
}
```

---

## 3. Scripts e Interfaz CLI

- `scripts/analyze_audio.py`:
  - `--audio <path>`: Analiza cualquier archivo de audio (MP3, WAV, AAC, FLAC).
  - `--output <path>`: Especifica la ruta del informe JSON (por defecto `campaign/audio/audio-analysis.json`).
  - `--commercial-cut <seconds>`: Limita el análisis detallado de cortes a la duración objetivo comercial (ej. 30s).
