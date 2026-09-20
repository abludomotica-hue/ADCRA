#!/usr/bin/env python3
"""
ADCRA — Remotion Orchestrator & Programmatic Video Engine
Genera composiciones React parametrizables, matrices de variantes publicitarias (A/B testing, bumpers),
renderizado de fotogramas clave y validación formal de esquemas.
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

def get_logo_data_uri() -> str:
    logo_file = WORKSPACE_ROOT / "Recursos" / "Imeges" / "WhatsApp Image 2026-09-16 at 10.21.14 PM.jpeg"
    if logo_file.is_file():
        with open(logo_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"
    return ""

def generate_react_components(remotion_dir: Path):
    remotion_dir.mkdir(parents=True, exist_ok=True)

    index_jsx = """import { registerRoot } from 'remotion';
import { Root } from './Root';

registerRoot(Root);
"""
    (remotion_dir / "index.jsx").write_text(index_jsx, encoding="utf-8")

    root_jsx = """import React from 'react';
import { Composition } from 'remotion';
import { Main } from './Main';
import defaultProps from './props.json';

export const Root = () => {
  return (
    <Composition
      id="LocosMaterosCommercial"
      component={Main}
      durationInFrames={defaultProps.format.duration_in_frames || 700}
      fps={defaultProps.format.fps || 24}
      width={defaultProps.format.width || 720}
      height={defaultProps.format.height || 1280}
      defaultProps={defaultProps}
    />
  );
};
"""
    (remotion_dir / "Root.jsx").write_text(root_jsx, encoding="utf-8")

    main_jsx = """import React from 'react';
import { Sequence, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

const SceneOverlay = ({ text, style, brand, isLastScene, logoUri }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const translateY = interpolate(frame, [0, 12], [25, 0], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: { damping: 12, mass: 0.5 } });

  if (isLastScene) {
    return (
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 720,
        height: 1280,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'radial-gradient(circle at center, rgba(13, 92, 58, 0.6) 0%, rgba(0, 0, 0, 0.88) 75%)',
        opacity,
        fontFamily: 'sans-serif',
        padding: 40,
        boxSizing: 'border-box'
      }}>
        {logoUri && (
          <div style={{
            width: 210,
            height: 210,
            borderRadius: '50%',
            overflow: 'hidden',
            border: `4px solid ${brand.accent_color}`,
            boxShadow: `0 0 35px ${brand.accent_color}88`,
            marginBottom: 35,
            backgroundColor: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `scale(${scale})`
          }}>
            <img src={logoUri} alt="Logo" style={{ width: '85%', height: '85%', objectFit: 'contain' }} />
          </div>
        )}
        <h1 style={{
          color: '#FFFFFF',
          fontSize: 38,
          fontWeight: 800,
          textAlign: 'center',
          lineHeight: 1.25,
          marginBottom: 25,
          textShadow: '0 4px 18px rgba(0,0,0,0.9)'
        }}>
          ¿Dónde estás tú? <span style={{ color: brand.accent_color }}>Está tu mate.</span>
        </h1>
        <div style={{
          backgroundColor: brand.accent_color,
          color: '#1A1A1A',
          fontSize: 22,
          fontWeight: 800,
          padding: '12px 34px',
          borderRadius: 30,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          boxShadow: '0 6px 20px rgba(0,0,0,0.4)'
        }}>
          {brand.cta_url}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      position: 'absolute',
      bottom: 230,
      left: 40,
      right: 40,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      pointerEvents: 'none'
    }}>
      <div style={{
        background: 'rgba(26, 26, 26, 0.85)',
        border: `2px solid ${brand.accent_color}`,
        borderRadius: 24,
        padding: '16px 28px',
        maxWidth: 620,
        textAlign: 'center',
        boxShadow: '0 8px 30px rgba(0,0,0,0.6)',
        opacity,
        transform: `translateY(${translateY}px)`
      }}>
        <span style={{
          color: '#FFFFFF',
          fontSize: 32,
          fontWeight: 600,
          fontFamily: 'sans-serif',
          lineHeight: 1.3,
          textShadow: '0 2px 8px rgba(0,0,0,0.8)'
        }}>
          {text}
        </span>
      </div>
    </div>
  );
};

export const Main = (props) => {
  const { scenes = [], brand = {}, logoUri } = props;

  return (
    <div style={{
      position: 'relative',
      width: 720,
      height: 1280,
      backgroundColor: '#000000',
      overflow: 'hidden'
    }}>
      {scenes.map((sc, index) => {
        const isLast = index === scenes.length - 1;
        return (
          <Sequence
            key={sc.scene_id}
            from={sc.start_frame}
            durationInFrames={sc.duration_frames}
          >
            {/* Background color placeholder simulating video frame */}
            <div style={{
              width: 720,
              height: 1280,
              backgroundColor: index % 2 === 0 ? '#111815' : '#0B1310',
              position: 'relative'
            }}>
              <SceneOverlay
                text={sc.text_overlay}
                style={sc.style}
                brand={brand}
                isLastScene={isLast}
                logoUri={logoUri}
              />
            </div>
          </Sequence>
        );
      })}
    </div>
  );
};
"""
    (remotion_dir / "Main.jsx").write_text(main_jsx, encoding="utf-8")

def build_composition_data() -> tuple[dict, list]:
    sb_path = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
    copy_path = WORKSPACE_ROOT / "campaign" / "creative" / "creative-copy.json"
    audio_path = WORKSPACE_ROOT / "campaign" / "audio" / "audio-analysis.json"

    with open(sb_path, "r", encoding="utf-8") as f:
        sb_data = json.load(f)

    with open(copy_path, "r", encoding="utf-8") as f:
        copy_data = json.load(f)

    with open(audio_path, "r", encoding="utf-8") as f:
        audio_data = json.load(f)

    copy_by_scene = {sc["scene_id"]: sc for sc in copy_data["scene_copies"]}

    fps = 24.0
    total_frames = int(round(sb_data["total_duration_seconds"] * fps))

    scenes = []
    current_frame = 0
    for i, sc in enumerate(sb_data["scenes"]):
        sc_id = sc["scene_id"]
        dur_frames = int(round(sc["duration"] * fps))
        # Ajustar último frame para calzar total
        if i == len(sb_data["scenes"]) - 1:
            dur_frames = total_frames - current_frame

        c_info = copy_by_scene.get(sc_id, {})
        text = c_info.get("selected_text", "")

        scenes.append({
            "scene_id": sc_id,
            "start_frame": current_frame,
            "duration_frames": dur_frames,
            "video_src": sc.get("asset_reference", f"Recursos/videos/{sc_id}.mp4"),
            "text_overlay": text,
            "style": sc.get("visual_movement", "slide_up_reveal")
        })
        current_frame += dur_frames

    logo_uri = get_logo_data_uri()

    brand_meta = {
        "name": "Locos Materos",
        "claim": "¿Dónde estás tú? Está tu mate.",
        "primary_color": "#0D5C3A",
        "accent_color": "#D4AF37",
        "cta_url": "www.locosmateros.cl",
        "logo_path": "Recursos/Imeges/WhatsApp Image 2026-09-16 at 10.21.14 PM.jpeg"
    }

    audio_track = {
        "src": "Recursos/Audios/Entre_mates_y_sol.mp3",
        "bpm": audio_data.get("rhythm", {}).get("tempo_bpm", 107.7),
        "duration_seconds": round(sb_data["total_duration_seconds"], 3)
    }

    variants = [
        {
            "variant_id": "master_30s_emocional",
            "name": "Master 30s Emocional",
            "target_audience": "Público general adulto (20-50 años), amantes de las pausas cotidianas",
            "props_override": {
                "tone": "emocional",
                "emphasis": "calidez y ritual"
            },
            "output_file": "campaign/remotion/renders/commercial_30s_emocional.mp4"
        },
        {
            "variant_id": "variant_publicitaria",
            "name": "Variante Comercial de Conversión",
            "target_audience": "Compradores en línea y prospectos de e-commerce mate",
            "props_override": {
                "tone": "publicitaria",
                "cta_url": "www.locosmateros.cl/ofertas",
                "scene_01_text": "Empezá tus mañanas con Locos Materos."
            },
            "output_file": "campaign/remotion/renders/commercial_30s_publicitaria.mp4"
        },
        {
            "variant_id": "variant_conversacional",
            "name": "Variante Cercana / Redes Sociales",
            "target_audience": "Jóvenes y usuarios activos en TikTok / Reels",
            "props_override": {
                "tone": "conversacional",
                "scene_01_text": "Suena el agua y parte el día."
            },
            "output_file": "campaign/remotion/renders/commercial_30s_conversacional.mp4"
        },
        {
            "variant_id": "bumper_15s",
            "name": "Bumper 15s Pre-roll",
            "target_audience": "Audiencias móviles con alta rotación en YouTube pre-roll",
            "props_override": {
                "duration_in_frames": 360,
                "scenes_subset": ["scene_01", "scene_05", "scene_08", "scene_09"]
            },
            "output_file": "campaign/remotion/renders/bumper_15s.mp4"
        }
    ]

    manifest = {
        "campaign_id": "camp_locos_materos_2026",
        "composition_id": "LocosMaterosCommercial",
        "format": {
            "width": 720,
            "height": 1280,
            "fps": fps,
            "duration_in_frames": total_frames,
            "duration_seconds": round(total_frames / fps, 3)
        },
        "brand_meta": brand_meta,
        "audio_track": audio_track,
        "scenes": scenes,
        "variants": variants
    }

    props_payload = {
        "format": manifest["format"],
        "brand": brand_meta,
        "audio": audio_track,
        "scenes": scenes,
        "logoUri": logo_uri
    }

    return manifest, props_payload

def validate_remotion_manifest(manifest: dict):
    schema_path = WORKSPACE_ROOT / "config" / "remotion-composition-schema.json"
    if not schema_path.is_file():
        raise FileNotFoundError(f"Esquema no encontrado: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=manifest, schema=schema)

def render_still_frame(remotion_dir: Path, frame: int, output_png: Path):
    output_png.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["NODE_PATH"] = "/data/nodejs/lib/node_modules:" + env.get("NODE_PATH", "")

    cmd = [
        "remotion",
        "still",
        str(remotion_dir / "index.jsx"),
        "LocosMaterosCommercial",
        str(output_png),
        f"--frame={frame}",
        "--props", str(remotion_dir / "props.json")
    ]
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
    if p.returncode != 0:
        raise RuntimeError(f"Error renderizando still con Remotion: {p.stderr}")

def main():
    parser = argparse.ArgumentParser(description="ADCRA Remotion Orchestrator CLI")
    parser.add_argument("--validate-only", action="store_true", help="Solo valida manifiesto existente")
    parser.add_argument("--list-variants", action="store_true", help="Lista las variantes disponibles")
    parser.add_argument("--render-still", type=int, default=None, help="Número de frame para renderizar captura still")
    parser.add_argument("--output", "-o", default="campaign/remotion/composition-manifest.json", help="Ruta de salida JSON")
    args = parser.parse_args()

    out_file = WORKSPACE_ROOT / args.output
    remotion_dir = WORKSPACE_ROOT / "campaign" / "remotion"

    if args.validate_only:
        if not out_file.is_file():
            print(f"[ERROR] Manifiesto no encontrado: {out_file}", file=sys.stderr)
            sys.exit(1)
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        validate_remotion_manifest(data)
        print(f"[VALID] El manifiesto {out_file} cumple 100% con config/remotion-composition-schema.json")
        return

    print("[REMOTION] Generando composición React programática y matriz de variantes...")
    manifest, props_payload = build_composition_data()

    # Validar formalmente
    try:
        validate_remotion_manifest(manifest)
        print("[SUCCESS] Manifiesto de composición validado contra config/remotion-composition-schema.json")
    except jsonschema.ValidationError as e:
        print(f"[ERROR] Error validando manifiesto de Remotion: {e.message}", file=sys.stderr)
        sys.exit(2)

    # Generar componentes React
    generate_react_components(remotion_dir)

    # Guardar props.json
    props_file = remotion_dir / "props.json"
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props_payload, f, indent=2, ensure_ascii=False)

    # Guardar variants.json
    variants_file = remotion_dir / "variants.json"
    with open(variants_file, "w", encoding="utf-8") as f:
        json.dump(manifest["variants"], f, indent=2, ensure_ascii=False)

    # Guardar composition-manifest.json
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Composición Remotion guardada en: {out_file}")
    print(f" - ID de Composición: {manifest['composition_id']}")
    print(f" - Duración: {manifest['format']['duration_in_frames']} frames ({manifest['format']['duration_seconds']}s @ {manifest['format']['fps']} fps)")
    print(f" - Secuencias: {len(manifest['scenes'])} escenas")
    print(f" - Variantes Paramétricas: {len(manifest['variants'])}")

    if args.list_variants:
        print("\n--- MATRIZ DE VARIANTES PARAMÉTRICAS ---")
        for v in manifest["variants"]:
            print(f" • [{v['variant_id']}] {v['name']} -> {v['target_audience']}")

    if args.render_still is not None:
        still_out = remotion_dir / "renders" / f"still_frame_{args.render_still}.png"
        print(f"[RENDER] Renderizando frame still {args.render_still} en {still_out}...")
        render_still_frame(remotion_dir, args.render_still, still_out)
        print(f"[SUCCESS] Still frame guardado exitosamente en: {still_out}")

if __name__ == "__main__":
    main()
