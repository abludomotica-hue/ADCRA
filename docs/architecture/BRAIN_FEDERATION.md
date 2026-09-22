# ADCRA Brain Profiles & Cognitive Federation Architecture

## 1. Overview
The ADCRA Cognitive Federation Architecture defines specialized creative and operational personas called **Brain Profiles**. Rather than deploying a monolithic, one-size-fits-all prompt, ADCRA partitions campaign execution into specialized cognitive domains, governed by the `BrainFederationEngine`.

---

## 2. The 14 Canonical Brain Profiles

| Brain ID | Display Name | Core Responsibility | Primary Capabilities |
|---|---|---|---|
| `creative_director` | Creative Director | Big Idea, Narrative Arc, Brand Tone & Emotional Resonance | `creative_writing`, `brand_analysis`, `strategic_reasoning` |
| `brand_strategist` | Brand Strategist | Target Audience, Value Proposition & Market Positioning | `audience_analysis`, `strategic_reasoning`, `brand_analysis` |
| `copy_director` | Creative Copywriter | Slogans, Headlines, Screenplay Scripts & Verbal Economy | `copy_generation`, `creative_writing`, `structured_generation` |
| `storyboard_director` | Storyboard Director | Visual Composition, Shot Lists, Camera Angles & Motion | `storyboard_generation`, `multimodal_vision`, `creative_writing` |
| `visual_director` | Motion & Visual Director | Color Harmony, Lighting, Graphics & Kinetic Aesthetics | `multimodal_vision`, `image_understanding`, `creative_writing` |
| `audio_director` | Sound Architect | Soundtrack Cues, Voice-Over Tone & EBU R128 Loudness | `audio_understanding`, `speech_transcription`, `classification` |
| `production_director` | Campaign Producer | Timeline Orchestration, Milestones & Asset Logistics | `structured_generation`, `strategic_reasoning`, `classification` |
| `qc_director` | QC & Compliance Director | Technical Standards, Safe Zones, Legal & Brand Guardrails | `classification`, `structured_generation`, `compliance` |
| `delivery_director` | Delivery & Package Director | Render Profiles, Master Manifests & SHA-256 Checksums | `structured_generation`, `tool_use`, `code_generation` |
| `market_researcher` | Market Research Analyst | Competitive Benchmarking, Industry Trends & Sentiment | `marketing_analysis`, `summarization`, `strategic_reasoning` |
| `audience_analyst` | Audience Profiler | Psychographics, Demographics, Pain Points & Behavioral Triggers | `audience_analysis`, `classification`, `summarization` |
| `strategic_planner` | Strategic Planner | Multi-Platform Rollout, Budget Allocation & Flighting | `strategic_reasoning`, `marketing_analysis`, `structured_generation` |
| `editorial_director` | Editorial Director | Tone Governance, Pacing, Narrative Rhythm & Consistency | `creative_writing`, `summarization`, `brand_analysis` |
| `post_mortem_analyst` | Post-Mortem & Learning Analyst | KPI Evaluation, Creative Insights & Epistemic Feedback Loops | `marketing_analysis`, `summarization`, `structured_generation` |

---

## 3. Brain Handoff Protocol (`BrainHandoff`)
When creative authority transitions from one profile to another, the transaction is structured as an immutable `BrainHandoff` contract:

```json
{
  "handoff_id": "handoff_89b2c1fa",
  "source_brain": "brand_strategist",
  "target_brain": "creative_director",
  "campaign_id": "camp_locos_materos_2026",
  "task_id": "brand_essence_formulation",
  "input_context": {
    "brand_name": "Locos Materos",
    "core_insight": "El mate transforma cualquier rincón en un punto de encuentro"
  },
  "artifacts": [
    { "type": "strategic_brief", "uri": "artifact://brief_v1.json" }
  ],
  "decisions": [
    "Territorio de marca: Autenticidad popular y pausa consciente",
    "Target primario: Jóvenes profesionales de 25 a 40 años"
  ],
  "constraints": [
    "Evitar estereotipos folclóricos caricaturescos",
    "Duración máxima de piezas master: 30 segundos"
  ],
  "open_questions": [
    "¿Se debe incluir plano explícito de preparación del mate en el Hook?"
  ],
  "confidence": 0.95,
  "epistemology": "AI_RECOMMENDATION",
  "timestamp": "2026-09-21T21:45:00Z"
}
```

---

## 4. Collaborative Federation Flow

```
[CLIENT INTAKE]
       |
       v
(Brand Strategist) --------[Handoff #1]-------> (Creative Director)
       |                                                |
       v                                                v
[Market Researcher]                             (Copywriter & Storyboard)
       |                                                |
       +------------------[Handoff #2]------------------+
                               |
                               v
                       (QC & Compliance)
                               |
                        [Handoff #3]
                               |
                               v
                      (Delivery Director)
```

The `BrainFederationEngine` guarantees:
1. **Context Preservation**: Strategic decisions made early are enforced as immutable constraints in downstream creative phases.
2. **Epistemic Tracking**: The receiving brain knows whether input data is verified client ground-truth or an AI hypothesis.
3. **Auditable History**: Full handoff traces can be inspected via `/api/ai/traces/{id}` for accountability.
