#!/usr/bin/env python3
"""
ADCRA — Social Media Formatter Engine
Genera especificaciones multi-ratio, cálculo de Safe Zones móviles (TikTok, Reels, Shorts, Feed 1:1, 16:9),
guías visuales PNG semitransparentes para NLEs y comandos FFmpeg de adaptación.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import jsonschema
from PIL import Image, ImageDraw, ImageFont

def get_workspace_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "config" / "social-formatter-schema.json").exists():
            return parent
    return Path("/data/usuario/Documentos/davinci resolve")

WORKSPACE_ROOT = get_workspace_root()

def generate_safe_zone_guides(platforms: list[dict], output_dir: Path) -> list[Path]:
    """Genera máscaras PNG semitransparentes con visualización de Safe Zones y zonas de oclusión UI."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_paths = []

    for platform in platforms:
        w = platform["target_resolution"]["width"]
        h = platform["target_resolution"]["height"]
        safe = platform["safe_zone"]

        # Crear imagen RGBA transparente
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 1. Dibujar zonas de oclusión UI en rojo semitransparente
        for zone in platform.get("ui_occlusion_zones", []):
            bb = zone["bounding_box"]
            x0 = bb["x"]
            y0 = bb["y"]
            x1 = x0 + bb["width"]
            y1 = y0 + bb["height"]

            # Relleno de oclusión UI
            draw.rectangle([x0, y0, x1, y1], fill=(220, 40, 40, 75), outline=(220, 20, 20, 160), width=2)
            # Etiqueta de la zona
            label_text = f"{zone['zone_name']}"
            draw.text((x0 + 10, y0 + 10), label_text, fill=(255, 255, 255, 220))

        # 2. Dibujar rectángulo de Safe Zone en verde institucional
        safe_x0 = safe["left_px"]
        safe_y0 = safe["top_px"]
        safe_x1 = w - safe["right_px"]
        safe_y1 = h - safe["bottom_px"]

        # Borde Safe Zone
        draw.rectangle([safe_x0, safe_y0, safe_x1, safe_y1], outline=(13, 92, 58, 240), width=3)
        # Línea de guía interna punteada / suave
        draw.rectangle([safe_x0 + 2, safe_y0 + 2, safe_x1 - 2, safe_y1 - 2], outline=(212, 175, 55, 200), width=1)

        # Rótulo de Safe Zone
        safe_label = f"SAFE ZONE — {platform['name']} ({safe_x1 - safe_x0}x{safe_y1 - safe_y0})"
        draw.text((safe_x0 + 15, safe_y0 + 15), safe_label, fill=(212, 175, 55, 255))

        out_file = output_dir / f"{platform['platform_id']}_safe_zone.png"
        img.save(out_file, "PNG")
        generated_paths.append(out_file)

    return generated_paths

def build_social_manifest(generate_guides: bool = True) -> tuple[dict, list[Path]]:
    """Construye el manifiesto formal de adaptación multiplataforma y safe zones."""
    guides_dir = WORKSPACE_ROOT / "campaign" / "deliverables" / "guides"

    platforms = [
        {
            "platform_id": "tiktok_9_16",
            "name": "TikTok Video",
            "aspect_ratio": "9:16",
            "target_resolution": {"width": 720, "height": 1280},
            "safe_zone": {
                "top_px": 110,
                "bottom_px": 220,
                "left_px": 40,
                "right_px": 90
            },
            "ui_occlusion_zones": [
                {
                    "zone_name": "Header & Search",
                    "description": "Buscador superior y pestañas Siguiendo / Para Ti",
                    "bounding_box": {"x": 0, "y": 0, "width": 720, "height": 110}
                },
                {
                    "zone_name": "Action Rail Lateral",
                    "description": "Botones de Perfil, Like, Comentarios, Favoritos, Compartir y Disco Musical",
                    "bounding_box": {"x": 630, "y": 500, "width": 90, "height": 560}
                },
                {
                    "zone_name": "Caption & Audio Info",
                    "description": "Nombre de usuario (@locosmateros), copy publicitario y título de la canción",
                    "bounding_box": {"x": 0, "y": 1060, "width": 630, "height": 220}
                }
            ]
        },
        {
            "platform_id": "instagram_reels_9_16",
            "name": "Instagram Reels",
            "aspect_ratio": "9:16",
            "target_resolution": {"width": 720, "height": 1280},
            "safe_zone": {
                "top_px": 100,
                "bottom_px": 200,
                "left_px": 40,
                "right_px": 85
            },
            "ui_occlusion_zones": [
                {
                    "zone_name": "Header Reels & Camera",
                    "description": "Título de Reels, ícono de cámara y menú superior",
                    "bounding_box": {"x": 0, "y": 0, "width": 720, "height": 100}
                },
                {
                    "zone_name": "Action Icons Rail",
                    "description": "Me gusta, comentarios, enviar por DM, tres puntos y avatar de audio",
                    "bounding_box": {"x": 635, "y": 550, "width": 85, "height": 530}
                },
                {
                    "zone_name": "Account & Audio Footer",
                    "description": "Usuario @locosmateros, botón Seguir, pie de foto y nombre de audio",
                    "bounding_box": {"x": 0, "y": 1080, "width": 635, "height": 200}
                }
            ]
        },
        {
            "platform_id": "youtube_shorts_9_16",
            "name": "YouTube Shorts",
            "aspect_ratio": "9:16",
            "target_resolution": {"width": 720, "height": 1280},
            "safe_zone": {
                "top_px": 90,
                "bottom_px": 180,
                "left_px": 40,
                "right_px": 80
            },
            "ui_occlusion_zones": [
                {
                    "zone_name": "Shorts Header",
                    "description": "Buscador, cámara y opciones",
                    "bounding_box": {"x": 0, "y": 0, "width": 720, "height": 90}
                },
                {
                    "zone_name": "Shorts Action Column",
                    "description": "Pulgar arriba, pulgar abajo, comentarios, compartir y remix",
                    "bounding_box": {"x": 640, "y": 600, "width": 80, "height": 500}
                },
                {
                    "zone_name": "Channel & Subscribe Bar",
                    "description": "Nombre de canal, botón suscribirse y título del video",
                    "bounding_box": {"x": 0, "y": 1100, "width": 640, "height": 180}
                }
            ]
        },
        {
            "platform_id": "meta_feed_1_1",
            "name": "Meta Feed Square (Instagram & Facebook)",
            "aspect_ratio": "1:1",
            "target_resolution": {"width": 1080, "height": 1080},
            "safe_zone": {
                "top_px": 50,
                "bottom_px": 50,
                "left_px": 50,
                "right_px": 50
            },
            "ui_occlusion_zones": [
                {
                    "zone_name": "Header Feed Post",
                    "description": "Barra de cuenta y ubicación del post en feed",
                    "bounding_box": {"x": 0, "y": 0, "width": 1080, "height": 50}
                },
                {
                    "zone_name": "Bottom Interaction Bar",
                    "description": "Barra inferior de acciones y texto colapsable",
                    "bounding_box": {"x": 0, "y": 1030, "width": 1080, "height": 50}
                }
            ]
        },
        {
            "platform_id": "youtube_widescreen_16_9",
            "name": "YouTube Widescreen & TV",
            "aspect_ratio": "16:9",
            "target_resolution": {"width": 1920, "height": 1080},
            "safe_zone": {
                "top_px": 80,
                "bottom_px": 80,
                "left_px": 100,
                "right_px": 100
            },
            "ui_occlusion_zones": [
                {
                    "zone_name": "Video Player Controls & Scrub Bar",
                    "description": "Línea de tiempo de reproducción, volumen, subtítulos y ajustes",
                    "bounding_box": {"x": 0, "y": 1000, "width": 1920, "height": 80}
                }
            ]
        }
    ]

    guide_paths = []
    if generate_guides:
        guide_paths = generate_safe_zone_guides(platforms, guides_dir)

    adaptation_strategies = {
        "vertical_9_16": {
            "method": "direct_passthrough",
            "description": "Passthrough 1:1 del master vertical 720x1280 @ 24fps respetando safe zones de UI"
        },
        "square_1_1": {
            "method": "pillarbox_brand_fill",
            "brand_fill_color": "#0D5C3A",
            "description": "Escalado vertical a 1080px de alto (608x1080) con franjas laterales institucionales #0D5C3A"
        },
        "widescreen_16_9": {
            "method": "blurred_background_pillarbox",
            "blur_sigma": 25.0,
            "description": "Escalado central con duplicado de fondo escalado a 1920x3413, recortado y desenfocado con boxblur"
        }
    }

    deliverables = [
        {
            "deliverable_id": "deliv_tiktok_9_16",
            "platform_id": "tiktok_9_16",
            "aspect_ratio": "9:16",
            "resolution": "720x1280",
            "guide_overlay_path": "campaign/deliverables/guides/tiktok_9_16_safe_zone.png",
            "ffmpeg_command": "ffmpeg -y -i input_master.mp4 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k campaign/deliverables/locos_materos_tiktok_9_16.mp4"
        },
        {
            "deliverable_id": "deliv_reels_9_16",
            "platform_id": "instagram_reels_9_16",
            "aspect_ratio": "9:16",
            "resolution": "720x1280",
            "guide_overlay_path": "campaign/deliverables/guides/instagram_reels_9_16_safe_zone.png",
            "ffmpeg_command": "ffmpeg -y -i input_master.mp4 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k campaign/deliverables/locos_materos_reels_9_16.mp4"
        },
        {
            "deliverable_id": "deliv_shorts_9_16",
            "platform_id": "youtube_shorts_9_16",
            "aspect_ratio": "9:16",
            "resolution": "720x1280",
            "guide_overlay_path": "campaign/deliverables/guides/youtube_shorts_9_16_safe_zone.png",
            "ffmpeg_command": "ffmpeg -y -i input_master.mp4 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k campaign/deliverables/locos_materos_shorts_9_16.mp4"
        },
        {
            "deliverable_id": "deliv_feed_1_1",
            "platform_id": "meta_feed_1_1",
            "aspect_ratio": "1:1",
            "resolution": "1080x1080",
            "guide_overlay_path": "campaign/deliverables/guides/meta_feed_1_1_safe_zone.png",
            "ffmpeg_command": "ffmpeg -y -i input_master.mp4 -vf 'scale=-1:1080,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:color=0x0D5C3A' -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k campaign/deliverables/locos_materos_feed_1_1.mp4"
        },
        {
            "deliverable_id": "deliv_widescreen_16_9",
            "platform_id": "youtube_widescreen_16_9",
            "aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "guide_overlay_path": "campaign/deliverables/guides/youtube_widescreen_16_9_safe_zone.png",
            "ffmpeg_command": "ffmpeg -y -i input_master.mp4 -filter_complex '[0:v]scale=1920:3413,crop=1920:1080,boxblur=25:25[bg];[0:v]scale=-1:1080[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[out]' -map '[out]' -map 0:a -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k campaign/deliverables/locos_materos_widescreen_16_9.mp4"
        }
    ]

    manifest = {
        "campaign_id": "camp_locos_materos_2026",
        "master_format": {
            "aspect_ratio": "9:16",
            "width": 720,
            "height": 1280,
            "fps": 24.0
        },
        "platforms": platforms,
        "adaptation_strategies": adaptation_strategies,
        "deliverables": deliverables
    }

    return manifest, guide_paths

def validate_social_manifest(manifest: dict):
    """Valida el manifiesto contra el contrato formal JSON Schema."""
    schema_path = WORKSPACE_ROOT / "config" / "social-formatter-schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=manifest, schema=schema)
    print(f"[SUCCESS] Manifiesto validado formalmente contra config/social-formatter-schema.json")

def main():
    parser = argparse.ArgumentParser(description="Social Media Formatter & Safe Zones Engine")
    parser.add_argument("--validate-only", action="store_true", help="Solo valida el archivo manifest existente")
    args = parser.parse_args()

    manifest_path = WORKSPACE_ROOT / "campaign" / "deliverables" / "social-format-manifest.json"

    if args.validate_only:
        if not manifest_path.is_file():
            print(f"[ERROR] No existe {manifest_path}", file=sys.stderr)
            sys.exit(1)
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        validate_social_manifest(data)
        print(f"[VALID] El manifiesto {manifest_path} cumple 100% con config/social-formatter-schema.json")
        sys.exit(0)

    print("[SOCIAL FORMATTER] Procesando especificaciones multiplataforma, safe zones y guías...")
    manifest, guides = build_social_manifest(generate_guides=True)
    validate_social_manifest(manifest)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Manifiesto guardado en: {manifest_path}")
    print(f" - Plataformas configuradas: {len(manifest['platforms'])}")
    print(f" - Entregables multi-ratio: {len(manifest['deliverables'])}")
    print(f" - Guías visuales PNG generadas: {len(guides)}")

if __name__ == "__main__":
    main()
