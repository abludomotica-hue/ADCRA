#!/usr/bin/env python3
"""
ADCRA — Color Grading Assistant
Genera tablas de color 3D LUTs (.cube) calibradas para la identidad visual de Locos Materos
y el manifiesto de etalonaje plano a plano validado contra config/color-grading-schema.json.
"""

import sys
import os
import json
import math
import argparse
from pathlib import Path
import jsonschema

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

def s_curve(x: float, contrast: float = 1.1) -> float:
    # Curva tonal suave en S con anclaje en 0 y 1
    x = max(0.0, min(1.0, x))
    return x ** contrast / (x ** contrast + (1.0 - x) ** contrast + 1e-7)

def generate_cube_lut(lut_path: Path, title: str, size: int = 33, look: str = "warm_cinematic"):
    lut_path.parent.mkdir(parents=True, exist_ok=True)

    with open(lut_path, "w", encoding="utf-8") as f:
        f.write(f'TITLE "{title}"\n')
        f.write(f"LUT_3D_SIZE {size}\n")
        f.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        f.write("DOMAIN_MAX 1.0 1.0 1.0\n\n")

        for k in range(size):
            b_in = k / (size - 1)
            for j in range(size):
                g_in = j / (size - 1)
                for i in range(size):
                    r_in = i / (size - 1)

                    if look == "warm_cinematic":
                        # Calidez dorada en altas luces, verde mate orgánico, negros profundos
                        # S-curve suave
                        r = s_curve(r_in, 1.08)
                        g = s_curve(g_in, 1.06)
                        b = s_curve(b_in, 1.04)

                        # Warm golden highlight boost
                        r = r * 1.04 + 0.01 * (r ** 2)
                        g = g * 1.02 + 0.008 * (g ** 2)
                        b = b * 0.95 - 0.005 * (b ** 2)

                        # Deepen organic greens
                        if g_in > r_in and g_in > b_in:
                            g = g * 1.03
                            r = r * 0.98

                    elif look == "editorial_film":
                        # Emulación film con sombras ligeramente elevadas y hombro suave
                        r = s_curve(r_in, 1.04) * 0.97 + 0.02
                        g = s_curve(g_in, 1.04) * 0.97 + 0.02
                        b = s_curve(b_in, 1.02) * 0.96 + 0.025

                        # Tonos cálidos en medios
                        r = r * 1.02
                        b = b * 0.98

                    else:  # master_grade
                        r = s_curve(r_in, 1.10) * 1.03
                        g = s_curve(g_in, 1.08) * 1.01
                        b = s_curve(b_in, 1.06) * 0.96

                    # Clamping estricto en [0.0, 1.0]
                    r = max(0.0, min(1.0, r))
                    g = max(0.0, min(1.0, g))
                    b = max(0.0, min(1.0, b))

                    f.write(f"{r:.6f} {g:.6f} {b:.6f}\n")

def build_color_manifest() -> dict:
    luts_dir = WORKSPACE_ROOT / "campaign" / "color" / "luts"
    luts_dir.mkdir(parents=True, exist_ok=True)

    lut_warm = luts_dir / "locos_materos_warm_cinematic.cube"
    lut_film = luts_dir / "locos_materos_editorial_film.cube"
    lut_master = luts_dir / "locos_materos_master_grade.cube"

    generate_cube_lut(lut_warm, "Locos Materos Warm Cinematic", size=33, look="warm_cinematic")
    generate_cube_lut(lut_film, "Locos Materos Editorial Film", size=33, look="editorial_film")
    generate_cube_lut(lut_master, "Locos Materos Master Grade", size=65, look="master_grade")

    luts_registered = [
        {
            "lut_name": "locos_materos_warm_cinematic",
            "lut_path": str(lut_warm.relative_to(WORKSPACE_ROOT)),
            "lut_type": "3D",
            "grid_size": 33,
            "description": "Look cinematográfico principal con altas luces doradas y verdes orgánicos profundos"
        },
        {
            "lut_name": "locos_materos_editorial_film",
            "lut_path": str(lut_film.relative_to(WORKSPACE_ROOT)),
            "lut_type": "3D",
            "grid_size": 33,
            "description": "Emulación analógica con sombras suaves y contraste sedoso para momentos cotidianos"
        },
        {
            "lut_name": "locos_materos_master_grade",
            "lut_path": str(lut_master.relative_to(WORKSPACE_ROOT)),
            "lut_type": "3D",
            "grid_size": 65,
            "description": "LUT maestra 65x65x65 para masterización final y render de máxima fidelidad"
        }
    ]

    scene_grades_data = [
        {
            "scene_id": "scene_01",
            "base_lut": str(lut_warm.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.15,
            "contrast": 1.08,
            "color_temperature_k": 5900,
            "tint": 1.5,
            "saturation": 1.05,
            "lift": [0.00, 0.00, -0.01],
            "gamma": [0.02, 0.01, -0.01],
            "gain": [1.03, 1.01, 0.97],
            "intent_rationale": "Acentuar la calidez matinal del vapor y la mesa de madera con luz de ventana envolvente."
        },
        {
            "scene_id": "scene_02",
            "base_lut": str(lut_warm.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.0,
            "contrast": 1.15,
            "color_temperature_k": 5700,
            "tint": 2.0,
            "saturation": 1.12,
            "lift": [-0.01, 0.00, -0.01],
            "gamma": [0.01, 0.03, -0.01],
            "gain": [1.02, 1.04, 0.96],
            "intent_rationale": "Mayor microcontraste para destacar las texturas de la yerba mate y brillo dorado en la virola."
        },
        {
            "scene_id": "scene_03",
            "base_lut": str(lut_warm.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": -0.1,
            "contrast": 1.12,
            "color_temperature_k": 6100,
            "tint": 1.0,
            "saturation": 1.08,
            "lift": [0.00, 0.00, 0.01],
            "gamma": [0.03, 0.02, -0.02],
            "gain": [1.05, 1.02, 0.95],
            "intent_rationale": "Proteger el detalle en el cielo cordillerano y bañar la escena con luz solar dorada."
        },
        {
            "scene_id": "scene_04",
            "base_lut": str(lut_film.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.1,
            "contrast": 1.06,
            "color_temperature_k": 5800,
            "tint": 0.5,
            "saturation": 1.04,
            "lift": [0.01, 0.00, 0.00],
            "gamma": [0.02, 0.01, 0.00],
            "gain": [1.02, 1.01, 0.98],
            "intent_rationale": "Tonos de piel naturales y orgánicos en la interacción de cebar el mate."
        },
        {
            "scene_id": "scene_05",
            "base_lut": str(lut_warm.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.0,
            "contrast": 1.10,
            "color_temperature_k": 5650,
            "tint": 0.0,
            "saturation": 1.05,
            "lift": [-0.01, 0.00, 0.00],
            "gamma": [0.01, 0.01, -0.01],
            "gain": [1.01, 1.01, 0.98],
            "intent_rationale": "Balance neutro urbano manteniendo coherencia con el termo y mate en mano."
        },
        {
            "scene_id": "scene_06",
            "base_lut": str(lut_film.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.05,
            "contrast": 1.05,
            "color_temperature_k": 5700,
            "tint": 1.0,
            "saturation": 1.02,
            "lift": [0.01, 0.01, 0.00],
            "gamma": [0.02, 0.02, 0.00],
            "gain": [1.02, 1.01, 0.98],
            "intent_rationale": "Contrarrestar luces fluorescentes de oficina con calidez dorada del mate en escritorio."
        },
        {
            "scene_id": "scene_07",
            "base_lut": str(lut_warm.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.0,
            "contrast": 1.08,
            "color_temperature_k": 5850,
            "tint": 1.5,
            "saturation": 1.06,
            "lift": [0.00, 0.00, 0.00],
            "gamma": [0.02, 0.02, -0.01],
            "gain": [1.03, 1.02, 0.97],
            "intent_rationale": "Ambiente juvenil luminoso, verde césped natural y mate compartido."
        },
        {
            "scene_id": "scene_08",
            "base_lut": str(lut_film.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.1,
            "contrast": 1.12,
            "color_temperature_k": 5900,
            "tint": 1.0,
            "saturation": 1.08,
            "lift": [0.00, 0.00, -0.01],
            "gamma": [0.02, 0.01, -0.01],
            "gain": [1.03, 1.01, 0.97],
            "intent_rationale": "Enfoque emocional en el disfrute del sorbo, alta fidelidad en tonos faciales."
        },
        {
            "scene_id": "scene_09",
            "base_lut": str(lut_master.relative_to(WORKSPACE_ROOT)),
            "exposure_offset_ev": 0.0,
            "contrast": 1.20,
            "color_temperature_k": 6000,
            "tint": 2.0,
            "saturation": 1.15,
            "lift": [-0.02, 0.00, -0.02],
            "gamma": [0.02, 0.03, -0.02],
            "gain": [1.05, 1.03, 0.95],
            "intent_rationale": "Máximo impacto publicitario con negros profundos, viñeta verde mate y dorados radiantes."
        }
    ]

    manifest = {
        "campaign_id": "camp_locos_materos_2026",
        "color_science": {
            "color_space": "Rec.709",
            "gamma": "Gamma 2.4",
            "target_display": "SDR 100 nits"
        },
        "brand_color_harmony": {
            "primary_green": "#0D5C3A",
            "golden_highlight": "#D4AF37",
            "deep_neutral_black": "#1A1A1A",
            "color_temperature_target_kelvin": 5900
        },
        "luts_registered": luts_registered,
        "scene_grades": scene_grades_data
    }
    return manifest

def validate_color_manifest(manifest: dict):
    schema_path = WORKSPACE_ROOT / "config" / "color-grading-schema.json"
    if not schema_path.is_file():
        raise FileNotFoundError(f"Esquema no encontrado: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=manifest, schema=schema)

def main():
    parser = argparse.ArgumentParser(description="ADCRA Color Grading Assistant CLI")
    parser.add_argument("--output", "-o", default="campaign/color/color-grading-manifest.json", help="Ruta de salida JSON")
    parser.add_argument("--validate-only", action="store_true", help="Solo valida el manifiesto existente")
    args = parser.parse_args()

    out_file = WORKSPACE_ROOT / args.output
    color_dir = WORKSPACE_ROOT / "campaign" / "color"
    color_dir.mkdir(parents=True, exist_ok=True)

    if args.validate_only:
        if not out_file.is_file():
            print(f"[ERROR] Archivo no encontrado: {out_file}", file=sys.stderr)
            sys.exit(1)
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        validate_color_manifest(data)
        print(f"[VALID] El manifiesto {out_file} cumple 100% con config/color-grading-schema.json")
        return

    print("[COLOR] Generando LUTs 3D .cube y manifiesto de etalonaje para Locos Materos...")
    manifest = build_color_manifest()

    try:
        validate_color_manifest(manifest)
        print("[SUCCESS] Manifiesto de color validado formalmente contra config/color-grading-schema.json")
    except jsonschema.ValidationError as e:
        print(f"[ERROR] Error de validación de color grading: {e.message}", file=sys.stderr)
        sys.exit(2)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Manifiesto de color guardado en: {out_file}")
    print(f" - LUTs 3D Generadas: {len(manifest['luts_registered'])}")
    print(f" - Escenas Etalonadas: {len(manifest['scene_grades'])}")
    print(f" - Espacio de Color: {manifest['color_science']['color_space']} / {manifest['color_science']['gamma']}")
    print(f" - Target Kelvin: {manifest['brand_color_harmony']['color_temperature_target_kelvin']}K")

if __name__ == "__main__":
    main()
