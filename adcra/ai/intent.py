"""
ADCRA AI Brain — Intent Engine
Parses natural language instructions and one-click UI action triggers into structured,
executable campaign intents with extracted entities, constraints, and target deliverables.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from adcra.ai.types import TaskType

logger = logging.getLogger("adcra.ai.intent")


@dataclass
class StructuredIntent:
    intent_type: str
    desired_action: str
    target: str = "campaign"
    platform: Optional[str] = None
    count: int = 1
    tone: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    raw_prompt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_type": self.intent_type,
            "desired_action": self.desired_action,
            "target": self.target,
            "platform": self.platform,
            "count": self.count,
            "tone": self.tone,
            "entities": self.entities,
            "constraints": self.constraints,
            "raw_prompt": self.raw_prompt
        }


class IntentEngine:
    def parse_intent(self, text_or_action: str, context: Optional[Dict[str, Any]] = None) -> StructuredIntent:
        raw = text_or_action.strip()
        lower = raw.lower()

        # 1. Detección de acciones rápidas UI directas
        if lower in ["create_concept", "crear concepto", "crear_concepto"]:
            return StructuredIntent(
                intent_type="CREATIVE_CONCEPT",
                desired_action="generate_creative_territories",
                target="creative_strategy",
                raw_prompt=raw
            )
        elif lower in ["generate_copy", "generar copy", "generar_copy"]:
            return StructuredIntent(
                intent_type="COPY_GENERATE",
                desired_action="generate_copy_variants",
                target="headlines_and_body",
                raw_prompt=raw
            )
        elif lower in ["create_storyboard", "crear storyboard", "crear_storyboard"]:
            return StructuredIntent(
                intent_type="STORYBOARD_GENERATE",
                desired_action="generate_shot_by_shot_storyboard",
                target="storyboard",
                raw_prompt=raw
            )
        elif lower in ["analyze_audio", "analizar audio", "analizar_audio"]:
            return StructuredIntent(
                intent_type="AUDIO_ANALYZE",
                desired_action="analyze_musical_tempo_and_beats",
                target="audio_track",
                raw_prompt=raw
            )
        elif lower in ["review_campaign", "revisar campaña", "qc", "run_qc"]:
            return StructuredIntent(
                intent_type="CREATIVE_QC",
                desired_action="evaluate_campaign_quality",
                target="campaign_deliverables",
                raw_prompt=raw
            )
        elif lower in ["produce_video", "producir video", "render", "produce"]:
            return StructuredIntent(
                intent_type="TECHNICAL_QC",
                desired_action="produce_final_commercial",
                target="video_master",
                raw_prompt=raw
            )

        # 2. Análisis por lenguaje natural
        # Plataforma
        platform = None
        for p in ["tiktok", "instagram", "reels", "shorts", "youtube", "feed"]:
            if p in lower:
                platform = p.capitalize()
                break

        # Conteo de variantes
        count = 1
        count_match = re.search(r"(\d+)\s*(versiones|variantes|copies|anuncios|opciones)", lower)
        if count_match:
            try:
                count = int(count_match.group(1))
            except Exception:
                count = 1

        # Tono
        tone = None
        if "juvenil" in lower or "joven" in lower:
            tone = "Juvenil & Dinámico"
        elif "emocional" in lower or "nostálgic" in lower:
            tone = "Emocional & Cercano"
        elif "auténtic" in lower:
            tone = "Auténtico & Realista"

        # Tipo de intención por palabras clave
        if any(w in lower for w in ["concepto", "campaña", "territorio", "estrategia"]):
            intent_type = "CREATIVE_CONCEPT"
            desired_action = "generate_creative_territories"
        elif any(w in lower for w in ["copy", "titular", "texto", "guión", "guion"]):
            intent_type = "COPY_GENERATE"
            desired_action = "generate_copy_variants"
        elif any(w in lower for w in ["storyboard", "escenas", "plano", "toma"]):
            intent_type = "STORYBOARD_GENERATE"
            desired_action = "generate_shot_by_shot_storyboard"
        elif any(w in lower for w in ["audio", "canción", "cancion", "ritmo", "bpm"]):
            intent_type = "AUDIO_ANALYZE"
            desired_action = "analyze_musical_tempo_and_beats"
        elif any(w in lower for w in ["revisar", "control", "qc", "auditar"]):
            intent_type = "CREATIVE_QC"
            desired_action = "evaluate_campaign_quality"
        elif any(w in lower for w in ["producir", "render", "armar", "video", "comercial"]):
            intent_type = "TECHNICAL_QC"
            desired_action = "produce_final_commercial"
        else:
            intent_type = "CUSTOM"
            desired_action = "process_custom_intent"

        return StructuredIntent(
            intent_type=intent_type,
            desired_action=desired_action,
            target="campaign",
            platform=platform,
            count=count,
            tone=tone,
            entities={"keywords": [w for w in lower.split() if len(w) > 4]},
            raw_prompt=raw
        )


_GLOBAL_INTENT = IntentEngine()

def get_intent_engine() -> IntentEngine:
    return _GLOBAL_INTENT
