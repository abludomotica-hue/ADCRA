# ADCRA AI Brain — Creative Variant Generator & Experiment Lab (Phase 9)
# Generates multivariate A/B/n test matrix for Hook (first 3s), Pacing (107.7 BPM sync), and CTA variations.
# Enforces verbal economy on all copy variants and logs hypotheses to Campaign Memory & Knowledge Graph.

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

from adcra.ai.verbal_economy import get_verbal_economy_engine, VerbalEconomyStatus

logger = logging.getLogger("adcra.ai.experiments")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class HookType(str, Enum):
    INTRIGUE_QUESTION = "INTRIGUE_QUESTION"
    SHOCKING_PROOF = "SHOCKING_PROOF"
    IDENTITY_CHALLENGE = "IDENTITY_CHALLENGE"
    SENSORY_DISRUPTION = "SENSORY_DISRUPTION"


class PacingType(str, Enum):
    CADENCE_107_BPM = "CADENCE_107_BPM"
    DYNAMIC_RAMP = "DYNAMIC_RAMP"
    MICRO_CUTS_FAST = "MICRO_CUTS_FAST"


class CTAType(str, Enum):
    COMMUNITY_BELONGING = "COMMUNITY_BELONGING"
    DIRECT_COMMERCIAL = "DIRECT_COMMERCIAL"
    RISK_REVERSAL = "RISK_REVERSAL"


@dataclass
class ExperimentVariant:
    variant_id: str
    name: str
    hook_type: HookType
    hook_copy: str
    hook_visual_direction: str
    pacing_type: PacingType
    bpm: float
    cta_type: CTAType
    cta_copy: str
    target_audience: str
    hypothesis: str
    primary_kpi: str
    projected_lift_pct: float
    confidence_score: float
    verbal_economy: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["hook_type"] = self.hook_type.value
        d["pacing_type"] = self.pacing_type.value
        d["cta_type"] = self.cta_type.value
        return d


@dataclass
class ExperimentMatrix:
    experiment_id: str
    campaign_id: str
    created_at: str
    updated_at: str
    status: str
    active_variant_id: str
    variants: List[ExperimentVariant]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["variants"] = [v.to_dict() for v in self.variants]
        return d


class CreativeExperimentEngine:
    EXPERIMENT_STORE_PATH = WORKSPACE_ROOT / "campaign" / "creative" / "creative-experiments.json"

    def __init__(self):
        self.verbal_engine = get_verbal_economy_engine()
        self._ensure_store()

    def _ensure_store(self) -> None:
        self.EXPERIMENT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not self.EXPERIMENT_STORE_PATH.exists():
            default_matrix = self.generate_default_matrix()
            self.save_matrix(default_matrix)

    def generate_default_matrix(self, campaign_id: str = "camp_locos_materos_2026") -> ExperimentMatrix:
        """Genera matriz de 4 variantes estratégicas para Locos Materos"""
        now = datetime.now(timezone.utc).isoformat()
        
        # 1. Variante A: Intriga Emocional
        hook_a = "Cada día comienza con una pausa."
        metric_a = self.verbal_engine.analyze_scene("hook_a", hook_a, duration_sec=3.5, is_hook=True)
        var_a = ExperimentVariant(
            variant_id="var_hook_a_intrigue",
            name="Variante A — Intriga Emocional (Control)",
            hook_type=HookType.INTRIGUE_QUESTION,
            hook_copy=hook_a,
            hook_visual_direction="Plano medio amanecer con luz de ventana y vapor ascendente del hervidor",
            pacing_type=PacingType.CADENCE_107_BPM,
            bpm=107.7,
            cta_type=CTAType.COMMUNITY_BELONGING,
            cta_copy="¿Dónde estás tú? Está tu mate.",
            target_audience="Materos tradicionales y público general (25-55 años)",
            hypothesis="Un hook reflexivo y cálido genera mayor afinidad de marca a largo plazo y retención de visualización completa.",
            primary_kpi="Hold_Rate_100 (Finalización de video)",
            projected_lift_pct=15.0,
            confidence_score=0.88,
            verbal_economy=metric_a.to_dict()
        )

        # 2. Variante B: Desafío de Identidad (Alta Retención 9:16)
        hook_b = "Si tu mate se lava rápido, no sabés cebar."
        metric_b = self.verbal_engine.analyze_scene("hook_b", hook_b, duration_sec=3.0, is_hook=True)
        var_b = ExperimentVariant(
            variant_id="var_hook_b_challenge",
            name="Variante B — Desafío de Identidad Matera",
            hook_type=HookType.IDENTITY_CHALLENGE,
            hook_copy=hook_b,
            hook_visual_direction="Macro detalle de yerba montañita perfecta recibiendo agua a 78°C",
            pacing_type=PacingType.DYNAMIC_RAMP,
            bpm=107.7,
            cta_type=CTAType.DIRECT_COMMERCIAL,
            cta_copy="Descubrí el termo con 12h de calor real en locosmateros.cl",
            target_audience="Jóvenes universitarios y profesionales (18-35 años)",
            hypothesis="El reto directo a la identidad matera detiene el scroll en los primeros 1.5s, aumentando el Hook Retention Rate en +35%.",
            primary_kpi="Hook_Rate_3s (Retención primeros 3 segundos)",
            projected_lift_pct=35.0,
            confidence_score=0.92,
            verbal_economy=metric_b.to_dict()
        )

        # 3. Variante C: Prueba Técnica / Performance
        hook_c = "12 horas hirviendo en la cordillera chilena."
        metric_c = self.verbal_engine.analyze_scene("hook_c", hook_c, duration_sec=3.0, is_hook=True)
        var_c = ExperimentVariant(
            variant_id="var_hook_c_proof",
            name="Variante C — Prueba Extrema de Rendimiento",
            hook_type=HookType.SHOCKING_PROOF,
            hook_copy=hook_c,
            hook_visual_direction="Paisaje andino nevado con termo sobre la nieve desprendiendo vapor intenso",
            pacing_type=PacingType.CADENCE_107_BPM,
            bpm=107.7,
            cta_type=CTAType.RISK_REVERSAL,
            cta_copy="Garantía térmica de por vida con despacho a todo Chile.",
            target_audience="Outdoor, deportistas, viajeros y trabajadores en terreno",
            hypothesis="La demostración técnica extrema en entorno hostil elimina objeciones de precio y maximiza la tasa de clics (CTR).",
            primary_kpi="CTR_Landing (Clics a página de producto)",
            projected_lift_pct=28.0,
            confidence_score=0.85,
            verbal_economy=metric_c.to_dict()
        )

        # 4. Variante D: Disrupción Sensorial / ASMR
        hook_d = "Escuchá esto antes de cebar tu próximo mate."
        metric_d = self.verbal_engine.analyze_scene("hook_d", hook_d, duration_sec=3.2, is_hook=True)
        var_d = ExperimentVariant(
            variant_id="var_hook_d_sensory",
            name="Variante D — Disrupción Sensorial ASMR",
            hook_type=HookType.SENSORY_DISRUPTION,
            hook_copy=hook_d,
            hook_visual_direction="Audio foley aislado del silbido del hervidor y primer sorbo crujiente en plano cerrado",
            pacing_type=PacingType.MICRO_CUTS_FAST,
            bpm=107.7,
            cta_type=CTAType.COMMUNITY_BELONGING,
            cta_copy="El ritual que nos une. Sumate a Locos Materos.",
            target_audience="Audiencia digital TikTok y Reels que consume contenido sonoro y relajante",
            hypothesis="El corte abrupto de audio foley con texto de intriga dispara el audio-on rate (+40%) en feeds silenciados.",
            primary_kpi="Audio_On_Rate (Activación de sonido en feed)",
            projected_lift_pct=42.0,
            confidence_score=0.89,
            verbal_economy=metric_d.to_dict()
        )

        return ExperimentMatrix(
            experiment_id="exp_hook_matrix_01",
            campaign_id=campaign_id,
            created_at=now,
            updated_at=now,
            status="ACTIVE",
            active_variant_id="var_hook_a_intrigue",
            variants=[var_a, var_b, var_c, var_d],
            metadata={
                "testing_methodology": "Multi-Armed Bandit / Sequential Bayesian A/B",
                "format_target": "9:16 Vertical Video (Instagram Reels / TikTok / YouTube Shorts)",
                "music_sync_bpm": 107.7,
                "verbal_economy_verified": True
            }
        )

    def get_matrix(self) -> ExperimentMatrix:
        if self.EXPERIMENT_STORE_PATH.exists():
            try:
                with open(self.EXPERIMENT_STORE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                variants = []
                for v in data.get("variants", []):
                    variants.append(ExperimentVariant(
                        variant_id=v["variant_id"],
                        name=v["name"],
                        hook_type=HookType(v["hook_type"]),
                        hook_copy=v["hook_copy"],
                        hook_visual_direction=v["hook_visual_direction"],
                        pacing_type=PacingType(v["pacing_type"]),
                        bpm=float(v.get("bpm", 107.7)),
                        cta_type=CTAType(v["cta_type"]),
                        cta_copy=v["cta_copy"],
                        target_audience=v["target_audience"],
                        hypothesis=v["hypothesis"],
                        primary_kpi=v["primary_kpi"],
                        projected_lift_pct=float(v["projected_lift_pct"]),
                        confidence_score=float(v["confidence_score"]),
                        verbal_economy=v.get("verbal_economy", {})
                    ))
                return ExperimentMatrix(
                    experiment_id=data["experiment_id"],
                    campaign_id=data["campaign_id"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    status=data["status"],
                    active_variant_id=data["active_variant_id"],
                    variants=variants,
                    metadata=data.get("metadata", {})
                )
            except Exception as e:
                logger.error(f"Error reading experiment matrix: {e}, recreating default")
        m = self.generate_default_matrix()
        self.save_matrix(m)
        return m

    def save_matrix(self, matrix: ExperimentMatrix) -> None:
        with open(self.EXPERIMENT_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(matrix.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved experiment matrix {matrix.experiment_id} with {len(matrix.variants)} variants")

    def select_active_variant(self, variant_id: str) -> Dict[str, Any]:
        matrix = self.get_matrix()
        selected = None
        for v in matrix.variants:
            if v.variant_id == variant_id:
                selected = v
                break

        if not selected:
            return {"success": False, "error": f"Variant '{variant_id}' not found in matrix"}

        matrix.active_variant_id = variant_id
        matrix.updated_at = datetime.now(timezone.utc).isoformat()
        self.save_matrix(matrix)

        # Sincronizar con storyboard escena 1
        sb_path = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
        if sb_path.exists():
            try:
                with open(sb_path, "r", encoding="utf-8") as f:
                    sb = json.load(f)
                if sb.get("scenes") and len(sb["scenes"]) > 0:
                    sb["scenes"][0]["copy"] = selected.hook_copy
                    sb["scenes"][0]["rationale"] = f"Hook variante '{selected.name}'. {selected.hypothesis}"
                    with open(sb_path, "w", encoding="utf-8") as f:
                        json.dump(sb, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Could not sync storyboard scene 1: {e}")

        # Sincronizar memoria de marca
        mem_path = WORKSPACE_ROOT / "campaign" / "memory" / "brand-profile-memory.json"
        if mem_path.exists():
            try:
                with open(mem_path, "r", encoding="utf-8") as f:
                    mem = json.load(f)
                mem["active_creative_experiment"] = {
                    "experiment_id": matrix.experiment_id,
                    "active_variant_id": variant_id,
                    "variant_name": selected.name,
                    "primary_kpi": selected.primary_kpi,
                    "projected_lift_pct": selected.projected_lift_pct,
                    "selected_at": matrix.updated_at
                }
                with open(mem_path, "w", encoding="utf-8") as f:
                    json.dump(mem, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Could not update brand memory with active variant: {e}")

        return {
            "success": True,
            "active_variant": selected.to_dict(),
            "experiment_id": matrix.experiment_id
        }


_GLOBAL_EXPERIMENT_ENGINE = CreativeExperimentEngine()

def get_creative_experiment_engine() -> CreativeExperimentEngine:
    return _GLOBAL_EXPERIMENT_ENGINE
