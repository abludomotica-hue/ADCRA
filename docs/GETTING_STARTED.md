# Getting Started with ADCRA

Welcome to **ADCRA** (*Autonomous Digital Campaign & Creative Production System*)! This guide will walk you through setting up ADCRA on your machine or server, understanding the two primary production modes, and generating your first autonomous advertising campaign.

---

## 1. System Requirements at a Glance

| Component | Minimum (Headless / Cloud) | Recommended (Creative Workstation) |
|---|---|---|
| **Operating System** | Ubuntu 22.04+, Debian 12+, macOS 13+, Windows WSL2 | Ubuntu 22.04 LTS or macOS Sonoma |
| **CPU** | 4 Cores (x86_64 or ARM64) | 8+ Cores (AMD Ryzen / Intel Core i7+ / Apple M-series) |
| **RAM** | 8 GB | 16 GB - 32 GB |
| **GPU / VRAM** | None (CPU Software Rendering supported) | NVIDIA GPU 4GB+ VRAM (CUDA 12+) or Apple Silicon |
| **Disk Space** | 5 GB available | 50 GB+ SSD for high-res video assets |
| **Python** | 3.10, 3.11, 3.12, or 3.13 | 3.12 |
| **Node.js** | v18.0+ / v20.0+ | v20 LTS |
| **Multimedia Tools** | FFmpeg 6.0+ (`ffmpeg`, `ffprobe`) | FFmpeg 6.0+ + DaVinci Resolve Studio 18/19/21 |

---

## 2. Platform Installation Guides

### A. Linux (Ubuntu / Debian)

1. **Install System Dependencies and Multimedia Libraries**:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip ffmpeg libavcodec-extra curl git
   ```

2. **Install Node.js (v20 LTS)**:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

3. **Clone the Repository**:
   ```bash
   git clone https://github.com/abludomotica-hue/ADCRA.git
   cd ADCRA
   ```

4. **Set Up Python Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your favorite editor to add API keys (OpenAI, Gemini, Anthropic, etc.)
   nano .env
   ```

---

### B. macOS (Apple Silicon M1/M2/M3/M4 & Intel)

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Dependencies**:
   ```bash
   brew install python@3.12 node ffmpeg git
   ```

3. **Clone and Configure**:
   ```bash
   git clone https://github.com/abludomotica-hue/ADCRA.git
   cd ADCRA
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

---

### C. Windows (via WSL2 - Recommended)

1. Open PowerShell as Administrator and ensure WSL2 with Ubuntu is enabled:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```
2. Enter Ubuntu WSL terminal:
   ```bash
   wsl
   ```
3. Follow the **Linux (Ubuntu / Debian)** steps above. WSL2 supports direct NVIDIA GPU pass-through via the Windows NVIDIA driver without installing separate Linux display drivers.

---

## 3. Choosing Your Production Mode

ADCRA features a **Dual Hybrid Engine**:

### Mode 1: Cloud / Headless Mode (Zero Hardware Setup)
- Renders video via **Remotion**, **HyperFrames**, and **FFmpeg**.
- Runs in Docker containers, headless cloud VMs (AWS, GCP, Hetzner), and CI/CD pipelines.
- No display server or proprietary video editor required.
- Set in `.env`: `DEFAULT_RENDER_ENGINE=headless`.

### Mode 2: Workstation Studio Mode (DaVinci Resolve Studio)
- Connects directly to the **DaVinci Resolve Studio Python Scripting API**.
- Automates timeline assembly, Fairlight audio mixing, Fusion node animations, and Color Page HDR LUTs.
- Requirements:
  - DaVinci Resolve Studio 18, 19, or 21 installed.
  - In DaVinci Resolve: **Preferences > General > External scripting using: Local**.
  - Scripting libraries path set in `.env` (e.g. `/opt/resolve/libs/Fusion`).
- Set in `.env`: `DEFAULT_RENDER_ENGINE=hybrid`. (ADCRA will automatically use Resolve if open; otherwise it gracefully falls back to Remotion/FFmpeg).

---

## 4. Launching ADCRA Mission Control

Once dependencies are installed, you can launch the Mission Control Web UI and API server:

```bash
# Using the ADCRA CLI wrapper
./bin/adcra dashboard

# Or directly via Python
python3 dashboard_server.py --port 8080 --host 0.0.0.0
```

Open your browser to:
👉 **[http://localhost:8080](http://localhost:8080)**

You will be greeted by the **ADCRA Mission Control Center**, featuring:
- **Campaign Intake Wizard**: 17 structured steps to input brand persona, audience, visual tone, and target formats.
- **Copywriting Lab**: Multi-variant headline, script, and CTA generation with verbal economy controls.
- **Storyboard Lab**: Beat-synchronized shot list with scene-by-scene timing and camera direction.
- **Creative Experiment Lab**: Multi-variant matrix testing (A/B hooks, color grading, audio tracks).
- **Quality Control**: Automated pre-flight compliance audit checking safe zones, audio loudness (-14 LUFS), and brand safety.
- **Delivery Center**: Final MP4 render package, social cuts (9:16, 1:1, 16:9), and technical specification sheets.

---

## 5. Command-Line Interface (CLI) Guide

ADCRA includes a comprehensive CLI tool for headless automation and terminal workflows:

```bash
# Check system status across all 22 phases
./bin/adcra status

# Run performance and latency benchmarks
./bin/adcra benchmark --iterations 15

# Introspect registered agent tools and creative skills
./bin/adcra introspect

# Generate and inspect commercial delivery package
./bin/adcra deliver

# Run complete regression test suite (317 tests)
./bin/adcra test
```

---

## 6. Next Steps

- Explore the complete [Architecture Guide](ARCHITECTURE.md) to understand the Multi-Agent Brain and Epistemic Memory.
- Read the [Hardware & Platform Guide](HARDWARE_AND_PLATFORMS.md) for GPU tuning and VRAM optimization.
- Check the [API Reference](API_REFERENCE.md) to integrate ADCRA with external CRMs, frontend apps, or CI/CD pipelines.
- Learn how to create custom agents in [Extending ADCRA](EXTENDING_ADCRA.md).
