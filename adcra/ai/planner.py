"""
ADCRA AI Brain — Plan Engine & Task Graph
Deconstructs high-level user intents into ordered, dependency-resolved task execution graphs.
Supports parallel branch resolution and specialized agent handoffs.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from adcra.ai.types import TaskType

logger = logging.getLogger("adcra.ai.planner")


@dataclass
class PlanStep:
    step_id: str
    name: str
    task_type: TaskType
    agent_role: str
    description: str
    depends_on: List[str] = field(default_factory=list)
    tool_id: Optional[str] = None
    output_key: str = "result"
    required_capabilities: List[str] = field(default_factory=list)
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "task_type": self.task_type.value if hasattr(self.task_type, "value") else str(self.task_type),
            "agent_role": self.agent_role,
            "description": self.description,
            "depends_on": self.depends_on,
            "tool_id": self.tool_id,
            "output_key": self.output_key,
            "status": self.status
        }


@dataclass
class TaskGraph:
    plan_id: str
    intent: str
    steps: List[PlanStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "intent": self.intent,
            "steps": [s.to_dict() for s in self.steps],
            "total_steps": len(self.steps)
        }

    def get_ready_steps(self, completed_steps: List[str]) -> List[PlanStep]:
        """Devuelve pasos cuyas dependencias ya han sido completadas."""
        ready = []
        for s in self.steps:
            if s.step_id in completed_steps or s.status == "COMPLETED":
                continue
            if all(dep in completed_steps for dep in s.depends_on):
                ready.append(s)
        return ready


class PlanEngine:
    def create_plan_for_intent(self, intent_type: str, context: Optional[Dict[str, Any]] = None) -> TaskGraph:
        ctx = context or {}
        intent_norm = intent_type.strip().lower()

        if "concept" in intent_norm or "territor" in intent_norm or "campaign" in intent_norm:
            steps = [
                PlanStep(
                    step_id="step_load_brand_dna",
                    name="Cargar Identidad de Marca y Memoria",
                    task_type=TaskType.CAMPAIGN_STRATEGY,
                    agent_role="Strategist",
                    description="Recupera la memoria histórica y Brand DNA de 6 dimensiones",
                    output_key="brand_dna"
                ),
                PlanStep(
                    step_id="step_audio_rhythm",
                    name="Perfilado Rítmico Musical",
                    task_type=TaskType.AUDIO_ANALYZE,
                    agent_role="Audio Analyst",
                    description="Analiza tempo musical, BPM y curvas de energía",
                    tool_id="audio_analysis",
                    output_key="audio_profile"
                ),
                PlanStep(
                    step_id="step_generate_territories",
                    name="Generación de Territorios Creativos",
                    task_type=TaskType.CREATIVE_CONCEPT,
                    agent_role="Creative Director",
                    description="Desarrolla 3 territorios creativos basados en Brand DNA y audio",
                    depends_on=["step_load_brand_dna", "step_audio_rhythm"],
                    output_key="territories"
                ),
                PlanStep(
                    step_id="step_evaluate_concept",
                    name="Evaluación de Coherencia de Marca",
                    task_type=TaskType.CREATIVE_QC,
                    agent_role="QC Director",
                    description="Evalúa adecuación al tono, audiencia y claims de la marca",
                    depends_on=["step_generate_territories"],
                    output_key="evaluation"
                )
            ]
            return TaskGraph(plan_id="plan_creative_concept", intent=intent_type, steps=steps)

        elif "storyboard" in intent_norm:
            steps = [
                PlanStep(
                    step_id="step_read_concept",
                    name="Cargar Concepto y Copy",
                    task_type=TaskType.CAMPAIGN_STRATEGY,
                    agent_role="Creative Director",
                    description="Carga el concepto seleccionado y claims aprobados",
                    output_key="concept"
                ),
                PlanStep(
                    step_id="step_generate_storyboard",
                    name="Construcción de Storyboard Visual",
                    task_type=TaskType.STORYBOARD_GENERATE,
                    agent_role="Storyboard Director",
                    description="Diseña desglose escena por escena alineado al ritmo",
                    depends_on=["step_read_concept"],
                    output_key="storyboard"
                )
            ]
            return TaskGraph(plan_id="plan_storyboard", intent=intent_type, steps=steps)

        elif "produce" in intent_norm or "video" in intent_norm:
            steps = [
                PlanStep(
                    step_id="step_motion_graphics",
                    name="Renderizado de Motion Graphics",
                    task_type=TaskType.TECHNICAL_QC,
                    agent_role="Motion Designer",
                    description="Genera secuencias gráficas de texto y logos",
                    tool_id="hyperframes_render",
                    output_key="motion_assets"
                ),
                PlanStep(
                    step_id="step_video_render",
                    name="Composición y Render Remotion",
                    task_type=TaskType.TECHNICAL_QC,
                    agent_role="Production Director",
                    description="Ensambla línea de tiempo y sincroniza audio",
                    tool_id="remotion_render",
                    depends_on=["step_motion_graphics"],
                    output_key="video_master"
                ),
                PlanStep(
                    step_id="step_qc_certify",
                    name="Certificación de Calidad y Loudness",
                    task_type=TaskType.TECHNICAL_QC,
                    agent_role="QC Director",
                    description="Verifica niveles de audio EBU R128 y márgenes de seguridad",
                    tool_id="qc_evaluator",
                    depends_on=["step_video_render"],
                    output_key="qc_report"
                )
            ]
            return TaskGraph(plan_id="plan_production", intent=intent_type, steps=steps)

        else:
            # Plan genérico de 1 paso
            steps = [
                PlanStep(
                    step_id="step_single_action",
                    name=f"Ejecutar {intent_type}",
                    task_type=TaskType.CUSTOM,
                    agent_role="Creative Director",
                    description="Ejecución directa de intención personalizada",
                    output_key="result"
                )
            ]
            return TaskGraph(plan_id="plan_generic", intent=intent_type, steps=steps)


_GLOBAL_PLANNER = PlanEngine()

def get_plan_engine() -> PlanEngine:
    return _GLOBAL_PLANNER
