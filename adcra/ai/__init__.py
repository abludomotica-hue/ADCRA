"""
ADCRA AI Brain & Agentic Infrastructure Layer
Initializes default providers, models, and orchestration components.
"""

from adcra.ai.types import (
    TaskType, ModelCapability, RoutingMode, AgentState,
    MemoryType, SourceEpistemology, PermissionLevel, RiskLevel,
    AutonomyLevel, BudgetStatus, AIMessage, AIToolDefinition,
    AIRequest, AIResponse, AgentRunResult, CostEstimate
)
from adcra.ai.gateway import get_ai_gateway, AIProviderGateway
from adcra.ai.adapters.mock_adapter import MockAIProvider
from adcra.ai.adapters.openai_adapter import OpenAIProvider
from adcra.ai.adapters.gemini_adapter import GeminiProvider
from adcra.ai.adapters.anthropic_adapter import AnthropicProvider
from adcra.ai.adapters.openrouter_adapter import OpenRouterProvider
from adcra.ai.models import get_model_registry
from adcra.ai.router import get_model_router
from adcra.ai.cost import get_cost_ledger, get_budget_engine
from adcra.ai.tools import get_tool_registry
from adcra.ai.permissions import get_permission_engine
from adcra.ai.approval import get_approval_engine
from adcra.ai.planner import get_plan_engine
from adcra.ai.context import get_context_engine
from adcra.ai.memory import get_memory_engine
from adcra.ai.intent import get_intent_engine
from adcra.ai.observability import get_observability
from adcra.ai.profiles import get_profile_manager
from adcra.ai.orchestrator import get_agent_orchestrator
from adcra.ai.verbal_economy import get_verbal_economy_engine, VerbalEconomyEngine
from adcra.ai.hardware import get_hardware_probe, HardwareEnvironmentProbe
from adcra.ai.experiments import get_creative_experiment_engine, CreativeExperimentEngine

# Auto-registrar proveedores en el gateway global
_gw = get_ai_gateway()
if not _gw.has_adapter("mock"):
    _gw.register_adapter(MockAIProvider())
if not _gw.has_adapter("openai"):
    _gw.register_adapter(OpenAIProvider())
if not _gw.has_adapter("gemini"):
    _gw.register_adapter(GeminiProvider())
if not _gw.has_adapter("anthropic"):
    _gw.register_adapter(AnthropicProvider())
if not _gw.has_adapter("openrouter"):
    _gw.register_adapter(OpenRouterProvider())

_gw.set_default_provider("mock")

__all__ = [
    "TaskType", "ModelCapability", "RoutingMode", "AgentState",
    "MemoryType", "SourceEpistemology", "PermissionLevel", "RiskLevel",
    "AutonomyLevel", "BudgetStatus", "AIMessage", "AIToolDefinition",
    "AIRequest", "AIResponse", "AgentRunResult", "CostEstimate",
    "get_ai_gateway", "get_model_registry", "get_model_router",
    "get_cost_ledger", "get_budget_engine", "get_tool_registry",
    "get_permission_engine", "get_approval_engine", "get_plan_engine",
    "get_context_engine", "get_memory_engine", "get_intent_engine",
    "get_observability", "get_profile_manager", "get_agent_orchestrator",
    "get_verbal_economy_engine", "VerbalEconomyEngine",
    "get_hardware_probe", "HardwareEnvironmentProbe",
    "get_creative_experiment_engine", "CreativeExperimentEngine"
]
