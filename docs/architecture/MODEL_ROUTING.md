# ADCRA Model Policy Engine & Intelligent Routing

## 1. Overview
The `ModelPolicyEngine` and `ModelRouter` govern model selection across multi-provider deployments. Model routing is multi-dimensional and capability-aware: it optimizes for quality, cost, speed, multimodal capabilities, and offline resiliency.

---

## 2. The 10 Logical Aliases

| Logical Alias | Preferred Provider | Preferred Model | Target Capability | Fallback Chain | Active Policy |
|---|---|---|---|---|---|
| `creative.high` | `openai` | `gpt-4o` | `creative_writing` | Claude 3.5 Sonnet -> Gemini 2.5 Pro -> Mock | `QUALITY_FIRST` |
| `creative.fast` | `gemini` | `gemini-2.5-flash` | `creative_writing` | GPT-4o-mini -> Claude 3.5 Haiku -> Mock | `LOW_LATENCY` |
| `strategy.deep` | `anthropic` | `claude-3-5-sonnet` | `strategic_reasoning` | GPT-4o -> Gemini 2.5 Pro -> Mock | `HIGH_REASONING` |
| `strategy.fast` | `openai` | `gpt-4o-mini` | `strategic_reasoning` | Gemini 2.5 Flash -> Mock | `BALANCED` |
| `vision.high` | `gemini` | `gemini-2.5-pro` | `multimodal_vision` | GPT-4o -> Claude 3.5 Sonnet -> Mock | `MULTIMODAL_FIRST` |
| `vision.fast` | `gemini` | `gemini-2.5-flash` | `multimodal_vision` | GPT-4o-mini -> Mock | `LOW_LATENCY` |
| `copy.high` | `anthropic` | `claude-3-5-sonnet` | `copy_generation` | GPT-4o -> Gemini 2.5 Flash -> Mock | `QUALITY_FIRST` |
| `copy.fast` | `openai` | `gpt-4o-mini` | `copy_generation` | Gemini 2.5 Flash -> Mock | `COST_OPTIMIZED` |
| `qc.deep` | `openai` | `gpt-4o` | `brand_analysis` | Claude 3.5 Sonnet -> Mock | `QUALITY_FIRST` |
| `qc.fast` | `gemini` | `gemini-2.5-flash` | `classification` | GPT-4o-mini -> Mock | `LOW_LATENCY` |

---

## 3. Policy Scoring Formula

The `ModelPolicyEngine` computes a composite score (0 to 100) for every candidate model based on normalized scores:
- **Capability Match ($C_{score}$)**: Percentage of required capabilities satisfied.
- **Quality Score ($Q_{score}$)**: Benchmark evaluation of cognitive reasoning depth (0-100).
- **Speed Score ($S_{score}$)**: Inverted latency rating based on historical P50 response times.
- **Cost Efficiency ($E_{score}$)**: Normalized token cost metric: $\max(0, 100 - (C_{input} + C_{output}) 	imes 5)$.

### Composite Score by Policy:
- **`QUALITY_FIRST` / `HIGH_REASONING`**:
  $$Score = (C_{score} 	imes 0.40) + (Q_{score} 	imes 0.45) + (S_{score} 	imes 0.10) + (E_{score} 	imes 0.05)$$
- **`COST_OPTIMIZED`**:
  $$Score = (C_{score} 	imes 0.30) + (E_{score} 	imes 0.50) + (S_{score} 	imes 0.10) + (Q_{score} 	imes 0.10)$$
- **`LOW_LATENCY`**:
  $$Score = (C_{score} 	imes 0.30) + (S_{score} 	imes 0.50) + (Q_{score} 	imes 0.10) + (E_{score} 	imes 0.10)$$
- **`BALANCED`**:
  $$Score = (C_{score} 	imes 0.35) + (Q_{score} 	imes 0.35) + (S_{score} 	imes 0.15) + (E_{score} 	imes 0.15)$$

---

## 4. Routing Explainer (`/api/ai/routing/explain`)
The router provides transparent, human-readable explanations of every routing decision, exposing:
- The winner model and provider
- Policy weights applied
- Exact score breakdown across quality, speed, cost, and capability match
- Active circuit breaker states
- Ordered fallback chain
