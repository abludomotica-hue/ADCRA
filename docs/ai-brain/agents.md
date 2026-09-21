# ADCRA AI Brain — Agent Orchestrator & State Machine

## 1. Overview
The Agent Orchestration system coordinates specialized creative roles (`Creative Director`, `Strategist`, `Copywriter`, `Storyboard Director`, `QC Director`, `Production Director`).

## 2. 12-State Lifecycle Machine
```
IDLE → PLANNING → WAITING_FOR_CONTEXT → READY → RUNNING → WAITING_FOR_TOOL
                                                    │            │
                                                    ▼            ▼
                                          WAITING_FOR_APPROVAL  VALIDATING
                                                    │            │
                                                    ▼            ▼
                                                ITERATING → COMPLETED / FAILED / CANCELLED
```

## 3. Loop Safety & Guardrails
- **Max Iterations**: Default 3 iterations per task.
- **Max Tool Invocations**: 10 calls per run.
- **Recursion Depth**: Strictly capped.
- **Idempotency**: Critical operations use deterministic keys to prevent duplicate execution.
