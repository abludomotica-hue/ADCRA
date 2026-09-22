# ADCRA AI Security, Epistemology & Secret Redaction Architecture

## 1. Zero API Key Exposure Guarantee
ADCRA enforces strict cryptographic and data boundary protection across all execution layers:
- **No Secret Leaks**: Provider API keys (`sk-...`, `AIza...`, Bearer tokens) are scrubbed in real-time from all outgoing HTTP responses, logs, telemetry events, and UI modals.
- **`SecretRedaction` Engine**: Employs high-speed regular expression filters and recursive dictionary sanitization before any data reaches disk or the network.
- **Decoupled Key Storage**: Keys are injected exclusively via environment variables (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`) and never persisted in campaign briefs or Git repositories.

---

## 2. Epistemic Classification System (`SourceEpistemology`)
To avoid hallucinated information poisoning brand assets, all creative data items carry an immutable epistemic badge:

1. **`CONFIRMED_FACT`** (Gold badge): Ground truth supplied explicitly by the client (e.g. verified brand name, legal entity, product ingredients, approved retail price).
2. **`CLIENT_INPUT`** (Emerald badge): Unvalidated preference or aesthetic request from the client intake brief.
3. **`RESEARCH`** (Cyan badge): External empirical data retrieved from verified market research, benchmarking, or industry indexes.
4. **`AI_RECOMMENDATION`** (Purple badge): Strategic or creative proposal synthesized by a Brain Profile, awaiting human approval.
5. **`AI_INFERENCE`** (Blue badge): Internal reasoning deduction or intermediate calculation made during pipeline execution.

---

## 3. Autonomy Levels & Human Guardrails
Every Brain Profile operates under a configurable `AutonomyLevel`:
- **`ASSIST`**: The AI suggests options; human approval is strictly required before proceeding to the next step.
- **`AUTOPILOT`**: The AI executes creative ideation, script drafting, and DaVinci timeline construction autonomously. It pauses and raises a human checkpoint for financial expenditure, media asset publication, or final master delivery.
- **`AUTONOMOUS`**: The agent executes end-to-end within pre-authorized budget ceilings ($0.05 default per task).

---

## 4. Multi-Tenant Isolation
All telemetry, cost ledgers, brain handoffs, and AIRuns are partitioned by `tenant_id` and `workspace_id`. Cross-tenant data leakage is prevented at the schema, storage, and API routing levels.
