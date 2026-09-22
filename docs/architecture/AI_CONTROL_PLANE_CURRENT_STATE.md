# ADCRA — AI Control Plane: Current State Audit (Phase 0)
**Version:** 1.0.0-audit  
**Date:** September 21, 2026  
**System:** ADCRA (Autonomous Digital Campaign & Creative Production System)  
**Author:** Principal Software Architect & AI Systems Architect  

---

## 1. Executive Summary

This document fulfills **Phase 0 (Mandatory Audit)** of the **ADCRA AI Intelligence Control Plane v2.0** initiative.
The existing ADCRA platform operates as a hybrid creative system combining deterministic audiovisual engines (FFmpeg, Remotion, DaVinci Resolve) with an agentic substrate (`adcra/ai/`).
The system has a baseline test suite of **317 tests passing with 0 failures, 0 errors, and 0 regressions**.

The purpose of this audit is to systematically map:
- The current architecture and data flow.
- Existing AI components, dependencies, interfaces, and endpoints.
- Tight couplings, technical debt, and duplication.
- The concrete migration path towards a true **Capability-Oriented AI Intelligence Control Plane**.

---

## 2. Current Architecture Map

Currently, ADCRA executes requests through a semi-decoupled hierarchy:

```
[ USER / UI / COMMAND PALETTE ]
               │
               ▼
       [ INTENT ENGINE ]  (adcra/ai/intent.py)
               │ (StructuredIntent)
               ▼
     [ AGENT ORCHESTRATOR ]  (adcra/ai/orchestrator.py)
      ├── [ PLANNER ]          (TaskGraph / PlanStep)
      ├── [ CONTEXT ENGINE ]   (Epistemic Context assembly)
      ├── [ MODEL ROUTER ]     (adcra/ai/router.py)
      │          │
      │          ▼
      │   [ PROVIDER GATEWAY ] (adcra/ai/gateway.py)
      │          │ (Adapter selection)
      │          ▼
      │   [ PROVIDER ADAPTER ] (OpenAI / Gemini / Claude / OpenRouter / Mock)
      │          │
      │          ▼
      │   [ PHYSICAL LLM API ]
      │
      ├── [ TOOL REGISTRY ]    (adcra/ai/tools.py)
      │          │ (RBAC via permissions.py)
      │          ▼
      │   [ CREATIVE & AV TOOLS ] (analyze_audio, build_storyboard, etc.)
      │
      ├── [ COST LEDGER ]      (adcra/ai/cost.py)
      ├── [ OBSERVABILITY ]    (adcra/ai/observability.py)
      └── [ MEMORY ENGINE ]    (adcra/ai/memory.py)
```

### Architectural Assessment:
- **Strong Foundations:** Normalized data types (`AIRequest`, `AIResponse`), cost ledgers, RBAC permissions, and epistemic memory tagging exist.
- **The Core Architectural Gap:** Currently, routing is tied to `TaskType` $\rightarrow$ `ModelCapability` enum flags (`reasoning`, `vision`, `toolCalling`). Models are selected based on static flags rather than dynamic, verifiable **Capability Requirements** (e.g. `video_understanding` with specific latency/cost bounds).
- **Vendor Independence Gap:** While provider adapters exist, Brain profiles still hold fields like `preferred_provider` and `preferred_model` in `config/ai-brain-profiles.json`, violating pure provider-agnosticism.

---

## 3. Existing Modules Inventory (`adcra/ai/`)

| Module | Primary Class / Functions | Responsibility | State & Quality |
|---|---|---|---|
| `adcra/ai/types.py` | `TaskType`, `ModelCapability`, `AIRequest`, `AIResponse`, `AgentState`, etc. | Canonical domain dataclasses and enums | Robust. 100% typed. |
| `adcra/ai/gateway.py` | `AIProviderGateway`, `AIProviderAdapter` (ABC) | Unified provider gateway, retry, fallback, validation | Production-ready. |
| `adcra/ai/adapters/` | `MockAdapter`, `OpenAIAdapter`, `GeminiAdapter`, `AnthropicAdapter`, `OpenRouterAdapter` | Vendor SDK abstractions and mock simulation | Well-isolated. Mock is deterministic. |
| `adcra/ai/models.py` | `ModelRegistry` | Model metadata, context windows, token pricing | JSON-backed (`ai-model-registry.json`). |
| `adcra/ai/router.py` | `ModelRouter` | Matrix matching, cost/quality scoring, fallback chain | Functional, but relies on static capabilities. |
| `adcra/ai/profiles.py` | `ProfileManager` | Loads personas (`creative_director`, `strategist`, etc.) | Minimalist wrapper around JSON. Needs capability contract. |
| `adcra/ai/orchestrator.py`| `AgentOrchestrator` | Multi-step agent state machine | Orchestrates 12 states. Comprehensive. |
| `adcra/ai/planner.py` | `PlanEngine`, `TaskGraph`, `PlanStep` | Breaks intents into dependency-ordered DAGs | Functional. Deterministic heuristics. |
| `adcra/ai/context.py` | `ContextEngine` | Epistemic context assembly with token budgets | Implements context window slicing. |
| `adcra/ai/memory.py` | `MemoryEngine`, `MemoryWriteValidator` | Multi-tenant episodic memory store | Has `tenant_id` validation and epistemic rules. |
| `adcra/ai/cost.py` | `AICostLedger`, `BudgetEngine` | Token usage, cost recording, threshold alerts | Atomic JSON logging, alerts on over-budget. |
| `adcra/ai/tools.py` | `AIToolRegistry` | Tool definitions, schemas, risk levels | 9 registered tools with JSON schemas. |
| `adcra/ai/permissions.py` | `PermissionEngine` | RBAC tool authorization matrix | Enforces role-to-permission mapping. |
| `adcra/ai/approval.py` | `ApprovalEngine` | Traps high-risk tasks in `WAITING_FOR_APPROVAL` | Human-in-the-loop state governance. |
| `adcra/ai/intent.py` | `IntentEngine` | Natural language prompt to `StructuredIntent` | Heuristic parser with fallback. |
| `adcra/ai/observability.py`| `AIObservability` | Event distribution, audit trails, traces | In-memory and JSON event logs. |
| `adcra/ai/verbal_economy.py`| `VerbalEconomyEngine` | Token ceilings, prompt compression, anti-bloat | High impact. Prevents context inflation. |
| `adcra/ai/hardware.py` | `HardwareProbe` | Probes host CPU, RAM, and GPU devices | Tests GM107/Pascal/RTX/Metal. |
| `adcra/ai/experiments.py` | `CreativeExperimentEngine` | Multi-variant A/B matrix generator | Generates hook/visual/audio variants. |

---

## 4. Dependencies & System Interconnects

### Internal Dependencies:
- `dashboard_server.py` imports `adcra.ai` as a first-class citizen.
- `web/intake.js` calls `/api/ai/*` via standard asynchronous `fetch`.
- `adcra_cli.py` interfaces with tests and system phases.

### External Libraries (Python):
- `jsonschema`: Strict schema enforcement.
- `psutil`: Hardware and memory telemetry.
- `Pillow`, `numpy`, `scipy`, `soundfile`: Audio and signal processing.
- `requests`: Outbound HTTP API communication in provider adapters.

---

## 5. API Endpoints Map (AI Subsystem)

The Mission Control server (`dashboard_server.py`) exposes the following endpoints:

| Endpoint | Method | Handler | Purpose |
|---|---|---|---|
| `/api/ai/health` | `GET` | `handle_api_ai_health()` | Overall AI subsystem connectivity and health |
| `/api/ai/providers` | `GET` | `handle_api_ai_providers()` | Registered providers, statuses, and model counts |
| `/api/ai/providers/test` | `POST` | `handle_api_ai_providers_test()` | Live ping / health probe of configured providers |
| `/api/ai/models` | `GET` | `handle_api_ai_models()` | Catalog of available models, capabilities, and pricing |
| `/api/ai/brains` | `GET` | `handle_api_ai_brains()` | Configured Brain Profiles (personas & policies) |
| `/api/ai/tools` | `GET` | `handle_api_ai_tools()` | Registered agent tools and schema definitions |
| `/api/ai/intent/execute` | `POST` | `handle_api_ai_intent_execute()` | Execute natural language intent via orchestrator |
| `/api/ai/approvals` | `GET` | `handle_api_ai_approvals()` | List pending approval requests |
| `/api/ai/approvals/{id}` | `POST` | `handle_api_ai_approvals()` | Approve or reject a gated action |
| `/api/ai/runs` | `GET` | `handle_api_ai_runs()` | List recent agent runs |
| `/api/ai/runs/{id}` | `GET` | `handle_api_ai_runs()` | Detailed run status, execution steps, and logs |
| `/api/ai/usage` | `GET` | `handle_api_ai_usage()` | Aggregated cost and token consumption |
| `/api/ai/hardware/probe` | `GET` | `handle_api_hardware_probe()` | Host CPU, RAM, and GPU detection |
| `/api/ai/verbal-economy/analyze` | `POST` | `handle_api_verbal_economy_analyze()` | Token compression analysis |
| `/api/ai/verbal-economy/current` | `GET` | `handle_api_verbal_economy_current()` | Real-time verbal economy settings |
| `/api/ai/experiments` | `GET` | `handle_api_ai_experiments()` | List creative A/B experiments |
| `/api/ai/experiments/generate` | `POST` | `handle_api_ai_experiments_generate()` | Generate creative experiment matrix |
| `/api/ai/experiments/select-variant` | `POST` | `handle_api_ai_experiments_select_variant()` | Select winning variant |

---

## 6. Current Test Baseline

A full execution of the test suite reveals:
```
Ran 317 tests in 24.352s
OK (0 failures, 0 errors, 0 regressions)
```
- **Foundational Tests:** 159 tests covering phases 1–22.
- **UI & Studio Tests:** 111 tests covering phases UI-01 to UI-22.
- **AI Brain Tests:** 47 tests covering routing, adapters, memory, permissions, orchestrator, verbal economy, hardware, and experiments.

---

## 7. Couplings, Technical Debt & Migration Risks

### Risk 1: Brain Profiles Tied to Model Preferences
- *Problem:* `config/ai-brain-profiles.json` contains `preferred_provider` and `preferred_model`.
- *Architecture Solution:* Replace model-specific preferences with **`required_capabilities`**, **`preferred_capabilities`**, and **`model_policy`**. Models must be chosen dynamically by the Control Plane.

### Risk 2: Coarse-Grained Capabilities
- *Problem:* `ModelCapability` enum has only 10 high-level tags (`reasoning`, `vision`, `toolCalling`, etc.).
- *Architecture Solution:* Implement the granular **Capability Domain** (`CapabilityRegistry`, `CapabilityRequirement`, `CapabilityDiscoveryEngine`, and `CapabilityProbe`).

### Risk 3: Lack of Provider Circuit Breakers & Dynamic Probes
- *Problem:* If an API provider experiences transient 500/503 errors or rate limits, the system retries without cooldown tracking or circuit breaker states (`OPEN`, `CLOSED`, `HALF_OPEN`).
- *Architecture Solution:* Introduce `ProviderHealthMonitor` with stateful circuit breakers and probe caching.

### Risk 4: Missing Inter-Brain Collaboration (Brain Federation)
- *Problem:* Agents currently run in isolation or via a single orchestrator pipeline. There is no structured handoff protocol (`BrainHandoff`) between specialized brains (e.g. Strategic Brain $\rightarrow$ Creative Brain $\rightarrow$ Storyboard Brain).
- *Architecture Solution:* Implement `BrainFederationEngine` and `BrainHandoff` contract.

---

## 8. Strategic Migration Plan (Phased Execution)

1. **Step 1 — Foundation & Contracts (Zero Breaking Changes):**
   - Introduce `adcra/ai/capabilities.py`: `Capability`, `CapabilityRequirement`, `CapabilityReport`, `CapabilityMatrix`.
   - Create `config/ai-capabilities.json`.
   - Create `CapabilityRegistry`.
2. **Step 2 — Probing & Discovery:**
   - Create `CapabilityDiscoveryEngine` and lightweight `CapabilityProbe`s with TTL caching.
3. **Step 3 — Brain Profiles & Federation:**
   - Expand `BrainProfile` contracts in `adcra/ai/brains.py` with 14 specialized cognitive profiles.
   - Implement `BrainFederation` and `BrainHandoff`.
4. **Step 4 — Model Policies, Routing & Aliases:**
   - Implement `ModelPolicyEngine` (`QUALITY_FIRST`, `COST_OPTIMIZED`, `BALANCED`, `LOCAL_FIRST`).
   - Introduce logical model aliases (`creative.high`, `strategy.deep`, `copy.fast`).
   - Enhance `ModelRouter` to resolve Capabilities $\rightarrow$ Policies $\rightarrow$ Providers.
5. **Step 5 — Health, Circuit Breakers & Fallback:**
   - Implement `ProviderHealthMonitor` and `CircuitBreaker`.
   - Formalize `FallbackEngine` with audit trail recording.
6. **Step 6 — Control Plane API & Observability:**
   - Add new REST endpoints (`/api/ai/capabilities/*`, `/api/ai/brains/*`, `/api/ai/routing/*`, `/api/ai/control-plane/status`).
7. **Step 7 — UI & Control Center Integration:**
   - Integrate AI Control Center view, Simple UX vs. Expert Mode toggles, and Routing Explainer.
8. **Step 8 — Verification, Regression Testing & Documentation:**
   - Maintain 317 existing tests green while adding targeted test suites for all new capabilities.
