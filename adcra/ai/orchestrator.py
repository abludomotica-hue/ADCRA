"""
ADCRA AI Brain — Agent Orchestrator & State Machine
Coordinates multi-step agent runs across intent parsing, planning, context loading,
tool execution, model routing, schema validation, human approval gates, and memory persistence.
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from adcra.ai.types import (
    AgentState, AgentRunResult, AIRequest, AIMessage,
    TaskType, AutonomyLevel, RiskLevel, ToolExecutionStatus
)
from adcra.ai.intent import StructuredIntent, get_intent_engine
from adcra.ai.planner import get_plan_engine, TaskGraph, PlanStep
from adcra.ai.context import get_context_engine
from adcra.ai.models import get_model_registry
from adcra.ai.router import get_model_router
from adcra.ai.gateway import get_ai_gateway
from adcra.ai.tools import get_tool_registry
from adcra.ai.cost import get_cost_ledger, get_budget_engine
from adcra.ai.memory import get_memory_engine, MemoryType, SourceEpistemology
from adcra.ai.observability import get_observability

logger = logging.getLogger("adcra.ai.orchestrator")


class AgentOrchestrator:
    def __init__(self):
        self.intent_engine = get_intent_engine()
        self.plan_engine = get_plan_engine()
        self.context_engine = get_context_engine()
        self.model_router = get_model_router()
        self.gateway = get_ai_gateway()
        self.tool_registry = get_tool_registry()
        self.cost_ledger = get_cost_ledger()
        self.budget_engine = get_budget_engine()
        self.memory_engine = get_memory_engine()
        self.observability = get_observability()

    def run_intent(
        self,
        intent_input: str,
        campaign_id: str = "camp_locos_materos_2026",
        tenant_id: str = "default_tenant",
        autonomy_level: AutonomyLevel = AutonomyLevel.AUTOPILOT,
        model_preference: Optional[str] = None
    ) -> AgentRunResult:
        """
        Executes complete intent lifecycle from user prompt through plan, tools, models, and memory.
        """
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(timezone.utc).isoformat()

        # 1. Parse intent
        structured_intent = self.intent_engine.parse_intent(intent_input)
        self.observability.record_event(
            event_type="intent.parsed",
            actor="IntentEngine",
            action="parse",
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            details={"intent": structured_intent.to_dict()}
        )

        # 2. State: PLANNING
        plan = self.plan_engine.create_plan_for_intent(structured_intent.intent_type)
        self.observability.record_event(
            event_type="plan.created",
            actor="PlanEngine",
            action="create_plan",
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            details={"plan": plan.to_dict()}
        )

        # 3. State: WAITING_FOR_CONTEXT
        context_packet = self.context_engine.assemble_context(campaign_id=campaign_id)
        prompt_context = self.context_engine.format_context_for_prompt(context_packet)

        # 4. State: READY -> RUNNING
        run_result = AgentRunResult(
            run_id=run_id,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            agent_id="Creative Director",
            task=structured_intent.intent_type,
            status=AgentState.RUNNING,
            started_at=started_at
        )

        completed_steps: List[str] = []
        step_outputs: Dict[str, Any] = {}
        total_tokens = 0
        total_cost = 0.0
        tools_used = []
        errors = []
        last_provider = "mock"
        last_model = "mock-creative-flash"

        # Iterar sobre los pasos del plan
        for step in plan.steps:
            step.status = "RUNNING"
            self.observability.record_event(
                event_type="step.started",
                actor=step.agent_role,
                action=f"execute_step:{step.step_id}",
                tenant_id=tenant_id,
                campaign_id=campaign_id,
                details={"step_id": step.step_id, "name": step.name}
            )

            # Si el paso ejecuta una herramienta determinista
            if step.tool_id:
                tools_used.append(step.tool_id)
                tool_res = self.tool_registry.execute_tool(
                    tool_id=step.tool_id,
                    arguments={"campaign_id": campaign_id},
                    context={
                        "run_id": run_id,
                        "agent_role": step.agent_role,
                        "campaign_id": campaign_id,
                        "autonomy_level": autonomy_level
                    }
                )

                if not tool_res["success"]:
                    if tool_res.get("metadata", {}).get("approval_required"):
                        # Requiere aprobación humana
                        run_result.status = AgentState.WAITING_FOR_APPROVAL
                        run_result.approvals.append(tool_res["metadata"]["approval"])
                        step.status = "WAITING_FOR_APPROVAL"
                        run_result.outputs = step_outputs
                        self.observability.record_run(run_result.to_dict())
                        return run_result
                    else:
                        err_msg = tool_res.get("error", {}).get("message", "Tool failed")
                        errors.append(f"Step {step.step_id} tool error: {err_msg}")
                        step.status = "FAILED"
                        break

                step_outputs[step.output_key] = tool_res["data"]
                step.status = "COMPLETED"
                completed_steps.append(step.step_id)

            else:
                # Si el paso invoca un modelo de IA para razonamiento o síntesis
                req = AIRequest(
                    request_id=f"req_{uuid.uuid4().hex[:8]}",
                    tenant_id=tenant_id,
                    campaign_id=campaign_id,
                    agent_id=step.agent_role,
                    task_type=step.task_type,
                    model_preference=model_preference,
                    messages=[
                        AIMessage(role="system", content=f"Eres {step.agent_role} en ADCRA COS.\n{prompt_context}"),
                        AIMessage(role="user", content=f"Tarea: {step.description}\nIntención del usuario: {structured_intent.raw_prompt}")
                    ]
                )

                # Enrutar modelo
                provider_id, model_id, fallbacks = self.model_router.route(req)
                last_provider = provider_id
                last_model = model_id

                # Verificar presupuesto
                budget_status, budget_msg = self.budget_engine.check_budget(campaign_id, estimated_cost=0.01, tenant_id=tenant_id)
                if budget_status.value == "BLOCKED":
                    errors.append(f"Budget blocked: {budget_msg}")
                    run_result.status = AgentState.FAILED
                    break

                # Ejecutar a través de AIProviderGateway con fallback
                try:
                    fallback_pids = [f[0] for f in fallbacks]
                    response = self.gateway.execute_with_fallback(req, provider_id, fallback_pids)
                    
                    # Registrar costos y tokens
                    u = response.usage
                    in_tok = u.get("input_tokens", 0)
                    out_tok = u.get("output_tokens", 0)
                    cost = u.get("estimated_cost_usd", 0.0)
                    total_tokens += (in_tok + out_tok)
                    total_cost += cost

                    self.cost_ledger.record_usage(
                        tenant_id=tenant_id,
                        campaign_id=campaign_id,
                        agent_id=step.agent_role,
                        task=step.task_type.value if hasattr(step.task_type, "value") else str(step.task_type),
                        provider_id=response.provider_id,
                        model_id=response.model_id,
                        input_tokens=in_tok,
                        output_tokens=out_tok,
                        cached_tokens=u.get("cached_tokens", 0),
                        cost_usd=cost,
                        latency_ms=response.latency_ms
                    )

                    step_outputs[step.output_key] = response.structured_data or response.content
                    step.status = "COMPLETED"
                    completed_steps.append(step.step_id)

                except Exception as ex:
                    logger.error(f"Error in step {step.step_id}: {ex}")
                    errors.append(f"Step {step.step_id} execution failed: {str(ex)}")
                    step.status = "FAILED"
                    break

        # 5. Determinar estado final
        run_result.completed_at = datetime.now(timezone.utc).isoformat()
        run_result.tools_used = tools_used
        run_result.total_tokens = total_tokens
        run_result.total_cost = round(total_cost, 6)
        run_result.model_id = last_model
        run_result.provider_id = last_provider
        run_result.outputs = step_outputs
        run_result.errors = errors

        if errors:
            run_result.status = AgentState.FAILED
        else:
            run_result.status = AgentState.COMPLETED
            # Guardar aprendizaje en Episodic Memory
            try:
                self.memory_engine.write_entry(
                    tenant_id=tenant_id,
                    scope="campaign",
                    memory_type=MemoryType.DECISION,
                    source=SourceEpistemology.AI_RECOMMENDATION,
                    content={
                        "intent": structured_intent.raw_prompt,
                        "plan_id": plan.plan_id,
                        "steps_completed": completed_steps,
                        "outputs_summary": list(step_outputs.keys())
                    },
                    confidence=0.92,
                    campaign_id=campaign_id
                )
            except Exception as me:
                logger.warning(f"Could not persist memory for run: {me}")

        self.observability.record_run(run_result.to_dict())
        self.observability.record_event(
            event_type="run.finished",
            actor="AgentOrchestrator",
            action="finish",
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            details={"status": run_result.status.value, "steps": len(completed_steps), "cost": total_cost}
        )

        return run_result


_GLOBAL_ORCHESTRATOR = AgentOrchestrator()

def get_agent_orchestrator() -> AgentOrchestrator:
    return _GLOBAL_ORCHESTRATOR
