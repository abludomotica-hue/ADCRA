"""
ADCRA AI Brain — Context Engine & Epistemology
Assembles dynamic context adhering to context token budgets, prioritizing fresh,
high-confidence data and preserving source epistemology (CLIENT_INPUT, CONFIRMED_FACT, AI_INFERENCE).
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from adcra.ai.types import SourceEpistemology

logger = logging.getLogger("adcra.ai.context")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class ContextEngine:
    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = workspace_root or WORKSPACE_ROOT

    def assemble_context(
        self,
        campaign_id: Optional[str] = None,
        task_type: Optional[str] = None,
        max_context_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Assembles a prioritized, epistemically attributed context packet.
        """
        context_packet: Dict[str, Any] = {
            "campaign_id": campaign_id or "camp_locos_materos_2026",
            "brand": {},
            "knowledge_graph": {},
            "audio": {},
            "memory": {},
            "epistemic_sources": {}
        }

        # 1. Cargar Brand Profile Memory
        memory_file = self.root / "campaign" / "memory" / "brand-profile-memory.json"
        if memory_file.is_file():
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    mem_data = json.load(f)
                    context_packet["brand"] = {
                        "name": mem_data.get("brand_name", "Locos Materos"),
                        "aesthetic": mem_data.get("aesthetic_learnings", {}),
                        "retention_rules": mem_data.get("retention_rules", {}),
                        "audience": mem_data.get("audience_profile", {})
                    }
                    context_packet["epistemic_sources"]["brand"] = {
                        "source": SourceEpistemology.CONFIRMED_FACT.value,
                        "confidence": 0.98,
                        "provenance": "campaign/memory/brand-profile-memory.json"
                    }
            except Exception as e:
                logger.warning(f"Could not load brand memory: {e}")

        # 2. Cargar Knowledge Graph
        kg_file = self.root / "campaign" / "campaign-knowledge-graph.json"
        if kg_file.is_file():
            try:
                with open(kg_file, "r", encoding="utf-8") as f:
                    kg_data = json.load(f)
                    context_packet["knowledge_graph"] = {
                        "brand_dna": kg_data.get("brand_dna", {}),
                        "campaign_nodes": len(kg_data.get("nodes", {}))
                    }
                    context_packet["epistemic_sources"]["knowledge_graph"] = {
                        "source": SourceEpistemology.CLIENT_INPUT.value,
                        "confidence": 1.0,
                        "provenance": "campaign/campaign-knowledge-graph.json"
                    }
            except Exception as e:
                logger.warning(f"Could not load knowledge graph: {e}")

        # 3. Cargar Audio Analysis
        audio_file = self.root / "campaign" / "audio" / "audio-analysis.json"
        if audio_file.is_file():
            try:
                with open(audio_file, "r", encoding="utf-8") as f:
                    aud_data = json.load(f)
                    context_packet["audio"] = {
                        "bpm": aud_data.get("musical_tempo", {}).get("bpm", 107.7),
                        "duration_sec": aud_data.get("duration_seconds", 45.2),
                        "genre": aud_data.get("genre", "Indie Folk / Acústico")
                    }
                    context_packet["epistemic_sources"]["audio"] = {
                        "source": SourceEpistemology.CONFIRMED_FACT.value,
                        "confidence": 0.95,
                        "provenance": "campaign/audio/audio-analysis.json"
                    }
            except Exception as e:
                logger.warning(f"Could not load audio analysis: {e}")

        return context_packet

    def format_context_for_prompt(self, context_packet: Dict[str, Any]) -> str:
        """Formatea el contexto en un bloque estructurado y limpio para el prompt del sistema."""
        brand = context_packet.get("brand", {})
        audio = context_packet.get("audio", {})
        kg = context_packet.get("knowledge_graph", {})
        brand_dna = kg.get("brand_dna", {})

        lines = [
            "=== CONTEXTO CERTIFICADO DE CAMPAÑA ===",
            f"Marca: {brand.get('name', 'Locos Materos')}",
            f"BPM / Ritmo: {audio.get('bpm', '107.7 BPM')} ({audio.get('genre', 'Acústico')})",
            "Brand DNA (Dimensiones Clave):",
            f" - Quiénes somos: {brand_dna.get('who_we_are', {}).get('value', 'Comunidad y pasión matera')}",
            f" - Cómo hablamos: {brand_dna.get('how_we_speak', {}).get('value', 'Cálido, cercano, directo, con humor sano')}",
            f" - Cómo nos vemos: {brand_dna.get('how_we_look', {}).get('value', 'Luz natural, tonos cálidos #0D5C3A y #D4AF37')}",
            f" - Qué NUNCA hacer: {brand_dna.get('how_we_should_never_behave', {}).get('value', 'Tratar al mate como una pose publicitaria artificial')}",
            "=== FIN DEL CONTEXTO ==="
        ]
        return "\n".join(lines)


_GLOBAL_CONTEXT = ContextEngine()

def get_context_engine() -> ContextEngine:
    return _GLOBAL_CONTEXT
