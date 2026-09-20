---
name: creative-copy-engine
description: Motor de redacción publicitaria y copywriting multivariante para ADCRA. Genera obligatoriamente 5 variantes de copy por escena (emocional, publicitaria, conversacional, minimalista, identidad de marca), evalúa métricas de impacto y selecciona la variante ganadora con justificación estratégica.
---

# Creative Copy Engine — Redacción Publicitaria Multivariante

El **Creative Copy Engine** es la pluma publicitaria de ADCRA. Su principio rector es que el copy en pantalla nunca debe ser una transcripción literal de la canción ni un texto plano generado sin alternativas estratégicas. Cada escena publicitaria exige explorar diferentes registros tonales para encontrar la frase exacta que potencie la imagen y la música.

---

## 1. Los 5 Registros de Copywriting Obligatorios

Para cada escena del storyboard, el motor genera y califica obligatoriamente:

1. **`emocional`:**  
   Conexión afectiva profunda, empatía con el ritual humano, nostalgia positiva y pertenencia. Evaluado por `emotional_impact_score` (0 a 10).
2. **`publicitaria`:**  
   Enfoque persuasivo centrado en propuesta de valor, beneficio tangible y llamado a la acción comercial. Evaluado por `call_to_action_score` (0 a 10).
3. **`conversacional`:**  
   Lenguaje coloquial, auténtico, cercano y descontracturado, propio de cómo habla la gente real en Chile. Evaluado por `naturalness_score` (0 a 10).
4. **`minimalista`:**  
   Síntesis extrema de 1 a 3 palabras de alto impacto visual y lectura instantánea (ideal para retención en redes sociales). Evaluado por `word_count` (entero).
5. **`identidad_de_marca`:**  
   Resonancia directa con el tagline, el propósito corporativo y el territorio de marca de *Locos Materos*. Evaluado por `brand_alignment_score` (0 a 10).

---

## 2. Proceso de Selección y Justificación

- **Insumos de Contexto:**  
  Cada escena considera: descripción visual, música, lírica cantada, emoción objetivo, público meta, tono de marca y los copys de la escena anterior y posterior para asegurar fluidez narrativa.
- **Justificación Obligatoria (`selection_rationale`):**  
  El motor debe fundamentar por qué la variante elegida supera a las otras cuatro en esa escena específica dentro del arco general de la campaña.

---

## 3. Validación de Esquema (`config/creative-copy-schema.json`)

El archivo generado `campaign/creative/creative-copy.json` debe validar sin errores contra el esquema JSON Schema Draft-07 oficial.

---

## 4. Scripts e Interfaz CLI

- `scripts/generate_copy.py`:
  - Lee `campaign/storyboard/storyboard.json` y `campaign/campaign-manifest.json`.
  - Genera las 5 variantes para cada escena.
  - Valida contra `config/creative-copy-schema.json`.
  - Guarda el resultado en `campaign/creative/creative-copy.json`.
