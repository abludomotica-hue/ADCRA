---
name: video-analysis
description: Motor de análisis y catalogación de video para ADCRA. Inspecciona streams técnicos de metraje (resolución, códec, fps, bitrate), clasifica planos cinematográficos (macro, medio, general), evalúa iluminación y movimiento de cámara, y genera el inventario estructurado de activos.
---

# Video Analysis — Análisis y Catalogación de Metraje

La habilidad **Video Analysis** constituye el ojo técnico y cinematográfico de ADCRA. Se encarga de examinar exhaustivamente cada archivo de video e imagen disponible en el proyecto para garantizar su conformidad técnica y clasificar su valor estético y narrativo antes de entrar a la sala de montaje.

---

## 1. Taxonomía de Clasificación Visual

Todo clip de video procesado es analizado y categorizado bajo tres dimensiones fundamentales:

### 1.1. Tipo de Plano Cinematográfico (`shot_type`)
- `macro_detail`: Primerísimo plano o fotografía macro (ej. yerba mate, bombilla, textura de madera).
- `close_up`: Primer plano enfocado en rostros, gestos, manos o el sorbo del mate.
- `medium_shot`: Plano medio que muestra a una persona interactuando con su entorno inmediato.
- `wide_establishing`: Plano general amplio de contexto territorial (ej. Cordillera de los Andes, amanecer urbano).
- `group_shot`: Plano de conjunto con múltiples personas interactuando (ej. estudiantes, reunión de amigos).

### 1.2. Iluminación y Paleta Lumínica (`lighting`)
- `golden_hour_morning`: Luz dorada rasante de amanecer o atardecer, sombras suaves y calidez terrosa.
- `warm_natural_window`: Luz natural suave filtrada por ventanas en ambientes interiores.
- `soft_daylight`: Luz de día difusa en espacios exteriores urbanos.
- `interior_ambient`: Iluminación práctica cálida y realista sin proyectores de estudio artificiales.

### 1.3. Movimiento y Estabilidad de Cámara (`camera_movement`)
- `static`: Cámara fija sobre trípode con mínima trepidación.
- `slow_pan`: Paneo horizontal lento y deliberado.
- `slow_dolly_tracking`: Desplazamiento suave en travelling siguiendo al sujeto.
- `handheld_organic`: Movimiento en mano orgánico, humano y elegante (nunca robótico ni excesivamente tembloroso).

---

## 2. Detección y Conformidad de Producto (Brand Rules)

En consonancia con las directivas de marca de *Locos Materos*:
- **`mate_presence`**: Bandera booleana que verifica si el mate aparece físicamente en la toma.
- **`realistic_mate_rules`**: Confirma proporciones de la calabaza, bombilla metálica, hojas de yerba y vapor natural.
- **`no_baked_text`**: Verifica que el video esté limpio de títulos o subtítulos incrustados que impidan la posterior diagramación gráfica.

---

## 3. Esquema de Salida (`campaign/assets/asset-inventory.json`)

El inventario de activos consolida:
1. `summary`: Total de clips de video, imágenes de referencia, duración acumulada y resolución dominante.
2. `video_assets`: Lista detallada de cada archivo `.mp4` con:
   - `asset_id`, `filename`, `relative_path`, `file_size_bytes`
   - `technical_specs`: `duration_seconds`, `width`, `height`, `aspect_ratio`, `fps`, `codec`, `bitrate_kbps`, `has_audio`
   - `cinematographic_classification`: `shot_type`, `lighting`, `camera_movement`, `primary_subjects`, `emotion_evoked`
   - `brand_attributes`: `mate_visible`, `setting_type` (interior_hogar, exterior_cordillera, calle_barrio, universidad)
   - `associated_scene_id`: Enlace formal con la escena del storyboard y la lírica
3. `image_assets`: Catálogo de imágenes de marca y referencias visuales.
4. `audio_assets`: Referencia a las pistas de audio disponibles.

---

## 4. Scripts Asociados

- `scripts/analyze_footage.py`:
  - `--input-dir`: Directorio a inspeccionar (por defecto `Recursos/videos/`).
  - `--output`: Destino del informe (por defecto `campaign/assets/asset-inventory.json`).
  - `--catalog-all`: Incluye también imágenes de `Recursos/Imeges/` y audio de `Recursos/Audios/`.
