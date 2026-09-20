# ADCRA — Campaign Intake Studio
## Especificación de Experiencia de Usuario e Interacción (CAMPAIGN-INTAKE-UX)
**Versión:** 1.0.0 | **Estado:** APROBADA PARA IMPLEMENTACIÓN  
**Sistema:** ADCRA (Autonomous Digital Campaign & Creative Production System)  

---

## 1. Filosofía de Diseño y Principios de UX

El **Campaign Intake Studio** está diseñado como un **Creative Operating System** para estrategas, directores creativos y marcas, distanciándose categóricamente de los CRMs corporativos saturados o los formularios interminables de 80 campos.

### Principios Fundamentales:
1. **Sensación de Construcción Progresiva:** El usuario experimenta que está *diseñando y esculpiendo* una campaña audiovisual, no rellenando una encuesta.
2. **Progressive Disclosure:** Cada etapa presenta únicamente las decisiones relevantes en el momento adecuado, revelando complejidad avanzada solo a demanda.
3. **Smart Defaults y Autocompletado Agéntico:** Las decisiones estándar (ej. 24 fps, EBU R128 -14 LUFS, safe zones automáticas) se configuran por defecto según el canal elegido.
4. **Respeto a la Verdad Epistemológica:** Toda sugerencia de la IA se etiqueta explícitamente como `AI SUGGESTION` o `AI INFERRED` y requiere aprobación expresa del usuario.
5. **Autosave Transparente y Draft Recovery:** Se guarda el estado localmente cada 500ms tras cualquier interacción, mostrando indicador sutil: *"Guardado hace 3 segundos"*.

---

## 2. Disposición del Layout Principal (Three-Zone Spatial Grid)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ADCRA  │  Campaign Intake Studio                  [Modo: Nuevo Cliente] [Guardado automático ✓]        │
├───────────────────┬────────────────────────────────────────────────────────────────────────────────────┤
│                   │                                                                                    │
│ CAMPAIGN PROGRESS │                               MAIN WORKSPACE                                       │
│                   │                                                                                    │
│ 01 Cliente      ✓ │   [Paso Activo: 04 Marca / Brand Identity Studio]                                  │
│ 02 Objetivo     ✓ │   ┌────────────────────────────────────────────────────────────────────────────┐   │
│ 03 Audiencia    ✓ │   │ Paleta de Color Institucional                                              │   │
│ 04 Marca        ● │   │ Primario: [#0D5C3A]  Secundario: [#D4AF37]  Acento: [#10B981]              │   │
│ 05 Producto    80%│   │                                                                            │   │
│ 06 Oferta       ○ │   │ Arrastra aquí logotipos (SVG/PNG), manuales de marca en PDF o fuentes:     │   │
│ 07 Creatividad  ⚠ │   │ ┌────────────────────────────────────────────────────────────────────────┐ │   │
│ 08 Audio        ✓ │   │ │   [ + ] Drag & Drop Brand Assets (Logos, Manuales, Fuentes)            │ │   │
│ 09 Video Assets ✓ │   │ └────────────────────────────────────────────────────────────────────────┘ │   │
│ 10 Referencias 40%│   └────────────────────────────────────────────────────────────────────────────┘   │
│ 11 Canales      ✓ │                                                                                    │
│ 12 Duración     ✓ │                                                                                    │
│ 13 CTA          ○ │                                                                                    │
│ 14 Restricciones✓ │                                                                                    │
│ 15 Automatización✓│                                                                                    │
│ 16 Readiness    ○ │                                                                                    │
│ 17 Blueprint    ○ │                                                                                    │
├───────────────────┴────────────────────────────────────────────────────────────────────────────────────┤
│ ⚡ AI CAMPAIGN ASSISTANT                                                                               │
│ "He detectado que el logotipo cargado está en formato JPG. Para generar overlays cinéticos en          │
│ HyperFrames sin fondo blanco, te sugiero adjuntar una versión en SVG vectorial o PNG transparente."    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Estados Semánticos en Campaign Progress

A diferencia de los indicadores porcentuales abstractos, cada uno de los pasos del Intake Studio comunica su estado cualitativo real:

| Estado | Indicador Visual | Significado |
|---|---|---|
| `COMPLETE` | `✓ Verde` | Información obligatoria y recomendada confirmada por el usuario. |
| `READY` | `● Dorado` | Requisitos mínimos cumplidos; listo para continuar o enriquecer. |
| `NEEDS_REVIEW` | `⚠ Ámbar` | Inconsistencia detectada o sugerencia de la IA pendiente de revisión. |
| `MISSING` | `○ Rojo tenue` | Campo o insumo crítico faltante (causa potencial de Blocker). |
| `OPTIONAL` | `— Gris neutro` | Módulo secundario no esencial para la modalidad de campaña. |

---

## 4. El Asistente Agéntico Contextual (AI Campaign Assistant)

Ubicado en la base de la pantalla, el asistente no es un chatbot de conversación vacía, sino un **monitor de diagnóstico proactivo en tiempo real**:

### Reglas de Operación del Asistente:
1. **Priorización por Severidad:**
   - `BLOCKER (Rojo)`: Falta de audio en comercial rítmico, resolución menor a 720p sin escalador, ausencia de producto en campaña de conversión.
   - `WARNING (Ámbar)`: Discrepancia entre la emoción del brief y el tempo de la música, logo en baja resolución, ausencia de URL para CTA.
   - `RECOMMENDATION (Azul)`: Oportunidad de adaptar a 16:9 con fondo difuminado, sugerencia de subtitulado dinámico para usuarios sin audio en redes.
2. **Acción Directa en un Clic:** Cada advertencia ofrece un botón de resolución rápida (ej. *[Auto-detectar con FFprobe]*, *[Sugerir Paleta]*, *[Ignorar advertencia]*).

---

## 5. Modos de Onboarding: Nuevo vs. Cliente Existente

### Modalidad [NUEVO CLIENTE]:
- Despliega el onboarding completo paso a paso (01 a 17).
- Habilita la herramienta **"Analizar Sitio Web"**: el usuario introduce una URL y el agente extrae propuesta de valor, colores predominantes, tipografías y enlaces a redes sociales, mostrándolos en un drawer de confirmación:
  `[ACEPTAR DETECCIONES] | [EDITAR PARÁMETROS] | [DESCARTAR]`

### Modalidad [CLIENTE EXISTENTE]:
- Presenta un selector de marcas registradas en `campaign/memory/brand-profile-memory.json`.
- Al seleccionar una marca (ej. *Locos Materos*), precarga instantáneamente:
  - Paleta institucional (`#0D5C3A`, `#D4AF37`).
  - Audiencia histórica y demografía validada.
  - Tono de voz consolidado y palabras clave prohibidas.
  - Assets de branding reutilizables (logos SVG, LUTs 3D `.cube` autorizadas).
- Los pasos completados pasan inmediatamente a `COMPLETE` y la UI enfoca al usuario directamente en: **Objetivo de la nueva campaña, nuevos assets y oferta específica**.

---

## 6. Las 17 Etapas de Construcción Progresiva

1. **Cliente:** Identificación, industria, contacto y rastreador agéntico web.
2. **Objetivo:** Selector visual de metas (Awareness, Conversión, Lanzamiento, etc.) y resultado deseado tras ver el anuncio.
3. **Audiencia:** Audience Builder tripartito (Primaria, Secundaria, Exploratoria) con sugerencias IA explícitamente etiquetadas.
4. **Marca:** Brand Identity Studio (propósito, valores, tono, palabras prohibidas, paleta HEX, logos y manuales).
5. **Producto / Servicio:** Ficha de producto con beneficios, características y claims permitidos (prohibido alucinar o inventar datos).
6. **Oferta:** Parámetros comerciales (precio, descuento, vigencia) o selector de *Branding Puro*.
7. **Creatividad:** Matriz de emociones clave (máx. 3), qué debe recordar el usuario y qué idea jamás debe transmitirse.
8. **Audio:** Audio Intake con drag & drop de MP3/WAV, extracción automática de BPM, waveform interactiva y letra sincronizable.
9. **Video Assets:** Asset Upload Studio con inspección FFprobe en vivo (resolución, FPS, orientación, tags de producto).
10. **Referencias:** Moodboard interactivo de enlaces o clips con etiqueta del atributo que gusta (color, ritmo, edición).
11. **Canales:** Matriz omnicanal (TikTok, Reels, Shorts, Feed 1:1, YouTube) o botón *Generar Todos Automáticamente*.
12. **Duración:** Selector 15s, 20s, 30s o sugerencia basada en la métrica del audio.
13. **CTA:** Constructor de llamados a la acción y canales de contacto (web, WhatsApp, app).
14. **Restricciones:** Brand safety, disclaimers legales, derechos de imagen y música.
15. **Presupuesto:** Opcional (medios, producción o campaña puramente orgánica).
16. **Nivel de Automatización:** Manual, Asistido, Autónomo, Autónomo + Aprobaciones.
17. **Puntos de Aprobación:** Checkboxes para compuertas de concepto, copy, storyboard y master final.

---

## 7. Cierre: Campaign Readiness Center & Campaign Blueprint

Antes de activar el renderizado o los agentes de producción:
- **Campaign Readiness Center:** Diagnóstico visual con porcentaje real de preparación, conteo de `Blockers`, `Warnings` y `Missing Optional`. Si existen Blockers, el botón de producción permanece deshabilitado.
- **AI Pre-Flight:** Ejecución de 10 pruebas automatizadas cruzando brief, assets y normas broadcast.
- **Campaign Blueprint:** Vista resumida integral que consolida todo el brief en un documento imprimible y editable antes de generar el `campaign-manifest.json` definitivo.
