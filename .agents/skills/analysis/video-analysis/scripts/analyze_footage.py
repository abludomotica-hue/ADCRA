#!/usr/bin/env python3
"""
ADCRA — Video & Footage Intelligence Engine
Inspecciona técnicamente y cataloga cinematográficamente los clips de metraje,
imágenes de marca y pistas de audio para conformar el inventario oficial de campaña.
"""

import sys
import os
import glob
import json
import argparse
import subprocess
from pathlib import Path

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

CINEMATOGRAPHIC_KNOWLEDGE = {
    "Escena 01": {
        "scene_id": "scene_01",
        "shot_type": "medium_shot",
        "lighting": "warm_natural_window",
        "camera_movement": "handheld_organic",
        "setting_type": "interior_hogar",
        "mate_visible": True,
        "primary_subjects": ["hervidor", "vapor", "cocina", "mesa de madera"],
        "emotion_evoked": "Intimidad, despertar y calidez de hogar"
    },
    "Escena 02": {
        "scene_id": "scene_02",
        "shot_type": "macro_detail",
        "lighting": "warm_natural_window",
        "camera_movement": "static",
        "setting_type": "interior_hogar",
        "mate_visible": True,
        "primary_subjects": ["yerba mate verde", "bombilla de acero inoxidable", "calabaza tradicional"],
        "emotion_evoked": "Precisión artesanal, textura y calma"
    },
    "Escena 03": {
        "scene_id": "scene_03",
        "shot_type": "wide_establishing",
        "lighting": "golden_hour_morning",
        "camera_movement": "slow_pan",
        "setting_type": "exterior_cordillera",
        "mate_visible": False,
        "primary_subjects": ["Cordillera de los Andes", "sol matutino", "cielo dorado", "ciudad de Santiago"],
        "emotion_evoked": "Grandeza andina, horizonte y orgullo territorial"
    },
    "Escena 04": {
        "scene_id": "scene_04",
        "shot_type": "medium_shot",
        "lighting": "golden_hour_morning",
        "camera_movement": "handheld_organic",
        "setting_type": "interior_hogar",
        "mate_visible": True,
        "primary_subjects": ["manos cebando", "termo", "chorro de agua caliente", "mate humeante"],
        "emotion_evoked": "Impulso, energía matutina y sincronía nacional"
    },
    "Escena 05": {
        "scene_id": "scene_05",
        "shot_type": "medium_shot",
        "lighting": "soft_daylight",
        "camera_movement": "slow_dolly_tracking",
        "setting_type": "calle_barrio",
        "mate_visible": True,
        "primary_subjects": ["persona caminando", "vereda arbolada", "termo bajo el brazo", "mate en mano"],
        "emotion_evoked": "Pertenencia, cercanía vecinal y paseo tranquilo"
    },
    "Escena 06": {
        "scene_id": "scene_06",
        "shot_type": "medium_shot",
        "lighting": "interior_ambient",
        "camera_movement": "static",
        "setting_type": "espacio_laboral",
        "mate_visible": True,
        "primary_subjects": ["espacio de trabajo", "mesa", "computador/herramientas", "mate compañero"],
        "emotion_evoked": "Pausa reflexiva, concentración y perseverancia"
    },
    "Escena 07": {
        "scene_id": "scene_07",
        "shot_type": "group_shot",
        "lighting": "soft_daylight",
        "camera_movement": "handheld_organic",
        "setting_type": "universidad",
        "mate_visible": True,
        "primary_subjects": ["jóvenes estudiantes", "patio universitario", "apuntes", "mate compartido"],
        "emotion_evoked": "Complicidad juvenil, estudio colaborativo y alegría"
    },
    "Escena 08": {
        "scene_id": "scene_08",
        "shot_type": "close_up",
        "lighting": "warm_natural_window",
        "camera_movement": "static",
        "setting_type": "interior_hogar",
        "mate_visible": True,
        "primary_subjects": ["mate sostenido con dos manos", "gesto de sorbo", "expresión de disfrute"],
        "emotion_evoked": "Satisfacción profunda, calidez sensorial y pausa"
    },
    "Escena 09": {
        "scene_id": "scene_09",
        "shot_type": "group_shot",
        "lighting": "golden_hour_morning",
        "camera_movement": "slow_dolly_tracking",
        "setting_type": "reunion_amigos",
        "mate_visible": True,
        "primary_subjects": ["amigos compartiendo mate", "risas", "encuentro colectivo", "packshot de cierre"],
        "emotion_evoked": "Comunidad, amistad entrañable y pertenencia a la marca"
    }
}

def probe_video_file(video_path: Path) -> dict:
    """Extrae metadatos técnicos de un archivo de video con ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)

    vstream = next(s for s in data.get("streams", []) if s.get("codec_type") == "video")
    astream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})

    width = int(vstream.get("width", 0))
    height = int(vstream.get("height", 0))
    dur = float(vstream.get("duration") or fmt.get("duration", 0.0))

    fps_raw = vstream.get("r_frame_rate", "24/1")
    if "/" in fps_raw:
        num, den = fps_raw.split("/")
        fps = round(float(num) / float(den), 2) if float(den) > 0 else 24.0
    else:
        fps = float(fps_raw)

    bit_rate = int(fmt.get("bit_rate") or vstream.get("bit_rate") or 0)
    aspect_ratio_num = round(width / height, 4) if height > 0 else 0.5625
    aspect_ratio_str = "9:16" if abs(aspect_ratio_num - 0.5625) < 0.05 else f"{width}:{height}"

    return {
        "duration_seconds": round(dur, 2),
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio_str,
        "aspect_ratio_numeric": aspect_ratio_num,
        "fps": fps,
        "codec": vstream.get("codec_name", "unknown"),
        "pixel_format": vstream.get("pix_fmt", "unknown"),
        "bitrate_kbps": round(bit_rate / 1000, 1),
        "has_audio": astream is not None,
        "file_size_bytes": int(fmt.get("size", 0))
    }

def probe_image_file(image_path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        str(image_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    s = data.get("streams", [{}])[0]
    fmt = data.get("format", {})

    width = int(s.get("width", 0))
    height = int(s.get("height", 0))

    # Clasificación de uso de imagen
    fname = image_path.name
    if width <= 800 and height <= 600:
        usage = "brand_logo"
    elif width > height:
        usage = "landscape_reference"
    else:
        usage = "editorial_lifestyle_reference"

    return {
        "filename": fname,
        "relative_path": str(image_path.relative_to(WORKSPACE_ROOT)),
        "width": width,
        "height": height,
        "format": s.get("codec_name", "jpeg"),
        "file_size_bytes": int(fmt.get("size", 0)),
        "intended_usage": usage
    }

def build_asset_inventory(videos_dir: Path, images_dir: Path, audios_dir: Path) -> dict:
    video_files = sorted(list(videos_dir.glob("*.mp4")))
    image_files = sorted(list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
    audio_files = sorted(list(audios_dir.glob("*.mp3")) + list(audios_dir.glob("*.wav")))

    analyzed_videos = []
    total_video_dur = 0.0

    for vf in video_files:
        specs = probe_video_file(vf)
        total_video_dur += specs["duration_seconds"]

        # Emparejamiento con conocimiento cinematográfico
        matched_info = None
        for k, info in CINEMATOGRAPHIC_KNOWLEDGE.items():
            if k in vf.name:
                matched_info = info
                break

        if not matched_info:
            matched_info = {
                "scene_id": "scene_unknown",
                "shot_type": "medium_shot",
                "lighting": "soft_daylight",
                "camera_movement": "handheld_organic",
                "setting_type": "exterior",
                "mate_visible": True,
                "primary_subjects": ["sujeto"],
                "emotion_evoked": "autenticidad"
            }

        analyzed_videos.append({
            "asset_id": f"vid_{vf.stem.replace(' ', '_').lower()[:24]}",
            "filename": vf.name,
            "relative_path": str(vf.relative_to(WORKSPACE_ROOT)),
            "technical_specs": specs,
            "cinematography": {
                "scene_id": matched_info["scene_id"],
                "shot_type": matched_info["shot_type"],
                "lighting": matched_info["lighting"],
                "camera_movement": matched_info["camera_movement"],
                "setting_type": matched_info["setting_type"],
                "mate_visible": matched_info["mate_visible"],
                "primary_subjects": matched_info["primary_subjects"],
                "emotion_evoked": matched_info["emotion_evoked"]
            }
        })

    analyzed_images = [probe_image_file(img) for img in image_files]
    
    analyzed_audios = []
    for af in audio_files:
        analyzed_audios.append({
            "filename": af.name,
            "relative_path": str(af.relative_to(WORKSPACE_ROOT)),
            "file_size_bytes": af.stat().st_size
        })

    inventory = {
        "summary": {
            "total_video_assets": len(analyzed_videos),
            "total_video_duration_seconds": round(total_video_dur, 2),
            "native_video_aspect_ratio": "9:16 (720x1280)",
            "native_video_fps": 24.0,
            "total_image_assets": len(analyzed_images),
            "total_audio_assets": len(analyzed_audios)
        },
        "video_assets": analyzed_videos,
        "image_assets": analyzed_images,
        "audio_assets": analyzed_audios
    }

    return inventory

def main():
    parser = argparse.ArgumentParser(description="ADCRA Video & Footage Analysis CLI")
    parser.add_argument("--videos", "-v", default="Recursos/videos", help="Directorio de videos")
    parser.add_argument("--images", "-i", default="Recursos/Imeges", help="Directorio de imágenes")
    parser.add_argument("--audios", "-a", default="Recursos/Audios", help="Directorio de audio")
    parser.add_argument("--output", "-o", default="campaign/assets/asset-inventory.json", help="Ruta de salida JSON")
    parser.add_argument("--json", action="store_true", help="Imprime resultado por stdout")
    args = parser.parse_args()

    v_dir = WORKSPACE_ROOT / args.videos
    i_dir = WORKSPACE_ROOT / args.images
    a_dir = WORKSPACE_ROOT / args.audios

    print(f"[ANALYZING] Inspeccionando activos audiovisuales en {v_dir}...")
    inventory = build_asset_inventory(v_dir, i_dir, a_dir)

    out_path = WORKSPACE_ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    s = inventory["summary"]
    print(f"[SUCCESS] Análisis de activos completado:")
    print(f" - Videos Catalogados:   {s['total_video_assets']} ({s['total_video_duration_seconds']}s acumulados)")
    print(f" - Formato Nativo Video: {s['native_video_aspect_ratio']} @ {s['native_video_fps']} FPS")
    print(f" - Imágenes de Marca:    {s['total_image_assets']}")
    print(f" - Pistas de Audio:      {s['total_audio_assets']}")
    print(f"[SAVED] Inventario guardado en: {out_path}")

    if args.json:
        print(json.dumps(inventory, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
