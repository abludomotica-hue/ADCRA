# ADCRA v2.1 — AUDITORÍA EXHAUSTIVA DE ARQUITECTURA & ESTADO REAL

**Documento:** `docs/architecture/ADCRA_V2_1_AUDIT.md`  
**Versión Objetivo:** ADCRA v2.1 (Creative Operating System & Real Execution Platform)  
**Fecha de Auditoría:** 2026-09-21  
**Auditor:** Principal Software Architect + Platform & Security Engineer  
**Estado del Repositorio:** 338 tests pasando (0 fallos, 0 errores)  
**Principio Rector:** *"No data may be presented as real unless it is backed by real system state."*

---

## 1. ESTADO ACTUAL DEL REPOSITORIO

El repositorio **ADCRA** (Autonomous Digital Campaign & Creative Production System) contiene una suite de control conceptual y de orquestación de alto nivel con una arquitectura modular orientada a campañas digitales y flujos audiovisuales.

### Métricas de Código y Verificación:
- **Test Suite Actual:** 338 tests ejecutados vía `python3 -m unittest discover -s tests -q` en 25.3s.
- **Resultado:** **338 OK (0 failures, 0 errors, 0 regressions)**.
- **Archivos de Test:** 60 archivos en `tests/` cubriendo fases de UI (01 a 22), análisis de audio, síntesis de video, grading, control de calidad tricameral, integración DaVinci/Remotion y el AI Control Plane v2.0 recientemente introducido.
- **Punto de Entrada del Servidor:** `dashboard_server.py` (2,571 líneas en un único archivo HTTP server con `http.server.HTTPServer`).
- **Puntos de Entrada Web:**
  - `web/index.html` + `web/app.js` (Dashboard de Misión / Pilot Delivery de Locos Materos).
  - `web/intake.html` + `web/intake.js` + `web/intake.css` (Campaign Intake Studio + AI Brain Control Center).
- **Capa AI:** `adcra/ai/` con 24 módulos y 5 adaptadores de proveedores (`mock`, `openai`, `gemini`, `anthropic`, `openrouter`).

---

## 2. ARQUITECTURA ACTUAL

La arquitectura presente en el repositorio opera en dos niveles:

1. **Pipeline Audiovisual y de Campaña (Legacy v1.0 / v2.0):**
   - Definido en torno a carpetas estáticas en `campaign/`: `audio/`, `creative/`, `storyboard/`, `timeline/`, `color/`, `motion-graphics/`, `deliverables/`, `reports/`, `memory/`.
   - Contratos JSON validados por JSON Schema en `config/` (25 esquemas canónicos).
   - Servidor HTTP embebido en `dashboard_server.py` que sirve endpoints REST monoliticos y estáticos.

2. **AI Intelligence Control Plane v2.0:**
   - **Capability Registry** (`adcra/ai/capabilities.py`): Catálogo canónico de 24 capacidades con dependencias, fallback chains y hardware hooks.
   - **Brain Federation** (`adcra/ai/brains.py`): 11 perfiles de directores cognitivos con handoffs formales y matriz de capacidades requeridas.
   - **Model Policy Engine & Router** (`adcra/ai/policies.py`, `adcra/ai/router.py`): Enrutamiento multidimensional basado en políticas (`QUALITY_FIRST`, `COST_OPTIMIZED`, `BALANCED`, etc.).
   - **Health Monitor & Circuit Breakers** (`adcra/ai/health.py`): Máquina de estados `CLOSED` -> `OPEN` -> `HALF_OPEN` con percentiles de latencia P50/P90/P95.
   - **Runtime & Fallback** (`adcra/ai/runtime.py`): Entidad `AIRun` en memoria, enmascaramiento de secretos por regex (`SecretRedaction`), y fallback en cascada.
   - **Cost Ledger & Budget Engine** (`adcra/ai/cost.py`): Registro inmutable en `campaign/reports/ai-cost-ledger.json`.
   - **Orchestrator** (`adcra/ai/orchestrator.py`): Cadena de intención -> plan -> contexto -> ejecución de herramientas/modelos -> memoria.

---

## 3. COMPONENTES REUTILIZABLES (PRESERVAR SIN REESCRIBIR)

Los siguientes componentes están sólidamente construidos, cuentan con pruebas unitarias exhaustivas y deben ser preservados y extendidos:

1. **`adcra/ai/capabilities.py` (CapabilityRegistry & DiscoveryEngine):**
   - Sistema canónico de capacidades con categorías (`CREATIVE`, `STRATEGY`, `MEDIA`, `PRODUCTION`, `ANALYSIS`).
   - Totalmente reutilizable. Extender con `discover_capabilities()` dinámico conectado a proveedores reales.

2. **`adcra/ai/brains.py` (BrainRegistry & BrainFederationEngine):**
   - 11 perfiles de directores cognitivos, dependencias cruzadas y handoffs.
   - Reutilizable intacto como especificación de agentes en el Control Plane.

3. **`adcra/ai/health.py` (ProviderHealthMonitor & CircuitBreaker):**
   - Lógica impecable de disyuntores de circuito (`CLOSED`, `OPEN`, `HALF_OPEN`) con ventana deslizante de latencias.
   - Reutilizable para evaluar estado de salud real (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`, `UNKNOWN`).

4. **`adcra/ai/policies.py` (ModelPolicyEngine):**
   - Algoritmos de scoring multidimensional y resolución de aliases lógicos.
   - Reutilizable en el router.

5. **`adcra/ai/cost.py` (AICostLedger & BudgetEngine):**
   - Registro de uso y verificación de presupuesto.
   - Reutilizable; extender para etiquetar `KNOWN_COST`, `ESTIMATED_COST`, `UNKNOWN_COST`.

6. **`adcra/ai/permissions.py` & `adcra/ai/approval.py`:**
   - Motores de permisos de rol y solicitud/aprobación de acciones críticas (gastos, publicaciones, eliminaciones).
   - Reutilizable para gobernar las ejecuciones durables del Execution Plane.

7. **`adcra/ai/types.py`:**
   - Definiciones estándar (`AIRequest`, `AIResponse`, `AIMessage`, `TaskType`, `ModelCapability`).
   - Reutilizable; extender con estados de proveedor y tipos de evento.

---

## 4. COMPONENTES INCOMPLETOS O CON GAPS

1. **Conectividad Real de Proveedores (`adcra/ai/gateway.py` y adaptadores):**
   - **Gap:** `AIProviderAdapter.validate_configuration()` solo verifica si `self._api_key` tiene longitud > 5 (`has_key = bool(self._api_key and len(self._api_key) > 5)`). No realiza peticiones HTTP reales a OpenAI, Gemini o Anthropic.
   - **Gap:** No existen llamadas reales a `test_connection()` ni descubrimiento dinámico de modelos (`list_models()` devuelve un array estático quemado en código).
   - **Gap:** Si no hay API key, no distingue entre `NOT_CONFIGURED`, `AVAILABLE`, `CONFIGURED`, `CONNECTING`, `CONNECTED`, `HEALTHY`, `DEGRADED`, `UNAVAILABLE`, `DISABLED`, `ERROR`.

2. **Gestión de Secretos (`adcra/ai/runtime.py`):**
   - **Gap:** `SecretProvider` actual solo ejecuta `os.environ.get(key_name, default)`. No permite guardar, actualizar, verificar existencia, ni gestionar credenciales cifradas localmente de forma segura.

3. **Plataforma de Clientes y Campañas:**
   - **Gap Conceptual Grave:** No existe una entidad `Client` independiente y persistente. Solo existe un archivo estático `campaign/memory/brand-profile-memory.json` perteneciente a una única campaña piloto ("Locos Materos").
   - **Gap:** Las campañas son huérfanas o globales; el sistema carece de almacenamiento multi-cliente y multi-campaña aislado.
   - **Gap:** No hay snapshot histórico formal de contexto al momento de iniciar una campaña (`CampaignContextSnapshot`).

4. **Execution Plane y Durable AI Runs:**
   - **Gap:** `AgentRuntime` almacena los runs en un diccionario volátil en memoria (`self._runs: Dict[str, AIRun] = {}`). Si el servidor se reinicia, todos los runs activos o completados se pierden.
   - **Gap:** No hay checkpoints por tarea ni mecanismo de reanudación (`resume`) ni cancelación (`cancel`).
   - **Gap:** No existe cola de trabajos (`JobQueue`).
   - **Gap:** No existe un bus de eventos reactivo (`EventBus`).

5. **Monolito de API (`dashboard_server.py`):**
   - **Gap:** 2,571 líneas de código donde coexisten rutas de intake, rutas de análisis audiovisual, rutas de IA, utilidades de archivos y CORS en un switch gigante de `if/elif`.
   - **Solución:** Reorganizar modularmente en sub-enrutadores (`adcra/api/routes/`) sin romper compatibilidad.

---

## 5. MOCKS, FAKE STATE Y HARDCODED DATA DETECTADOS

Siguiendo la **Regla Absoluta** (*"No data may be presented as real unless it is backed by real system state"*), se auditaron las siguientes inconsistencias:

| Ubicación | Estado Ficticio Detectado | Causa Raíz | Acción Requerida en v2.1 |
|---|---|---|---|
| `adcra/ai/__init__.py` (L70-80) | Registra automáticamente 5 adaptadores (`mock`, `openai`, `gemini`, `anthropic`, `openrouter`) en el gateway global. | Todos los adaptadores figuran en `list_providers()` sin importar si tienen credenciales o no. | Registrar adaptadores como `AVAILABLE` y marcar estado como `NOT_CONFIGURED` si no hay credenciales válidas. |
| `adcra/ai/adapters/*.py` | `validate_configuration()` retorna `CONNECTED` si `len(api_key) > 5`. | Validación puramente sintáctica sin test de red ni autenticación real. | Reemplazar por handshake real contra el endpoint de salud/modelos del proveedor. |
| `adcra/ai/router.py` (L165-175) | Si no hay proveedores conectados, cae en Mock silenciosamente. | Emergency fallback automático que simula una respuesta sin advertir al usuario. | Emitir `NO_CAPABLE_PROVIDER_AVAILABLE` o requerir modo explícito `SIMULATION_MODE`. |
| `web/intake.html` (L260-310) | `id="aiProvidersActiveCount">5 Activos</span>` y badges `OPERATIVO`/`STANDBY` fijos en HTML. | Marcado HTML inicial con datos duros antes de la consulta al backend. | Renderizar dinámicamente desde backend: "0 Configurados, 0 Conectados" cuando no haya ninguno. |
| `web/intake.js` (L39950) | Si `this.clientsList` está vacío, inyecta `[{id: 'locos-materos', name: 'Locos Materos'}]`. | Fallback en frontend para no mostrar pantalla vacía. | Mostrar Estado Vacío real (*Empty State*): "No clients yet. [+ New Client]". |
| `web/intake.js` (L16347) | Asigna `legal_name = 'Locos Materos SpA'` y `website_url = 'https://locosmateros.cl'` por defecto. | Datos quemados en el formulario de creación. | Inicializar campos en blanco (`""`) o `null` si no provienen de un cliente seleccionado. |
| `dashboard_server.py` (L720) | `handle_api_intake_clients` sintetiza el cliente `locos-materos` leyendo un único archivo de memoria. | Carencia de un repositorio de persistencia de clientes. | Implementar repositorio de clientes persistente en disco (`campaign/clients/`). |
| `web/index.html` (L100-150) | Tarjetas métricas con `100.0%`, `100.0 / 100`, `-12.7 LUFS` fijadas en HTML estático. | Datos del piloto de demostración mostrados como métricas en vivo. | Cargar dinámicamente del reporte de QC o mostrar `NO_DATA` si no hay corrida. |

---

## 6. DEPENDENCIAS Y ENTORNO

- **Python:** 3.13.5 en Linux x86_64.
- **Librerías instaladas:** `jsonschema`, `psutil`, `requests`, `urllib3`, `numpy`, `scipy`, `soundfile`, `Pillow`.
- **Herramientas de medios del sistema:** `ffmpeg`, `ffprobe` detectadas y funcionando en el probe de hardware.
- **Node.js / Remotion:** Disponible en el sistema.
- **DaVinci Resolve:** Scripting API presente (`RESOLVE_SCRIPT_API`).
- **Restricción de Entorno Identificada:** El directorio de trabajo `/home/ablutech/Documentos/davinci resolve` es un enlace simbólico a `/data/usuario/Documentos/davinci resolve`. La creación y modificación de archivos debe realizarse asegurando compatibilidad de rutas canónicas y sin violar políticas del entorno.

---

## 7. RIESGOS IDENTIFICADOS

1. **Riesgo de Regresión en Pruebas Unitarias:**
   - Existen 338 pruebas existentes que dependen de estructuras de datos actuales, incluyendo `test_phase_ui03_client_onboarding.py` que valida la existencia del cliente legado `locos-materos`.
   - *Mitigación:* Crear una estrategia de compatibilidad hacia atrás: los endpoints legados (`/api/intake/clients`, `/api/status`) deben seguir respondiendo con los datos históricos migrados a un cliente `legacy`, mientras los nuevos endpoints (`/api/clients`, `/api/campaigns`) exponen el nuevo modelo multi-tenant estricto.

2. **Riesgo de Fuga de Credenciales (Secret Leakage):**
   - Almacenar API keys en texto plano o enviarlas accidentalmente a la UI o en traces de auditoría.
   - *Mitigación:* Diseñar `EncryptedLocalSecretStore` o `FileSecretStore` con permisos de lectura `0600`, redacción estricta en respuestas JSON (nunca retornar API keys, solo `configured: true`, `masked_key: "sk-...abcd"`), y pruebas de seguridad automatizadas en `tests/security/`.

3. **Riesgo de Bloqueo por Fallos de Red en Tests:**
   - Pruebas que intenten conectarse a internet fallarán o tardarán indefinidamente.
   - *Mitigación:* Separar pruebas de contrato (`contract`) con mocks controlados de pruebas de integración en vivo (`live`), que se omitirán (`SKIP`) si no existen credenciales reales en el entorno.

---

## 8. GAPS RESPECTO A LOS CINCO PILARES DE ADCRA v2.1

### Pilar 1: Real AI Provider Connectivity
- [x] Abstracción base de adaptador (`AIProviderAdapter`).
- [ ] Validación de conexión en vivo (`test_connection()` real con handshake HTTP).
- [ ] Estados canónicos: `NOT_CONFIGURED`, `CONFIGURED`, `CONNECTING`, `CONNECTED`, `HEALTHY`, `DEGRADED`, `UNAVAILABLE`, `DISABLED`, `ERROR`.
- [ ] Descubrimiento dinámico de modelos (`discover_models()`).
- [ ] Descubrimiento dinámico de capacidades (`discover_capabilities()`).
- [ ] Almacenamiento seguro de secretos (`SecretProvider` con persistencia local encriptada/restringida).
- [ ] Contract tests estandarizados para todos los proveedores.

### Pilar 2: Real Client Platform
- [ ] Entidad de dominio `Client` con ciclo de vida completo (Identity, Brand DNA, Products, Audiences, Assets).
- [ ] Repositorio persistente de clientes (`ClientRepository`).
- [ ] Memoria persistente y aislada de cliente (`ClientMemory`).
- [ ] Endpoints REST canónicos (`GET/POST/PATCH/DELETE /api/clients`).
- [ ] UI de gestión de clientes con Estado Vacío real.

### Pilar 3: Real Campaign Platform
- [ ] Entidad de dominio `Campaign` con relación obligatoria `client_id`.
- [ ] Aislamiento de datos: Campaign A nunca comparte memoria con Campaign B.
- [ ] Herencia contextual: Campaña hereda Brand DNA por referencia y registra modificaciones delta.
- [ ] `CampaignContextSnapshot` para reproducibilidad inmutable.
- [ ] Eliminación de variable global mutable `currentCampaign`; uso de `active_campaign_id` contextualizado.
- [ ] Endpoints REST canónicos (`GET/POST/PATCH/DELETE /api/campaigns`).

### Pilar 4: Execution Plane & Durable Runs & Event Bus
- [ ] Desacoplamiento estricto de Control Plane vs Execution Plane.
- [ ] Entidad `DurableRun` con checkpoints transaccionales por paso del `TaskGraph`.
- [ ] Reanudación de runs tras reinicio del servidor (`resume_run`).
- [ ] Abstracción de cola de trabajos (`JobQueue`).
- [ ] Bus de eventos desacoplado (`EventBus`) con eventos canónicos (`ai.run.*, brain.*, provider.*, qc.*`).
- [ ] Streaming de eventos en tiempo real hacia la UI (SSE / WebSocket).

### Pilar 5: Production Hardening & Reality Verification
- [ ] Suite de pruebas de realidad (`tests/reality/`) que valida 0 datos ficticios.
- [ ] Suite de pruebas de seguridad (`tests/security/`) para secrets, path traversal y tenant isolation.
- [ ] Manejador estructurado de errores con códigos estándar (`PROVIDER_NOT_CONFIGURED`, etc.).
- [ ] Refactorización modular de rutas en `dashboard_server.py`.

---

## 9. PROPUESTA DE ARQUITECTURA ADCRA v2.1

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                ADCRA UI                                     │
│  Campaign Studio · Client Manager · Brain Center · Execution Viewer         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / SSE
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API LAYER (REST / SSE)                           │
│  /api/clients   /api/campaigns   /api/ai/providers   /api/ai/runs   /api/events
└──────────────────┬───────────────────────────────────────────┬──────────────┘
                   │                                           │
                   ▼                                           ▼
┌─────────────────────────────────────┐     ┌─────────────────────────────────┐
│           CONTROL PLANE             │     │         EXECUTION PLANE         │
│                                     │     │                                 │
│ · Intent Engine                     │     │ · Job Queue (in-memory/durable) │
│ · Brain Federation                  │     │ · Durable Run Coordinator       │
│ · Capability Registry               │     │ · Task Graph Execution Engine   │
│ · Model Router & Policies           │     │ · Checkpoint Store              │
│ · Provider Health & Circuit Breakers│     │ · Tool Execution & Media Pipe   │
│ · Permissions & Approvals           │     │ · Retry & Fallback Coordinator  │
│ · Cost Ledger (Real/Estimates)      │     │ · Event Bus (Pub/Sub)           │
│ · Memory Governance (Client/Camp)   │     │ · Worker Pool                   │
└──────────────────┬──────────────────┘     └─────────────────┬───────────────┘
                   │                                          │
                   └───────────────────┬──────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE & PERSISTENCE                       │
│                                                                             │
│ · SecretProvider (Secure local keystore / Env fallback)                     │
│ · ClientRepository (storage/clients/<client_id>/client.json)                │
│ · CampaignRepository (storage/clients/<client_id>/campaigns/<camp_id>/)     │
│ · DurableRunRepository (storage/runs/<run_id>.json)                         │
│ · EventBus (In-process subscription + SSE push)                             │
│ · AI Provider Adapters (OpenAI, Gemini, Anthropic, OpenRouter, Mock)        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. ESTRATEGIA DE COMPATIBILIDAD Y MIGRACIÓN

1. **Migración de Datos Existentes:**
   - La campaña existente "Locos Materos" y sus archivos en `campaign/` se migran automáticamente al cliente inicial persistido:
     - `client_id`: `locos-materos`
     - `campaign_id`: `camp_locos_materos_2026`
   - Se crea el directorio persistente estructurado:
     - `storage/clients/locos-materos/client.json`
     - `storage/clients/locos-materos/brand_dna.json`
     - `storage/clients/locos-materos/campaigns/camp_locos_materos_2026/campaign.json`
2. **Compatibilidad con Tests Existentes:**
   - Los endpoints `/api/intake/clients`, `/api/intake/draft`, `/api/status`, `/api/deliver`, etc. mantendrán su contrato intacto mapeando internamente a los repositorios persistentes.
   - De esta forma, los **338 tests existentes** seguirán pasando al 100% sin ninguna regresión.
3. **Nuevos Endpoints v2.1:**
   - Se introducen las rutas canónicas `/api/clients`, `/api/campaigns`, `/api/ai/providers/{id}/configure`, `/api/ai/providers/{id}/test`, `/api/ai/providers/{id}/discover-models`, `/api/ai/runs`, `/api/events`.

---

## 11. PLAN DE FASES DE IMPLEMENTACIÓN

- **Fase 1:** Reality Model & Limpieza de Estado Falso (Eliminar hardcoded counts en HTML/JS).
- **Fase 2:** Infraestructura de Secretos & Configuración Segura (`SecretProvider` con almacenamiento seguro).
- **Fase 3:** Conectividad Real de Proveedores de IA (Handshakes reales, estados `NOT_CONFIGURED` a `HEALTHY`, test de conexión y contract tests).
- **Fase 4:** Descubrimiento Dinámico de Modelos y Capacidades.
- **Fase 5:** Plataforma Persistente de Clientes (Entidad, repositorio, memoria y endpoints REST).
- **Fase 6:** Plataforma Persistente de Campañas (Entidad, pertenencia a cliente, herencia delta, snapshots).
- **Fase 7:** Execution Plane & Durable AI Runs (Checkpoints, reanudación, cola de tareas).
- **Fase 8:** Event Bus & Transmisión de Eventos en Tiempo Real (SSE).
- **Fase 9:** Integración de UI (Empty states reales, Provider Connection Center, switch de clientes/campañas).
- **Fase 10:** Seguridad, Pruebas de Realidad (`tests/reality/`) y Verificación Final de Cero Regresiones.

---
*Fin del informe de auditoría — Procediendo a la formulación del Implementation Plan formal.*
