<div align="center">

# 🎬 ADCRA
### Autonomous Digital Campaign & Creative Production System
**The Creative Operating System for Autonomous Advertising, Audiovisual Mastery & Brand Intelligence**

[![Tests Passing](https://img.shields.io/badge/Tests-317%20Passed%20(100%25)-success?style=flat-square&logo=pytest)](tests/)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square&logo=python)](requirements.txt)
[![Node.js Version](https://img.shields.io/badge/Node.js-%3E%3D18.0%20LTS-green?style=flat-square&logo=node.js)](package.json)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange?style=flat-square)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent%20%2B%20Hybrid%20Render-purple?style=flat-square)](docs/ARCHITECTURE.md)
[![Hardware Acceleration](https://img.shields.io/badge/Hardware-NVIDIA%20CUDA%20%7C%20Apple%20Metal%20%7C%20CPU%20Headless-lightgrey?style=flat-square)](docs/HARDWARE_AND_PLATFORMS.md)

[English](#english) • [Español](#español) • [Quickstart](#-3-minute-quickstart) • [Architecture](#-system-architecture) • [Documentation Hub](docs/)

---
</div>

## 🌐 Overview / Descripción General

### English
**ADCRA** is an enterprise-grade **Creative Operating System** designed to bridge the gap between high-level brand strategy, generative AI intelligence, and broadcast-quality audiovisual production.

It is **not** a chatbot, **not** a simple video template tool, and **not** a traditional CRM. ADCRA is an autonomous production agency:
- **Transforms Client Intent into Actionable Strategy:** Uses a 17-step intake engine to extract audience, emotional tone, visual language, and format requirements.
- **Multi-Model AI Brain with Cost Governance:** Orchestrates top-tier LLMs (OpenAI, Anthropic Claude, Google Gemini, OpenRouter, and local Ollama/vLLM) with automatic cost routing and strict verbal economy.
- **Hybrid Audiovisual Production Engine:** Renders videos either through **DaVinci Resolve Studio** (native Fairlight DAW, Fusion nodes, Color grading) or via **Remotion / HyperFrames / FFmpeg** (headless, cloud VMs, Docker).
- **Epistemic Memory & Dynamic Brand Graph:** Learns brand constraints, legal disclaimers, and past performance, preventing repeated creative errors across campaigns.
- **Automated Quality Control (QC):** Enforces broadcast audio loudness (-14 LUFS), social safe zones (9:16 / 1:1 / 16:9), and visual contrast with a self-healing re-render loop.

### Español
**ADCRA** es un **Sistema Operativo Creativo** de nivel empresarial diseñado para unir la estrategia de marca, la inteligencia artificial generativa y la producción audiovisual profesional.

No es un simple generador de texto ni una plantilla de video. Es una agencia publicitaria autónoma completa:
- **Transforma la Intención del Cliente en Estrategia:** Motor de intake de 17 pasos estructurados (audiencia, tono emocional, estilo visual, entregables).
- **Cerebro Multi-Agente con Gobierno de Costos:** Enrutador inteligente entre modelos (OpenAI, Claude, Gemini, OpenRouter y Ollama local) con economía verbal estricta.
- **Motor Híbrido de Producción Audiovisual:** Renderizado nativo vía **DaVinci Resolve Studio** o renderizado sin interfaz gráfica (headless) mediante **Remotion / FFmpeg** para la nube o Docker.
- **Memoria Epistémica y Grafo de Marca:** Aprende restricciones legales, paletas y aprendizajes previos para garantizar consistencia absoluta.
- **Control de Calidad Autónomo (QC):** Audita normas broadcast (-14 LUFS, márgenes de seguridad 9:16/16:9/1:1) con bucle de auto-corrección e iteración automática.

---

## ⚡ 3-Minute Quickstart

Get ADCRA up and running on your local machine or server in 3 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/abludomotica-hue/ADCRA.git
cd ADCRA

# 2. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Create your environment file from the template
cp .env.example .env

# 5. Launch the ADCRA Mission Control Web Dashboard
./bin/adcra dashboard
```

Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🐳 Instant Docker Deployment

Run ADCRA headless in any cloud server or local environment with zero manual dependency installation:

```bash
# Clone and enter directory
git clone https://github.com/abludomotica-hue/ADCRA.git
cd ADCRA

# Copy environment variables
cp .env.example .env

# Launch with Docker Compose
docker compose up -d --build

# Verify health
curl http://localhost:8080/api/health
```

---

## 🖥️ Platform & Hardware Requirements

ADCRA automatically detects host hardware capabilities via its integrated **Hardware Probe** (`adcra/ai/hardware.py`):

| Environment Tier | Target Use Case | Recommended Hardware | Rendering Mode |
|---|---|---|---|
| **Headless Cloud / VPS** | Docker, CI/CD, SaaS Backends, Cloud VMs | 4–8 vCPU, 8–16 GB RAM, No GPU needed | Remotion + FFmpeg (CPU Software) |
| **Creative Workstation** | Agencies, High-res Video Masters | 8+ CPU Cores, 16–32 GB RAM, NVIDIA GPU (4GB+ VRAM) | DaVinci Resolve Studio + NVENC |
| **Apple Silicon Mac** | Solo Creators, In-House Teams | Apple M1/M2/M3/M4 (16GB+ Unified Memory) | Metal & VideoToolbox Acceleration |

> 📖 **Full Hardware Guide:** See [docs/HARDWARE_AND_PLATFORMS.md](docs/HARDWARE_AND_PLATFORMS.md) for GPU compatibility, VRAM benchmarks, and cloud provisioning guides.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            OPERATOR / CLIENT                                │
│                     (Web UI / REST API / Terminal CLI)                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               17-STEP STRATEGIC CAMPAIGN INTAKE ENGINE                      │
│   • Client Profile & Tone        • Target Audience Segmentation             │
│   • Multi-Format Matrix          • Automated Pre-Flight Validation Audit    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AI BRAIN & AGENTIC ORCHESTRATION                         │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────┐  │
│  │ Model Router            │  │ Verbal Economy Engine   │  │ RBAC Tools  │  │
│  │ (OpenAI/Anthropic/Gemini)│ │ (Token Ceilings & JSON) │  │ & Safety    │  │
│  └─────────────────────────┘  └─────────────────────────┘  └─────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Epistemic Memory & Dynamic Brand Graph (campaign-knowledge-graph.json)│  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               CREATIVE EXPERIMENTATION & STORYBOARD ENGINE                  │
│   • Multi-Variant Copywriting (A/B Hooks, Body, CTAs)                       │
│   • Audio Beat Analysis (BPM, Downbeats, Energy Drops)                      │
│   • Storyboard Scene Synchronization & Camera Direction                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 DUAL-ENGINE AUDIOVISUAL PRODUCTION LAYER                    │
│   MODE A: DaVinci Resolve Studio        MODE B: Headless Remotion / FFmpeg  │
│   • Native Fairlight Audio Mastering   • Serverless / Cloud VM Ready       │
│   • Fusion 3D Motion Graphics Nodes     • CSS/SVG/WebGL Motion Graphics     │
│   • Color Page 32-Bit Float HDR LUTs   • Multi-Threaded FFmpeg Filtergraphs│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 AUTOMATED QUALITY CONTROL & SELF-HEALING                    │
│   • Technical: -14 LUFS Audio, Safe Zones, True Peak ≤ -1 dBTP              │
│   • Creative: Hook Retention (<3s), Beat Sync Alignment                     │
│   • Autonomous Iteration Loop: Auto-remediates & re-renders (Max 3 retries) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FINAL DELIVERY & ASSET PACKAGING                        │
│   • Landscape (16:9) • Vertical (9:16) • Square (1:1) • Ficha Técnica       │
└─────────────────────────────────────────────────────────────────────────────┘
```

> 📖 **Deep Dive:** Read the complete [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for sequence diagrams and module taxonomy.

---

## 🎛️ Mission Control Web UI Tour

The interactive web dashboard (`dashboard_server.py`) provides an all-in-one mission control center:

1. **Intake Wizard:** 17 structured visual steps guiding operators through brief creation with real-time preflight validation.
2. **Copywriting Lab:** Multi-variant script and hook generator with token consumption monitoring and tone sliders.
3. **Storyboard Lab:** Beat-synced timeline view displaying scene cuts, duration, camera framing, and audio synchronization.
4. **Creative Experimentation Lab:** Direct matrix testing of hooks, color grades, and audio tracks with side-by-side comparison.
5. **Quality Control Inspector:** Automated compliance cards checking audio loudness, title safe zones, and visual contrast.
6. **Delivery Center:** Direct playback of rendered masters (with HTTP byte-range video scrubbing), SHA-256 hash validation, and technical export sheets.
7. **Interactive Terminal & Deck Generator:** Run CLI commands directly in the browser and export campaign slide decks with one click.

---

## ⌨️ CLI Cheatsheet

ADCRA includes an executable command-line wrapper at `./bin/adcra`:

```bash
# Display system version and build info
./bin/adcra version

# Inspect status of all 22 system phases
./bin/adcra status

# Start the Mission Control Web Server
./bin/adcra dashboard

# Re-render master commercial and social adaptations
./bin/adcra produce

# Inspect delivery package and technical specs
./bin/adcra deliver

# Run audio and timeline latency benchmarks
./bin/adcra benchmark --iterations 15

# Introspect registered skills and agent tools
./bin/adcra introspect

# Run complete regression test suite (317 tests)
./bin/adcra test
```

---

## 🔌 REST API Overview

The Mission Control server exposes a high-performance JSON REST API on port `8080`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health, CPU cores, RAM, active GPU device, and server PID. |
| `GET` | `/api/status` | Compliance and execution status across all 22 system phases. |
| `GET` | `/api/intake/draft` | Retrieve the active intake wizard draft state. |
| `POST` | `/api/intake/draft` | Update intake draft fields (audience, tone, deliverables). |
| `POST` | `/api/intake/preflight-audit` | Audit draft against schema before allocating generative resources. |
| `POST` | `/api/intake/blueprint/generate` | Compile validated draft into an immutable campaign blueprint. |
| `POST` | `/api/ai/intent/execute` | Dispatch natural language creative commands to the AI Brain. |
| `POST` | `/api/ai/providers/test` | Test connectivity and latency for all configured LLM providers. |
| `GET` | `/api/ai/cost` | Retrieve token consumption ledgers and financial expenditure. |
| `GET` | `/api/experiments` | List all active and completed creative A/B experiments. |
| `POST` | `/api/experiments/run` | Execute multi-variant matrix experiment generation. |
| `GET` | `/api/deliver` | Retrieve delivery package, master MP4 paths, and audio compliance data. |
| `GET` | `/api/artifact?path=...` | Securely stream video/audio artifacts with HTTP byte-range scrubbing. |

> 📖 **Full API Reference:** See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for complete request and response JSON schemas.

---

## 📚 Documentation Hub

Detailed documentation is organized in the [`docs/`](docs/) directory:

- 🚀 **[Getting Started Guide](docs/GETTING_STARTED.md):** Complete installation guide for Linux, macOS, and Windows WSL2.
- 🏗️ **[System Architecture](docs/ARCHITECTURE.md):** In-depth technical architecture, data flows, and security model.
- 💻 **[Hardware & Platform Matrix](docs/HARDWARE_AND_PLATFORMS.md):** GPU requirements, VRAM tuning, and cloud deployment tiers.
- 📡 **[REST API Reference](docs/API_REFERENCE.md):** Exhaustive endpoint reference with request/response payloads.
- 🛠️ **[Extending ADCRA](docs/EXTENDING_ADCRA.md):** How to create custom agents, add new LLMs, and build creative tools.
- 🚀 **[Production Deployment](docs/DEPLOYMENT.md):** Docker, Systemd service, Nginx reverse proxy, and CI/CD pipelines.

---

## 🧪 Testing & Quality Assurance

ADCRA maintains a comprehensive automated test suite covering all 22 phases, AI Brain routing, permissions, verbal economy, and hardware detection:

```bash
# Run all 317 unit and integration tests
python3 -m unittest discover -s tests -q

# Or via the CLI wrapper
./bin/adcra test
```

Current test suite status: **317 tests passed, 0 failures, 0 regressions.**

---

## 🤝 Contributing

We welcome contributions from software developers, AI engineers, video editors, and creative technologists!
Please check our [Contributing Guide](CONTRIBUTING.md) for details on code standards, local setup, and pull request workflows.

---

## 📄 License

ADCRA is open-source software licensed under the **[Apache License 2.0](LICENSE)**.
You are free to use, modify, distribute, and integrate ADCRA into commercial or proprietary workflows.

---

<div align="center">
Built with precision for the future of autonomous creative production.
</div>
