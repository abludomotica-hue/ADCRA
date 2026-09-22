# REST API Reference Manual
## ADCRA — Autonomous Digital Campaign & Creative Production System

The ADCRA Mission Control server (`dashboard_server.py`) exposes a comprehensive JSON REST API on port `8080` (configurable via `ADCRA_PORT`). All JSON responses return standard HTTP status codes (`200 OK`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `500 Server Error`).

---

## 1. System & Health Endpoints

### `GET /api/health`
Returns system health, host CPU cores, RAM, active GPU device, and server process ID.
- **Request:** `GET /api/health`
- **Response `200 OK`:**
```json
{
  "status": "HEALTHY",
  "system_version": "1.0.0-gold",
  "cpu_cores": 8,
  "ram_total_gb": 8.65,
  "gpu_device": "GPU 0: NVIDIA GeForce GTX 750 Ti",
  "server_pid": 660915
}
```

### `GET /api/status`
Returns execution and compliance status across all 22 phases of the ADCRA system.
- **Request:** `GET /api/status`
- **Response `200 OK`:**
```json
{
  "total_phases": 22,
  "completed_phases": 22,
  "phases": {
    "phase_01_intake": "COMPLIANT",
    "phase_02_blueprint": "COMPLIANT",
    "phase_03_routing": "COMPLIANT",
    "phase_11_beat_edit": "COMPLIANT",
    "phase_16_qc": "COMPLIANT",
    "phase_22_delivery": "COMPLIANT"
  }
}
```

### `GET /api/benchmark`
Executes latency and throughput benchmarks for audio beat analysis, JSON validation, and timeline generation.
- **Query Params:** `?iterations=10` (optional, default: 5)
- **Response `200 OK`:**
```json
{
  "iterations": 10,
  "latency_p50_ms": 1.42,
  "latency_p95_ms": 3.88,
  "throughput_ops_sec": 714.2
}
```

### `GET /api/introspect`
Returns the full inventory of registered agent tools, creative skills, and schema signatures.
- **Response `200 OK`:**
```json
{
  "total_skills": 18,
  "skills": [
    {
      "name": "analyze_audio_beats",
      "domain": "analysis",
      "description": "Extracts BPM, downbeats, and energy drops from WAV/MP3 files."
    }
  ]
}
```

---

## 2. Campaign Intake & Strategic Blueprint

### `GET /api/intake/draft`
Retrieves the current active campaign intake session state.
- **Response `200 OK`:** Returns `draft-session.json` content.

### `POST /api/intake/draft`
Updates one or more fields in the intake session draft.
- **Request Body:**
```json
{
  "client_name": "Acme Corp",
  "campaign_name": "Summer Launch 2026",
  "target_audience": "Urban Tech Enthusiasts 25-40",
  "duration_seconds": 30,
  "target_formats": ["16:9", "9:16", "1:1"]
}
```

### `POST /api/intake/preflight-audit`
Performs an automated pre-flight audit of the current draft against `campaign-intake-schema.json`.
- **Response `200 OK`:**
```json
{
  "passed": true,
  "errors": [],
  "warnings": ["No secondary CTA specified; default will be used."],
  "compliance_score": 98.5
}
```

### `POST /api/intake/blueprint/generate`
Transforms the validated intake session into a formal, immutable `campaign-blueprint.json`.
- **Response `200 OK`:**
```json
{
  "status": "GENERATED",
  "blueprint_path": "campaign/campaign-blueprint.json",
  "timestamp": "2026-09-21T21:00:00Z"
}
```

---

## 3. AI Brain & Agentic Framework

### `POST /api/ai/intent/execute`
Submits a natural language creative command to the autonomous Multi-Agent Brain.
- **Request Body:**
```json
{
  "prompt": "Create 3 high-converting viral hooks for TikTok targeting busy professionals.",
  "agent_role": "Senior Copywriter",
  "preferred_provider": "openai",
  "enforce_verbal_economy": true
}
```
- **Response `200 OK`:**
```json
{
  "request_id": "req_8f1b2c",
  "agent_role": "Senior Copywriter",
  "model_used": "gpt-4o-mini",
  "provider": "openai",
  "output": [
    "Hook 1: Still answering emails at 11 PM? Watch this.",
    "Hook 2: The 5-minute routine high-performers never skip.",
    "Hook 3: Stop wasting 10 hours a week on manual video editing."
  ],
  "tokens_used": 142,
  "cost_usd": 0.000085,
  "latency_ms": 680
}
```

### `POST /api/ai/providers/test`
Tests network connectivity and credential validity for all configured LLM providers (OpenAI, Anthropic, Gemini, OpenRouter, Ollama).
- **Response `200 OK`:**
```json
{
  "providers": {
    "openai": { "status": "ONLINE", "latency_ms": 190 },
    "gemini": { "status": "ONLINE", "latency_ms": 215 },
    "anthropic": { "status": "ONLINE", "latency_ms": 240 },
    "ollama": { "status": "OFFLINE", "message": "Connection refused on localhost:11434" }
  }
}
```

### `GET /api/ai/cost`
Returns token usage statistics and financial cost ledgers broken down by agent, provider, and model tier.

---

## 4. Creative Experimentation Lab (A/B Testing)

### `GET /api/experiments`
Lists all active and completed creative experiments in `campaign/creative/creative-experiments.json`.

### `POST /api/experiments/run`
Generates a multi-variant creative matrix comparing hooks, color grades, and audio tracks.
- **Request Body:**
```json
{
  "experiment_name": "Hook & Pacing A/B Test",
  "variants": [
    { "id": "var_A", "hook_type": "Direct Question", "color_lut": "Punchy Teal & Orange" },
    { "id": "var_B", "hook_type": "Curiosity Gap", "color_lut": "Clean Commercial Natural" }
  ]
}
```

---

## 5. Quality Control & Delivery

### `GET /api/deliver`
Inspects the commercial delivery package and technical specifications (`FICHA_TECNICA.md`).
- **Response `200 OK`:**
```json
{
  "campaign_id": "CAMP-2026-09-01",
  "status": "APPROVED",
  "masters": {
    "landscape_16x9": "campaign/deliverables/masters/master_16x9.mp4",
    "vertical_9x16": "campaign/deliverables/masters/master_9x16.mp4",
    "square_1x1": "campaign/deliverables/masters/master_1x1.mp4"
  },
  "audio_compliance": {
    "integrated_lufs": -14.1,
    "true_peak_dbtp": -1.2,
    "standard": "EBU R128 / ITU-R BS.1770"
  }
}
```

### `POST /api/intake/delivery/verify-hash`
Verifies SHA-256 cryptographic integrity hashes for all delivered video files.

### `GET /api/artifact`
Securely streams rendered video, audio stem, or report files to the browser with HTTP Byte-Range support for smooth scrubbing.
- **Query Parameter:** `?path=campaign/deliverables/masters/master_16x9.mp4`
- **Path Sanitization:** Automatically rejects any path with directory traversal (`../`).
