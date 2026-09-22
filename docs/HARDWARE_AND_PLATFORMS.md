# Hardware Requirements & Platform Deployment Guide
## ADCRA — Autonomous Digital Campaign & Creative Production System

ADCRA is engineered with an adaptive **Dual-Engine Architecture**. It runs seamlessly across a wide spectrum of environments, from lightweight cloud servers (CPU-only) up to multi-GPU creative editing workstations.

---

## 1. Deployment Profiles & Hardware Tiers

Choose the deployment profile that matches your organization's infrastructure and goals:

### Tier 1: Headless Cloud Server (Zero-GPU / Docker / CI/CD)
> **Best for:** Web apps, SaaS backends, automated social media video generation, budget cloud hosting.

- **CPU:** 4 to 8 virtual cores (x86_64 AMD/Intel or ARM64 Graviton/Ampere).
- **RAM:** 8 GB minimum (16 GB recommended for concurrent 1080p renders).
- **GPU:** None required. Renders using Remotion, HyperFrames, and FFmpeg via CPU software rasterization (SwiftShader/OSMesa).
- **Storage:** 20 GB SSD.
- **Estimated Cloud Cost:** $10 – $40 / month (e.g., Hetzner CPX31, DigitalOcean Droplet, AWS t3.xlarge).

---

### Tier 2: Creative Workstation (NVIDIA CUDA / Linux or Windows WSL2)
> **Best for:** Boutique agencies, high-throughput commercial production, hybrid DaVinci + Remotion rendering.

- **CPU:** 8+ physical cores (AMD Ryzen 7/9, Intel Core i7/i9).
- **RAM:** 16 GB to 32 GB DDR4/DDR5.
- **GPU:** NVIDIA GPU with 4 GB+ VRAM.
  - *Minimum Tested:* NVIDIA GeForce GTX 750 Ti 4GB (GM107 Maxwell).
  - *Recommended:* NVIDIA RTX 3060 (12GB), RTX 4070/4080/4090 (16-24GB).
- **Software:** Linux (Ubuntu 22.04 LTS) or Windows 11 with WSL2.
- **DaVinci Resolve:** DaVinci Resolve Studio 18, 19, or 21 (Optional, for advanced Fairlight audio mixing and Fusion 3D graphics).

---

### Tier 3: Apple Silicon Mac (M1 / M2 / M3 / M4)
> **Best for:** Solo creators, video directors, in-house marketing teams using macOS.

- **Processor:** Apple M1, M2, M3, or M4 (Base, Pro, Max, or Ultra).
- **Unified Memory:** 16 GB unified memory minimum (32 GB+ recommended for 4K video exports).
- **GPU Acceleration:** Handled automatically via Apple Metal and VideoToolbox hardware encoders (`h264_videotoolbox`, `hevc_videotoolbox`).
- **DaVinci Resolve:** DaVinci Resolve Studio for Mac supported natively via Apple Silicon API.

---

## 2. Hardware Probe & Auto-Detection Engine

ADCRA includes an integrated **Hardware Probe** (`adcra/ai/hardware.py`). Upon startup or when executing video operations, the system scans the host environment:

```bash
# Query hardware status via REST API
curl -s http://localhost:8080/api/health
```

Output:
```json
{
  "status": "HEALTHY",
  "system_version": "1.0.0-gold",
  "cpu_cores": 8,
  "ram_total_gb": 8.65,
  "gpu_device": "GPU 0: NVIDIA GeForce GTX 750 Ti (UUID: GPU-748a0ca0-8645-103c-6f4d-18626e46537a)",
  "server_pid": 660915
}
```

### Auto-Configuration Logic:
1. **GPU Detected + DaVinci Scripting Available:** ADCRA enables the full Blackmagic Fusion, Fairlight, and Color Page pipeline.
2. **GPU Detected + No DaVinci:** ADCRA accelerates Remotion and FFmpeg using NVENC / CUDA hardware encoders (`h264_nvenc`).
3. **Apple Silicon Detected:** Accelerates rendering using macOS Metal and VideoToolbox.
4. **No GPU Detected (Headless Cloud):** Automatically switches to multi-threaded CPU rendering with optimized FFmpeg filtergraphs.

---

## 3. DaVinci Resolve Studio Integration

### Do you need DaVinci Resolve Studio?
- **NO**, it is completely optional. ADCRA produces broadcast-quality MP4/H.264 video deliverables in 16:9, 9:16, and 1:1 using its built-in Remotion and FFmpeg engines.
- **YES**, if your workflow requires:
  - Exporting native DaVinci project files (`.drp`).
  - Editing timelines interactively inside DaVinci Resolve.
  - Multi-track Fairlight DAW audio mastering with third-party VST/AU plugins.
  - Advanced 32-bit floating point HDR color grading nodes and DaVinci YRGB Color Managed timelines.

### Enabling DaVinci Resolve Studio Scripting:
1. Open DaVinci Resolve Studio.
2. Go to **Preferences > System > General**.
3. Under **External scripting using**, select **Local** (or **Network** if connecting remotely).
4. Verify environment variable paths in `.env`:
   - **Linux:** `RESOLVE_SCRIPT_API=/opt/resolve/libs/Fusion`
   - **macOS:** `RESOLVE_SCRIPT_API=/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion`
   - **Windows:** `RESOLVE_SCRIPT_API=C:\Program Files\Blackmagic Design\DaVinci Resolve`

---

## 4. Cloud VM Deployment Recommendations

When provisioning virtual machines on public clouds:

| Cloud Provider | Recommended Instance | Specifications | Notes |
|---|---|---|---|
| **Hetzner Cloud** | `CPX31` or `CCX33` | 4–8 vCPU, 8–16 GB RAM | Best value for CPU-based rendering ($15–$30/mo) |
| **AWS EC2** | `g4dn.xlarge` | 4 vCPU, 16 GB RAM, 1x NVIDIA T4 (16GB) | Ideal for GPU NVENC rendering ($0.526/hr) |
| **Google Cloud** | `g2-standard-4` | 4 vCPU, 16 GB RAM, 1x NVIDIA L4 (24GB) | State-of-the-art AI video processing ($0.70/hr) |
| **DigitalOcean** | 8 GB / 4 vCPU Droplet | 4 vCPU, 8 GB RAM | Simple, reliable headless hosting ($48/mo) |

---

## 5. Summary Matrix: Feature Availability by Platform

| Capability | Headless CPU | NVIDIA GPU (CUDA) | Apple Silicon (Metal) | DaVinci Studio Workstation |
|---|:---:|:---:|:---:|:---:|
| **17-Step Intake Wizard** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Multi-Agent Brain** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Beat & Audio Analysis** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Creative Experiments** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Social Video Renders** | ✅ Fast (FFmpeg) | ⚡ Ultra-Fast (NVENC) | ⚡ Ultra-Fast (VideoToolbox) | ⚡ Studio Grade (Native) |
| **32-Bit HDR Color Nodes** | ❌ (Emulated LUTs)| ❌ (Emulated LUTs) | ❌ (Emulated LUTs) | 🌟 Native Color Page |
| **Fairlight DAW Mastering** | ❌ (FFmpeg Audio)| ❌ (FFmpeg Audio) | ❌ (FFmpeg Audio) | 🌟 Native Fairlight |
| **Interactive UI** | ✅ Web Port 8080 | ✅ Web Port 8080 | ✅ Web Port 8080 | ✅ Web + Local GUI |
