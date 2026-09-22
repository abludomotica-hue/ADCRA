# ADCRA AI Intelligence Control Plane v2.0 — Architecture Overview

## 1. Executive Summary
The **ADCRA AI Intelligence Control Plane v2.0** transforms ADCRA from a basic multi-model router into an autonomous, provider-agnostic, and capability-driven **Creative Operating System**. It establishes a centralized governance and orchestration layer that decouples cognitive creative agent workflows from underlying vendor APIs (Google Gemini, Anthropic Claude, OpenAI, OpenRouter, and Local/Offline Mock Engines).

---

## 2. Core Architecture Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                    ADCRA CREATIVE OPERATING SYSTEM                                 |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   +-----------------------+     +------------------------+     +-------------------------------+   |
|   | 14 Cognitive Brains   | --> | Capability Domain Req  | --> | Model Policy Engine           |   |
|   | (Creative, Strategy,  |     | (24 Canonical Domains, |     | (Quality, Cost, Speed,        |   |
|   |  Copy, Audio, QC...)  |     |  Probes & Constraints) |     |  10 Logical Aliases)          |   |
|   +-----------------------+     +------------------------+     +-------------------------------+   |
|               |                             |                                  |                   |
|               v                             v                                  v                   |
|   +--------------------------------------------------------------------------------------------+   |
|   |                              PROVIDER-AGNOSTIC AGENT RUNTIME                               |   |
|   |    - AIRun Lifecycle & Tracing (QUEUED -> RUNNING -> COMPLETED / FALLING_BACK / FAILED)    |   |
|   |    - Epistemic Ledger (Client Input, AI Recommendation, Confirmed Fact, AI Inference)      |   |
|   |    - Real-Time Secret Redaction (Zero Token/API Key Exposure)                              |   |
|   +--------------------------------------------------------------------------------------------+   |
|               |                                                                |                   |
|               v                                                                v                   |
|   +---------------------------------------+       +--------------------------------------------+   |
|   | Resilient Fallback Engine             |       | Provider Health & Circuit Breakers         |   |
|   | Primary -> Secondary -> Mock Fallback | <---> | States: CLOSED, OPEN, HALF_OPEN            |   |
|   +---------------------------------------+       | Latency Percentiles: P50, P90, P95, P99    |   |
|                                                   +--------------------------------------------+   |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   |                                  MULTI-PROVIDER ADAPTERS                                   |   |
|   |       [Google Gemini]      [Anthropic Claude]      [OpenAI]      [OpenRouter]      [Mock]  |   |
|   +--------------------------------------------------------------------------------------------+   |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Key Architectural Pillars

### 3.1. Capability-Driven Decoupling
Agents and Brain Profiles never request specific model names (e.g. `gpt-4o` or `gemini-2.5-pro`) directly. Instead, they declare operational requirements using the **24 Canonical Capability Domains** (e.g. `creative_writing`, `strategic_reasoning`, `multimodal_vision`, `structured_generation`). The control plane resolves the optimal physical model at runtime based on active policies and health telemetry.

### 3.2. Cognitive Brain Federation
Collaborative multi-agent workflows are governed by the `BrainFederationEngine`. When a campaign transitions across creative stages (such as from `brand_strategist` to `creative_director` and then to `storyboard_director`), structured `BrainHandoff` tokens transfer context, decisions, constraints, and epistemic tags without loss of creative fidelity.

### 3.3. Multi-Objective Routing & Logical Aliases
The `ModelPolicyEngine` evaluates candidate models against active operational policies:
- `QUALITY_FIRST`: Prioritizes cognitive depth, nuance, and structural reasoning.
- `COST_OPTIMIZED`: Enforces economical token utilization for high-volume background tasks.
- `LOW_LATENCY`: Prioritizes P50 response speeds for interactive UX flows.
- `BALANCED`: Optimizes composite score across quality, latency, and financial cost.
- `OFFLINE_ONLY`: Enforces zero network egress using the deterministic local Mock Engine.

Logical routing aliases (`creative.high`, `copy.fast`, `strategy.deep`, `vision.high`, `qc.deep`) provide stable integration endpoints for frontend and external callers.

### 3.4. Resilient Health & Circuit Breaker Architecture
Network failures, rate limits (HTTP 429), or upstream provider outages are isolated using per-provider and per-model `CircuitBreaker` instances. When failure thresholds are exceeded, the circuit trips from `CLOSED` to `OPEN`, immediately shielding the system and routing requests to backup candidates via the `FallbackEngine`. After a cooldown period, `HALF_OPEN` state verifies upstream recovery via canary probes.

### 3.5. Air-Tight Security & Epistemic Auditability
All prompts, responses, tool calls, and debug telemetry undergo automated real-time string scrubbing via `SecretRedaction`, guaranteeing zero exposure of sensitive provider API keys or bearer tokens. The system stamps all generated creative artifacts with a `SourceEpistemology` classification to maintain strict human-in-the-loop oversight.
