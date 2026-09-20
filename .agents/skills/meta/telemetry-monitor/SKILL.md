---
name: telemetry-monitor
description: Monitor de telemetría y salud operativa del pipeline ADCRA.
domain: meta
version: 1.0.0
schema: null
inputs:
  - campaign/
outputs:
  - campaign/meta/telemetry-monitor-output.json
---

# Telemetry Monitor Skill

## Propósito
Monitorea tiempos de ciclo, latencia de renderizado y disponibilidad de aceleración GPU/OpenCL.

---

## Arquitectura y Operación
- **Dominio:** `meta`
- **Versión:** `1.0.0`
- **Script Operacional:** `scripts/telemetry_collector.py`
- **Contrato Formal:** `null`

---

## Modos de Ejecución CLI
```bash
python3 .agents/skills/meta/telemetry-monitor/scripts/telemetry_collector.py --validate-only
python3 .agents/skills/meta/telemetry-monitor/scripts/telemetry_collector.py --run
```
