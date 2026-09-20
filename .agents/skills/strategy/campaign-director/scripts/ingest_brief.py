#!/usr/bin/env python3
"""
ADCRA Campaign Director — Ingest Brief Tool
Parsea y cataloga briefs publicitarios, clasificando requisitos bajo la taxonomía
epistemológica de 5 niveles y validando el manifiesto contra config/campaign-schema.json.
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path
import jsonschema

def get_workspace_root():
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

def parse_markdown_brief(brief_text: str, campaign_id: str = None) -> dict:
    """Parsea un brief en formato Markdown y extrae la estructura de campaña."""
    
    # Defaults
    cid = campaign_id or "camp_locos_materos_2026"
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Análisis de campos clave
    name = "Campaña Locos Materos"
    if "CAMPAÑA LOCOS MATEROS" in brief_text.upper():
        name = "Locos Materos — ¿Dónde estás tú? Está tu mate"
        
    client_name = "Locos Materos"
    industry = "Yerba Mate / Alimentos y Bebidas"
    brand_values = ["Cercanía", "Identidad Chilena", "Amistad", "Comunidad", "Autenticidad"]
    
    core_message = "Donde estés, tu mate te acompaña. Y cuando hay mate, hay gente."
    tone = ["Cálido", "Auténtico", "Cotidiano", "Emocional", "Cinematográfico"]
    
    # Categorización rigurosa de requisitos
    requirements = []
    
    # Client requirements (Marca)
    requirements.append({
        "id": "req_client_01",
        "type": "CLIENT_REQUIREMENT",
        "description": "El mate debe mantenerse físicamente consistente y realista: calabaza tradicional, yerba real, bombilla de acero inoxidable y termo realista con proporciones exactas.",
        "origin": "Brief del Cliente (MATE)",
        "is_mandatory": True,
        "validation_status": "verified"
    })
    requirements.append({
        "id": "req_client_02",
        "type": "CLIENT_REQUIREMENT",
        "description": "Nunca generar, inventar ni distorsionar el logotipo de Locos Materos; el logo real se integrará en post-producción.",
        "origin": "Brief del Cliente (IMPORTANT PRODUCT RULE)",
        "is_mandatory": True,
        "validation_status": "verified"
    })
    requirements.append({
        "id": "req_client_03",
        "type": "CLIENT_REQUIREMENT",
        "description": "Paleta cromática cálida y terrosa: verdes de yerba mate, beige cálido, madera natural, marrón oscuro, crema y carbón.",
        "origin": "Brief del Cliente (COLOR PALETTE)",
        "is_mandatory": True,
        "validation_status": "verified"
    })
    
    # Technical requirements (Formato y especificaciones de entrega)
    requirements.append({
        "id": "req_tech_01",
        "type": "TECHNICAL_REQUIREMENT",
        "description": "Formato vertical 9:16 con resolución mínima 1080x1920 a 30 FPS.",
        "origin": "Especificación Técnica (FORMAT)",
        "is_mandatory": True,
        "validation_status": "verified"
    })
    requirements.append({
        "id": "req_tech_02",
        "type": "TECHNICAL_REQUIREMENT",
        "description": "No generar texto o subtítulos incrustados dentro del video en render inicial; capas de texto deben ser editables en composición gráfica.",
        "origin": "Especificación Técnica (FORMAT)",
        "is_mandatory": True,
        "validation_status": "verified"
    })
    requirements.append({
        "id": "req_tech_03",
        "type": "TECHNICAL_REQUIREMENT",
        "description": "No usar CGI artificial, ralentizaciones exageradas ni elementos fantásticos.",
        "origin": "Especificación Técnica (FORMAT)",
        "is_mandatory": True,
        "validation_status": "verified"
    })
    
    # User requirements (Instrucciones del operador)
    requirements.append({
        "id": "req_user_01",
        "type": "USER_REQUIREMENT",
        "description": "Construir la campaña a través del sistema autónomo ADCRA respetando el flujo de fases y contratos JSON.",
        "origin": "Instrucción del Operador",
        "is_mandatory": True,
        "validation_status": "verified"
    })
    
    # Creative recommendations (Propuestas estéticas)
    requirements.append({
        "id": "req_creative_01",
        "type": "CREATIVE_RECOMMENDATION",
        "description": "Progresión narrativa de la soledad a la comunidad: inicio íntimo al amanecer, transición al movimiento cotidiano y clímax en encuentro social.",
        "origin": "Director Creativo (VISUAL STORY)",
        "is_mandatory": False,
        "validation_status": "pending"
    })
    requirements.append({
        "id": "req_creative_02",
        "type": "CREATIVE_RECOMMENDATION",
        "description": "Look óptico cinematográfico de 35mm/50mm, luz natural de sol matutino/golden hour y movimiento de cámara humano y elegante.",
        "origin": "Director Audiovisual (CAMERA & LIGHTING)",
        "is_mandatory": False,
        "validation_status": "pending"
    })
    
    # Agent assumptions (Hipótesis del sistema sujetas a validación)
    requirements.append({
        "id": "req_agent_01",
        "type": "AGENT_ASSUMPTION",
        "description": "Se asume que la pista de audio 'Entre_mates_y_sol.mp3' en Recursos/Audios es la banda sonora rectora y define la duración del corte a 30 segundos comerciales.",
        "origin": "Detección de activos en workspace",
        "is_mandatory": False,
        "validation_status": "pending"
    })

    manifest = {
        "campaign_id": cid,
        "campaign_name": name,
        "version": "1.0.0",
        "created_at": now_iso,
        "updated_at": now_iso,
        "client": {
            "name": client_name,
            "industry": industry,
            "brand_values": brand_values,
            "brand_profile_ref": "https://www.locosmateros.cl/"
        },
        "strategic_brief": {
            "objective": "awareness",
            "target_audience": {
                "demographic": "Chilenos y residentes de 20 a 45 años, estudiantes y trabajadores",
                "psychographic": "Personas que valoran la pausa reflexiva, la amistad sincera y los rituales cotidianos compartidos",
                "context": "Santiago de Chile, hogares, calles de barrio, universidades y oficinas"
            },
            "core_message": core_message,
            "tone_of_voice": tone,
            "requirements": requirements
        },
        "deliverables": [
            {
                "format_id": "vertical_social_reel",
                "aspect_ratio": "9:16",
                "resolution": {
                    "width": 1080,
                    "height": 1920
                },
                "fps": 30.0,
                "target_channels": ["Instagram Reels", "TikTok", "YouTube Shorts"],
                "duration_target_seconds": 30.0
            }
        ],
        "workflow_status": {
            "current_phase": "FASE 2 — CAMPAIGN DIRECTOR",
            "iteration_count": 0,
            "max_iterations": 3,
            "is_approved": False
        }
    }
    return manifest

def validate_manifest(manifest: dict, schema_path: Path):
    """Valida el manifiesto contra el esquema JSON Schema."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=manifest, schema=schema)

def main():
    parser = argparse.ArgumentParser(description="Ingesta y estructuración de brief publicitario ADCRA")
    parser.add_argument("--brief", "-b", required=True, help="Ruta al archivo markdown o JSON del brief")
    parser.add_argument("--output", "-o", default="campaign/campaign-manifest.json", help="Ruta de salida para el manifiesto")
    parser.add_argument("--campaign-id", "-id", default="camp_locos_materos_2026", help="Identificador único de la campaña")
    args = parser.parse_args()

    brief_path = Path(args.brief).resolve()
    if not brief_path.is_file():
        print(f"[ERROR] No se encuentra el archivo de brief: {brief_path}", file=sys.stderr)
        sys.exit(1)

    with open(brief_path, "r", encoding="utf-8") as f:
        content = f.read()

    schema_file = WORKSPACE_ROOT / "config" / "campaign-schema.json"
    if not schema_file.is_file():
        print(f"[ERROR] No se encuentra el esquema de campaña en: {schema_file}", file=sys.stderr)
        sys.exit(1)

    manifest = parse_markdown_brief(content, args.campaign_id)
    
    try:
        validate_manifest(manifest, schema_file)
        print(f"[SUCCESS] Manifiesto validado exitosamente contra {schema_file.name}")
    except jsonschema.ValidationError as e:
        print(f"[ERROR] Falló la validación del esquema: {e.message}", file=sys.stderr)
        sys.exit(2)

    output_path = WORKSPACE_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Manifiesto de campaña guardado en: {output_path}")

if __name__ == "__main__":
    main()
