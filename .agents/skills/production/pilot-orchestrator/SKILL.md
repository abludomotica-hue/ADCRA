---
name: pilot-orchestrator
description: Orquestador maestro para la ejecución, auditoría y certificación end-to-end de la Campaña Piloto en ADCRA. Conecta en secuencia continua e ininterrumpida los dominios de estrategia, análisis sensorial, copywriting, diseño de storyboard, ensamblado rítmico, etalonaje, diseño sonoro, control de calidad, bucle de iteración, memoria de marca y telemetría.
domain: production
version: 1.0.0
schema: config/pilot-campaign-schema.json
inputs:
  - campaign/campaign-manifest.json
  - campaign/audio/audio-analysis.json
  - campaign/audio/lyric-alignment.json
  - campaign/assets/asset-inventory.json
  - campaign/creative/creative-copy.json
  - campaign/storyboard/storyboard.json
  - campaign/timeline/timeline.json
  - campaign/color/color-grading-manifest.json
  - campaign/audio/sound-design-manifest.json
  - campaign/deliverables/social-format-manifest.json
  - campaign/reports/quality-control-report.json
outputs:
  - campaign/pilot/pilot-campaign-manifest.json
  - campaign/pilot/pilot-run-report.json
---

# Pilot Campaign Orchestrator Skill

## Propósito
El **pilot-orchestrator** consolida la ejecución integral y autónoma de la **Campaña Piloto** en ADCRA (*Autonomous Digital Campaign & Creative Production System*). Su objetivo es garantizar que la totalidad de los módulos construidos a lo largo de las fases 1 a 19 operen de forma sinérgica, sin desvíos de metadatos, con 100% de coherencia técnica, creativa y de marca, y generando los entregables finales con certificación formal broadcast.

---

## Cadena Unificada de Producción E2E

```mermaid
graph TD
    A[1. Estrategia: Brief & Manifiesto] --> B[2. Análisis de Audio & Lírica]
    B --> C[3. Análisis de Metraje & Video]
    C --> D[4. Copywriting 5 Variantes]
    D --> E[5. Storyboard 9 Escenas]
    E --> F[6. Ensamblado & Timeline EDL/XML]
    F --> G[7. Color Grading 3D LUTs 5900K]
    G --> H[8. Sound Design Foley & EBU R128]
    H --> I[9. Formateador Safe Zones 9:16]
    I --> J[10. Quality Control Tricameral]
    J --> K[11. Iteration Engine Tope <= 3]
    K --> L[12. Memoria de Campaña & Telemetría]
    L --> M[Emisión de Manifiesto Piloto Certificado]
```

---

## Matriz de Verificación de Integridad Cruzada

Para declarar la campaña piloto como `COMPLETED` y `APPROVED`, el orquestador verifica:
1. **Duración Temporal Estricta:** La suma continua de los tiempos de corte de las 9 escenas coincide con 29.187s (delta < 0.05s).
2. **Sincronía Rítmica:** Todos los cortes de escena están indexados a los downbeats y compases de `Entre_mates_y_sol.mp3` (107.7 BPM).
3. **Identidad Cromática:** Las 9 escenas cuentan con corrección de color ligada a la temperatura cinematográfica de 5900K y LUTs 3D `.cube`.
4. **Acústica Broadcast:** La mezcla final `locos_materos_master_mix.wav/mp3` cumple la norma EBU R128 (-12.7 LUFS integrados, -1.0 dBTP ceiling).
5. **Auditoría Tricameral:** El Quality Score alcanza la máxima calificación (100.0/100.0) sin alertas rojas ni amarillas pendientes.
6. **Límite de Iteraciones:** El ciclo concluye en $\le 3$ iteraciones cumpliendo el invariante inquebrantable de ADCRA.

---

## Modos de Ejecución CLI

```bash
# Ejecutar y auditar la campaña piloto completa end-to-end
python3 .agents/skills/production/pilot-orchestrator/scripts/pilot_runner.py --run-pilot

# Validar el manifiesto formal de campaña piloto contra el esquema JSON
python3 .agents/skills/production/pilot-orchestrator/scripts/pilot_runner.py --validate-only
```
