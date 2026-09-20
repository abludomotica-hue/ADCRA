---
name: color-grading
description: Asistente de etalonaje y corrección de color para DaVinci Resolve y FFmpeg con identidad visual de marca, generación matemática de LUTs 3D .cube y balance cromático plano a plano.
version: 1.0.0
domain: post-production
tools_integrated:
  - DaVinci Resolve Color Page
  - 3D LUT Generator (.cube)
  - FFmpeg lut3d Filter
contracts:
  input:
    - campaign/storyboard/storyboard.json
    - campaign/assets/asset-inventory.json
    - campaign/timeline/timeline.json
  output:
    - campaign/color/color-grading-manifest.json
    - campaign/color/luts/locos_materos_warm_cinematic.cube
    - campaign/color/luts/locos_materos_editorial_film.cube
    - campaign/color/luts/locos_materos_master_grade.cube
schema: config/color-grading-schema.json
---

# Color Grading Assistant — Identidad Cromática y LUTs 3D

## 1. Misión
Establecer y aplicar una identidad cromática cinematográfica, cálida y coherente para la campaña de **Locos Materos**. Garantizar la continuidad tonal entre tomas dispares (amaneceres en cocina, macros de yerba, exteriores cordilleranos, escenas urbanas y packshots), eliminando dominantes frías y potenciando la calidez del ritual matero.

---

## 2. Identidad Visual y Paleta Cromática

1. **Altas Luces Doradas (`#D4AF37` / 5800K - 6200K):**
   Inspiradas en los primeros rayos de sol filtrándose por la ventana y el reflejo cálido sobre el metal de la bombilla y la pava.
2. **Verdes Orgánicos Profundos (`#0D5C3A`):**
   Saturación selectiva y densidad en las hojas secas y corte de yerba mate, evitando tonos artificiales o radioactivos.
3. **Medios Tonos Terrosos:**
   Pieles naturales con tonos cobre/dorado y maderas de mesas cálidas con gradación suave.
4. **Negros Densos y Limpios (`#1A1A1A`):**
   Punto negro anclado para evitar sombras empastadas o deslavadas, manteniendo un contraste cinematográfico de curva en 'S' suave.

---

## 3. Especificación de LUTs 3D Generadas (.cube)

Las Look-Up Tables 3D se generan siguiendo el estándar de la industria (Adobe / Blackmagic Design CMX):
- **Formato:** Texto plano ASCII en rejilla regular cúbica ($N \times N \times N$).
- **Tamaño estándar:** $33 \times 33 \times 33$ (35,937 puntos tridimensionales) para previsualización fluida y $65 \times 65 \times 65$ (274,625 puntos) para masterización final.
- **Espacio de Color Objetivo:** Rec.709 / Gamma 2.4 (SDR 100 nits).

### Catálogo de LUTs:
1. `locos_materos_warm_cinematic.cube` (33x33x33): Look principal para escenas cotidianas, calidez envolvente y contraste suave.
2. `locos_materos_editorial_film.cube` (33x33x33): Emulación de película analógica con hombro suave en altas luces y microcontraste.
3. `locos_materos_master_grade.cube` (65x65x65): Tabla maestra de alta precisión para renderizado final sin artefactos de gradación.

---

## 4. Comandos de Operación CLI

- **Generación de LUTs y Manifiesto de Color:**
  ```bash
  python3 .agents/skills/post-production/color-grading/scripts/generate_color_grade.py
  ```
- **Validación Únicamente:**
  ```bash
  python3 .agents/skills/post-production/color-grading/scripts/generate_color_grade.py --validate-only
  ```
