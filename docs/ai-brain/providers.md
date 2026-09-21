# ADCRA AI Brain — Providers & Adapters Specification

## 1. Overview
The Provider Layer decouples ADCRA from commercial and open-source model providers.
Every provider implements `AIProviderAdapter` (`adcra/ai/gateway.py`).

## 2. Supported Adapters
- **MockAIProvider (`adcra/ai/adapters/mock_adapter.py`)**: Deterministic, offline provider for test suites, CI/CD, and zero-cost local development.
- **OpenAIProvider (`adcra/ai/adapters/openai_adapter.py`)**: GPT-4o, GPT-4o Mini, OpenAI o1, Azure OpenAI, and local OpenAI-compatible endpoints (vLLM, Ollama).
- **GeminiProvider (`adcra/ai/adapters/gemini_adapter.py`)**: Gemini 2.5 Flash and Gemini 2.5 Pro with native audio/visual multimodal capabilities.
- **AnthropicProvider (`adcra/ai/adapters/anthropic_adapter.py`)**: Claude 3.5 Sonnet and Claude 3.5 Haiku.
- **OpenRouterProvider (`adcra/ai/adapters/openrouter_adapter.py`)**: Aggregated gateway to Llama 3.3 70B, DeepSeek R1, and over 150+ models.

## 3. Extending with a New Provider
To add a new provider:
1. Subclass `AIProviderAdapter`.
2. Implement required methods: `list_models()`, `get_model_capabilities()`, `generate()`, `stream()`, `estimate_cost()`, `validate_configuration()`.
3. Register adapter in `AIProviderGateway` via `gateway.register_adapter(NewAdapter())`.
