# ADCRA AI Brain — Cost Intelligence & Budget Engine

## 1. Immutable AI Cost Ledger
All AI requests record immutable telemetry in `campaign/reports/ai-cost-ledger.json`:
- `entry_id`, `timestamp`, `tenant_id`, `campaign_id`, `agent_id`, `task`, `provider_id`, `model_id`
- `input_tokens`, `output_tokens`, `cached_tokens`, `cost_usd`, `latency_ms`

## 2. Budget Engine Enforcement
- **NORMAL**: Spend < 80% of authorized limit.
- **WARNING**: Spend between 80% and 100% of limit.
- **LIMIT_REACHED**: Operations capped, requiring budget extension.
- **BLOCKED**: Single request or tenant strictly exceeds safety limits.
