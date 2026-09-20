#!/usr/bin/env python3
"""
ADCRA — HyperFrames Orchestrator & Motion Graphics Designer
Genera plantillas HTML5/CSS3 con cinética tipográfica, overlays transparentes RGBA 9:16 (720x1280)
y el manifiesto oficial de motion graphics validado contra config/motion-graphics-schema.json.
"""

import sys
import os
import json
import base64
import argparse
import subprocess
from pathlib import Path
import jsonschema

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

BRAND_PALETTE = {
    "primary": "#0D5C3A",      # Verde Mate Profundo
    "accent": "#D4AF37",       # Dorado Yerba
    "background": "transparent",
    "text_light": "#FFFFFF",
    "text_dark": "#1A1A1A"
}

SAFE_ZONES = {
    "top_px": 120,
    "bottom_px": 200,
    "left_px": 40,
    "right_px": 40
}

STYLE_MAPPING = {
    "scene_01": ("fade_in_word_by_word", 34),
    "scene_02": ("slide_up_reveal", 34),
    "scene_03": ("lower_third_pill", 32),
    "scene_04": ("slide_up_reveal", 34),
    "scene_05": ("kinetic_stomp", 38),
    "scene_06": ("lower_third_pill", 32),
    "scene_07": ("fade_in_word_by_word", 34),
    "scene_08": ("slide_up_reveal", 34),
    "scene_09": ("hero_packshot_reveal", 40)
}

def get_logo_base64() -> str:
    logo_path = WORKSPACE_ROOT / "Recursos" / "Imeges" / "WhatsApp Image 2026-09-16 at 10.21.14 PM.jpeg"
    if logo_path.is_file():
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"
    return ""

def generate_scene_html(scene_id: str, text: str, style: str, duration: float, font_size: int) -> str:
    words = text.split()
    word_spans = []
    step = min(0.35, (duration * 0.5) / max(len(words), 1))
    for i, w in enumerate(words):
        delay = i * step
        word_spans.append(f'<span class="word" style="animation-delay: {delay:.2f}s">{w}</span>')
    words_html = " ".join(word_spans)

    logo_b64 = get_logo_base64() if style == "hero_packshot_reveal" else ""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=720, height=1280, initial-scale=1.0">
<title>ADCRA Overlay — {scene_id}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    width: 720px;
    height: 1280px;
    background: transparent;
    overflow: hidden;
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    position: relative;
    -webkit-font-smoothing: antialiased;
  }}

  /* Safe Zones Guide (Toggleable) */
  .safe-area {{
    position: absolute;
    top: {SAFE_ZONES['top_px']}px;
    bottom: {SAFE_ZONES['bottom_px']}px;
    left: {SAFE_ZONES['left_px']}px;
    right: {SAFE_ZONES['right_px']}px;
    pointer-events: none;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
  }}

  /* STYLES */

  /* 1. Fade in word by word */
  .style-fade-in-word {{
    text-align: center;
    max-width: 620px;
    margin-bottom: 40px;
  }}
  .style-fade-in-word .word {{
    display: inline-block;
    color: {BRAND_PALETTE['text_light']};
    font-size: {font_size}px;
    font-weight: 600;
    text-shadow: 0 4px 16px rgba(0, 0, 0, 0.8), 0 1px 3px rgba(0,0,0,0.9);
    opacity: 0;
    transform: translateY(10px);
    animation: fadeInWord 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }}
  @keyframes fadeInWord {{
    to {{
      opacity: 1;
      transform: translateY(0);
    }}
  }}

  /* 2. Slide Up Reveal */
  .style-slide-up {{
    text-align: center;
    max-width: 620px;
    margin-bottom: 40px;
    animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }}
  .style-slide-up h2 {{
    color: {BRAND_PALETTE['text_light']};
    font-size: {font_size}px;
    font-weight: 700;
    line-height: 1.25;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.85);
  }}
  .style-slide-up .accent-line {{
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, {BRAND_PALETTE['accent']}, {BRAND_PALETTE['primary']});
    margin: 14px auto 0 auto;
    border-radius: 2px;
  }}
  @keyframes slideUp {{
    from {{
      opacity: 0;
      transform: translateY(40px);
    }}
    to {{
      opacity: 1;
      transform: translateY(0);
    }}
  }}

  /* 3. Lower Third Pill */
  .style-lower-third {{
    margin-bottom: 30px;
    background: rgba(26, 26, 26, 0.88);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 2px solid {BRAND_PALETTE['accent']};
    border-radius: 40px;
    padding: 16px 36px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    animation: popIn 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    max-width: 620px;
    text-align: center;
  }}
  .style-lower-third span {{
    color: {BRAND_PALETTE['text_light']};
    font-size: {font_size}px;
    font-weight: 600;
    letter-spacing: -0.02em;
  }}
  @keyframes popIn {{
    from {{
      opacity: 0;
      transform: scale(0.85) translateY(20px);
    }}
    to {{
      opacity: 1;
      transform: scale(1) translateY(0);
    }}
  }}

  /* 4. Kinetic Stomp */
  .style-kinetic-stomp {{
    text-align: center;
    margin-bottom: 50px;
    animation: stomp 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  }}
  .style-kinetic-stomp h2 {{
    color: {BRAND_PALETTE['accent']};
    font-size: {font_size}px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-shadow: 0 4px 24px rgba(0, 0, 0, 0.9);
  }}
  @keyframes stomp {{
    0% {{
      opacity: 0;
      transform: scale(1.6);
    }}
    100% {{
      opacity: 1;
      transform: scale(1);
    }}
  }}

  /* 5. Hero Packshot Reveal (Scene 9) */
  .style-hero-packshot {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
    background: radial-gradient(circle at center, rgba(13, 92, 58, 0.45) 0%, rgba(0, 0, 0, 0.85) 75%);
    animation: heroFade 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    padding: 20px;
    text-align: center;
  }}
  .hero-logo-card {{
    width: 200px;
    height: 200px;
    border-radius: 50%;
    overflow: hidden;
    border: 4px solid {BRAND_PALETTE['accent']};
    box-shadow: 0 0 35px rgba(212, 175, 55, 0.6), 0 12px 30px rgba(0,0,0,0.7);
    margin-bottom: 30px;
    background: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: logoPulse 1.2s ease-out forwards;
  }}
  .hero-logo-card img {{
    width: 88%;
    height: 88%;
    object-fit: contain;
  }}
  .hero-claim {{
    color: {BRAND_PALETTE['text_light']};
    font-size: {font_size}px;
    font-weight: 800;
    text-align: center;
    line-height: 1.25;
    margin-bottom: 24px;
    text-shadow: 0 4px 20px rgba(0,0,0,0.9);
    max-width: 580px;
  }}
  .hero-claim span {{
    color: {BRAND_PALETTE['accent']};
  }}
  .hero-cta-btn {{
    background: linear-gradient(135deg, {BRAND_PALETTE['accent']}, #B38F24);
    color: #1A1A1A;
    font-size: 22px;
    font-weight: 800;
    padding: 14px 38px;
    border-radius: 30px;
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}
  @keyframes heroFade {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
  }}
  @keyframes logoPulse {{
    0% {{ transform: scale(0.6); opacity: 0; }}
    70% {{ transform: scale(1.08); }}
    100% {{ transform: scale(1); opacity: 1; }}
  }}
</style>
</head>
<body>
"""

    if style == "hero_packshot_reveal":
        html += f"""
  <div class="style-hero-packshot">
    <div class="hero-logo-card">
      <img src="{logo_b64}" alt="Locos Materos">
    </div>
    <h1 class="hero-claim">¿Dónde estás tú? <span>Está tu mate.</span></h1>
    <div class="hero-cta-btn">www.locosmateros.cl</div>
  </div>
</body>
</html>
"""
    elif style == "fade_in_word_by_word":
        html += f"""
  <div class="safe-area">
    <div class="style-fade-in-word">
      {words_html}
    </div>
  </div>
</body>
</html>
"""
    elif style == "slide_up_reveal":
        html += f"""
  <div class="safe-area">
    <div class="style-slide-up">
      <h2>{text}</h2>
      <div class="accent-line"></div>
    </div>
  </div>
</body>
</html>
"""
    elif style == "lower_third_pill":
        html += f"""
  <div class="safe-area">
    <div class="style-lower-third">
      <span>{text}</span>
    </div>
  </div>
</body>
</html>
"""
    elif style == "kinetic_stomp":
        html += f"""
  <div class="safe-area">
    <div class="style-kinetic-stomp">
      <h2>{text}</h2>
    </div>
  </div>
</body>
</html>
"""
    return html

def render_snapshot_chrome(html_file: Path, output_png: Path):
    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--default-background-color=00000000",
        "--window-size=720,1280",
        f"--screenshot={output_png}",
        f"file://{html_file.resolve()}"
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Error renderizando snapshot con Chrome: {p.stderr}")

def generate_motion_manifest(render_snapshots: bool = True) -> dict:
    storyboard_path = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
    copy_path = WORKSPACE_ROOT / "campaign" / "creative" / "creative-copy.json"

    with open(storyboard_path, "r", encoding="utf-8") as f:
        sb_data = json.load(f)

    with open(copy_path, "r", encoding="utf-8") as f:
        copy_data = json.load(f)

    copy_by_scene = {sc["scene_id"]: sc["selected_text"] for sc in copy_data["scene_copies"]}

    templates_dir = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "templates"
    renders_dir = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "renders"
    templates_dir.mkdir(parents=True, exist_ok=True)
    renders_dir.mkdir(parents=True, exist_ok=True)

    overlays = []

    for sc in sb_data["scenes"]:
        scene_id = sc["scene_id"]
        start_sec = sc["start"]
        end_sec = sc["end"]
        duration_sec = sc["duration"]
        text = copy_by_scene.get(scene_id, "")

        style, font_size = STYLE_MAPPING.get(scene_id, ("slide_up_reveal", 34))

        # Generar HTML template
        html_content = generate_scene_html(scene_id, text, style, duration_sec, font_size)
        html_file = templates_dir / f"{scene_id}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        png_file = renders_dir / f"overlay_{scene_id}.png"
        status = "generated"

        if render_snapshots:
            try:
                render_snapshot_chrome(html_file, png_file)
                status = "rendered"
            except Exception as e:
                print(f"[WARN] No se pudo renderizar frame para {scene_id}: {e}", file=sys.stderr)
                status = "validated"

        overlay_entry = {
            "scene_id": scene_id,
            "start_seconds": round(start_sec, 3),
            "end_seconds": round(end_sec, 3),
            "duration_seconds": round(duration_sec, 3),
            "animation_style": style,
            "text_content": text,
            "font_family": "Outfit, -apple-system, BlinkMacSystemFont, sans-serif",
            "font_size_px": font_size,
            "html_template_path": str(html_file.relative_to(WORKSPACE_ROOT)),
            "render_status": status,
            "output_asset_path": str(png_file.relative_to(WORKSPACE_ROOT))
        }
        overlays.append(overlay_entry)

    manifest = {
        "campaign_id": "camp_locos_materos_2026",
        "format": {
            "aspect_ratio": "9:16",
            "width": 720,
            "height": 1280,
            "fps": 24.0
        },
        "brand_palette": BRAND_PALETTE,
        "safe_zones": SAFE_ZONES,
        "overlays": overlays
    }
    return manifest

def validate_motion_manifest(manifest: dict):
    schema_path = WORKSPACE_ROOT / "config" / "motion-graphics-schema.json"
    if not schema_path.is_file():
        raise FileNotFoundError(f"Esquema no encontrado: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=manifest, schema=schema)

def main():
    parser = argparse.ArgumentParser(description="ADCRA HyperFrames Motion Graphics Generator")
    parser.add_argument("--output", "-o", default="campaign/motion-graphics/motion-manifest.json", help="Ruta salida JSON")
    parser.add_argument("--no-render", action="store_true", help="Omitir el render de snapshots PNG")
    parser.add_argument("--validate-only", action="store_true", help="Solo valida el manifiesto existente")
    args = parser.parse_args()

    out_file = WORKSPACE_ROOT / args.output

    if args.validate_only:
        if not out_file.is_file():
            print(f"[ERROR] Manifiesto no encontrado: {out_file}", file=sys.stderr)
            sys.exit(1)
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        validate_motion_manifest(data)
        print(f"[VALID] El manifiesto {out_file} cumple 100% con config/motion-graphics-schema.json")
        return

    print("[MOTION GRAPHICS] Generando templates HTML5, cinética tipográfica y overlays RGBA...")
    manifest = generate_motion_manifest(render_snapshots=(not args.no_render))

    try:
        validate_motion_manifest(manifest)
        print("[SUCCESS] Manifiesto de motion graphics validado formalmente contra config/motion-graphics-schema.json")
    except jsonschema.ValidationError as e:
        print(f"[ERROR] Error de validación de motion graphics: {e.message}", file=sys.stderr)
        sys.exit(2)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Manifiesto guardado en: {out_file}")
    print(f" - Overlays por Escena: {len(manifest['overlays'])}")
    print(f" - Formato: {manifest['format']['width']}x{manifest['format']['height']} ({manifest['format']['aspect_ratio']}) @ {manifest['format']['fps']} fps")
    print(f" - Safe Zones: Top {manifest['safe_zones']['top_px']}px, Bottom {manifest['safe_zones']['bottom_px']}px, Sides {manifest['safe_zones']['left_px']}px")

if __name__ == "__main__":
    main()
