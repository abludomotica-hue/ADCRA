---
name: campaign-memory
description: Sistema de memoria episódica y persistencia de aprendizajes cross-campaign para Locos Materos. Consolida lineamientos estéticos, patrones rítmicos óptimos, benchmarks de rendimiento y reglas de retención para futuras iteraciones creativas.
domain: memory
version: 1.0.0
schema: config/campaign-memory-schema.json
inputs:
  - campaign/campaign-manifest.json
  - campaign/audio/audio-analysis.json
  - campaign/timeline/timeline.json
  - campaign/color/color-grading-manifest.json
  - campaign/reports/quality-control-report.json
outputs:
  - campaign/memory/brand-profile-memory.json
---

# Campaign Memory System Skill

## Propósito
Preserva y capitaliza el conocimiento generado durante la producción de campañas publicitarias. Transforma los hallazgos técnicos, métricas de edición, decisiones cromáticas y reglas de marca en una base de memoria evolutiva reutilizable para maximizar la consistencia y la velocidad de entrega de futuras campañas de **Locos Materos**.

---

## Dimensiones del Perfil de Memoria de Marca

### 1. Aprendizajes Estéticos (Aesthetic Learnings)
- **Paleta de Identidad:** Consolidación de Verde Mate (`#0D5C3A`), Dorado Yerba (`#D4AF37`) y Carbón (`#1A1A1A`).
- **Colorimetría:** Calibración de temperatura de color objetivo en 5900K con curvas de contraste suaves.
- **Colección de LUTs Validadas:** Catálogo de LUTs 3D `.cube` (`locos_materos_warm_cinematic.cube`, `locos_materos_editorial_film.cube`, `locos_materos_master_grade.cube`).
- **Iluminación:** Preferencia por luz natural de hora dorada y luz matutina difusa (35mm / 50mm look analógico).

### 2. Aprendizajes Musicales y Ritmo de Edición (Musical & Tempo Learnings)
- **Rango de BPM Exitoso:** Rango óptimo identificado entre 100.0 y 115.0 BPM (último BPM calibrado: 107.7 BPM).
- **Métrica Rítmica:** Compás 4/4 con sincronización estricta de transiciones a downbeats musicales.
- **Duración Promedio de Escena:** 3.24 segundos por toma (700 cuadros / 9 escenas en 29.167s comerciales).
- **Estrategia de Montaje:** Hook de apertura en < 3.5s, progresión íntima y clímax social con remate publicitario.

### 3. Perfil de Audiencia y Contexto Cultural
- **Demografía:** Hombres y mujeres de 20 a 45 años, estudiantes universitarios y trabajadores en Santiago de Chile.
- **Psicografía:** Personas que buscan una pausa reflexiva en la rutina urbana, valorando la autenticidad, la conexión humana y el ritual del mate compartido.

### 4. Reglas de Retención y Restricciones Obligatorias
- **Reglas Mandatorias:** Mantener el mate físicamente verosímil (calabaza real, yerba con textura, agua humeante, bombilla inoxidable); safe zones respetadas en formatos verticales 9:16.
- **Patrones Prohibidos:** Prohibido deformar o inventar el logotipo oficial; prohibido el uso de CGI fantástico; prohibidos textos publicitarios sobre botones de interfaz móvil.

---

## Modos de Operación CLI
- `--record`: Ingesta los artefactos de la campaña actual y actualiza el perfil en memoria.
- `--query <topic>`: Realiza búsquedas temáticas (`color`, `tempo`, `rhythm`, `rules`, `audience`) para orientar nuevas sesiones de briefing.
- `--validate-only`: Valida formalmente el archivo de memoria contra `config/campaign-memory-schema.json`.
