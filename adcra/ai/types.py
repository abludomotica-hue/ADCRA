"""
ADCRA AI Brain & Agentic Infrastructure Layer — Core Domain Types & Contracts
Defines normalized request/response contracts, capability enums, epistemic ratings,
and state machine representations.
"""

import enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


class TaskType(str, enum.Enum):
    CAMPAIGN_STRATEGY = "campaign.strategy"
    CREATIVE_CONCEPT = "creative.concept"
    COPY_GENERATE = "copy.generate"
    COPY_REVIEW = "copy.review"
    AUDIO_ANALYZE = "audio.analyze"
    VIDEO_ANALYZE = "video.analyze"
    IMAGE_ANALYZE = "image.analyze"
    STORYBOARD_GENERATE = "storyboard.generate"
    CREATIVE_QC = "creative.qc"
    TECHNICAL_QC = "technical.qc"
    MARKET_RESEARCH = "market.research"
    TREND_RESEARCH = "trend.research"
    CAMPAIGN_POSTMORTEM = "campaign.postmortem"
    CUSTOM = "custom"


class ModelCapability(str, enum.Enum):
    REASONING = "reasoning"
    VISION = "vision"
    AUDIO_INPUT = "audioInput"
    AUDIO_OUTPUT = "audioOutput"
    AUDIO = "audioInput"
    LONG_CONTEXT = "longContext"
    IMAGE_GENERATION = "imageGeneration"
    VIDEO_GENERATION = "videoGeneration"
    TOOL_CALLING = "toolCalling"
    STRUCTURED_OUTPUT = "structuredOutput"
    STREAMING = "streaming"
    WEB_SEARCH = "webSearch"


class RoutingMode(str, enum.Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    PREFERRED = "PREFERRED"
    COST_OPTIMIZED = "COST_OPTIMIZED"
    QUALITY_FIRST = "QUALITY_FIRST"
    BALANCED = "BALANCED"


class AgentState(str, enum.Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    WAITING_FOR_CONTEXT = "WAITING_FOR_CONTEXT"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING_FOR_TOOL = "WAITING_FOR_TOOL"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    VALIDATING = "VALIDATING"
    ITERATING = "ITERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class MemoryType(str, enum.Enum):
    FACT = "FACT"
    OBSERVATION = "OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"
    LEARNING = "LEARNING"
    PREFERENCE = "PREFERENCE"
    REJECTION = "REJECTION"
    DECISION = "DECISION"


class SourceEpistemology(str, enum.Enum):
    CLIENT_INPUT = "CLIENT_INPUT"
    CONFIRMED_FACT = "CONFIRMED_FACT"
    AI_INFERENCE = "AI_INFERENCE"
    AI_RECOMMENDATION = "AI_RECOMMENDATION"
    RESEARCH = "RESEARCH"
    UNKNOWN = "UNKNOWN"


class PermissionLevel(str, enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    DELETE = "DELETE"
    PUBLISH = "PUBLISH"
    EXTERNAL = "EXTERNAL"
    PAID = "PAID"
    DESTRUCTIVE = "DESTRUCTIVE"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AutonomyLevel(str, enum.Enum):
    ASSIST = "ASSIST"
    AUTOPILOT = "AUTOPILOT"
    AUTONOMOUS = "AUTONOMOUS"



class ProviderStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"              # Adapter exists in registry
    NOT_CONFIGURED = "NOT_CONFIGURED"    # No API credentials configured
    CONFIGURED = "CONFIGURED"            # Credentials present/saved
    CONNECTING = "CONNECTING"            # Handshake in progress
    CONNECTED = "CONNECTED"              # Authentication successful
    HEALTHY = "HEALTHY"                  # Health check / probe passed
    DEGRADED = "DEGRADED"                # Responding slowly or intermittent errors
    UNAVAILABLE = "UNAVAILABLE"          # Endpoint unreachable or circuit tripped
    DISABLED = "DISABLED"                # Disabled by configuration
    ERROR = "ERROR"                      # Authentication failed, network error, or invalid setup


class CostConfidence(str, enum.Enum):
    KNOWN_COST = "KNOWN_COST"          # Cost delivered from provider usage/invoice
    ESTIMATED_COST = "ESTIMATED_COST"  # Calculated via published token pricing
    UNKNOWN_COST = "UNKNOWN_COST"      # No pricing available; never invent values

class BudgetStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    LIMIT_REACHED = "LIMIT_REACHED"
    BLOCKED = "BLOCKED"


class ToolExecutionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_UNAVAILABLE = "TOOL_UNAVAILABLE"
    INVALID_INPUT = "INVALID_INPUT"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    TIMEOUT = "TIMEOUT"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    RATE_LIMIT = "RATE_LIMIT"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    POLICY_BLOCKED = "POLICY_BLOCKED"


class AgentExecutionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_ERROR = "MODEL_ERROR"
    CONTEXT_LIMIT = "CONTEXT_LIMIT"
    TOOL_FAILURE = "TOOL_FAILURE"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    POLICY_BLOCKED = "POLICY_BLOCKED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    MAX_ITERATIONS = "MAX_ITERATIONS"


@dataclass
class AIMessage:
    role: str  # 'system', 'user', 'assistant', 'tool'
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"role": self.role, "content": self.content}
        if self.name:
            d["name"] = self.name
        if self.tool_calls:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d


@dataclass
class AIToolDefinition:
    tool_id: str
    name: str
    description: str
    category: str
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    capabilities: List[str] = field(default_factory=list)
    permissions: List[PermissionLevel] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    cost: float = 0.0
    timeout_sec: int = 30
    provider: str = "internal"
    availability: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "capabilities": self.capabilities,
            "permissions": [p.value if isinstance(p, PermissionLevel) else str(p) for p in self.permissions],
            "risk_level": self.risk_level.value if isinstance(self.risk_level, RiskLevel) else str(self.risk_level),
            "cost": self.cost,
            "timeout_sec": self.timeout_sec,
            "provider": self.provider,
            "availability": self.availability
        }


@dataclass
class AIRequest:
    request_id: str
    tenant_id: str = "default_tenant"
    workspace_id: str = "default_workspace"
    campaign_id: Optional[str] = None
    agent_id: Optional[str] = None
    task_type: TaskType = TaskType.CUSTOM
    model_preference: Optional[str] = None
    messages: List[AIMessage] = field(default_factory=list)
    context: Optional[Dict[str, Any]] = None
    tools: Optional[List[AIToolDefinition]] = None
    tool_policy: Optional[str] = "auto"
    output_schema: Optional[Dict[str, Any]] = None
    temperature: float = 0.7
    max_output_tokens: int = 4096
    timeout_ms: int = 30000
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "campaign_id": self.campaign_id,
            "agent_id": self.agent_id,
            "task_type": self.task_type.value if isinstance(self.task_type, TaskType) else str(self.task_type),
            "model_preference": self.model_preference,
            "messages": [m.to_dict() for m in self.messages],
            "context": self.context,
            "tools": [t.to_dict() for t in self.tools] if self.tools else None,
            "output_schema": self.output_schema,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "timeout_ms": self.timeout_ms,
            "metadata": self.metadata
        }


@dataclass
class AIResponse:
    request_id: str
    provider_id: str
    model_id: str
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    structured_data: Optional[Dict[str, Any]] = None
    usage: Dict[str, Any] = field(default_factory=lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "cached_tokens": 0,
        "estimated_cost_usd": 0.0
    })
    latency_ms: float = 0.0
    finish_reason: str = "stop"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "structured_data": self.structured_data,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
            "finish_reason": self.finish_reason
        }


@dataclass
class AIStreamEvent:
    event_type: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        }


@dataclass
class AgentRunResult:
    run_id: str
    tenant_id: str
    campaign_id: str
    agent_id: str
    task: str
    status: AgentState
    started_at: str
    completed_at: Optional[str] = None
    model_id: Optional[str] = None
    provider_id: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    total_tokens: int = 0
    total_cost: float = 0.0
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    iterations: int = 1
    approvals: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "tenant_id": self.tenant_id,
            "campaign_id": self.campaign_id,
            "agent_id": self.agent_id,
            "task": self.task,
            "status": self.status.value if isinstance(self.status, AgentState) else str(self.status),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "model_id": self.model_id,
            "provider_id": self.provider_id,
            "tools_used": self.tools_used,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "outputs": self.outputs,
            "errors": self.errors,
            "iterations": self.iterations,
            "approvals": self.approvals
        }


@dataclass
class CostEstimate:
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    currency: str = "USD"
    confidence: CostConfidence = CostConfidence.ESTIMATED_COST


class AIError(Exception):
    """Base exception for ADCRA AI system."""
    pass


class AIProviderError(AIError, RuntimeError):
    """Raised when an AI provider fails or is unconfigured."""
    pass


class AIAuthenticationError(AIProviderError, PermissionError):
    """Raised when provider credentials are missing or invalid."""
    pass
