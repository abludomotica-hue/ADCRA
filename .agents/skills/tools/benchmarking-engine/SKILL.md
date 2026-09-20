---
name: benchmarking-engine
description: Motor de evaluación de rendimiento, latencia y stress-testing para los subsistemas de ADCRA
domain: tools
version: 1.0.0
author: ADCRA Core Architecture Team
---

# Benchmarking Engine (Fase 22)

## Propósito
El motor `benchmarking-engine` ejecuta pruebas de micro-rendimiento y profiling sobre todos los motores del sistema ADCRA:
1. Análisis sensorial de audio y detección rítmica.
2. Motor de generación de storyboard cinemático.
3. Pipeline de color grading matemático (ACEScc / CDL / LUTs).
4. Motor de masterización Fairlight (EBU R128 / ITU-R BS.1770).
5. Compositor y sintetizador de overlays gráficos (Remotion / HyperFrames).
6. Motor de auditoría y certificación de Control de Calidad (QC).
7. Transcodificador multi-formato de entrega omnicanal.
8. Sintetizador de meta-habilidades (Skill Synthesizer & AST validator).

## Capacidades
- **Medición de latencia precisa:** `mean`, `min`, `max`, `p95` en milisegundos con alta resolución (`time.perf_counter_ns`).
- **Monitoreo de huella de memoria:** Deltas de consumo en MB (`tracemalloc`).
- **Throughput:** Cálculo de operaciones por segundo (`ops/sec`).
- **Certificación de grado de rendimiento:** Asignación de rating (`EXCELLENT`, `GOOD`, `SATISFACTORY`, etc.).
- **Validación de Schema:** Genera `campaign/reports/benchmarking-report.json` validado contra `config/benchmarking-schema.json`.

## Uso
```bash
python3 .agents/skills/tools/benchmarking-engine/scripts/run_benchmarks.py [--iterations N] [--output PATH]
```
