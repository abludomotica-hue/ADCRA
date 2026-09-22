# ADCRA Canonical Capability Domain System

## 1. Overview
The Capability System establishes a canonical abstraction layer between ADCRA's operational tasks and underlying model architectures. Instead of coupling code to vendor-specific APIs or changing model names, all operations define explicit **Capability Requirements**.

---

## 2. The 24 Canonical Capabilities

| Category | Capability ID | Display Name | Description |
|---|---|---|---|
| **Creative** | `creative_writing` | Creative Writing | Narrative, metaphorical and conceptual synthesis |
| **Creative** | `copy_generation` | Copywriting & Scripting | Headlines, CTAs, voice-over scripts and dialogues |
| **Creative** | `storyboard_generation` | Storyboard Composition | Scene progression, shot framing and visual cues |
| **Strategy** | `brand_analysis` | Brand Strategy Analysis | Brand DNA extraction, positioning and pillars |
| **Strategy** | `audience_analysis` | Audience Profiling | Demographics, psychographics, motivations and triggers |
| **Strategy** | `strategic_reasoning` | Strategic Reasoning | Multi-step marketing hypothesis and tactical synthesis |
| **Generation** | `text_generation` | Natural Language Text | General-purpose natural language completion |
| **Generation** | `structured_generation` | Structured JSON Enforcement | Guaranteed adherence to valid JSON schemas |
| **Generation** | `code_generation` | Code Generation | Python scripting, automation hooks and logic |
| **Generation** | `image_generation` | Image Synthesis | Generative visuals and moodboard creation |
| **Generation** | `video_generation` | Video Synthesis | B-roll generation and generative motion clips |
| **Multimodal**| `multimodal_vision` | Multimodal Vision | Combined image-text analysis and visual scene breakdown |
| **Multimodal**| `image_understanding` | Image Scene Understanding | Framing, composition, color gamut and object detection |
| **Multimodal**| `video_understanding` | Video Temporal Analysis | Motion pacing, shot transitions and scene coherence |
| **Audio** | `audio_understanding` | Audio & Music Analysis | Acoustic mood, genre, rhythm and dynamic range analysis |
| **Audio** | `speech_transcription` | Speech Recognition | High-fidelity voice transcription and audio sync |
| **Analysis** | `classification` | Semantic Classification | Intent recognition, categorization and sentiment tagging |
| **Analysis** | `summarization` | Text Summarization | Executive digests and contextual compression |
| **Analysis** | `marketing_analysis` | Performance Analytics | Hook retention, pacing analysis and A/B/n scoring |
| **Production**| `tool_use` | Tool Calling / Function Execution | Deterministic execution of external tools and APIs |
| **Production**| `streaming` | Token & Chunk Streaming | Real-time SSE token delivery for low TTFT |
| **Memory** | `embeddings` | Semantic Vector Embeddings | Vector representation for semantic search and retrieval |
| **Memory** | `long_context` | Extended Context Window | >128k token ingestion for full campaign decks |
| **Production**| `translation` | Creative Translation | Culturally nuanced localization and transcreation |

---

## 3. Capability Probing & Discovery Engine
Capabilities are continuously evaluated in runtime via the `CapabilityDiscoveryEngine` and lightweight micro-probes:
- **`TextProbe`**: Verifies text generation and basic latency threshold (<5000ms).
- **`JsonProbe`**: Enforces strict JSON schema generation and structure parsing.
- **`ToolProbe`**: Verifies function calling and parameter binding.

Results are cached in `ProbeCache` with configurable TTL (default 1800s) to minimize token consumption while ensuring reliable telemetry.
