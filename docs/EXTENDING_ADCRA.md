# Developer Guide: Extending ADCRA
## Building Custom Agents, Generative Tools, and Brand Rules

ADCRA is designed around modular, decoupled abstractions. Whether you want to add a new AI provider (like DeepSeek or a fine-tuned local model), define a specialized agent role (like a TikTok Trend Strategist), or connect an external rendering engine (like Blender or ComfyUI), this guide shows you how.

---

## 1. Creating a Custom AI Agent Profile

Agent profiles are defined in `adcra/ai/profiles.py`. Each agent has a designated role, specialization, system prompt, temperature, default tool permissions, and model tier.

### Example: Adding a "Social Media Hook Specialist"
Open `adcra/ai/profiles.py` and register your profile:

```python
from adcra.ai.types import AgentProfile, AgentRole, ModelTier

HOOK_SPECIALIST_PROFILE = AgentProfile(
    role="Social Media Hook Specialist",
    description="Specialized in crafting viral, high-retention opening hooks for vertical video formats (Reels, TikTok, Shorts).",
    system_prompt=(
        "You are an elite short-form video retention strategist. Your goal is to write 3-second opening "
        "hooks that maximize 3-second view-through rates. You must strictly obey brand tone rules, "
        "keep hooks under 12 words, and enforce active, curiosity-driven verbs."
    ),
    temperature=0.8,
    model_tier=ModelTier.FAST,          # Uses fast, low-cost models (e.g. gpt-4o-mini, gemini-flash)
    allowed_tools=[
        "generate_copy_variants",
        "query_brand_memory",
        "evaluate_retention_score"
    ]
)
```

Register the new profile in the `get_default_agent_profiles()` registry list.

---

## 2. Registering a New Tool or Creative Skill

Tools provide agents with concrete abilities (e.g., calculating audio beats, generating image assets, or manipulating video timelines).

### Step 1: Implement the Tool Function
In `adcra/ai/tools.py`:

```python
def generate_voiceover_elevenlabs(script_text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> dict:
    """
    Generates realistic synthetic voiceover using ElevenLabs API and returns audio path and duration.
    """
    # Tool implementation logic here...
    output_wav_path = f"campaign/audio/vo_{int(time.time())}.wav"
    return {
        "status": "SUCCESS",
        "audio_path": output_wav_path,
        "duration_seconds": 15.4,
        "sample_rate": 48000
    }
```

### Step 2: Define the JSON Schema & Register Tool
In `adcra/ai/tools.py`:

```python
VOICEOVER_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "script_text": {"type": "string", "description": "Text script for voiceover narration"},
        "voice_id": {"type": "string", "description": "ElevenLabs Voice ID"}
    },
    "required": ["script_text"]
}

# Register into the ToolRegistry
tool_registry.register(
    name="generate_voiceover",
    description="Generates AI voiceover audio from text script.",
    func=generate_voiceover_elevenlabs,
    parameters=VOICEOVER_TOOL_SCHEMA,
    required_permission="AUDIO_SYNTHESIS"
)
```

### Step 3: Grant Role Permission
In `adcra/ai/permissions.py`, add `"AUDIO_SYNTHESIS"` to the permissible tool sets for authorized agent roles (e.g. `Sound Designer`, `Executive Director`).

---

## 3. Adding a New LLM Provider (e.g., DeepSeek / vLLM)

All LLM communication flows through `adcra/ai/gateway.py` and `adcra/ai/router.py`. To connect a custom OpenAI-compatible endpoint (such as DeepSeek, Groq, or a local vLLM server):

1. **Configure Environment:**
   In `.env`:
   ```bash
   DEEPSEEK_API_KEY=sk-your-key-here
   DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
   ```

2. **Register Model in `adcra/ai/models.py`:**
   ```python
   ModelConfig(
       provider="deepseek",
       model_name="deepseek-chat",
       context_window=64000,
       cost_per_1k_input_tokens=0.00014,
       cost_per_1k_output_tokens=0.00028,
       tier=ModelTier.REASONING
   )
   ```

3. **Gateway Dispatch:**
   The gateway automatically detects OpenAI-compatible REST APIs and routes requests with full telemetry, latency tracking, and cost accounting.

---

## 4. Extending the Brand Knowledge Graph

ADCRA uses a structured knowledge graph (`campaign/campaign-knowledge-graph.json`) to persist brand rules and constraints across sessions.

### Adding Custom Constraint Node Types
You can insert nodes via the REST API:

```bash
curl -X POST http://localhost:8080/api/intake/knowledge-graph/node \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "rule_font_family",
    "type": "TYPOGRAPHY_CONSTRAINT",
    "properties": {
      "primary_font": "Inter Bold",
      "minimum_font_size_pt": 24,
      "enforce_all_caps": false
    }
  }'
```

The preflight audit and QC engines will automatically query these nodes to enforce compliance during rendering.

---

## 5. Adding Custom Quality Control Assertions

To add a new quality check (e.g., verifying that subtitle text never covers more than 20% of the screen area):

1. Open `evaluate_quality.py` or `adcra/ai/qc.py`.
2. Define the assertion function:
   ```python
   def assert_subtitle_density(timeline_manifest: dict) -> dict:
       # Inspect text bounding boxes and durations
       # Return pass/fail status and remediation suggestion
       return {
           "check": "subtitle_density",
           "passed": True,
           "score": 100.0,
           "remediation": None
       }
   ```
3. Add the check to the pre-flight and master delivery validation suites.
