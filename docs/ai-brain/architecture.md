# ADCRA — AI Brain & Agentic Infrastructure Layer Architecture

## 1. Executive Summary

ADCRA (**Autonomous Digital Campaign & Creative Production System**) implements a decoupled, provider-agnostic, multi-tenant, and observable **AI Brain & Agentic Infrastructure Layer** as the central nervous system beneath all creative and production workflows.

```
                    ADCRA
                      │
                      ▼
          ┌───────────────────────┐
          │ CREATIVE EXPERIENCE   │
          │ Campaign Studio       │
          │ Creative Intelligence │
          │ Asset Lab / Copy Lab  │
          │ Storyboard / Delivery │
          └───────────┬───────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  AI BRAIN & AGENTIC LAYER   │
        │                             │
        │ Intent Engine               │
        │ Agent Orchestrator          │
        │ Model Router & Fallback     │
        │ Provider Gateway            │
        │ Tool Registry & Permissions │
        │ Context & Memory Engines    │
        │ Cost Intelligence & Budget  │
        │ Observability & Audit Log   │
        └─────────────┬───────────────┘
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
       AI MODELS    TOOLS        MEMORY
      OpenAI/Gemini Remotion/HF  Campaign/Client
      Anthropic/Mock DaVinci/FFmpeg Creative/Brand
```

---

## 2. Decoupled Processing Pipeline

No front-end component or creative tool directly invokes OpenAI, Google Gemini, Anthropic, or external providers.
All requests travel through the verified pipeline:

```
ADCRA AI CORE → AI PROVIDER GATEWAY → PROVIDER ADAPTER → MODEL
```

1. **Intent Engine (`adcra/ai/intent.py`)**: Converts natural language instructions or one-click action triggers into structured, validated campaign intents (`StructuredIntent`).
2. **Agent Orchestrator (`adcra/ai/orchestrator.py`)**: Manages the multi-step lifecycle across 12 discrete states (`IDLE`, `PLANNING`, `WAITING_FOR_CONTEXT`, `READY`, `RUNNING`, `WAITING_FOR_TOOL`, `WAITING_FOR_APPROVAL`, `VALIDATING`, `ITERATING`, `COMPLETED`, `FAILED`, `CANCELLED`).
3. **Plan Engine (`adcra/ai/planner.py`)**: Builds dependency graphs (`TaskGraph`) resolving parallel and sequential steps.
4. **Context Engine (`adcra/ai/context.py`)**: Assembles real-time context respecting context token budgets and preserving source epistemology (`CLIENT_INPUT`, `CONFIRMED_FACT`, `AI_INFERENCE`, `AI_RECOMMENDATION`, `RESEARCH`, `UNKNOWN`).
5. **Model Router (`adcra/ai/router.py`)**: Evaluates task requirements against registered model capabilities, applying routing modes (`AUTO`, `COST_OPTIMIZED`, `QUALITY_FIRST`, `BALANCED`) and automated fallback chains.
6. **AI Provider Gateway (`adcra/ai/gateway.py`)**: Normalizes request/response payloads, validates output schemas (`jsonschema`), and handles retries and timeouts.
7. **Tool Registry & Permissions (`adcra/ai/tools.py`, `adcra/ai/permissions.py`)**: Catalogs 24 tools across 8 categories with granular permissions (`READ`, `WRITE`, `EXECUTE`, `DELETE`, `PUBLISH`, `EXTERNAL`, `PAID`, `DESTRUCTIVE`).
8. **Approval Engine (`adcra/ai/approval.py`)**: Traps high-risk actions into `WAITING_FOR_APPROVAL` based on autonomy levels (`ASSIST`, `AUTOPILOT`, `AUTONOMOUS`).
9. **Cost Ledger & Budget (`adcra/ai/cost.py`)**: Tracks tokens and financial cost per request, task, agent, campaign, and tenant.
10. **Memory Engine (`adcra/ai/memory.py`)**: Manages Client Memory, Campaign Memory, and Creative Genome across 7 memory types with multi-tenant isolation.
