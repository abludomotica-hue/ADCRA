---
name: lyric-intelligence
description: Inteligencia lírica y alineación semántica para ADCRA. Alinea versos y palabras clave con timestamps de audio, analiza el significado temático y mapea momentos líricos con intenciones visuales y metraje correspondiente.
---

# Lyric Intelligence — Inteligencia Lírica y Semántica

La habilidad **Lyric Intelligence** establece el puente cognitivo entre el contenido vocal/lírico de la música y la narrativa visual de la campaña. Su propósito es garantizar que lo que se ve en pantalla resuene conceptual y temporalmente con lo que se escucha en la canción.

---

## 1. Principios de Alineación Lírico-Visual

1. **No Espejo Literal:**  
   La imagen no debe ser un subtítulo redundante ni una traducción literal palabra por palabra; debe ampliar y enriquecer la emoción que evoca la lírica.
2. **Sincronización Rítmica y Fonética:**  
   Los momentos clave de vocalización (entradas de voz, silencios y remates de frase) deben coordinarse con transiciones, miradas o cambios de plano.
3. **Categorización Temática:**  
   Cada línea cantada se clasifica en una dimensión conceptual de la marca:
   - `RITUAL_START`: Preparación, intimidad, despertar.
   - `NATURAL_IDENTITY`: Territorio, cordillera, sol, paisaje chileno.
   - `COMMUNITY_MOVEMENT`: Calles, barrio, energía compartida de un país en marcha.
   - `WORK_AND_STUDY`: Esfuerzo, universidad, oficinas, perseverancia cotidiana.
   - `SENSORY_CLOSENESS`: Primer plano, textura, calidez del sorbo.
   - `BRAND_CORE`: Tagline y propósito existencial de la marca.

---

## 2. Esquema de Salida (`campaign/audio/lyric-alignment.json`)

El análisis genera el archivo de alineación lírica con la siguiente estructura:

```json
{
  "song_title": "Entre mates y sol",
  "total_phrases": 9,
  "language": "es-CL",
  "thematic_arc": "Ritual matutino -> Identidad territorial -> Movimiento cotidiano -> Unión comunitaria",
  "alignment": [
    {
      "phrase_id": "lyric_01",
      "text": "Ya está sonando el hervidor",
      "start": 0.50,
      "end": 3.80,
      "duration": 3.30,
      "thematic_category": "RITUAL_START",
      "emotional_tone": "Intimidad y calma matutina",
      "associated_video_asset": "Recursos/videos/Escena 01 Ya está sonando el hervidor.mp4",
      "visual_intention": "Plano medio de la cocina con luz suave matutina, vapor saliendo del hervidor",
      "keywords": [
        {"word": "sonando", "approx_time": 1.20},
        {"word": "hervidor", "approx_time": 2.40}
      ]
    },
    ...
  ]
}
```

---

## 3. Scripts Asociados

- `scripts/align_lyrics.py`:
  - Lee `campaign/audio/audio-analysis.json` para obtener los beats y compases de referencia.
  - Genera el mapa temporal detallado de cada verso y palabra clave.
  - Vincula cada segmento lírico con los archivos de metraje disponibles en `Recursos/videos/`.
  - Exporta el informe formal a `campaign/audio/lyric-alignment.json`.
