---
name: social-formatter
description: Formateador multiplataforma para redes sociales (TikTok, Instagram Reels, YouTube Shorts, Feed 1:1, Widescreen 16:9) con cálculo estricto de Safe Zones, prevención de oclusiones de interfaz móvil y adaptación de ratios visuales.
domain: production
version: 1.0.0
schema: config/social-formatter-schema.json
inputs:
  - campaign/timeline/timeline.json
  - campaign/motion-graphics/motion-manifest.json
  - campaign/storyboard/storyboard.json
outputs:
  - campaign/deliverables/social-format-manifest.json
  - campaign/deliverables/guides/tiktok_safe_zone.png
  - campaign/deliverables/guides/reels_safe_zone.png
  - campaign/deliverables/guides/shorts_safe_zone.png
  - campaign/deliverables/guides/feed_square_safe_zone.png
  - campaign/deliverables/guides/widescreen_safe_zone.png
---

# Social Media Formatter Skill

## Propósito
Garantiza que el material publicitario de la campaña *"¿Dónde estás tú? Está tu mate"* de **Locos Materos** se entregue optimizado y sin pérdidas de legibilidad en cualquier plataforma social contemporánea, evitando que los textos, logotipos y elementos clave queden ocultos debajo de los elementos de interfaz nativos de cada aplicación móvil (botones de like, comentarios, nombre de usuario, títulos de audio y barras de navegación).

## Plataformas y Ratios Soportados

| Plataforma / Destino | Ratio | Resolución Target | Safe Margins (Top / Bottom / Left / Right) |
| :--- | :--- | :--- | :--- |
| **TikTok** | 9:16 | 720x1280 (HD) / 1080x1920 (FHD) | Top: 110px / Bottom: 220px / Left: 40px / Right: 90px |
| **Instagram Reels** | 9:16 | 720x1280 (HD) / 1080x1920 (FHD) | Top: 100px / Bottom: 200px / Left: 40px / Right: 85px |
| **YouTube Shorts** | 9:16 | 720x1280 (HD) / 1080x1920 (FHD) | Top: 90px / Bottom: 180px / Left: 40px / Right: 80px |
| **Meta Feed Square** | 1:1 | 1080x1080 | Top: 50px / Bottom: 50px / Left: 50px / Right: 50px |
| **YouTube Widescreen** | 16:9 | 1920x1080 | Top: 80px / Bottom: 80px / Left: 100px / Right: 100px |

## Estrategias de Adaptación Multi-Ratio

1. **Vertical Nativo 9:16 (TikTok / Reels / Shorts):**
   - Passthrough directo de la composición master vertical (720x1280 @ 24 fps).
   - Verificación de que los tercios inferiores y superiores de Motion Graphics respeten las zonas de oclusión UI de cada app.

2. **Cuadrado 1:1 (Meta Feed / Carousel):**
   - Adaptación de 9:16 a 1:1 manteniendo la escena centrada verticalmente.
   - Relleno de franjas laterales con color oficial de identidad de marca `#0D5C3A` (verde mate profundo) o degradado institucional con acento `#D4AF37`.

3. **Widescreen 16:9 (YouTube Horizontal / TV / Display):**
   - Centrado vertical de la toma 9:16 con fondo ampliado dinámico con desenfoque gausiano/caja (`boxblur=20:20`) del propio contenido para conservar continuidad visual cinematográfica sin bandas negras vacías.

## Generación de Guías Visuales de Safe Zone
El formateador genera máscaras PNG semitransparentes en resolución nativa para ser superpuestas en DaVinci Resolve, Remotion o editores NLE para verificación visual previa a la exportación final.

## Validación Formal
El manifiesto `campaign/deliverables/social-format-manifest.json` se valida contra `config/social-formatter-schema.json`.
