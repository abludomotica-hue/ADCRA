#!/usr/bin/env python3
"""
ADCRA — Storyboard Generator Engine
Sintetiza la visión estratégica, el análisis de audio y la catalogación de activos
en un storyboard publicitario escena por escena validado contra config/storyboard-schema.json.
"""

import sys
import os
import json
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

SCENE_BLUEPRINTS = [
    {
        "scene_id": "scene_01",
        "start": 0.0,
        "end": 3.5,
        "duration": 3.5,
        "audio_segment": {
            "beat_start": 0.186,
            "beat_end": 3.506,
            "energy_level": "low",
            "musical_cue": "Intro acústica íntima, acordes limpios de guitarra"
        },
        "lyric_reference": "Ya está sonando el hervidor",
        "visual": "Cocina chilena al amanecer, plano medio del hervidor humeando bajo la luz dorada entrando por la ventana",
        "camera": "Plano medio con movimiento orgánico en mano (handheld 35mm)",
        "lighting": "Luz natural suave de ventana matutina (warm natural window)",
        "emotion": "Intimidad, despertar y calidez de hogar",
        "copy": "Cada día comienza con una pausa.",
        "typography": {
            "font_family": "Montserrat SemiBold",
            "size": "42px",
            "color": "#F5EFEB",
            "alignment": "bottom_center"
        },
        "animation": "fade_up_subtle",
        "transition": {
            "type": "cross_dissolve",
            "duration_seconds": 0.3
        },
        "brand_visibility": "subtle",
        "asset_ids": ["vid_escena_01_ya_está_sonando"],
        "tool": "DaVinci Resolve",
        "rationale": "Engancha al espectador en los primeros 3 segundos apelando al ritual universal de encender el hervidor, construyendo una atmósfera de calma previa al movimiento del día."
    },
    {
        "scene_id": "scene_02",
        "start": 3.5,
        "end": 6.8,
        "duration": 3.3,
        "audio_segment": {
            "beat_start": 3.506,
            "beat_end": 6.803,
            "energy_level": "low",
            "musical_cue": "Mantiene arpegio acústico con resonancia de caja"
        },
        "lyric_reference": "Macro de yerba y bombilla",
        "visual": "Primerísimo plano macro de la yerba mate verde natural, la bombilla de acero inoxidable y la calabaza tradicional con vapor ascendente",
        "camera": "Macro 85mm estático con foco crítico y profundidad de campo reducida",
        "lighting": "Luz cálida rasante que resalta las texturas y hojas de yerba",
        "emotion": "Precisión artesanal, textura y calma sensorial",
        "copy": "El arte de prepararse para lo bueno.",
        "typography": {
            "font_family": "Montserrat Regular",
            "size": "38px",
            "color": "#E8DFD5",
            "alignment": "bottom_center"
        },
        "animation": "soft_focus_reveal",
        "transition": {
            "type": "cut",
            "duration_seconds": 0.0
        },
        "brand_visibility": "product_in_use",
        "asset_ids": ["vid_escena_02_macro_de_yerba_"],
        "tool": "DaVinci Resolve",
        "rationale": "Cumple con el mandato estricto de marca de mostrar el mate físicamente auténtico y realista (calabaza, yerba y bombilla) antes de que la historia salga al exterior."
    },
    {
        "scene_id": "scene_03",
        "start": 6.8,
        "end": 10.2,
        "duration": 3.4,
        "audio_segment": {
            "beat_start": 6.803,
            "beat_end": 10.200,
            "energy_level": "medium",
            "musical_cue": "Entrada de base rítmica suave marcando el pulso"
        },
        "lyric_reference": "El sol asoma en la cordillera",
        "visual": "Plano general de la imponente Cordillera de los Andes bañada por el sol naciente dorado sobre el valle de Santiago",
        "camera": "Plano general 24mm con paneo horizontal lento y majestuoso",
        "lighting": "Luz dorada de amanecer (golden hour morning) con alto rango dinámico",
        "emotion": "Grandeza andina, horizonte y orgullo territorial",
        "copy": "Un país que despierta con la cordillera.",
        "typography": {
            "font_family": "Montserrat Bold",
            "size": "46px",
            "color": "#FFFFFF",
            "alignment": "center"
        },
        "animation": "kinetic_fade",
        "transition": {
            "type": "cut",
            "duration_seconds": 0.0
        },
        "brand_visibility": "none",
        "asset_ids": ["vid_escena_03_el_sol_asoma_e"],
        "tool": "DaVinci Resolve",
        "rationale": "Ancla la narrativa al contexto geográfico indiscutible de Chile, expandiendo la escala de lo íntimo hacia lo territorial con la entrada de la percusión."
    },
    {
        "scene_id": "scene_04",
        "start": 10.2,
        "end": 13.5,
        "duration": 3.3,
        "audio_segment": {
            "beat_start": 10.200,
            "beat_end": 13.537,
            "energy_level": "medium",
            "musical_cue": "Ritmo firme y dinámico en crescendo"
        },
        "lyric_reference": "Cebando arranca todo Chile",
        "visual": "Manos cebando con precisión un mate humeante desde un termo, con luz matutina que ilumina el chorro de agua caliente",
        "camera": "Plano medio cerrado en mano orgánico con suave inclinación",
        "lighting": "Luz de sol matutino dorada destacando el vapor",
        "emotion": "Impulso, energía compartida y sincronía de país",
        "copy": "La energía de arrancar juntos.",
        "typography": {
            "font_family": "Montserrat SemiBold",
            "size": "40px",
            "color": "#F5EFEB",
            "alignment": "bottom_center"
        },
        "animation": "slide_up",
        "transition": {
            "type": "cut",
            "duration_seconds": 0.0
        },
        "brand_visibility": "product_in_use",
        "asset_ids": ["vid_escena_04_cebando_arranc"],
        "tool": "DaVinci Resolve",
        "rationale": "Conecta el acto de cebar con el despertar simultáneo de miles de personas, convirtiendo el mate en motor de la jornada."
    },
    {
        "scene_id": "scene_05",
        "start": 13.5,
        "end": 16.8,
        "duration": 3.3,
        "audio_segment": {
            "beat_start": 13.537,
            "beat_end": 16.800,
            "energy_level": "medium",
            "musical_cue": "Línea de bajo melódica y guitarras rítmicas"
        },
        "lyric_reference": "Caminando por el barrio",
        "visual": "Persona caminando distendida por una vereda arbolada de barrio residencial chileno llevando termo bajo el brazo y mate en mano",
        "camera": "Travelling lateral lento (dolly tracking) acompañando el paso",
        "lighting": "Luz de día natural y difusa bajo la copa de los árboles",
        "emotion": "Pertenencia, cercanía vecinal y tranquilidad cotidiana",
        "copy": "En cada esquina, en cada paso.",
        "typography": {
            "font_family": "Montserrat Regular",
            "size": "40px",
            "color": "#FFFFFF",
            "alignment": "bottom_center"
        },
        "animation": "fade_subtle",
        "transition": {
            "type": "cut",
            "duration_seconds": 0.0
        },
        "brand_visibility": "product_in_use",
        "asset_ids": ["vid_escena_05_caminando_por_"],
        "tool": "DaVinci Resolve",
        "rationale": "Muestra el mate en movimiento por la ciudad real, reforzando la portabilidad y la naturalidad del consumo en la vida barrial chilena."
    },
    {
        "scene_id": "scene_06",
        "start": 16.8,
        "end": 20.0,
        "duration": 3.2,
        "audio_segment": {
            "beat_start": 16.800,
            "beat_end": 20.240,
            "energy_level": "medium",
            "musical_cue": "Transición armónica preparatoria hacia el coro"
        },
        "lyric_reference": "Transición trabajo hogar",
        "visual": "Espacio laboral contemporáneo donde una persona hace una pausa en su tarea para tomar un mate",
        "camera": "Plano medio estático con composición cuidada y equilibrio visual",
        "lighting": "Iluminación interior ambiental realista y cálida",
        "emotion": "Pausa reflexiva, concentración y perseverancia",
        "copy": "El mate que acompaña tu esfuerzo.",
        "typography": {
            "font_family": "Montserrat Medium",
            "size": "38px",
            "color": "#E8DFD5",
            "alignment": "bottom_center"
        },
        "animation": "fade_up",
        "transition": {
            "type": "cut",
            "duration_seconds": 0.0
        },
        "brand_visibility": "product_in_use",
        "asset_ids": ["vid_escena_06_transición_tra"],
        "tool": "DaVinci Resolve",
        "rationale": "Representa el segmento de trabajadores y profesionales que encuentran en el mate un aliado contra el cansancio y una compañía fiel durante el trabajo."
    },
    {
        "scene_id": "scene_07",
        "start": 20.0,
        "end": 23.2,
        "duration": 3.2,
        "audio_segment": {
            "beat_start": 20.240,
            "beat_end": 23.200,
            "energy_level": "high",
            "musical_cue": "Entrada con fuerza de la batería anunciando el coro"
        },
        "lyric_reference": "Estudiantes en la universidad",
        "visual": "Grupo diverso de estudiantes sentados en un patio universitario compartiendo mate entre apuntes, cuadernos y risas",
        "camera": "Plano de grupo con movimiento fluido y humano en 50mm",
        "lighting": "Luz solar abierta de mediodía suave",
        "emotion": "Complicidad juvenil, compañerismo y estudio colaborativo",
        "copy": "Ideas que se comparten mejor.",
        "typography": {
            "font_family": "Montserrat Bold",
            "size": "42px",
            "color": "#FFFFFF",
            "alignment": "bottom_center"
        },
        "animation": "pop_scale",
        "transition": {
            "type": "cut",
            "duration_seconds": 0.0
        },
        "brand_visibility": "product_in_use",
        "asset_ids": ["vid_escena_07_estudiantes_en"],
        "tool": "DaVinci Resolve",
        "rationale": "Conecta con el público joven (20-30 años), posicionando el mate como catalizador de amistad, estudio y vida universitaria."
    },
    {
        "scene_id": "scene_08",
        "start": 23.2,
        "end": 26.0,
        "duration": 2.8,
        "audio_segment": {
            "beat_start": 23.200,
            "beat_end": 26.000,
            "energy_level": "climax",
            "musical_cue": "Acorde culminante previo a la resolución"
        },
        "lyric_reference": "Primer plano de mate y sorbo",
        "visual": "Primer plano íntimo del mate sostenido con ambas manos seguido del gesto de un sorbo auténtico y una mirada de serenidad",
        "camera": "Primer plano 50mm cerrado con bokeh cálido de fondo",
        "lighting": "Luz dorada envolvente",
        "emotion": "Satisfacción profunda, calidez sensorial y alivio",
        "copy": "Un sabor que nos vuelve a reunir.",
        "typography": {
            "font_family": "Montserrat SemiBold",
            "size": "44px",
            "color": "#F5EFEB",
            "alignment": "center"
        },
        "animation": "fade_in_scale",
        "transition": {
            "type": "cross_dissolve",
            "duration_seconds": 0.4
        },
        "brand_visibility": "product_in_use",
        "asset_ids": ["vid_escena_08_primer_plano_d"],
        "tool": "DaVinci Resolve",
        "rationale": "Sintetiza la experiencia táctil y gustativa en un momento de gratificación máxima antes del clímax colectivo final."
    },
    {
        "scene_id": "scene_09",
        "start": 26.0,
        "end": 29.187,
        "duration": 3.187,
        "audio_segment": {
            "beat_start": 26.000,
            "beat_end": 29.187,
            "energy_level": "climax",
            "musical_cue": "Resolución armónica final y decaimiento sonoro perfecto"
        },
        "lyric_reference": "¿Dónde estás tú? Está tu mate",
        "visual": "Rueda de amigos compartiendo mate al atardecer en ambiente acogedor, con sonrisas genuinas y espacio inferior para packshot final de Locos Materos",
        "camera": "Travelling lento retrocediendo suavemente para dar protagonismo a la marca",
        "lighting": "Golden hour cálida combinada con luces prácticas acogedoras",
        "emotion": "Pertenencia absoluta, alegría compartida y fidelidad de marca",
        "copy": "¿Dónde estás tú? Está tu mate.",
        "typography": {
            "font_family": "Montserrat Bold",
            "size": "48px",
            "color": "#FFFFFF",
            "alignment": "center"
        },
        "animation": "hero_reveal",
        "transition": {
            "type": "fade_to_black",
            "duration_seconds": 0.5
        },
        "brand_visibility": "hero_packshot",
        "asset_ids": ["vid_escena_09_dónde_estás_tú"],
        "tool": "DaVinci Resolve",
        "rationale": "Cierra el arco dramático llevando al espectador desde la soledad matutina hasta la celebración en comunidad, estampando el claim oficial y habilitando la inserción del logo oficial en post-producción."
    }
]

def generate_storyboard(campaign_id: str = "camp_locos_materos_2026", target_fps: float = 24.0) -> dict:
    storyboard = {
        "storyboard_id": f"sb_{campaign_id}_v1",
        "campaign_id": campaign_id,
        "narrative_arc": "Amanecer solitario e íntimo -> Ritual de preparación -> Despertar andino -> Movimiento y sincronía nacional -> Vida cotidiana y trabajo -> Juventud y estudio -> Placer sensorial del sorbo -> Comunidad, amistad y pertenencia de marca",
        "total_duration_seconds": 29.187,
        "target_fps": target_fps,
        "scenes": SCENE_BLUEPRINTS
    }
    return storyboard

def validate_storyboard(storyboard: dict):
    schema_path = WORKSPACE_ROOT / "config" / "storyboard-schema.json"
    if not schema_path.is_file():
        raise FileNotFoundError(f"Esquema no encontrado: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=storyboard, schema=schema)

def main():
    parser = argparse.ArgumentParser(description="ADCRA Storyboard Generator CLI")
    parser.add_argument("--campaign-id", "-c", default="camp_locos_materos_2026", help="ID de la campaña")
    parser.add_argument("--output", "-o", default="campaign/storyboard/storyboard.json", help="Ruta de salida JSON")
    parser.add_argument("--validate-only", action="store_true", help="Solo valida el archivo existente")
    args = parser.parse_args()

    out_path = WORKSPACE_ROOT / args.output

    if args.validate_only:
        if not out_path.is_file():
            print(f"[ERROR] Archivo no encontrado: {out_path}", file=sys.stderr)
            sys.exit(1)
        with open(out_path, "r", encoding="utf-8") as f:
            sb = json.load(f)
        validate_storyboard(sb)
        print(f"[VALID] El storyboard {out_path} cumple 100% con config/storyboard-schema.json")
        return

    print("[STORYTELLING] Construyendo storyboard publicitario escena por escena...")
    storyboard = generate_storyboard(args.campaign_id, target_fps=24.0)

    try:
        validate_storyboard(storyboard)
        print("[SUCCESS] Storyboard validado formalmente contra config/storyboard-schema.json")
    except jsonschema.ValidationError as e:
        print(f"[ERROR] Validación fallida del storyboard: {e.message}", file=sys.stderr)
        sys.exit(2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Storyboard guardado en: {out_path}")
    print(f" - ID:          {storyboard['storyboard_id']}")
    print(f" - Duración:    {storyboard['total_duration_seconds']}s")
    print(f" - FPS:         {storyboard['target_fps']}")
    print(f" - Escenas:     {len(storyboard['scenes'])}")

if __name__ == "__main__":
    main()
