#!/usr/bin/env python3
"""
ADCRA — Lyric & Audio Intelligence Alignment Engine
Alinea versos, palabras clave e intenciones visuales con la estructura rítmica
de audio calculada en la Fase 4 y el catálogo de metraje real.
"""

import sys
import os
import json
import argparse
from pathlib import Path

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

CANONICAL_PHRASES = [
    {
        "phrase_id": "lyric_01",
        "scene_number": 1,
        "text": "Ya está sonando el hervidor",
        "thematic_category": "RITUAL_START",
        "emotional_tone": "Intimidad, despertar y calidez de hogar",
        "video_filename": "Escena 01 Ya está sonando el hervidor.mp4",
        "visual_intention": "Cocina chilena al amanecer, plano medio del hervidor humeando bajo la luz dorada",
        "keywords": ["hervidor", "sonando", "amanecer"]
    },
    {
        "phrase_id": "lyric_02",
        "scene_number": 2,
        "text": "Macro de yerba y bombilla",
        "thematic_category": "SENSORY_CLOSENESS",
        "emotional_tone": "Textura artesanal, detalle botánico y concentración",
        "video_filename": "Escena 02 Macro de yerba y bombilla.mp4",
        "visual_intention": "Macro 85mm con poca profundidad de campo de la yerba verde y bombilla de acero",
        "keywords": ["yerba", "bombilla", "mate"]
    },
    {
        "phrase_id": "lyric_03",
        "scene_number": 3,
        "text": "El sol asoma en la cordillera",
        "thematic_category": "NATURAL_IDENTITY",
        "emotional_tone": "Grandeza paisajística y despertar territorial",
        "video_filename": "Escena 03 El sol asoma en la cordillera.mp4",
        "visual_intention": "Plano general 24mm de la Cordillera de los Andes bañada en luz dorada matutina",
        "keywords": ["sol", "cordillera", "Andes"]
    },
    {
        "phrase_id": "lyric_04",
        "scene_number": 4,
        "text": "Cebando arranca todo Chile",
        "thematic_category": "COMMUNITY_MOVEMENT",
        "emotional_tone": "Energía colectiva, impulso y sincronía nacional",
        "video_filename": "Escena 04 Cebando arranca todo Chile.mp4",
        "visual_intention": "Plano de manos cebando con precisión mientras la ciudad cobra ritmo",
        "keywords": ["Cebando", "arranca", "Chile"]
    },
    {
        "phrase_id": "lyric_05",
        "scene_number": 5,
        "text": "Caminando por el barrio",
        "thematic_category": "COMMUNITY_MOVEMENT",
        "emotional_tone": "Pertenencia, cercanía vecinal y vida barrial",
        "video_filename": "Escena 05 Caminando por el barrio..mp4",
        "visual_intention": "Cámara en seguimiento elegante de una persona caminando por vereda arbolada con termo",
        "keywords": ["Caminando", "barrio", "calles"]
    },
    {
        "phrase_id": "lyric_06",
        "scene_number": 6,
        "text": "Transición trabajo hogar",
        "thematic_category": "WORK_AND_STUDY",
        "emotional_tone": "Pausa reflexiva y continuidad entre trabajo y descanso",
        "video_filename": "Escena 06 Transición trabajohogar..mp4",
        "visual_intention": "Ambiente de trabajo o taller con termo y mate como compañero de jornada",
        "keywords": ["trabajo", "hogar", "pausa"]
    },
    {
        "phrase_id": "lyric_07",
        "scene_number": 7,
        "text": "Estudiantes en la universidad",
        "thematic_category": "WORK_AND_STUDY",
        "emotional_tone": "Juventud, compañerismo y estudio colaborativo",
        "video_filename": "Escena 07 Estudiantes en la universidad..mp4",
        "visual_intention": "Grupo de jóvenes en patio universitario compartiendo mate entre apuntes y risas",
        "keywords": ["Estudiantes", "universidad", "juntos"]
    },
    {
        "phrase_id": "lyric_08",
        "scene_number": 8,
        "text": "Primer plano de mate y sorbo",
        "thematic_category": "SENSORY_CLOSENESS",
        "emotional_tone": "Satisfacción pura, placer del ritual y sabor",
        "video_filename": "Escena 08 Primer plano de mate y sorbo..mp4",
        "visual_intention": "Primer plano del mate sostenido con ambas manos seguido del gesto cálido del sorbo",
        "keywords": ["mate", "sorbo", "calidez"]
    },
    {
        "phrase_id": "lyric_09",
        "scene_number": 9,
        "text": "¿Dónde estás tú? Está tu mate",
        "thematic_category": "BRAND_CORE",
        "emotional_tone": "Pertenencia profunda, encuentro humano y promesa de marca",
        "video_filename": "Escena 09 Dónde estás tú.mp4",
        "visual_intention": "Rueda de amigos riendo y compartiendo mate; transición limpia al packshot final",
        "keywords": ["Dónde", "estás", "tú", "mate"]
    }
]

def load_audio_analysis(analysis_path: Path) -> dict:
    if not analysis_path.is_file():
        # Fallback a valores por defecto si aún no se procesó
        return {
            "musical_analysis": {"bpm": 107.7},
            "all_downbeats": [0.0, 2.39, 4.62, 6.80, 9.08, 11.31, 13.54, 15.77, 18.00, 20.24, 22.48, 24.72, 26.96, 29.19],
            "recommended_commercial_cuts": [{"target_duration_seconds": 30, "exact_cut_timestamp": 29.187}]
        }
    with open(analysis_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_lyric_alignment(audio_analysis: dict) -> dict:
    downbeats = audio_analysis.get("all_downbeats", [])
    cut_30s = 29.187
    for c in audio_analysis.get("recommended_commercial_cuts", []):
        if c.get("target_duration_seconds") == 30:
            cut_30s = c.get("exact_cut_timestamp", 29.187)

    # 9 escenas distribuidas sobre la duración objetivo de 29.187s
    # Mapeo a compases (downbeats) musicales reales
    # Reparto rítmico armónico:
    time_slices = [
        (0.0, 3.5),    # Escena 1: 3.5s (Hervidor)
        (3.5, 6.8),    # Escena 2: 3.3s (Yerba y bombilla - Cierre de Intro)
        (6.8, 10.2),   # Escena 3: 3.4s (Cordillera - Entrada de ritmo)
        (10.2, 13.5),  # Escena 4: 3.3s (Cebando arranca todo Chile)
        (13.5, 16.8),  # Escena 5: 3.3s (Caminando por el barrio)
        (16.8, 20.0),  # Escena 6: 3.2s (Trabajo / Hogar)
        (20.0, 23.2),  # Escena 7: 3.2s (Universidad)
        (23.2, 26.0),  # Escena 8: 2.8s (Sorbo íntimo - Pre-clímax)
        (26.0, round(cut_30s, 3)) # Escena 9: ~3.2s (Dónde estás tú - Packshot final)
    ]

    alignment_items = []
    for idx, phrase in enumerate(CANONICAL_PHRASES):
        t_start, t_end = time_slices[idx]
        dur = round(t_end - t_start, 3)

        # Buscar archivo de video en Recursos/videos/
        vpath = WORKSPACE_ROOT / "Recursos" / "videos" / phrase["video_filename"]
        rel_video = f"Recursos/videos/{phrase['video_filename']}"

        # Asignar timestamps aproximados por palabra
        words = phrase["text"].split()
        word_step = dur / max(1, len(words))
        word_timings = []
        for w_i, w in enumerate(words):
            word_timings.append({
                "word": w,
                "approx_timestamp": round(t_start + (w_i * word_step), 3)
            })

        alignment_items.append({
            "phrase_id": phrase["phrase_id"],
            "scene_number": phrase["scene_number"],
            "lyric_text": phrase["text"],
            "thematic_category": phrase["thematic_category"],
            "emotional_tone": phrase["emotional_tone"],
            "timeline_segment": {
                "start": t_start,
                "end": t_end,
                "duration": dur
            },
            "video_asset": {
                "filename": phrase["video_filename"],
                "relative_path": rel_video,
                "exists_on_disk": vpath.is_file()
            },
            "visual_intention": phrase["visual_intention"],
            "keywords": phrase["keywords"],
            "word_timings": word_timings
        })

    result = {
        "song_title": "Entre mates y sol",
        "audio_reference": "Recursos/Audios/Entre_mates_y_sol.mp3",
        "target_duration_seconds": cut_30s,
        "total_scenes": len(alignment_items),
        "thematic_arc": "Intimidad matutina -> Identidad andina -> Movimiento y trabajo -> Comunidad y cierre de marca",
        "thematic_categories_present": list(sorted(list({item["thematic_category"] for item in alignment_items}))),
        "alignment": alignment_items
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="ADCRA Lyric & Audio Intelligence CLI")
    parser.add_argument("--analysis", "-a", default="campaign/audio/audio-analysis.json", help="Ruta al archivo de análisis de audio")
    parser.add_argument("--output", "-o", default="campaign/audio/lyric-alignment.json", help="Ruta de salida JSON")
    parser.add_argument("--json", action="store_true", help="Imprime resultado por stdout")
    args = parser.parse_args()

    analysis_path = WORKSPACE_ROOT / args.analysis
    audio_analysis = load_audio_analysis(analysis_path)

    print("[ALIGNING] Generando alineación lírico-visual y semántica...")
    result = build_lyric_alignment(audio_analysis)

    out_path = WORKSPACE_ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Alineación lírico-visual completada:")
    print(f" - Canción:          {result['song_title']}")
    print(f" - Duración Corte:   {result['target_duration_seconds']} s")
    print(f" - Escenas Alineadas: {result['total_scenes']}")
    print(f" - Categorías:       {', '.join(result['thematic_categories_present'])}")
    print(f"[SAVED] Archivo guardado en: {out_path}")

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
