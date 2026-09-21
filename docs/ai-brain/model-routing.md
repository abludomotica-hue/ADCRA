# ADCRA AI Brain — Model Router & Fallback Policy

## 1. Routing Modes
- **AUTO**: Dynamically balances quality score (50%), latency/speed (30%), and token cost (20%).
- **MANUAL**: Explicit administrator or user override.
- **COST_OPTIMIZED**: Selects lowest cost model fulfilling task capability constraints.
- **QUALITY_FIRST**: Prioritizes reasoning depth and highest benchmark score.
- **BALANCED**: Default operational mode.

## 2. Fallback Chain
```
Primary Model (e.g. Gemini 2.5 Pro)
         ↓ Failure / Timeout
Fallback Model (e.g. Claude 3.5 Sonnet)
         ↓ Failure / Timeout
Secondary Provider (e.g. GPT-4o Mini / Mock)
         ↓ Failure
Human Review Escalation (WAITING_FOR_APPROVAL)
```
