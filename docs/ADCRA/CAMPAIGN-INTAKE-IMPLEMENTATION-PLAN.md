# ADCRA — Campaign Intake Studio
## Plan Maestro de Implementación (CAMPAIGN-INTAKE-IMPLEMENTATION-PLAN)
**Versión:** 1.0.0 | **Estado:** APROBADA PARA EJECUCIÓN  
**Estrategia:** Desarrollo Fase por Fase con Verificación Estricta y Cero Regresiones  

---

## 1. Hoja de Ruta de las 22 Fases de Desarrollo

Cada fase debe implementarse de forma atómica y autosuficiente. Queda terminantemente prohibido saltar a la fase subsiguiente sin haber ejecutado las pruebas de lint, verificación de contratos, tests unitarios y comprobación visual en navegador de la fase activa.

| Fase | Denominación | Entregable Principal | Criterio de Verificación |
| :--- | :--- | :--- | :--- |
| **UI-01** | **Design System + Layout Base** | Layout tripartito (Progress, Workspace, AI Assistant) + Glassmorphism tokens | Responsive 100%, navegación de 17 pasos y contenedor agéntico |
| **UI-02** | **Campaign Wizard** | Motor de avance progresivo, autosave (500ms) y recuperación de sesión | Restauración de estado tras recarga sin pérdida de datos |
| **UI-03** | **Client Onboarding** | Selector [Nuevo Cliente] vs [Cliente Existente] + Rastreador de sitios web | Carga de memoria para existentes e inferencia web simulada |
| **UI-04** | **Brand Intake** | Brand Identity Studio (Logos, paleta HEX, claims, manuales PDF) | Drag & Drop funcional y validación de colores institucionales |
| **UI-05** | **Audience + Objective** | Matriz de 14 objetivos + Audience Builder (Primaria/Secundaria/Exploratoria) | Etiquetado estricto de sugerencias IA vs hechos confirmados |
| **UI-06** | **Product + Offer** | Ficha de productos/servicios múltiples + Oferta comercial o Branding | Prohibición de alucinación de beneficios o precios |
| **UI-07** | **Asset Upload + Intelligence**| Drag & Drop con probing técnico en tiempo real (FFprobe) | Detección de resolución, orientación, FPS, códec y badges |
| **UI-08** | **Audio Intake + Visualization** | Reproductor de audio, waveform, detector de BPM y sincronización de letra | Waveform interactiva y asignación de secciones musicales |
| **UI-09** | **Creative Direction** | Selector de 3 emociones primarias, takeaway clave y conceptos prohibidos | Validación de coherencia emocional y narrativa |
| **UI-10** | **Reference Board** | Moodboard de URLs/videos/imágenes con atributo de atracción | Catalogación estructurada de referencias de inspiración |
| **UI-11** | **Campaign Readiness** | Diagnóstico visual pre-flight (Readiness %, Blockers, Warnings) | Bloqueo de producción si existen Blockers no resueltos |
| **UI-12** | **Campaign Blueprint** | Documento visual integral previo a producción con Editar/Aprobar/Regenerar | Generación y exportación de ficha técnica ejecutiva |
| **UI-13** | **Agent Activity** | Consola de telemetría de agentes en vivo con estados reales (sin fake progress) | Monitoreo en tiempo real de qué agente está activo |
| **UI-14** | **Copy Lab** | Laboratorio de variantes de copy por escena con justificación estratégica | Selección A/B/C y regeneración contextual |
| **UI-15** | **Storyboard Lab** | Storyboard visual con reordenamiento drag & drop y recálculo de tiempos | Ajuste dinámico de timeline y cortes al mover escenas |
| **UI-16** | **Color/Sound/Motion** | Aprobación visual de LUTs 3D, mastering Fairlight y tipografía HyperFrames | Aprobación no destructiva con previsualización |
| **UI-17** | **QC Dashboard** | Auditoría tricameral desglosada (Técnico, Creativo, Marca, Legal) | Indicadores transparentes de no conformidad |
| **UI-18** | **Delivery Center** | Emisión y descarga del master 9:16 y los 5 formatos para redes sociales | Reproducción fluida y hashes SHA-256 verificables |
| **UI-19** | **Campaign History** | Vista histórica de campañas previas con lecciones aprendidas | Apertura y consulta de auditorías anteriores |
| **UI-20** | **Client Memory** | Persistencia vectorial y perfil episódico por cliente | Cero redundancia de preguntas para clientes recurrentes |
| **UI-21** | **Backend / Data Contracts** | Endpoints REST en `dashboard_server.py` y validación JSON Schema | Contratos formales Draft-07 pasando validación estricta |
| **UI-22** | **ADCRA Agent Integration** | Enlace orquestado con los 9 dominios de agentes existentes | Disparo de renderizado real de la nueva campaña creada |

---

## 2. Regla de Oro de Desarrollo

Para cada una de las fases:
1. **Implementación de Componentes y Estilos:** Limpio, modular, accesible.
2. **Pruebas Unitarias Automatizadas:** Agregar test suite específico en `tests/`.
3. **Verificación en el Servidor:** Comprobar que responde con HTTP 200/206 sin excepciones.
4. **Verificación en Navegador:** Validar que la interfaz se visualiza correctamente en `http://localhost:8080/intake.html` (o integrada en el dashboard).
5. **Actualización del Estado del Proyecto:** Registrar el avance en `docs/ADCRA/PROJECT_STATE.md`.
6. **Comprobación antes de avanzar:** Solo tras verificar con éxito la fase activa se avanza a la siguiente.
