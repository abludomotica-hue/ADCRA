# ADCRA AI Brain — Security & Epistemic Governance Model

## 1. Secrets Management
- Zero API keys are stored in the frontend, Git repositories, or logs.
- The UI only receives operational states: `CONNECTED`, `STANDBY`, `INVALID`.
- Environment variable references (`OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.) are resolved securely by backend adapters.

## 2. Prompt Injection Defense & Untrusted Input Isolation
- External files, web content, and tool outputs are strictly isolated into an `UNTRUSTED DATA` envelope.
- System prompt policies and instructions are immutable and separate from campaign assets.

## 3. Epistemic Integrity
- Data retains source taxonomy: `CLIENT_INPUT`, `CONFIRMED_FACT`, `AI_INFERENCE`, `AI_RECOMMENDATION`, `RESEARCH`, `UNKNOWN`.
- `MemoryWriteValidator` prevents storing unverified `AI_INFERENCE` as a `CONFIRMED_FACT`.
