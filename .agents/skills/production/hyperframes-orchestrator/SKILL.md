---
name: hyperframes-orchestrator
description: Orquestador de motion graphics, cinética tipográfica y overlays animados basados en HTML/CSS/SVG para campañas audiovisuales ADCRA.
version: 1.0.0
domain: production
tools_integrated:
  - HyperFrames CLI
  - Google Chrome Headless
  - FFmpeg / FFprobe
contracts:
  input:
    - campaign/storyboard/storyboard.json
    - campaign/creative/creative-copy.json
  output:
    - campaign/motion-graphics/motion-manifest.json
    - campaign/motion-graphics/templates/*.html
    - campaign/motion-graphics/renders/*.png
schema: config/motion-graphics-schema.json
---

# HyperFrames Orchestrator — Motion Graphics Designer

## 1. Misión
Transformar los textos publicitarios seleccionados (`creative-copy.json`) y la estructura temporal del guion gráfico (`storyboard.json`) en composiciones animadas de alta fidelidad estética, tipografía cinética y overlays de marca usando tecnologías web estándares (HTML5, CSS3 Animations, SVG).

---

## 2. Pautas de Identidad de Marca (Locos Materos)

El diseño de motion graphics debe honrar la identidad visual de **Locos Materos**:
- **Verde Mate Profundo (`#0D5C3A`):** Representa la yerba mate, la naturaleza y la autenticidad. Utilizado en acentos principales, barras decorativas y sombras sutiles.
- **Dorado Yerba / Calidez (`#D4AF37`):** Representa el sol, la calidez del hogar y la calidad artesanal. Utilizado en bordes destacados, glows y detalles tipográficos de alto impacto.
- **Blanco Puro (`#FFFFFF`):** Máxima legibilidad y contraste para el texto sobre cualquier fondo de video.
- **Carbón Mate (`#1A1A1A`):** Fondos de tarjetas, viñetas de contraste y pastillas lower-third con opacidades controladas (`rgba(26, 26, 26, 0.85)`).

---

## 3. Especificaciones del Canvas y Safe Zones (9:16 Vertical)

En video vertical para redes sociales (TikTok, Instagram Reels, YouTube Shorts), elementos clave de la interfaz gráfica de la plataforma cubren los bordes superior, inferior y derecho.

- **Resolución Canvas:** 720 × 1280 píxeles.
- **Frame Rate:** 24.0 fps.
- **Margen Superior (Top Safe Zone):** 120 px (espacio libre para barra de estado y buscador).
- **Margen Inferior (Bottom Safe Zone):** 200 px (espacio libre para nombre de cuenta, caption y audio tag).
- **Margen Lateral Izquierdo / Derecho:** 40 px.
- **Área Útil Segura:** 640 × 960 píxeles centrada verticalmente.

---

## 4. Estilos de Cinética Tipográfica

1. **`fade_in_word_by_word`:**
   Aparición progresiva palabra por palabra, ideal para textos poéticos o reflexivos (ej. "Cada día comienza con una pausa").
2. **`slide_up_reveal`:**
   Desplazamiento vertical suave de abajo hacia arriba con desenfoque de entrada (`translateY(30px) -> 0`, `blur(8px) -> 0`).
3. **`lower_third_pill`:**
   Cápsula geométrica moderna flotante con fondo carbón translúcido y borde dorado de 2px, ideal para subtítulos y llamadas conversacionales.
4. **`kinetic_stomp`:**
   Impacto tipográfico rítmico sincronizado al beat musical con escala (`scale(1.3) -> 1.0`).
5. **`hero_packshot_reveal`:**
   Cierre comercial majestuoso que combina el logo vectorial, el claim oficial *"¿Dónde estás tú? Está tu mate"* y la URL web (`www.locosmateros.cl`).

---

## 5. Protocolo de Ejecución y Validación

1. **Generación de Templates:**
   El script operacional `generate_motion_graphics.py` extrae cada escena, asocia la variante de copy ganadora y renderiza un documento HTML autosuficiente en `campaign/motion-graphics/templates/scene_XX.html`.
2. **Validación contra Schema:**
   El manifiesto generado `campaign/motion-graphics/motion-manifest.json` debe validar sin excepciones contra `config/motion-graphics-schema.json`.
3. **Renderizado de Validación:**
   Generación de capturas visuales (PNG) para verificación de composición, contraste y safe zones.
