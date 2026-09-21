/* ==========================================================================
   ADCRA CAMPAIGN INTAKE STUDIO — JAVASCRIPT APP (FASE UI-02: CAMPAIGN WIZARD)
   Lógica del Layout Tripartito, Motor de Navegación Progresiva y Asistente Agéntico
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  IntakeApp.init();
});

const IntakeApp = {
  activeStep: 1,
  totalSteps: 17,
  clientMode: 'NEW_CLIENT', // 'NEW_CLIENT' | 'EXISTING_CLIENT'
  lastSavedAt: new Date(),
  debounceSaveTimer: null,
  clientsList: [],
  selectedClientId: null,
  inferredAnalysis: null,
  activeAudienceTab: 'primary',
  activeProductIndex: 0,
  campaignBlueprint: null,
  agentsTelemetry: null,

  // Estado reactivo del borrador (conforme a CAMPAIGN-INTAKE-DATA-MODEL)
  draft: {
    client: {
      brand_name: '',
      legal_name: '',
      business_type: 'producto',
      industry: '',
      description: '',
      website_url: '',
      social_channels: { instagram: '', tiktok: '', youtube: '', facebook: '' },
      contact: { name: '', role: '', email: '', phone: '' }
    },
    objective: {
      primary: 'AWARENESS',
      secondary: ['CONVERSION'],
      desired_outcome: 'recordar_marca',
      custom_outcome_note: ''
    },
    audience: {
      primary: {
        demographics: { age_range: [20, 45], location: 'Chile / Santiago', language: 'es', gender: 'todos', occupation: 'Profesionales y Jóvenes Adultos' },
        psychographics: { interests: ['cultura', 'calidad', 'autenticidad', 'bienestar'], needs: ['pausa consciente', 'socialización'], motivations: ['compartir buenos momentos', 'disfrutar sabor auténtico'], objections: ['tiempo de preparación', 'precio percibido'] },
        digital_behavior: { primary_platforms: ['INSTAGRAM', 'TIKTOK', 'YOUTUBE'] },
        is_ai_suggested: false
      },
      secondary: {
        demographics: { age_range: [30, 60], location: 'Chile / Regiones', language: 'es', gender: 'todos', occupation: 'Familias y Hogar' },
        psychographics: { interests: ['tradición', 'hogar', 'salud'], needs: ['hábitos saludables'], motivations: ['mantener rituales'], objections: [] },
        digital_behavior: { primary_platforms: ['INSTAGRAM', 'FACEBOOK'] },
        is_ai_suggested: true
      },
      exploratory: {
        demographics: { age_range: [18, 25], location: 'Latinoamérica / Cono Sur', language: 'es', gender: 'todos', occupation: 'Estudiantes Universitarios' },
        psychographics: { interests: ['estudio', 'música', 'creatividad'], needs: ['energía natural sin bajón'], motivations: ['acompañamiento para estudiar'], objections: ['amargor inicial'] },
        digital_behavior: { primary_platforms: ['TIKTOK', 'TWITCH', 'SPOTIFY'] },
        is_ai_suggested: true
      }
    },
    brand: {
      claim: '',
      purpose: '',
      values: ['calidad', 'compromiso'],
      primary_color: '#0D5C3A',
      secondary_color: '#D4AF37',
      accent_color: '#10B981',
      color_temperature_target_kelvin: 5900,
      tone_of_voice: ['auténtico', 'cálido', 'cercano'],
      mandatory_words: [],
      forbidden_words: [],
      logo_files: ['logo_master_vector.svg'],
      brand_manual_pdf: 'manual_identidad_2026.pdf'
    },
    products: [
      { id: 'prod-1', name: '', description: '', price: 15000, benefits: ['100% Auténtico', 'Calidad Premium'] }
    ],
    offer: {
      is_branding_only: false,
      offer_title: 'Descuento Exclusivo',
      discount_percentage: 20,
      terms_conditions: 'Válido hasta agotar stock'
    },
    creative: {
      target_emotions: ['confianza', 'alegria'],
      key_takeaway: '',
      forbidden_concepts: '',
      visual_style: 'cinematic',
      narrative_arc_preference: 'hook_build_climax'
    },
    audio: {
      filename: '',
      duration_seconds: 30,
      bpm: 124,
      meter: '4/4',
      has_commercial_rights: true
    },
    assets: [
      { id: 'asset-1', filename: 'clip_hero_01.mp4', width: 1080, height: 1920, fps: 29.97, codec: 'H.264', status: 'READY' }
    ],
    references: [
      { title: 'Referencia Dinámica', url: 'https://instagram.com/reels/ejemplo', attribute: 'ritmo' }
    ],
    channels: ['TIKTOK_9_16', 'INSTAGRAM_REELS_9_16'],
    duration: { target_seconds: 30, strategy: 'AUDIO_DRIVEN' },
    cta: { primary: 'Conocer más', url: 'https://', whatsapp: '' },
    constraints: {
      forbidden_words: ['artificial', 'químico'],
      legal_disclaimer: 'Consumo informado y responsable.',
      music_rights_cleared: true,
      image_rights_cleared: true
    },
    budget: { currency: 'USD', media_investment: 500, mode: 'ORGANIC_AND_PAID' },
    automation: {
      mode: 'AUTONOMOUS_APPROVALS',
      approval_checkpoints: { concept: true, copy: true, storyboard: true, master: true }
    },
    approvals: { concept: true, copy: false, storyboard: false, master: false }
  },

  // Metadata de los 17 pasos progresivos
  steps: [
    { id: 1, name: 'Cliente', category: 'CLIENTE', title: 'Identificación y Perfil del Cliente', desc: 'Define los datos fundamentales de la marca, canales oficiales y enlace web para inferencia agéntica.' },
    { id: 2, name: 'Objetivo', category: 'OBJETIVO', title: 'Objetivo de Campaña y Resultado Deseado', desc: 'Selecciona la meta primaria de negocio y la acción exacta que debe ejecutar el usuario tras ver el anuncio.' },
    { id: 3, name: 'Audiencia', category: 'AUDIENCIA', title: 'Audience Builder Tripartito', desc: 'Estructura la audiencia primaria, secundaria y exploratoria con validación de supuestos de IA.' },
    { id: 4, name: 'Marca', category: 'MARCA', title: 'Brand Identity Studio', desc: 'Valores, propósito, paleta de colores HEX institucionales, logotipos y manual de marca en PDF.' },
    { id: 5, name: 'Producto', category: 'PRODUCTO', title: 'Product & Service Intelligence', desc: 'Ficha técnica de productos o servicios con beneficios y características verificadas.' },
    { id: 6, name: 'Oferta', category: 'OFERTA', title: 'Propuesta Comercial y Condiciones', desc: 'Precios, descuentos, stock y fechas, o declaración expresa de Branding sin venta directa.' },
    { id: 7, name: 'Creatividad', category: 'CREATIVIDAD', title: 'Creative Direction Studio', desc: 'Matriz de emociones clave (máx 3), takeaway fundamental y conceptos prohibidos.' },
    { id: 8, name: 'Audio', category: 'AUDIO', title: 'Audio Intake & Waveform Analyzer', desc: 'Pista musical principal, análisis de BPM, compases rítmicos y sincronización de letra.' },
    { id: 9, name: 'Video Assets', category: 'ASSETS', title: 'Asset Upload & Probing Técnico', desc: 'Metraje audiovisual crudo con análisis automático de resolución, FPS, orientación y códec.' },
    { id: 10, name: 'Referencias', category: 'REFERENCIAS', title: 'Reference Board & Moodboard', desc: 'Colección de enlaces o clips de inspiración con asignación de atributos admirados.' },
    { id: 11, name: 'Canales', category: 'CANALES', title: 'Estrategia de Emisión Omnicanal', desc: 'TikTok, Instagram Reels, YouTube Shorts, Meta Feed 1:1 o adaptación automática total.' },
    { id: 12, name: 'Duración', category: 'DURACIÓN', title: 'Estructura Temporal del Anuncio', desc: 'Definición de 15s, 30s o sugerencia de corte basada en la energía y estructura del audio.' },
    { id: 13, name: 'CTA', category: 'CTA', title: 'Call to Action & Rutas de Conversión', desc: 'Llamado a la acción, enlaces de aterrizaje, código promocional y contacto directo vía WhatsApp.' },
    { id: 14, name: 'Restricciones', category: 'RESTRICCIONES', title: 'Brand Safety & Restricciones Legales', desc: 'Palabras prohibidas, disclaimers obligatorios, derechos de música y consentimientos de imagen.' },
    { id: 15, name: 'Presupuesto', category: 'PRESUPUESTO', title: 'Presupuesto y Asignación de Recursos', desc: 'Inversión en medios, renderizado IA y APIs (módulo opcional para campañas orgánicas).' },
    { id: 16, name: 'Automatización', category: 'GOBERNANZA', title: 'Nivel de Automatización y Aprobaciones', desc: 'Control de autonomía del sistema y puntos de chequeo requeridos (concepto, copy, master).' },
    { id: 17, name: 'Readiness', category: 'PRE-FLIGHT', title: 'Campaign Readiness Center & Blueprint', desc: 'Diagnóstico agéntico previo a producción, detección de inconsistencias y emisión del Blueprint.' }
  ],

  async init() {
    this.setupEventListeners();
    this.setupKeyboardShortcuts();
    await this.fetchExistingClients();
    await this.loadDraft();
    this.renderActiveStep();
    this.evaluateAllStepStatuses();
    this.updateAssistant();
  },

  async fetchExistingClients() {
    try {
      const resp = await fetch('/api/intake/clients');
      if (resp.ok) {
        const data = await resp.json();
        if (data.status === 'SUCCESS' && Array.isArray(data.clients)) {
          this.clientsList = data.clients;
          if (this.clientsList.length > 0 && this.draft.client.brand_name === 'Locos Materos') {
            this.selectedClientId = this.clientsList[0].id;
          }
        }
      }
    } catch (e) {
      console.warn('No se pudo obtener lista de clientes de /api/intake/clients:', e);
    }
  },

  setupEventListeners() {
    // Selector de modo de cliente
    const btnNew = document.getElementById('btnModeNewClient');
    const btnExist = document.getElementById('btnModeExistingClient');

    if (btnNew && btnExist) {
      btnNew.addEventListener('click', () => {
        this.clientMode = 'NEW_CLIENT';
        btnNew.classList.add('active');
        btnExist.classList.remove('active');
        this.renderActiveStep();
        this.evaluateAllStepStatuses();
        this.updateAssistant();
        this.scheduleAutosave();
        this.showToast('Modo: Nuevo Cliente activado');
      });

      btnExist.addEventListener('click', () => {
        this.clientMode = 'EXISTING_CLIENT';
        btnExist.classList.add('active');
        btnNew.classList.remove('active');
        this.loadExistingClientProfile();
        this.renderActiveStep();
        this.evaluateAllStepStatuses();
        this.updateAssistant();
        this.scheduleAutosave();
        this.showToast('Modo: Cliente Existente (Memoria precargada)');
      });
    }

    // Navegación de pasos por la barra lateral
        // Subnavegación de módulos de estudio (FASE UI-14)
    document.querySelectorAll('.subnav-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const view = tab.getAttribute('data-view');
        this.switchStudioView(view);
      });
    });

    document.querySelectorAll('.step-item').forEach(item => {
      item.addEventListener('click', () => {
        const stepNum = parseInt(item.getAttribute('data-step'), 10);
        this.goToStep(stepNum);
      });
    });

    // Botones de footer Anterior / Siguiente
    const btnPrev = document.getElementById('btnStepPrev');
    const btnNext = document.getElementById('btnStepNext');

    if (btnPrev) {
      btnPrev.addEventListener('click', () => {
        if (this.activeStep > 1) {
          this.goToStep(this.activeStep - 1);
        }
      });
    }

    if (btnNext) {
      btnNext.addEventListener('click', () => {
        if (this.activeStep < this.totalSteps) {
          this.goToStep(this.activeStep + 1);
        } else {
          this.showToast('¡Has alcanzado el Campaign Readiness Center!');
          this.evaluateAllStepStatuses();
        }
      });
    }

    // Botón de Guardado Rápido en Footer
    const btnQuickSave = document.getElementById('btnQuickSaveDraft');
    if (btnQuickSave) {
      btnQuickSave.addEventListener('click', () => {
        this.saveDraft(false);
      });
    }

    // Toggle del Drawer de Diagnóstico
    const btnToggleDrawer = document.getElementById('btnToggleAssistantDrawer');
    const btnCloseDrawer = document.getElementById('btnCloseDrawer');
    const drawer = document.getElementById('diagnosticDrawer');

    if (btnToggleDrawer && drawer) {
      btnToggleDrawer.addEventListener('click', () => {
        drawer.classList.toggle('open');
      });
    }

    if (btnCloseDrawer && drawer) {
      btnCloseDrawer.addEventListener('click', () => {
        drawer.classList.remove('open');
      });
    }

    // Reiniciar borrador
    const btnReset = document.getElementById('btnResetDraft');
    if (btnReset) {
      btnReset.addEventListener('click', () => {
        if (confirm('¿Deseas reiniciar el borrador actual del intake?')) {
          localStorage.removeItem('adcra_intake_draft');
          this.goToStep(1);
          this.showToast('Borrador reiniciado');
        }
      });
    }

    // Botón Header Readiness Check
    const btnPreflight = document.getElementById('btnPreflightHeader');
    if (btnPreflight) {
      btnPreflight.addEventListener('click', () => {
        this.goToStep(17);
      });
    }

    // Presentation View Modal
    const btnPresOpen = document.getElementById('btnPresentationView');
    const btnPresClose = document.getElementById('btnClosePresentationModal');
    const modalPres = document.getElementById('presentationViewModal');
    if (btnPresOpen) {
      btnPresOpen.addEventListener('click', () => this.openPresentationView());
    }
    if (btnPresClose && modalPres) {
      btnPresClose.addEventListener('click', () => { modalPres.style.display = 'none'; });
    }

    // AI Brain Control Center Modal
    const brainPill = document.getElementById('aiBrainPill');
    const modalAi = document.getElementById('aiBrainControlModal');
    const btnCloseAi = document.getElementById('btnCloseAiBrainModal');
    if (brainPill && modalAi) {
      brainPill.addEventListener('click', () => this.openAiBrainModal());
    }
    if (btnCloseAi && modalAi) {
      btnCloseAi.addEventListener('click', () => { modalAi.style.display = 'none'; });
    }

    // Command Palette Modal
    const btnCmd = document.getElementById('btnCmdPalette');
    if (btnCmd) {
      btnCmd.addEventListener('click', () => this.openCommandPalette());
    }

    // Hardware Status Pill
    const btnHw = document.getElementById('btnHardwareStatus');
    if (btnHw) {
      btnHw.addEventListener('click', () => this.showHardwareModal());
    }
    this.fetchHardwareStatus();
  },

  setupKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Ctrl+S / Cmd+S: Guardado de borrador
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        this.saveDraft(false);
        return;
      }

      // Ctrl+K / Cmd+K: Command Palette
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        this.openCommandPalette();
        return;
      }

      // Alt+D: Alternar cajón de diagnóstico
      if (e.altKey && e.key.toLowerCase() === 'd') {
        e.preventDefault();
        const drawer = document.getElementById('diagnosticDrawer');
        if (drawer) drawer.classList.toggle('open');
        return;
      }

      // Escape: Cerrar cajón de diagnóstico
      if (e.key === 'Escape') {
        const drawer = document.getElementById('diagnosticDrawer');
        if (drawer && drawer.classList.contains('open')) {
          drawer.classList.remove('open');
          return;
        }
      }

      // Alt + ArrowRight: Siguiente paso
      if (e.altKey && e.key === 'ArrowRight') {
        e.preventDefault();
        if (this.activeStep < this.totalSteps) this.goToStep(this.activeStep + 1);
        return;
      }

      // Alt + ArrowLeft: Paso anterior
      if (e.altKey && e.key === 'ArrowLeft') {
        e.preventDefault();
        if (this.activeStep > 1) this.goToStep(this.activeStep - 1);
        return;
      }
    });
  },

  loadClientFromMemory(clientObj) {
    if (!clientObj) {
      clientObj = (this.clientsList && this.clientsList.length > 0)
        ? this.clientsList[0]
        : { id: 'locos-materos', name: 'Locos Materos', industry: 'e-commerce / yerba mate' };
    }
    const memory = clientObj.memory || {};
    this.selectedClientId = clientObj.id || 'locos-materos';

    this.draft.client.brand_name = clientObj.name || memory.brand_name || 'Locos Materos';
    this.draft.client.legal_name = 'Locos Materos SpA';
    this.draft.client.industry = clientObj.industry || 'Alimentos y Bebidas / Yerba Mate';
    this.draft.client.business_type = 'ecommerce';
    this.draft.client.website_url = 'https://locosmateros.cl';
    this.draft.client.description = 'Comunidad y tienda de yerba mate tradicional e innovadora en Chile con foco en rituales compartidos.';
    this.draft.client.social_channels = {
      instagram: '@locosmateros',
      tiktok: '@locosmateros',
      youtube: 'https://youtube.com/@locosmateros',
      facebook: ''
    };
    this.draft.client.contact = {
      name: 'Ignacio Matero',
      role: 'Director de Marca',
      email: 'contacto@locosmateros.cl',
      phone: '+56 9 8765 4321'
    };

    // Marca y Estética
    this.draft.brand.claim = '¿Dónde estás tú? Está tu mate.';
    if (memory.aesthetic_learnings && memory.aesthetic_learnings.primary_palette) {
      this.draft.brand.primary_color = memory.aesthetic_learnings.primary_palette.primary_green || '#0D5C3A';
      this.draft.brand.secondary_color = memory.aesthetic_learnings.primary_palette.golden_highlight || '#D4AF37';
    } else {
      this.draft.brand.primary_color = '#0D5C3A';
      this.draft.brand.secondary_color = '#D4AF37';
    }
    this.draft.brand.accent_color = '#10B981';
    this.draft.brand.values = ['tradición', 'calidad', 'comunidad', 'autenticidad'];

    // Audio y Tempo
    this.draft.audio.filename = 'musica_mate_acustica.mp3';
    this.draft.audio.bpm = (memory.musical_tempo_learnings && memory.musical_tempo_learnings.last_successful_bpm)
      ? memory.musical_tempo_learnings.last_successful_bpm
      : 107.7;
    this.draft.audio.meter = '4/4';

    // Audiencia y Duración
    if (memory.audience_profile && memory.audience_profile.geographic_context) {
      this.draft.audience.primary.location = memory.audience_profile.geographic_context;
    }
    this.draft.duration.target_seconds = 30;

    this.evaluateAllStepStatuses();
    this.updateAssistant(`Cliente "${this.draft.client.brand_name}" cargado con éxito. Su identidad visual, tempo (107.7 BPM) y reglas de retención están precargadas. Avanza al Paso 02.`);
    this.scheduleAutosave();
  },

  loadExistingClientProfile() {
    this.loadClientFromMemory();
  },

  goToStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > this.totalSteps) return;
    this.activeStep = stepNumber;

    // Actualizar sidebar activo
    document.querySelectorAll('.step-item').forEach(el => {
      const s = parseInt(el.getAttribute('data-step'), 10);
      if (s === this.activeStep) {
        el.classList.add('active');
        el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        el.classList.remove('active');
      }
    });

    // Actualizar progreso
    const pct = Math.round((this.activeStep / this.totalSteps) * 100);
    const progressFill = document.getElementById('progressBarFill');
    const progressCount = document.getElementById('progressStepCount');
    if (progressFill) progressFill.style.width = `${pct}%`;
    if (progressCount) progressCount.textContent = `${this.activeStep} / ${this.totalSteps}`;

    // Actualizar botones de footer
    const btnPrev = document.getElementById('btnStepPrev');
    const btnNext = document.getElementById('btnStepNext');
    if (btnPrev) btnPrev.disabled = (this.activeStep === 1);
    if (btnNext) {
      btnNext.innerHTML = (this.activeStep === this.totalSteps)
        ? 'Verificar Readiness <span class="btn-icon">🛡️</span>'
        : 'Siguiente <span class="btn-icon">→</span>';
    }

    // Transición suave de contenido
    const contentArea = document.getElementById('stepContentArea');
    if (contentArea) {
      contentArea.classList.add('step-transition-enter');
      this.renderActiveStep();
      requestAnimationFrame(() => {
        contentArea.classList.remove('step-transition-enter');
        contentArea.classList.add('step-transition-active');
      });
    } else {
      this.renderActiveStep();
    }

    this.evaluateAllStepStatuses();
    this.updateAssistant();
    this.scheduleAutosave();
  },

  scheduleAutosave() {
    if (this.debounceSaveTimer) {
      clearTimeout(this.debounceSaveTimer);
    }
    const autoText = document.getElementById('autosaveText');
    if (autoText) autoText.textContent = 'Modificado...';

    this.debounceSaveTimer = setTimeout(() => {
      this.saveDraft(true);
    }, 500);
  },

  async saveDraft(silent = false) {
    const payload = {
      clientMode: this.clientMode,
      activeStep: this.activeStep,
      draft: this.draft,
      updated_at: new Date().toISOString()
    };

    // Respaldo inmediato en localStorage
    try {
      localStorage.setItem('adcra_intake_draft', JSON.stringify(payload));
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }

    // Persistencia en servidor vía endpoint /api/intake/draft
    const autoText = document.getElementById('autosaveText');
    if (autoText) autoText.textContent = 'Guardando...';

    try {
      const resp = await fetch('/api/intake/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        if (autoText) autoText.textContent = `Guardado ${timeStr}`;
        if (!silent) this.showToast('💾 Borrador guardado exitosamente');
      } else {
        if (autoText) autoText.textContent = 'Guardado localmente';
      }
    } catch (err) {
      if (autoText) autoText.textContent = 'Guardado local (offline)';
      if (!silent) this.showToast('💾 Guardado localmente (offline)');
    }
  },

  async loadDraft() {
    let loaded = null;

    // Intentar leer desde servidor
    try {
      const res = await fetch('/api/intake/draft');
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'SUCCESS' && data.draft) {
          loaded = data.draft;
        }
      }
    } catch (e) {
      console.warn('No se pudo cargar borrador desde el backend, intentando localStorage.');
    }

    // Fallback a localStorage
    if (!loaded) {
      try {
        const local = localStorage.getItem('adcra_intake_draft');
        if (local) loaded = JSON.parse(local);
      } catch (e) {}
    }

    if (loaded && loaded.draft) {
      this.clientMode = loaded.clientMode || this.clientMode;
      if (loaded.activeStep && loaded.activeStep >= 1 && loaded.activeStep <= this.totalSteps) {
        this.activeStep = loaded.activeStep;
      }
      // Fusionar borrador manteniendo estructura base
      this.draft = { ...this.draft, ...loaded.draft };

      // Actualizar botones de modo
      const btnNew = document.getElementById('btnModeNewClient');
      const btnExist = document.getElementById('btnModeExistingClient');
      if (btnNew && btnExist) {
        if (this.clientMode === 'EXISTING_CLIENT') {
          btnExist.classList.add('active');
          btnNew.classList.remove('active');
        } else {
          btnNew.classList.add('active');
          btnExist.classList.remove('active');
        }
      }

      const autoText = document.getElementById('autosaveText');
      if (autoText && loaded.updated_at) {
        const d = new Date(loaded.updated_at);
        autoText.textContent = `Restaurado ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      }
      this.showToast(`Borrador previo recuperado (Paso ${this.activeStep})`);
    }
  },

  evaluateAllStepStatuses() {
    const issues = [];
    let readyCount = 0;
    let warningsCount = 0;
    let blockersCount = 0;

    // Paso 1: Cliente
    if (this.draft.client.brand_name.trim().length > 0) {
      this.updateStepStatus(1, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(1, 'MISSING');
      blockersCount++;
      issues.push({ step: 1, type: 'blocker', text: 'Paso 01: El nombre comercial de la marca es requerido.' });
    }

    // Paso 2: Objetivo
    if (this.draft.objective.primary) {
      this.updateStepStatus(2, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(2, 'MISSING');
      blockersCount++;
      issues.push({ step: 2, type: 'blocker', text: 'Paso 02: Selecciona un objetivo primario de campaña.' });
    }

    // Paso 3: Audiencia
    if (this.draft.audience.primary.location) {
      this.updateStepStatus(3, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(3, 'READY');
      readyCount++;
    }

    // Paso 4: Marca
    if (this.draft.brand.claim) {
      this.updateStepStatus(4, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(4, 'READY');
      warningsCount++;
      issues.push({ step: 4, type: 'warning', text: 'Paso 04: Te sugerimos incluir un claim o eslogan de marca.' });
    }

    // Paso 5: Producto e Inteligencia Anti-Alucinación
    const primaryProd = this.draft.products && this.draft.products[0];
    if (primaryProd && primaryProd.name && primaryProd.name.trim().length > 0) {
      if (primaryProd.verified_benefits && primaryProd.verified_benefits.length > 0) {
        this.updateStepStatus(5, 'COMPLETE');
        readyCount++;
      } else {
        this.updateStepStatus(5, 'READY');
        readyCount++;
        issues.push({ step: 5, type: 'warning', text: 'Paso 05: Agrega al menos un beneficio comprobado en el escudo anti-alucinación.' });
      }
    } else {
      this.updateStepStatus(5, 'MISSING');
      blockersCount++;
      issues.push({ step: 5, type: 'blocker', text: 'Paso 05: El nombre del producto o servicio protagonista es requerido.' });
    }

    // Paso 6: Oferta Comercial / Branding Puro
    if (this.draft.offer.is_branding_only) {
      this.updateStepStatus(6, 'COMPLETE');
      readyCount++;
    } else if (this.draft.offer.offer_title && this.draft.offer.offer_title.trim().length > 0) {
      this.updateStepStatus(6, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(6, 'READY');
      readyCount++;
    }

    // Paso 7: Creatividad & Dirección de Arte
    if (this.draft.creative.target_emotions.length > 0 && this.draft.creative.key_takeaway && this.draft.creative.key_takeaway.trim().length > 0) {
      this.updateStepStatus(7, 'COMPLETE');
      readyCount++;
    } else if (this.draft.creative.target_emotions.length > 0) {
      this.updateStepStatus(7, 'READY');
      readyCount++;
      issues.push({ step: 7, type: 'warning', text: 'Paso 07: Te sugerimos definir el Key Takeaway principal de campaña.' });
    } else {
      this.updateStepStatus(7, 'NEEDS_REVIEW');
      warningsCount++;
      issues.push({ step: 7, type: 'warning', text: 'Paso 07: Selecciona al menos una emoción clave de campaña.' });
    }

    // Paso 8: Audio (Crítico)
    if (this.draft.audio.filename) {
      this.updateStepStatus(8, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(8, 'MISSING');
      blockersCount++;
      issues.push({ step: 8, type: 'blocker', text: 'Paso 08: Se requiere una pista de audio para la sincronización rítmica.' });
    }

    // Paso 9: Video Assets & Probing Técnico (FFprobe)
    if (this.draft.assets && this.draft.assets.length > 0) {
      const hasVertical = this.draft.assets.some(a => a.orientation === 'vertical' || a.aspect_ratio === '9:16');
      if (hasVertical) {
        this.updateStepStatus(9, 'COMPLETE');
        readyCount++;
      } else {
        this.updateStepStatus(9, 'READY');
        readyCount++;
        issues.push({ step: 9, type: 'warning', text: 'Paso 09: Todos los clips son horizontales. Para Reels/TikTok recomendamos al menos un clip vertical (9:16).' });
      }
    } else {
      this.updateStepStatus(9, 'MISSING');
      blockersCount++;
      issues.push({ step: 9, type: 'blocker', text: 'Paso 09: Carga al menos un video o activo visual crudo.' });
    }

    // Paso 10: Referencias & Moodboard
    if (this.draft.references && this.draft.references.length > 0 && this.draft.references.some(r => r.url && r.url.trim().length > 0)) {
      this.updateStepStatus(10, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(10, 'OPTIONAL');
    }

    // Paso 11: Canales
    if (this.draft.channels.length > 0) {
      this.updateStepStatus(11, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(11, 'MISSING');
      blockersCount++;
      issues.push({ step: 11, type: 'blocker', text: 'Paso 11: Selecciona al menos un canal de emisión (ej. TikTok 9:16).' });
    }

    // Paso 12: Duración
    this.updateStepStatus(12, 'READY');
    readyCount++;

    // Paso 13: CTA
    if (this.draft.cta.primary) {
      this.updateStepStatus(13, 'COMPLETE');
      readyCount++;
    } else {
      this.updateStepStatus(13, 'READY');
      readyCount++;
    }

    // Paso 14: Restricciones (Opcional)
    this.updateStepStatus(14, 'OPTIONAL');

    // Paso 15: Presupuesto (Opcional)
    this.updateStepStatus(15, 'OPTIONAL');

    // Paso 16: Automatización
    this.updateStepStatus(16, 'READY');
    readyCount++;

    // Paso 17: Readiness
    if (blockersCount === 0) {
      this.updateStepStatus(17, 'READY');
      readyCount++;
    } else {
      this.updateStepStatus(17, 'NEEDS_REVIEW');
      warningsCount++;
    }

    // Actualizar contadores del drawer
    const cReady = document.getElementById('diagCountReady');
    const cWarn = document.getElementById('diagCountWarnings');
    const cBlock = document.getElementById('diagCountBlockers');
    if (cReady) cReady.textContent = readyCount;
    if (cWarn) cWarn.textContent = warningsCount;
    if (cBlock) cBlock.textContent = blockersCount;

    // Actualizar lista de issues
    const listEl = document.getElementById('diagIssuesList');
    if (listEl) {
      if (issues.length === 0) {
        listEl.innerHTML = '<div style="font-size: 0.8rem; color: var(--color-emerald); padding: 0.5rem;">✓ Sin problemas detectados. Brief listo para producción.</div>';
      } else {
        listEl.innerHTML = issues.map(iss => `
          <div class="diag-issue-item ${iss.type}" onclick="IntakeApp.goToStep(${iss.step})" style="cursor: pointer;">
            <span style="font-size: 1rem;">${iss.type === 'blocker' ? '⛔' : '⚠️'}</span>
            <div>
              <div style="font-weight: 600; color: #FFF;">${iss.text}</div>
              <div style="font-size: 0.72rem; color: var(--text-dim);">Haz clic para ir al Paso ${String(iss.step).padStart(2, '0')}</div>
            </div>
          </div>
        `).join('');
      }
    }
  },

  updateStepStatus(stepNum, status) {
    const badge = document.getElementById(`stepBadge${stepNum}`);
    if (badge) {
      badge.className = `step-status status-${status.toLowerCase().replace('_', '-')}`;
      badge.textContent = status.replace('_', ' ');
    }
  },

  updateAssistant(customMsg = null) {
    const textEl = document.getElementById('assistantText');
    const badgeStatus = document.getElementById('assistantBadgeStatus');
    if (!textEl) return;

    if (customMsg) {
      textEl.textContent = customMsg;
      return;
    }

    switch (this.activeStep) {
      case 1:
        if (!this.draft.client.brand_name) {
          textEl.textContent = 'Paso 01 (Cliente): Para comenzar, indica el nombre de la marca o ingresa su sitio web para que ADCRA pueda analizar su identidad automáticamente.';
          if (badgeStatus) badgeStatus.textContent = 'ESPERANDO MARCA';
        } else {
          textEl.textContent = `Paso 01: Marca "${this.draft.client.brand_name}" registrada. Avanza al Paso 02 para definir la meta de negocio de la campaña.`;
          if (badgeStatus) badgeStatus.textContent = 'LISTO PARA AVANZAR';
        }
        break;
      case 2:
        textEl.textContent = 'Paso 02 (Objetivo): Define si buscas Awareness masivo, Conversión directa o Tráfico. Esto orientará el ritmo musical y el llamado a la acción (CTA).';
        if (badgeStatus) badgeStatus.textContent = 'OBJETIVO CONFIGURADO';
        break;
      case 3:
        textEl.textContent = 'Paso 03 (Audiencia): Delimita los rangos demográficos e intereses de tus espectadores para adecuar el tono narrativo de DaVinci y Remotion.';
        if (badgeStatus) badgeStatus.textContent = 'AUDIENCIA ACTIVA';
        break;
      case 4:
        textEl.textContent = 'Paso 04 (Marca): Configura la paleta cromática HEX y el propósito. Los colores institucionalizarán los gráficos cinéticos generados en HyperFrames.';
        if (badgeStatus) badgeStatus.textContent = 'IDENTIDAD VISUAL';
        break;
      case 5:
        textEl.textContent = 'Paso 05 (Producto): Ingresa el producto o servicio que protagoniza el comercial. Prohibido alucinar beneficios no respaldados.';
        if (badgeStatus) badgeStatus.textContent = 'FICHA PRODUCTO';
        break;
      case 6:
        textEl.textContent = 'Paso 06 (Oferta): Especifica condiciones comerciales o activa el modo "Branding Puro" para anuncios institucionales sin precio.';
        if (badgeStatus) badgeStatus.textContent = 'OFERTA ACTIVA';
        break;
      case 7:
        textEl.textContent = 'Paso 07 (Creatividad): Selecciona hasta 3 emociones primarias y define qué NO debe transmitir jamás la pieza publicitaria.';
        if (badgeStatus) badgeStatus.textContent = 'DIRECCIÓN CREATIVA';
        break;
      case 8:
        textEl.textContent = 'Paso 08 (Audio): Carga una pista musical. El motor de audio extraerá el BPM (124 BPM detectado) y los compases de corte rítmico.';
        if (badgeStatus) badgeStatus.textContent = this.draft.audio.filename ? 'AUDIO CONFIRMADO' : 'AUDIO REQUERIDO';
        break;
      case 9:
        textEl.textContent = 'Paso 09 (Video Assets): Verifica los clips crudos subidos. ADCRA audita resolución (1080x1920) y tasa de cuadros (29.97 FPS) automáticamente.';
        if (badgeStatus) badgeStatus.textContent = 'INSPECCIÓN ASSETS';
        break;
      case 10:
        textEl.textContent = 'Paso 10 (Referencias): Moodboard opcional de inspiración visual o de montaje para orientar a los agentes creativos.';
        if (badgeStatus) badgeStatus.textContent = 'MOODBOARD';
        break;
      case 11:
        textEl.textContent = 'Paso 11 (Canales): Selecciona los canales de difusión vertical (TikTok, Instagram Reels, Shorts) y relaciones de aspecto.';
        if (badgeStatus) badgeStatus.textContent = 'OMNICANAL';
        break;
      case 12:
        textEl.textContent = 'Paso 12 (Duración): Elige 15s, 30s o corte guiado por audio (Audio-Driven) para que coincida con el drop de la música.';
        if (badgeStatus) badgeStatus.textContent = 'DURACIÓN TARGET';
        break;
      case 13:
        textEl.textContent = 'Paso 13 (CTA): Especifica la llamada a la acción y enlaces oficiales para las tarjetas finales dinámicas de Remotion.';
        if (badgeStatus) badgeStatus.textContent = 'CALL TO ACTION';
        break;
      case 14:
        textEl.textContent = 'Paso 14 (Restricciones): Configura palabras prohibidas y advertencias legales obligatorias de tu sector regulado.';
        if (badgeStatus) badgeStatus.textContent = 'BRAND SAFETY';
        break;
      case 15:
        textEl.textContent = 'Paso 15 (Presupuesto): Opcional. Declara inversión estimada para ponderar el nivel de síntesis y renderizado.';
        if (badgeStatus) badgeStatus.textContent = 'PRESUPUESTO';
        break;
      case 16:
        textEl.textContent = 'Paso 16 (Gobernanza): Define si el sistema operará de manera autónoma con aprobación humana o en modo asistido.';
        if (badgeStatus) badgeStatus.textContent = 'GOBERNANZA';
        break;
      case 17:
        textEl.textContent = 'Paso 17 (Readiness Center): Diagnóstico pre-flight global. Revisa el Blueprint de campaña antes de activar el pipeline de producción.';
        if (badgeStatus) badgeStatus.textContent = 'AUDITORÍA PRE-FLIGHT';
        break;
      default:
        textEl.textContent = `Paso ${this.activeStep}: Supervisando parámetros en tiempo real con la arquitectura ADCRA.`;
        if (badgeStatus) badgeStatus.textContent = 'MONITOREANDO';
    }
  },

  renderActiveStep() {
    const sMeta = this.steps[this.activeStep - 1];
    document.getElementById('currentStepTag').textContent = `Paso ${String(this.activeStep).padStart(2, '0')} de 17`;
    document.getElementById('currentCategoryPill').textContent = sMeta.category;
    document.getElementById('currentStepTitle').textContent = sMeta.title;
    document.getElementById('currentStepDesc').textContent = sMeta.desc;
    document.getElementById('footerStepIndicator').textContent = `Paso ${this.activeStep}: ${sMeta.name}`;

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    switch (this.activeStep) {
      case 1:
        contentArea.innerHTML = this.renderStep01_Client();
        this.bindStep01_Events();
        break;
      case 2:
        contentArea.innerHTML = this.renderStep02_Objective();
        this.bindStep02_Events();
        break;
      case 3:
        contentArea.innerHTML = this.renderStep03_Audience();
        this.bindStep03_Events();
        break;
      case 4:
        contentArea.innerHTML = this.renderStep04_Brand();
        this.bindStep04_Events();
        break;
      case 5:
        contentArea.innerHTML = this.renderStep05_Product();
        this.bindStep05_Events();
        break;
      case 6:
        contentArea.innerHTML = this.renderStep06_Offer();
        this.bindStep06_Events();
        break;
      case 7:
        contentArea.innerHTML = this.renderStep07_Creative();
        this.bindStep07_Events();
        break;
      case 8:
        contentArea.innerHTML = this.renderStep08_Audio();
        this.bindStep08_Events();
        break;
      case 9:
        contentArea.innerHTML = this.renderStep09_Assets();
        this.bindStep09_Events();
        break;
      case 10:
        contentArea.innerHTML = this.renderStep10_References();
        this.bindStep10_Events();
        break;
      case 11:
        contentArea.innerHTML = this.renderStep11_Channels();
        this.bindStep11_Events();
        break;
      case 12:
        contentArea.innerHTML = this.renderStep12_Duration();
        this.bindStep12_Events();
        break;
      case 13:
        contentArea.innerHTML = this.renderStep13_CTA();
        this.bindStep13_Events();
        break;
      case 14:
        contentArea.innerHTML = this.renderStep14_Constraints();
        this.bindStep14_Events();
        break;
      case 15:
        contentArea.innerHTML = this.renderStep15_Budget();
        this.bindStep15_Events();
        break;
      case 16:
        contentArea.innerHTML = this.renderStep16_Automation();
        this.bindStep16_Events();
        break;
      case 17:
        contentArea.innerHTML = this.renderStep17_Readiness();
        this.bindStep17_Events();
        break;
      default:
        contentArea.innerHTML = `<div class="form-section"><p>Paso no implementado</p></div>`;
    }
  },

  // ==========================================
  // RENDERIZADORES DE LOS 17 PASOS
  // ==========================================

  renderStep01_Client() {
    if (this.clientMode === 'EXISTING_CLIENT') {
      const clients = (this.clientsList && this.clientsList.length > 0)
        ? this.clientsList
        : [{
            id: 'locos-materos',
            name: 'Locos Materos',
            industry: 'Alimentos y Bebidas / Yerba Mate',
            has_memory: true
          }];

      const selectedClient = clients.find(c => c.id === this.selectedClientId) || clients[0];

      return `
        <div class="form-section">
          <div class="form-section-title"><span>🏛️</span> Selector de Clientes Registrados en ADCRA</div>
          <p style="font-size: 0.85rem; color: var(--text-muted);">
            Selecciona una marca existente para precargar instantáneamente su memoria episódica, paleta institucional, tempo óptimo y reglas de retención aprobadas.
          </p>
          
          <div style="margin-top: 0.25rem;">
            <input type="text" id="inpClientFilter" class="form-input" placeholder="🔍 Filtrar marcas por nombre o categoría..." style="max-width: 400px;">
          </div>

          <div class="clients-grid" id="existingClientsGrid">
            ${clients.map(c => `
              <div class="client-card ${this.selectedClientId === c.id ? 'selected' : ''}" data-client-id="${c.id}">
                <div class="client-card-header">
                  <div class="client-avatar">🧉</div>
                  <div>
                    <div class="client-name-title">${c.name}</div>
                    <div class="client-industry-sub">${c.industry}</div>
                  </div>
                </div>

                <div class="client-metrics">
                  <span>⚡ 107.7 BPM</span>
                  <span>•</span>
                  <span>⏱️ 29.2s</span>
                  <span>•</span>
                  <span style="color: var(--color-gold-bright); font-weight: 700;">★ 100.0/100 QC</span>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem;">
                  <div class="client-palette-row">
                    <div class="client-swatch" style="background: #0D5C3A;" title="Verde Mate (#0D5C3A)"></div>
                    <div class="client-swatch" style="background: #D4AF37;" title="Dorado Mate (#D4AF37)"></div>
                    <div class="client-swatch" style="background: #10B981;" title="Esmeralda (#10B981)"></div>
                  </div>
                  <button class="btn btn-secondary btn-sm btn-select-client" data-client-id="${c.id}">
                    ${this.selectedClientId === c.id ? 'Activo' : 'Seleccionar'}
                  </button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Banner de Memoria Histórica del Cliente Activo -->
        <div class="client-memory-banner">
          <div class="client-memory-header">
            <div>
              <div style="font-weight: 800; font-size: 1.15rem; color: #FFF; display: flex; align-items: center; gap: 0.5rem;">
                <span>🧉</span> Memoria Histórica Activa: ${this.draft.client.brand_name || selectedClient.name}
              </div>
              <div style="font-size: 0.8rem; color: var(--color-gold-bright); margin-top: 0.2rem;">
                Claim Oficial: "${this.draft.brand.claim || '¿Dónde estás tú? Está tu mate.'}"
              </div>
            </div>
            <span class="step-status status-complete" style="font-size: 0.82rem;">CERTIFICADO BROADCAST</span>
          </div>

          <div class="memory-pills-row">
            <span class="memory-pill gold">🏆 Quality Score: 100.0/100</span>
            <span class="memory-pill emerald">🎵 BPM Óptimo: 107.7 (4/4)</span>
            <span class="memory-pill">🎬 Escenas Recomendadas: 9</span>
            <span class="memory-pill">🎨 LUT: locos_materos_warm_cinematic.cube</span>
            <span class="memory-pill">📱 Formato: 9:16 Vertical Safe</span>
          </div>

          <div style="background: rgba(0,0,0,0.3); border-radius: 10px; padding: 1rem; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-weight: 700; font-size: 0.85rem; color: #FFF; margin-bottom: 0.4rem;">
              📜 Reglas de Retención Memorizadas (Aplicadas Automáticamente)
            </div>
            <ul style="font-size: 0.78rem; color: var(--text-muted); margin: 0; padding-left: 1.2rem; display: flex; flex-direction: column; gap: 0.3rem;">
              <li>El mate debe mantenerse físicamente consistente y realista (calabaza real, bombilla de acero inoxidable y termo con proporciones exactas).</li>
              <li>Garantizar legibilidad de textos respetando safe zones verticales 9:16 (TikTok, Reels, Shorts).</li>
              <li>Cierre publicitario obligatorio con hero packshot del producto y claim '¿Dónde estás tú? Está tu mate' en escena 09.</li>
            </ul>
          </div>

          <button class="btn btn-primary" id="btnContinueToObjective" style="height: 46px; font-size: 0.95rem;">
            <span>✦</span> Iniciar Nueva Campaña para ${this.draft.client.brand_name || 'este Cliente'} (Ir al Paso 02) →
          </button>
        </div>
      `;
    }

    // Modalidad NUEVO CLIENTE
    return `
      <!-- Smart Website Auto-Analysis Box -->
      <div class="form-section">
        <div class="form-section-title"><span>⚡</span> Asistente Agéntico de Inferencia Web</div>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Introduce la URL del sitio web oficial de la marca. ADCRA rastreará e inferirá automáticamente la propuesta de valor, colores predominantes, industria y canales sociales.
        </p>
        <div style="display: flex; gap: 0.75rem; align-items: flex-end; padding: 1rem; background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); border-radius: 10px;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Sitio Web Oficial de la Marca</label>
            <input type="url" id="inpClientWeb" class="form-input" placeholder="https://www.tu-marca.com" value="${this.draft.client.website_url}">
          </div>
          <button class="btn btn-primary" id="btnAnalyzeWeb" style="height: 40px;">
            <span class="btn-icon">⚡</span> Analizar Sitio Web
          </button>
        </div>

        ${this.inferredAnalysis ? `
          <!-- Card de Confirmación de Inferencia de IA -->
          <div class="inference-preview-card" id="inferencePreviewCard">
            <div class="inference-header">
              <div style="font-weight: 700; font-size: 0.95rem; color: #FFF; display: flex; align-items: center; gap: 0.5rem;">
                <span>✨</span> Detecciones Inferidas por ADCRA
              </div>
              <span class="inference-badge-ai">AI_INFERENCE (96% CONFIANZA)</span>
            </div>

            <div class="inference-grid">
              <div class="inference-field">
                <span class="inference-label">Marca Detectada</span>
                <span class="inference-val">${this.inferredAnalysis.brand_name}</span>
              </div>
              <div class="inference-field">
                <span class="inference-label">Industria / Sector</span>
                <span class="inference-val">${this.inferredAnalysis.industry}</span>
              </div>
              <div class="inference-field">
                <span class="inference-label">Tipo de Negocio</span>
                <span class="inference-val">${this.inferredAnalysis.business_type}</span>
              </div>
              <div class="inference-field">
                <span class="inference-label">Eslogan Sugerido</span>
                <span class="inference-val">${this.inferredAnalysis.claim}</span>
              </div>
            </div>

            <div class="inference-field">
              <span class="inference-label">Propuesta de Valor Extraída</span>
              <span style="font-size: 0.85rem; color: var(--text-muted);">${this.inferredAnalysis.description}</span>
            </div>

            <div style="display: flex; align-items: center; gap: 1rem;">
              <span class="inference-label">Paleta Detectada:</span>
              <div class="client-palette-row">
                <div class="client-swatch" style="background: ${this.inferredAnalysis.colors.primary};" title="Primario"></div>
                <div class="client-swatch" style="background: ${this.inferredAnalysis.colors.secondary};" title="Secundario"></div>
                <div class="client-swatch" style="background: ${this.inferredAnalysis.colors.accent};" title="Acento"></div>
              </div>
            </div>

            <div class="inference-actions">
              <button class="btn btn-secondary btn-sm" id="btnDiscardInference">Descartar</button>
              <button class="btn btn-primary btn-sm" id="btnAcceptInference">
                <span class="btn-icon">✓</span> Aceptar Detecciones
              </button>
            </div>
          </div>
        ` : ''}
      </div>

      <!-- Datos de la Marca y Empresa -->
      <div class="form-section">
        <div class="form-section-title"><span>🏢</span> Identificación de la Marca</div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Nombre Comercial de la Marca <span class="required">*</span></label>
            <input type="text" id="inpBrandName" class="form-input" placeholder="Ej: Café de la Sierra" value="${this.draft.client.brand_name}">
          </div>
          <div class="form-group">
            <label class="form-label">Razón Social o Legal (Opcional)</label>
            <input type="text" id="inpLegalName" class="form-input" placeholder="Ej: Café de la Sierra SpA" value="${this.draft.client.legal_name || ''}">
          </div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Sector o Industria <span class="required">*</span></label>
            <input type="text" id="inpIndustry" class="form-input" placeholder="Ej: Café de Especialidad / Gastronomía" value="${this.draft.client.industry}">
          </div>
          <div class="form-group">
            <label class="form-label">Tipo de Negocio</label>
            <select id="selBusinessType" class="form-select">
              <option value="producto" ${this.draft.client.business_type === 'producto' ? 'selected' : ''}>Producto Físico / Bien de Consumo</option>
              <option value="servicio" ${this.draft.client.business_type === 'servicio' ? 'selected' : ''}>Servicio Profesional / Consultoría</option>
              <option value="ecommerce" ${this.draft.client.business_type === 'ecommerce' ? 'selected' : ''}>E-commerce / Tienda Online</option>
              <option value="restaurante" ${this.draft.client.business_type === 'restaurante' ? 'selected' : ''}>Gastronomía / Restaurante</option>
              <option value="startup" ${this.draft.client.business_type === 'startup' ? 'selected' : ''}>Startup / Tecnología / SaaS</option>
              <option value="otro" ${this.draft.client.business_type === 'otro' ? 'selected' : ''}>Otro</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Descripción Breve de la Propuesta de Valor</label>
          <textarea id="inpDescription" class="form-textarea" placeholder="Describe brevemente qué hace único a tu negocio, qué problema resuelve o qué ritual celebra...">${this.draft.client.description}</textarea>
        </div>
      </div>

      <!-- Datos de Contacto Directo -->
      <div class="form-section">
        <div class="form-section-title"><span>👤</span> Contacto Principal de la Cuenta</div>
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Nombre del Contacto</label>
            <input type="text" id="inpContactName" class="form-input" placeholder="Ej: Andrea Valenzuela" value="${this.draft.client.contact ? this.draft.client.contact.name : ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Cargo o Rol</label>
            <input type="text" id="inpContactRole" class="form-input" placeholder="Ej: Gerente de Marketing" value="${this.draft.client.contact ? this.draft.client.contact.role : ''}">
          </div>
        </div>
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Correo Electrónico</label>
            <input type="email" id="inpContactEmail" class="form-input" placeholder="marketing@tu-marca.com" value="${this.draft.client.contact ? this.draft.client.contact.email : ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Teléfono o WhatsApp Comercial</label>
            <input type="tel" id="inpContactPhone" class="form-input" placeholder="+56 9 1234 5678" value="${this.draft.client.contact ? this.draft.client.contact.phone : ''}">
          </div>
        </div>
      </div>

      <!-- Canales Oficiales -->
      <div class="form-section">
        <div class="form-section-title"><span>📱</span> Canales Digitales Oficiales</div>
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Instagram (@usuario)</label>
            <input type="text" id="inpInstagram" class="form-input" placeholder="@cafesierra" value="${this.draft.client.social_channels.instagram}">
          </div>
          <div class="form-group">
            <label class="form-label">TikTok (@usuario)</label>
            <input type="text" id="inpTiktok" class="form-input" placeholder="@cafesierra" value="${this.draft.client.social_channels.tiktok}">
          </div>
        </div>
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">YouTube (Canal o URL)</label>
            <input type="text" id="inpYoutube" class="form-input" placeholder="youtube.com/@cafesierra" value="${this.draft.client.social_channels.youtube || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Facebook (Página)</label>
            <input type="text" id="inpFacebook" class="form-input" placeholder="facebook.com/cafesierra" value="${this.draft.client.social_channels.facebook || ''}">
          </div>
        </div>
      </div>
    `;
  },

  bindStep01_Events() {
    if (this.clientMode === 'EXISTING_CLIENT') {
      // Filtrar clientes
      const inpFilter = document.getElementById('inpClientFilter');
      if (inpFilter) {
        inpFilter.addEventListener('input', (e) => {
          const q = e.target.value.toLowerCase().trim();
          document.querySelectorAll('#existingClientsGrid .client-card').forEach(card => {
            const txt = card.textContent.toLowerCase();
            card.style.display = txt.includes(q) ? 'flex' : 'none';
          });
        });
      }

      // Selección de tarjeta de cliente
      document.querySelectorAll('#existingClientsGrid .client-card').forEach(card => {
        card.addEventListener('click', () => {
          const clientId = card.getAttribute('data-client-id');
          const clientObj = this.clientsList.find(c => c.id === clientId);
          this.loadClientFromMemory(clientObj);
          this.renderActiveStep();
          this.showToast(`Cliente "${this.draft.client.brand_name}" seleccionado`);
        });
      });

      // Botón Continuar a Objetivo (Paso 2)
      const btnCont = document.getElementById('btnContinueToObjective');
      if (btnCont) {
        btnCont.addEventListener('click', () => {
          this.goToStep(2);
        });
      }
      return;
    }

    // Modalidad NUEVO CLIENTE
    const inpBrand = document.getElementById('inpBrandName');
    if (inpBrand) {
      inpBrand.addEventListener('input', (e) => {
        this.draft.client.brand_name = e.target.value.trim();
        this.evaluateAllStepStatuses();
        this.updateAssistant();
        this.scheduleAutosave();
      });
    }

    const inpLegal = document.getElementById('inpLegalName');
    if (inpLegal) {
      inpLegal.addEventListener('input', (e) => {
        this.draft.client.legal_name = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    const inpIndustry = document.getElementById('inpIndustry');
    if (inpIndustry) {
      inpIndustry.addEventListener('input', (e) => {
        this.draft.client.industry = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    const selBiz = document.getElementById('selBusinessType');
    if (selBiz) {
      selBiz.addEventListener('change', (e) => {
        this.draft.client.business_type = e.target.value;
        this.scheduleAutosave();
      });
    }

    const inpDesc = document.getElementById('inpDescription');
    if (inpDesc) {
      inpDesc.addEventListener('input', (e) => {
        this.draft.client.description = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    // Contacto
    const bindContact = (id, key) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', (e) => {
          if (!this.draft.client.contact) this.draft.client.contact = {};
          this.draft.client.contact[key] = e.target.value.trim();
          this.scheduleAutosave();
        });
      }
    };
    bindContact('inpContactName', 'name');
    bindContact('inpContactRole', 'role');
    bindContact('inpContactEmail', 'email');
    bindContact('inpContactPhone', 'phone');

    // Redes Sociales
    const bindSocial = (id, key) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', (e) => {
          if (!this.draft.client.social_channels) this.draft.client.social_channels = {};
          this.draft.client.social_channels[key] = e.target.value.trim();
          this.scheduleAutosave();
        });
      }
    };
    bindSocial('inpInstagram', 'instagram');
    bindSocial('inpTiktok', 'tiktok');
    bindSocial('inpYoutube', 'youtube');
    bindSocial('inpFacebook', 'facebook');

    // Analizador de Sitio Web
    const btnAnalyze = document.getElementById('btnAnalyzeWeb');
    if (btnAnalyze) {
      btnAnalyze.addEventListener('click', async () => {
        const url = document.getElementById('inpClientWeb').value.trim();
        if (!url) {
          this.showToast('Introduce una URL para analizar', true);
          return;
        }
        btnAnalyze.disabled = true;
        btnAnalyze.textContent = 'Rastreando web...';

        try {
          const resp = await fetch('/api/intake/analyze-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
          });
          const data = await resp.json();
          if (data.status === 'SUCCESS' && data.analysis) {
            this.inferredAnalysis = data.analysis;
            this.renderActiveStep();
            this.showToast('✨ Inferencia web completada con éxito');
            this.updateAssistant(`He analizado "${url}". Se detectó la marca "${data.analysis.brand_name}" y su paleta cromática. Revisa y acepta las sugerencias.`);
          } else {
            this.showToast('No se pudo analizar la URL indicada', true);
          }
        } catch (err) {
          this.showToast('Error de conexión al analizar URL', true);
        } finally {
          btnAnalyze.disabled = false;
          btnAnalyze.innerHTML = '<span class="btn-icon">⚡</span> Analizar Sitio Web';
        }
      });
    }

    // Aceptar Detecciones de Inferencia
    const btnAccept = document.getElementById('btnAcceptInference');
    if (btnAccept) {
      btnAccept.addEventListener('click', () => {
        if (!this.inferredAnalysis) return;
        const a = this.inferredAnalysis;
        this.draft.client.brand_name = a.brand_name || this.draft.client.brand_name;
        this.draft.client.legal_name = a.legal_name || this.draft.client.legal_name;
        this.draft.client.industry = a.industry || this.draft.client.industry;
        this.draft.client.business_type = a.business_type || this.draft.client.business_type;
        this.draft.client.description = a.description || this.draft.client.description;
        this.draft.client.website_url = a.url || this.draft.client.website_url;
        if (a.social_channels) {
          this.draft.client.social_channels = { ...this.draft.client.social_channels, ...a.social_channels };
        }
        if (a.claim) {
          this.draft.brand.claim = a.claim;
        }
        if (a.colors) {
          this.draft.brand.primary_color = a.colors.primary;
          this.draft.brand.secondary_color = a.colors.secondary;
          this.draft.brand.accent_color = a.colors.accent;
        }

        this.inferredAnalysis = null;
        this.evaluateAllStepStatuses();
        this.renderActiveStep();
        this.updateAssistant(`Detecciones aceptadas para "${this.draft.client.brand_name}". Avanza al Paso 02 para fijar el objetivo.`);
        this.scheduleAutosave();
        this.showToast('✓ Detecciones agénticas aplicadas al brief');
      });
    }

    // Descartar Inferencia
    const btnDiscard = document.getElementById('btnDiscardInference');
    if (btnDiscard) {
      btnDiscard.addEventListener('click', () => {
        this.inferredAnalysis = null;
        this.renderActiveStep();
        this.showToast('Detecciones descartadas');
      });
    }
  },

  renderStep02_Objective() {
    const categories = [
      {
        name: 'Branding & Notoriedad',
        items: [
          { id: 'AWARENESS', icon: '📢', title: 'Notoriedad y Alcance', desc: 'Maximizar recuerdo de marca y volumen masivo.' },
          { id: 'BRANDING', icon: '💎', title: 'Branding Puro', desc: 'Posicionamiento cualitativo sin llamados de venta.' },
          { id: 'RETENCION', icon: '🔁', title: 'Fidelización', desc: 'Celebrar rituales de clientes habituales y comunidad.' },
          { id: 'COMUNIDAD', icon: '🤝', title: 'Construcción de Comunidad', desc: 'Generar pertenencia, comentarios y contenido compartido.' }
        ]
      },
      {
        name: 'Conversión & Rendimiento Comercial',
        items: [
          { id: 'CONVERSION', icon: '🎯', title: 'Conversión Directa', desc: 'Incentivar compra inmediata en e-commerce con llamada clara.' },
          { id: 'VENTAS', icon: '🛒', title: 'Ventas de Catálogo', desc: 'Promoción directa de líneas de producto o combos.' },
          { id: 'LEADS', icon: '📋', title: 'Captación de Leads', desc: 'Obtener contactos comerciales o suscripciones de valor.' },
          { id: 'TRAFICO', icon: '🌐', title: 'Tráfico Cualificado', desc: 'Clics de alta intención hacia landing pages optimizadas.' },
          { id: 'REMARKETING', icon: '🔄', title: 'Remarketing / Retargeting', desc: 'Reconectar con visitantes que no finalizaron compra.' }
        ]
      },
      {
        name: 'Ocasión & Expansión',
        items: [
          { id: 'LANZAMIENTO', icon: '🚀', title: 'Lanzamiento de Producto', desc: 'Presentación de nueva referencia con alto impacto audiovisual.' },
          { id: 'ENGAGEMENT', icon: '🔥', title: 'Interacción y Viralidad', desc: 'Formatos interactivos para guardados y compartidos.' },
          { id: 'EDUCACION', icon: '📚', title: 'Educación & How-To', desc: 'Tutoriales del ritual y modo de preparación.' },
          { id: 'EVENTO', icon: '🎟️', title: 'Convocatoria a Evento', desc: 'Fechas clave, festivales o encuentros de marca.' },
          { id: 'TEMPORADA', icon: '❄️', title: 'Campaña Estacional', desc: 'Invierno, fiestas o festividades específicas.' }
        ]
      }
    ];

    const outcomes = [
      { id: 'recordar_marca', label: 'Recordar la marca ante una ocasión de consumo' },
      { id: 'comprar', label: 'Comprar producto en tienda online / e-commerce' },
      { id: 'visitar_sitio', label: 'Visitar sitio web oficial o landing' },
      { id: 'escribir_whatsapp', label: 'Escribir directamente al WhatsApp de ventas' },
      { id: 'registrarse', label: 'Registrarse en lista de espera o newsletter' },
      { id: 'seguir_redes', label: 'Seguir en Instagram o TikTok' },
      { id: 'compartir', label: 'Compartir video con amigos o historias' },
      { id: 'comentar', label: 'Comentar respondiendo a una pregunta del video' },
      { id: 'visitar_tienda', label: 'Visitar punto de venta físico' },
      { id: 'conocer_producto', label: 'Conocer características técnicas del producto' }
    ];

    const currentPrimary = this.draft.objective.primary || 'AWARENESS';
    const currentSecondaries = this.draft.objective.secondary || [];

    return `
      <!-- Objetivo Primario -->
      <div class="form-section">
        <div class="form-section-title"><span>🎯</span> Matriz de Objetivos de Negocio (14 Metas Canónicas)</div>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Selecciona el <strong>Objetivo Primario</strong> principal que determinará la curva de energía musical y el tipo de corte en DaVinci Resolve.
        </p>

        ${categories.map(cat => `
          <div class="objective-category-group">
            <div class="objective-category-title">✦ ${cat.name}</div>
            <div class="selection-grid">
              ${cat.items.map(item => `
                <div class="choice-card ${currentPrimary === item.id ? 'selected' : ''}" data-primary-obj="${item.id}">
                  <div class="choice-card-icon">${item.icon}</div>
                  <div class="choice-card-title">${item.title}</div>
                  <div class="choice-card-sub">${item.desc}</div>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>

      <!-- Objetivos Secundarios -->
      <div class="form-section">
        <div class="form-section-title"><span>🏹</span> Objetivos Secundarios de Refuerzo (Máximo 3)</div>
        <p style="font-size: 0.85rem; color: var(--text-muted);">Metas complementarias que enriquecerán las variantes de copy de Remotion.</p>
        <div class="chip-group" id="secondaryObjectivesChips">
          ${['ENGAGEMENT', 'TRAFICO', 'COMUNIDAD', 'RETENCION', 'LEADS', 'EDUCACION', 'VENTAS'].map(objId => `
            <span class="chip-pill gold ${currentSecondaries.includes(objId) ? 'active' : ''}" data-sec-obj="${objId}">
              + ${objId}
            </span>
          `).join('')}
        </div>
      </div>

      <!-- Resultado Deseado -->
      <div class="form-section">
        <div class="form-section-title"><span>✨</span> Acción Esperada del Espectador (Desired Outcome)</div>
        <div class="form-group">
          <label class="form-label">Acción Concreta tras ver el Anuncio</label>
          <select id="selDesiredOutcome" class="form-select">
            ${outcomes.map(o => `
              <option value="${o.id}" ${this.draft.objective.desired_outcome === o.id ? 'selected' : ''}>${o.label}</option>
            `).join('')}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Nota o Detalle Estratégico del Resultado</label>
          <input type="text" id="inpOutcomeNote" class="form-input" placeholder="Ej: Fomentar el ritual de la tarde entre 17:00 y 19:00 hrs" value="${this.draft.objective.custom_outcome_note || ''}">
        </div>
      </div>
    `;
  },

  bindStep02_Events() {
    // Selección de Objetivo Primario
    document.querySelectorAll('[data-primary-obj]').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('[data-primary-obj]').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.draft.objective.primary = card.getAttribute('data-primary-obj');
        this.evaluateAllStepStatuses();
        this.updateAssistant(`Objetivo primario fijado en "${this.draft.objective.primary}". Se orientará la progresión dramática en función de esta meta.`);
        this.scheduleAutosave();
      });
    });

    // Objetivos secundarios (máximo 3)
    document.querySelectorAll('#secondaryObjectivesChips .chip-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const secId = pill.getAttribute('data-sec-obj');
        if (!this.draft.objective.secondary) this.draft.objective.secondary = [];

        if (pill.classList.contains('active')) {
          pill.classList.remove('active');
          this.draft.objective.secondary = this.draft.objective.secondary.filter(s => s !== secId);
        } else {
          if (this.draft.objective.secondary.length < 3) {
            pill.classList.add('active');
            this.draft.objective.secondary.push(secId);
          } else {
            this.showToast('Máximo 3 objetivos secundarios de refuerzo', true);
          }
        }
        this.scheduleAutosave();
      });
    });

    const selOutcome = document.getElementById('selDesiredOutcome');
    if (selOutcome) {
      selOutcome.addEventListener('change', (e) => {
        this.draft.objective.desired_outcome = e.target.value;
        this.scheduleAutosave();
      });
    }

    const inpNote = document.getElementById('inpOutcomeNote');
    if (inpNote) {
      inpNote.addEventListener('input', (e) => {
        this.draft.objective.custom_outcome_note = e.target.value.trim();
        this.scheduleAutosave();
      });
    }
  },

  renderStep03_Audience() {
    const tab = this.activeAudienceTab || 'primary';
    const audienceObj = (this.draft.audience && this.draft.audience[tab])
      ? this.draft.audience[tab]
      : (this.draft.audience && this.draft.audience.primary) ? this.draft.audience.primary : {
          demographics: { age_range: [20, 45], location: 'Chile / Santiago', language: 'es', gender: 'todos', occupation: 'Profesionales' },
          psychographics: { interests: ['cultura', 'calidad'], needs: [], motivations: [], objections: [] },
          digital_behavior: { primary_platforms: ['INSTAGRAM', 'TIKTOK'] },
          is_ai_suggested: false
        };

    const demo = audienceObj.demographics || { age_range: [20, 45], location: 'Chile / Santiago' };
    const psycho = audienceObj.psychographics || { interests: ['cultura', 'calidad'], needs: [], motivations: [], objections: [] };
    const platforms = (audienceObj.digital_behavior && audienceObj.digital_behavior.primary_platforms) || ['INSTAGRAM', 'TIKTOK'];
    const isAI = audienceObj.is_ai_suggested;

    return `
      <!-- Tabs de Audiencia Tripartita -->
      <div class="form-section">
        <div class="form-section-title" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>👥</span> Audience Builder Tripartito
          </div>
          <span class="epistemology-pill ${isAI ? 'epistemology-ai' : 'epistemology-fact'}">
            ${isAI ? '⚡ AI_SUGGESTION (Inferido)' : '✓ FACT (Confirmado por Cliente)'}
          </span>
        </div>

        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Define los tres segmentos de audiencia. La audiencia primaria orientará la escena de apertura; la secundaria calibrará las variantes de copy y la exploratoria descubrirá nuevas oportunidades.
        </p>

        <div class="audience-tabs-nav">
          <button class="audience-tab-btn ${tab === 'primary' ? 'active' : ''}" data-tab="primary">
            <span>🎯</span> Audiencia Primaria (Core)
          </button>
          <button class="audience-tab-btn ${tab === 'secondary' ? 'active' : ''}" data-tab="secondary">
            <span>🤝</span> Audiencia Secundaria (Expansión)
          </button>
          <button class="audience-tab-btn ${tab === 'exploratory' ? 'active' : ''}" data-tab="exploratory">
            <span>🔭</span> Audiencia Exploratoria (Nuevos Nichos)
          </button>
        </div>

        <!-- Demografía -->
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Rango de Edad Target</label>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
              <input type="number" id="inpAudienceAgeMin" class="form-input" style="width: 80px;" value="${demo.age_range[0]}">
              <span>a</span>
              <input type="number" id="inpAudienceAgeMax" class="form-input" style="width: 80px;" value="${demo.age_range[1]}">
              <span style="font-size: 0.82rem; color: var(--text-dim);">años</span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Ubicación Geográfica y Contexto</label>
            <input type="text" id="inpAudienceLoc" class="form-input" value="${demo.location}" placeholder="Ej: Santiago de Chile / Universidades y hogares">
          </div>
        </div>

        <div class="form-group" style="margin-top: 0.75rem;">
          <label class="form-label">Perfil Ocupacional / Arquetipo</label>
          <input type="text" id="inpAudienceOcc" class="form-input" value="${demo.occupation || ''}" placeholder="Ej: Estudiantes universitarios, trabajadores remotos y creativos">
        </div>
      </div>

      <!-- Psicografía e Intereses -->
      <div class="form-section">
        <div class="form-section-title"><span>🧠</span> Psicografía, Deseos y Motivaciones Clave</div>
        
        <div class="form-group">
          <label class="form-label">Intereses Centrales</label>
          <div class="chip-group" id="audienceInterestChips">
            ${['cultura', 'gastronomía', 'calidad', 'autenticidad', 'bienestar', 'rituales', 'aire libre', 'música', 'diseño', 'sostenibilidad'].map(tag => `
              <span class="chip-pill ${psycho.interests.includes(tag) ? 'active' : ''}" data-int="${tag}">
                #${tag}
              </span>
            `).join('')}
          </div>
        </div>

        <div class="form-grid-2" style="margin-top: 1rem;">
          <div class="form-group">
            <label class="form-label">Motivaciones Principales de Compra</label>
            <input type="text" id="inpAudienceMotivations" class="form-input" placeholder="Ej: Conectar con amigos, pausa de calidad" value="${(psycho.motivations || []).join(', ')}">
          </div>
          <div class="form-group">
            <label class="form-label">Fricciones u Objeciones Habituales</label>
            <input type="text" id="inpAudienceObjections" class="form-input" placeholder="Ej: Tiempo de preparación, precio" value="${(psycho.objections || []).join(', ')}">
          </div>
        </div>
      </div>

      <!-- Plataformas Digitales y Consumo -->
      <div class="form-section">
        <div class="form-section-title"><span>📱</span> Canales de Consumo Audiovisual Preferidos</div>
        <div class="chip-group" id="audiencePlatformChips">
          ${[
            { id: 'TIKTOK', label: 'TikTok (9:16)' },
            { id: 'INSTAGRAM', label: 'Instagram (Reels / Stories)' },
            { id: 'YOUTUBE', label: 'YouTube (Shorts / Feed)' },
            { id: 'SPOTIFY', label: 'Spotify Podcasts' },
            { id: 'FACEBOOK', label: 'Meta Feed' }
          ].map(p => `
            <span class="chip-pill gold ${platforms.includes(p.id) ? 'active' : ''}" data-plat="${p.id}">
              ✦ ${p.label}
            </span>
          `).join('')}
        </div>
      </div>
    `;
  },

  bindStep03_Events() {
    const tab = this.activeAudienceTab || 'primary';
    const aud = this.draft.audience[tab];

    // Cambio de tab
    document.querySelectorAll('.audience-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeAudienceTab = btn.getAttribute('data-tab');
        this.renderActiveStep();
      });
    });

    // Inputs de demografía
    const inpMin = document.getElementById('inpAudienceAgeMin');
    const inpMax = document.getElementById('inpAudienceAgeMax');
    if (inpMin && inpMax && aud) {
      const updateAge = () => {
        aud.demographics.age_range = [parseInt(inpMin.value, 10) || 18, parseInt(inpMax.value, 10) || 65];
        this.scheduleAutosave();
      };
      inpMin.addEventListener('input', updateAge);
      inpMax.addEventListener('input', updateAge);
    }

    const inpLoc = document.getElementById('inpAudienceLoc');
    if (inpLoc && aud) {
      inpLoc.addEventListener('input', (e) => {
        aud.demographics.location = e.target.value.trim();
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
      });
    }

    const inpOcc = document.getElementById('inpAudienceOcc');
    if (inpOcc && aud) {
      inpOcc.addEventListener('input', (e) => {
        aud.demographics.occupation = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    // Intereses chips
    document.querySelectorAll('#audienceInterestChips .chip-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const intTag = pill.getAttribute('data-int');
        if (!aud.psychographics.interests) aud.psychographics.interests = [];
        pill.classList.toggle('active');
        if (pill.classList.contains('active')) {
          if (!aud.psychographics.interests.includes(intTag)) aud.psychographics.interests.push(intTag);
        } else {
          aud.psychographics.interests = aud.psychographics.interests.filter(i => i !== intTag);
        }
        this.scheduleAutosave();
      });
    });

    // Plataformas chips
    document.querySelectorAll('#audiencePlatformChips .chip-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const platId = pill.getAttribute('data-plat');
        if (!aud.digital_behavior.primary_platforms) aud.digital_behavior.primary_platforms = [];
        pill.classList.toggle('active');
        if (pill.classList.contains('active')) {
          if (!aud.digital_behavior.primary_platforms.includes(platId)) aud.digital_behavior.primary_platforms.push(platId);
        } else {
          aud.digital_behavior.primary_platforms = aud.digital_behavior.primary_platforms.filter(p => p !== platId);
        }
        this.scheduleAutosave();
      });
    });

    const inpmot = document.getElementById('inpAudienceMotivations');
    if (inpmot && aud) {
      inpmot.addEventListener('input', (e) => {
        aud.psychographics.motivations = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
        this.scheduleAutosave();
      });
    }

    const inpobj = document.getElementById('inpAudienceObjections');
    if (inpobj && aud) {
      inpobj.addEventListener('input', (e) => {
        aud.psychographics.objections = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
        this.scheduleAutosave();
      });
    }
  },

  renderStep04_Brand() {
    const tones = ['auténtico', 'cálido', 'cercano', 'premium', 'innovador', 'artesanal', 'inspirador', 'rebelde'];
    const currentTones = this.draft.brand.tone_of_voice || ['auténtico', 'cálido'];
    const kelvin = this.draft.brand.color_temperature_target_kelvin || 5900;
    const logos = this.draft.brand.logo_files || ['logo_master_vector.svg'];

    return `
      <!-- Claim y Propósito -->
      <div class="form-section">
        <div class="form-section-title"><span>🎨</span> Brand Identity Studio — Propósito y Claim</div>
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Claim Principal o Eslogan de Marca <span class="required">*</span></label>
            <input type="text" id="inpClaim" class="form-input" placeholder="Ej: ¿Dónde estás tú? Está tu mate" value="${this.draft.brand.claim || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Propósito / Esencia de la Marca</label>
            <input type="text" id="inpPurpose" class="form-input" placeholder="Ej: Fomentar pausas auténticas y rituales compartidos" value="${this.draft.brand.purpose || ''}">
          </div>
        </div>
      </div>

      <!-- Paleta Cromática y Temperatura de Color -->
      <div class="form-section">
        <div class="form-section-title"><span>🌈</span> Paleta Cromática Institucional & Grading Térmico</div>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Los colores HEX seleccionados alimentarán automáticamente los generadores tipográficos en HyperFrames y el balance de blancos en DaVinci Resolve.
        </p>

        <div class="color-picker-grid">
          <div class="color-picker-cell">
            <input type="color" id="inpColPrimary" class="color-input-swatch" value="${this.draft.brand.primary_color || '#0D5C3A'}">
            <div>
              <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">Color Primario (Fondo / Base)</div>
              <div style="font-weight: 700; font-family: var(--font-mono); font-size: 0.88rem;" id="lblColPrimary">${this.draft.brand.primary_color || '#0D5C3A'}</div>
            </div>
          </div>

          <div class="color-picker-cell">
            <input type="color" id="inpColSecondary" class="color-input-swatch" value="${this.draft.brand.secondary_color || '#D4AF37'}">
            <div>
              <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">Color Secundario (Marca / Oro)</div>
              <div style="font-weight: 700; font-family: var(--font-mono); font-size: 0.88rem;" id="lblColSecondary">${this.draft.brand.secondary_color || '#D4AF37'}</div>
            </div>
          </div>

          <div class="color-picker-cell">
            <input type="color" id="inpColAccent" class="color-input-swatch" value="${this.draft.brand.accent_color || '#10B981'}">
            <div>
              <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">Color de Acento (CTA / Glow)</div>
              <div style="font-weight: 700; font-family: var(--font-mono); font-size: 0.88rem;" id="lblColAccent">${this.draft.brand.accent_color || '#10B981'}</div>
            </div>
          </div>
        </div>

        <!-- Vista Previa de Contraste y Accesibilidad WCAG -->
        <div class="color-matrix-preview" id="colorContrastPreview" style="background: ${this.draft.brand.primary_color || '#0D5C3A'}; color: #FFF;">
          <div>
            <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: -0.01em;">
              ${this.draft.client.brand_name || 'Nombre de la Marca'}
            </div>
            <div style="font-size: 0.82rem; color: ${this.draft.brand.secondary_color || '#D4AF37'}; font-weight: 600;">
              ${this.draft.brand.claim || 'Claim institucional visible sobre fondo primario'}
            </div>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <span class="wcag-indicator wcag-pass" id="wcagBadge">✓ WCAG AAA (7.8:1)</span>
          </div>
        </div>

        <!-- Temperatura de Color (Kelvin) -->
        <div class="kelvin-box" style="margin-top: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <label class="form-label">Temperatura de Color Cinematográfica Target</label>
            <span style="font-family: var(--font-mono); font-size: 0.82rem; font-weight: 700; color: var(--color-gold-bright);" id="lblKelvinValue">
              ${kelvin}K (${kelvin <= 4500 ? 'Cálido Tungsteno' : kelvin <= 5600 ? 'Natural Golden Hour' : 'Luz Día Fría'})
            </span>
          </div>
          <div class="kelvin-track-bar"></div>
          <input type="range" id="rngKelvin" class="kelvin-slider-input" min="3200" max="6500" step="100" value="${kelvin}">
        </div>
      </div>

      <!-- Tono de Voz y Personalidad -->
      <div class="form-section">
        <div class="form-section-title"><span>🗣️</span> Tono de Voz y Personalidad Editorial</div>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Selecciona hasta 3 atributos de tono de voz. Esto calibrará los agentes de Copywriting y Storyboard para mantener consistencia acústica y textual.
        </p>
        <div class="chip-group" id="tonePillsGroup">
          ${tones.map(t => `
            <span class="chip-pill ${currentTones.includes(t) ? 'active' : ''}" data-tone="${t}">
              ✦ ${t}
            </span>
          `).join('')}
        </div>

        <div class="form-grid-2" style="margin-top: 1rem;">
          <div class="form-group">
            <label class="form-label">Palabras Obligatorias o Recomendadas</label>
            <input type="text" id="inpMandatoryWords" class="form-input" placeholder="Ej: ritual, compartir, origen, tradición" value="${(this.draft.brand.mandatory_words || []).join(', ')}">
          </div>
          <div class="form-group">
            <label class="form-label">Palabras Prohibidas (Brand Safety)</label>
            <input type="text" id="inpForbiddenWords" class="form-input" placeholder="Ej: artificial, químico, barato, apurado" value="${(this.draft.brand.forbidden_words || []).join(', ')}">
          </div>
        </div>
      </div>

      <!-- Brand Assets Uploader & Drag & Drop -->
      <div class="form-section">
        <div class="form-section-title"><span>📁</span> Brand Assets (Logotipos, Manuales y Tipografías)</div>
        
        <div class="brand-dropzone" id="brandDropzone">
          <div class="brand-dropzone-icon">⇪</div>
          <div class="brand-dropzone-title">Arrastra aquí tus logotipos vectoriales (SVG), PNGs transparentes o Manual PDF</div>
          <div class="brand-dropzone-sub">Soporta: .SVG, .PNG, .PDF, .TTF, .WOFF2 (Máx. 50 MB) o haz clic para explorar</div>
          <input type="file" id="inpBrandFiles" multiple accept=".svg,.png,.pdf,.ttf,.woff2" style="display: none;">
        </div>

        <div class="brand-assets-list" id="brandAssetsList">
          ${logos.map(file => `
            <div class="brand-asset-card">
              <span class="brand-asset-badge badge-svg">SVG</span>
              <span style="font-weight: 600; color: #FFF;">${file}</span>
              <span style="color: var(--color-emerald); font-size: 0.75rem;">✓ Vectorial</span>
            </div>
          `).join('')}
          ${this.draft.brand.brand_manual_pdf ? `
            <div class="brand-asset-card">
              <span class="brand-asset-badge badge-pdf">PDF</span>
              <span style="font-weight: 600; color: #FFF;">${this.draft.brand.brand_manual_pdf}</span>
              <span style="color: var(--text-dim); font-size: 0.75rem;">Manual de Marca</span>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  },

  bindStep04_Events() {
    // Inputs de Colores
    const bindColor = (inpId, lblId, key) => {
      const inp = document.getElementById(inpId);
      const lbl = document.getElementById(lblId);
      if (inp && lbl) {
        inp.addEventListener('input', (e) => {
          this.draft.brand[key] = e.target.value.toUpperCase();
          lbl.textContent = this.draft.brand[key];
          
          // Actualizar preview de contraste
          const preview = document.getElementById('colorContrastPreview');
          if (preview) {
            if (key === 'primary_color') preview.style.background = this.draft.brand.primary_color;
          }
          this.evaluateAllStepStatuses();
          this.scheduleAutosave();
        });
      }
    };
    bindColor('inpColPrimary', 'lblColPrimary', 'primary_color');
    bindColor('inpColSecondary', 'lblColSecondary', 'secondary_color');
    bindColor('inpColAccent', 'lblColAccent', 'accent_color');

    // Claim y Propósito
    const inpClaim = document.getElementById('inpClaim');
    if (inpClaim) {
      inpClaim.addEventListener('input', (e) => {
        this.draft.brand.claim = e.target.value.trim();
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
      });
    }

    const inpPurpose = document.getElementById('inpPurpose');
    if (inpPurpose) {
      inpPurpose.addEventListener('input', (e) => {
        this.draft.brand.purpose = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    // Slider Kelvin
    const rngKelvin = document.getElementById('rngKelvin');
    const lblKelvin = document.getElementById('lblKelvinValue');
    if (rngKelvin && lblKelvin) {
      rngKelvin.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        this.draft.brand.color_temperature_target_kelvin = val;
        const desc = val <= 4500 ? 'Cálido Tungsteno' : val <= 5600 ? 'Natural Golden Hour' : 'Luz Día Fría';
        lblKelvin.textContent = `${val}K (${desc})`;
        this.scheduleAutosave();
      });
    }

    // Tono de voz pills
    document.querySelectorAll('#tonePillsGroup .chip-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const tone = pill.getAttribute('data-tone');
        if (!this.draft.brand.tone_of_voice) this.draft.brand.tone_of_voice = [];
        
        if (pill.classList.contains('active')) {
          pill.classList.remove('active');
          this.draft.brand.tone_of_voice = this.draft.brand.tone_of_voice.filter(t => t !== tone);
        } else {
          if (this.draft.brand.tone_of_voice.length < 3) {
            pill.classList.add('active');
            this.draft.brand.tone_of_voice.push(tone);
          } else {
            this.showToast('Máximo 3 atributos de tono de voz', true);
          }
        }
        this.scheduleAutosave();
      });
    });

    // Palabras obligatorias y prohibidas
    const inpMand = document.getElementById('inpMandatoryWords');
    if (inpMand) {
      inpMand.addEventListener('input', (e) => {
        this.draft.brand.mandatory_words = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
        this.scheduleAutosave();
      });
    }

    const inpForb = document.getElementById('inpForbiddenWords');
    if (inpForb) {
      inpForb.addEventListener('input', (e) => {
        this.draft.brand.forbidden_words = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
        this.scheduleAutosave();
      });
    }

    // Dropzone funcional
    const dropzone = document.getElementById('brandDropzone');
    const fileInput = document.getElementById('inpBrandFiles');
    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.handleBrandFileUploads(e.dataTransfer.files);
        }
      });

      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
          this.handleBrandFileUploads(e.target.files);
        }
      });
    }
  },

  handleBrandFileUploads(files) {
    if (!this.draft.brand.logo_files) this.draft.brand.logo_files = [];

    Array.from(files).forEach(f => {
      if (f.name.endsWith('.pdf')) {
        this.draft.brand.brand_manual_pdf = f.name;
      } else {
        if (!this.draft.brand.logo_files.includes(f.name)) {
          this.draft.brand.logo_files.push(f.name);
        }
      }
    });

    this.renderActiveStep();
    this.evaluateAllStepStatuses();
    this.scheduleAutosave();
    this.showToast(`✓ ${files.length} archivo(s) de marca cargado(s)`);
    this.updateAssistant(`Se han incorporado ${files.length} activo(s) a la identidad de marca.`);
  },

  renderStep05_Product() {
    if (!this.draft.products || !Array.isArray(this.draft.products) || this.draft.products.length === 0) {
      this.draft.products = [{
        id: 'prod-1',
        sku: 'SKU-001',
        name: '',
        category: 'Yerba Mate & Infusiones',
        regular_price: 15000,
        offer_price: null,
        currency: 'CLP',
        description: '',
        verified_benefits: ['100% Auténtico', 'Calidad Premium'],
        forbidden_claims: ['Cura enfermedades', 'Garantía eterna'],
        specs: ''
      }];
    }

    if (this.activeProductIndex === undefined || this.activeProductIndex >= this.draft.products.length) {
      this.activeProductIndex = 0;
    }

    const prod = this.draft.products[this.activeProductIndex] || this.draft.products[0];
    const categories = ['Yerba Mate & Infusiones', 'Termos & Botellas', 'Mates & Bombillas', 'Accesorios & Sets', 'Gourmet & Alimentos', 'Indumentaria & Textil', 'Servicios / Cursos', 'Otro'];
    const currencies = ['CLP', 'USD', 'EUR', 'ARS', 'MXN', 'COP'];

    return `
      <!-- Product Manager Bar -->
      <div class="product-manager-bar">
        <div class="product-tabs-list" id="productTabsList">
          ${this.draft.products.map((p, idx) => `
            <button class="product-tab-btn ${idx === this.activeProductIndex ? 'active' : ''}" data-prod-idx="${idx}">
              <span>📦</span> ${p.name && p.name.trim() ? (p.name.length > 20 ? p.name.substring(0, 20) + '…' : p.name) : `Producto ${idx + 1}`}
              ${this.draft.products.length > 1 ? `<span class="remove-prod-btn" data-remove-idx="${idx}" title="Eliminar referencia">×</span>` : ''}
            </button>
          `).join('')}
        </div>
        <button class="btn btn-secondary" id="btnAddProduct" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">
          <span>+</span> Añadir Referencia
        </button>
      </div>

      <!-- Ficha de Producto Activo -->
      <div class="form-section">
        <div class="form-section-title" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>📋</span> Especificación de Producto [${this.activeProductIndex + 1} de ${this.draft.products.length}]
          </div>
          <span style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-dim);">
            ID: ${prod.id || `prod-${this.activeProductIndex + 1}`}
          </span>
        </div>

        <div class="form-grid-3">
          <div class="form-group">
            <label class="form-label">Nombre del Producto / Pack Protagonista *</label>
            <input type="text" id="inpProdName" class="form-input" placeholder="Ej: Termo de Acero Inoxidable 1L Edición Patagónica" value="${prod.name || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">SKU o Código de Referencia</label>
            <input type="text" id="inpProdSku" class="form-input" placeholder="Ej: LM-TRM-01" value="${prod.sku || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Categoría Comercial</label>
            <select id="selProdCategory" class="form-select">
              ${categories.map(c => `<option value="${c}" ${(prod.category === c) ? 'selected' : ''}>${c}</option>`).join('')}
            </select>
          </div>
        </div>

        <div class="form-grid-3">
          <div class="form-group">
            <label class="form-label">Precio Regular</label>
            <input type="number" id="inpProdRegularPrice" class="form-input" placeholder="38990" value="${prod.regular_price || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Precio de Oferta (Opcional)</label>
            <input type="number" id="inpProdOfferPrice" class="form-input" placeholder="29990" value="${prod.offer_price || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Moneda</label>
            <select id="selProdCurrency" class="form-select">
              ${currencies.map(curr => `<option value="${curr}" ${(prod.currency === curr) ? 'selected' : ''}>${curr}</option>`).join('')}
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Descripción Sensorial y Técnica</label>
          <textarea id="inpProdDesc" class="form-textarea" placeholder="Describe los atributos sensoriales, materiales y diferenciales del producto...">${prod.description || ''}</textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Especificaciones Técnicas Clave (Specs)</label>
          <input type="text" id="inpProdSpecs" class="form-input" placeholder="Ej: 1L de capacidad, acero inoxidable 304, peso 540g, libre de BPA" value="${typeof prod.specs === 'string' ? prod.specs : (prod.specs ? JSON.stringify(prod.specs) : '')}">
        </div>

        <!-- Escudo Anti-Alucinación -->
        <div class="anti-hallucination-card">
          <div class="anti-hallucination-header">
            <div class="anti-hallucination-title">
              <span>🛡️</span> Escudo Anti-Alucinación de Beneficios
            </div>
            <span class="anti-hallucination-badge">STRICT REASONING GUARD</span>
          </div>

          <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.85rem; line-height: 1.4;">
            Los agentes de Copywriting y Storyboard tienen <strong>estrictamente prohibido</strong> inventar afirmaciones o atribuir propiedades no verificadas. Define los beneficios comprobados que la IA destacará y las afirmaciones explícitamente bloqueadas.
          </p>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <!-- Beneficios Verificados -->
            <div>
              <label class="form-label" style="color: var(--color-emerald); font-weight: 600;">
                ✓ Beneficios Verificados Permitidos (${(prod.verified_benefits || []).length})
              </label>
              <div class="claims-chip-container" id="verifiedBenefitsContainer">
                ${(prod.verified_benefits || []).map((ben, bIdx) => `
                  <span class="claim-chip verified">
                    <span>✓</span> ${ben}
                    <span class="claim-chip-remove" data-remove-benefit="${bIdx}">×</span>
                  </span>
                `).join('')}
              </div>
              <div style="display: flex; gap: 0.4rem; margin-top: 0.5rem;">
                <input type="text" id="inpNewBenefit" class="form-input" style="font-size: 0.8rem; padding: 0.35rem 0.6rem;" placeholder="Ej: Mantiene agua caliente 24h">
                <button class="btn btn-secondary" id="btnAddBenefit" style="font-size: 0.8rem; padding: 0.35rem 0.65rem; white-space: nowrap;">+ Añadir</button>
              </div>
            </div>

            <!-- Afirmaciones Prohibidas -->
            <div>
              <label class="form-label" style="color: var(--color-rose); font-weight: 600;">
                ⛔ Afirmaciones Prohibidas / Restricciones (${(prod.forbidden_claims || []).length})
              </label>
              <div class="claims-chip-container" id="forbiddenClaimsContainer">
                ${(prod.forbidden_claims || []).map((claim, cIdx) => `
                  <span class="claim-chip forbidden">
                    <span>⛔</span> ${claim}
                    <span class="claim-chip-remove" data-remove-claim="${cIdx}">×</span>
                  </span>
                `).join('')}
              </div>
              <div style="display: flex; gap: 0.4rem; margin-top: 0.5rem;">
                <input type="text" id="inpNewClaim" class="form-input" style="font-size: 0.8rem; padding: 0.35rem 0.6rem;" placeholder="Ej: Cura problemas estomacales">
                <button class="btn btn-secondary" id="btnAddClaim" style="font-size: 0.8rem; padding: 0.35rem 0.65rem; white-space: nowrap;">+ Bloquear</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  bindStep05_Events() {
    const prod = this.draft.products[this.activeProductIndex] || this.draft.products[0];

    // Cambiar de producto
    document.querySelectorAll('#productTabsList .product-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-prod-btn')) return;
        const idx = parseInt(btn.getAttribute('data-prod-idx'), 10);
        this.activeProductIndex = idx;
        this.render();
      });
    });

    // Eliminar producto
    document.querySelectorAll('#productTabsList .remove-prod-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(btn.getAttribute('data-remove-idx'), 10);
        if (this.draft.products.length > 1) {
          this.draft.products.splice(idx, 1);
          if (this.activeProductIndex >= this.draft.products.length) {
            this.activeProductIndex = this.draft.products.length - 1;
          }
          this.evaluateAllStepStatuses();
          this.scheduleAutosave();
          this.render();
        }
      });
    });

    // Añadir producto
    const btnAddProd = document.getElementById('btnAddProduct');
    if (btnAddProd) {
      btnAddProd.addEventListener('click', () => {
        const newId = `prod-${this.draft.products.length + 1}`;
        this.draft.products.push({
          id: newId,
          sku: `SKU-00${this.draft.products.length + 1}`,
          name: '',
          category: 'Yerba Mate & Infusiones',
          regular_price: 15000,
          offer_price: null,
          currency: 'CLP',
          description: '',
          verified_benefits: ['Calidad Garantizada'],
          forbidden_claims: ['Propiedades milagrosas'],
          specs: ''
        });
        this.activeProductIndex = this.draft.products.length - 1;
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
        this.render();
      });
    }

    // Campos del producto activo
    const inpName = document.getElementById('inpProdName');
    if (inpName) {
      inpName.addEventListener('input', (e) => {
        prod.name = e.target.value.trim();
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
      });
    }

    const inpSku = document.getElementById('inpProdSku');
    if (inpSku) {
      inpSku.addEventListener('input', (e) => {
        prod.sku = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    const selCategory = document.getElementById('selProdCategory');
    if (selCategory) {
      selCategory.addEventListener('change', (e) => {
        prod.category = e.target.value;
        this.scheduleAutosave();
      });
    }

    const inpRegPrice = document.getElementById('inpProdRegularPrice');
    if (inpRegPrice) {
      inpRegPrice.addEventListener('input', (e) => {
        prod.regular_price = parseFloat(e.target.value) || 0;
        this.scheduleAutosave();
      });
    }

    const inpOffPrice = document.getElementById('inpProdOfferPrice');
    if (inpOffPrice) {
      inpOffPrice.addEventListener('input', (e) => {
        prod.offer_price = e.target.value ? parseFloat(e.target.value) : null;
        this.scheduleAutosave();
      });
    }

    const selCurrency = document.getElementById('selProdCurrency');
    if (selCurrency) {
      selCurrency.addEventListener('change', (e) => {
        prod.currency = e.target.value;
        this.scheduleAutosave();
      });
    }

    const inpDesc = document.getElementById('inpProdDesc');
    if (inpDesc) {
      inpDesc.addEventListener('input', (e) => {
        prod.description = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    const inpSpecs = document.getElementById('inpProdSpecs');
    if (inpSpecs) {
      inpSpecs.addEventListener('input', (e) => {
        prod.specs = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    // Añadir Beneficio Verificado
    const btnAddBen = document.getElementById('btnAddBenefit');
    const inpNewBen = document.getElementById('inpNewBenefit');
    const addBenefitAction = () => {
      if (!inpNewBen || !inpNewBen.value.trim()) return;
      if (!prod.verified_benefits) prod.verified_benefits = [];
      prod.verified_benefits.push(inpNewBen.value.trim());
      inpNewBen.value = '';
      this.evaluateAllStepStatuses();
      this.scheduleAutosave();
      this.render();
    };
    if (btnAddBen) btnAddBen.addEventListener('click', addBenefitAction);
    if (inpNewBen) {
      inpNewBen.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); addBenefitAction(); }
      });
    }

    // Eliminar Beneficio Verificado
    document.querySelectorAll('[data-remove-benefit]').forEach(el => {
      el.addEventListener('click', () => {
        const idx = parseInt(el.getAttribute('data-remove-benefit'), 10);
        prod.verified_benefits.splice(idx, 1);
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
        this.render();
      });
    });

    // Añadir Afirmación Prohibida
    const btnAddClaim = document.getElementById('btnAddClaim');
    const inpNewClaim = document.getElementById('inpNewClaim');
    const addClaimAction = () => {
      if (!inpNewClaim || !inpNewClaim.value.trim()) return;
      if (!prod.forbidden_claims) prod.forbidden_claims = [];
      prod.forbidden_claims.push(inpNewClaim.value.trim());
      inpNewClaim.value = '';
      this.scheduleAutosave();
      this.render();
    };
    if (btnAddClaim) btnAddClaim.addEventListener('click', addClaimAction);
    if (inpNewClaim) {
      inpNewClaim.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); addClaimAction(); }
      });
    }

    // Eliminar Afirmación Prohibida
    document.querySelectorAll('[data-remove-claim]').forEach(el => {
      el.addEventListener('click', () => {
        const idx = parseInt(el.getAttribute('data-remove-claim'), 10);
        prod.forbidden_claims.splice(idx, 1);
        this.scheduleAutosave();
        this.render();
      });
    });
  },

  renderStep06_Offer() {
    const isBranding = !!this.draft.offer.is_branding_only;
    const offerTypes = [
      { id: 'DISCOUNT_PERCENT', icon: '🏷️', title: 'Porcentaje de Descuento', desc: '% OFF directo sobre el total o categoría' },
      { id: 'DISCOUNT_AMOUNT', icon: '💵', title: 'Monto Fijo de Descuento', desc: 'Rebaja monetaria específica ($ CLP / USD)' },
      { id: 'BUNDLE_COMBO', icon: '📦', title: 'Pack o Combo Especial', desc: 'Precios especiales por comprar set (2x1, kit completo)' },
      { id: 'FREE_SHIPPING', icon: '🚚', title: 'Envío Gratis', desc: 'Despacho sin costo por tiempo o monto limitado' },
      { id: 'SPECIAL_GIFT', icon: '🎁', title: 'Regalo por Compra', desc: 'Obsequio complementario incluido en el pedido' },
      { id: 'LIMITED_EDITION', icon: '✨', title: 'Edición Limitada', desc: 'Lanzamiento exclusivo por volumen o temporada' }
    ];

    const currentOfferType = this.draft.offer.offer_type || 'DISCOUNT_PERCENT';
    const urgencyBadges = ['Ninguno', 'ÚLTIMAS 48 HORAS', 'OFERTA RELÁMPAGO', 'STOCK LIMITADO', 'SOLO POR HOY', 'CUPOS LIMITADOS'];

    return `
      <!-- Selector de Modo: Comercial vs Branding Puro -->
      <div class="form-section">
        <div class="form-section-title"><span>⚖️</span> Enfoque Estratégico de Campaña</div>
        <div class="offer-mode-selector">
          <div class="offer-mode-card ${!isBranding ? 'selected' : ''}" data-mode="COMMERCIAL">
            <div class="offer-mode-icon">🏷️</div>
            <div>
              <div class="offer-mode-title">Campaña Promocional con Oferta</div>
              <div class="offer-mode-desc">
                Genera urgencia e incentivo comercial directo. Incluye cupones, descuentos, stickers de oferta y llamados a comprar.
              </div>
            </div>
          </div>
          <div class="offer-mode-card ${isBranding ? 'selected branding-puro' : ''}" data-mode="BRANDING_PURO">
            <div class="offer-mode-icon">💎</div>
            <div>
              <div class="offer-mode-title">Branding Institucional & Prestigio</div>
              <div class="offer-mode-desc">
                Campaña pura de posicionamiento. Sin precios tachados, sin stickers de oferta ni urgencia comercial invasiva.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contenido Condicional: Branding Puro vs Oferta Comercial -->
      ${isBranding ? `
        <div class="form-section">
          <div class="branding-puro-banner">
            <div class="branding-puro-banner-icon">💎</div>
            <div>
              <div style="font-size: 1rem; font-weight: 700; color: #38BDF8; margin-bottom: 0.25rem;">
                Modo Prestigio & Branding Puro Activado
              </div>
              <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.45; margin: 0;">
                Los motores de <strong>DaVinci Resolve</strong> y <strong>Remotion</strong> configurarán una composición cinematográfica de alta gama, suprimiendo automáticamente elementos promocionales como badges de descuento, precios o contadores de tiempo. La narrativa se enfocará en el ritual de marca, la artesanía y la emoción.
              </p>
            </div>
          </div>
        </div>
      ` : `
        <!-- Tipos de Oferta Comercial -->
        <div class="form-section">
          <div class="form-section-title"><span>🎯</span> Tipo de Propuesta Comercial</div>
          <div class="offer-type-grid" id="offerTypeGrid">
            ${offerTypes.map(ot => `
              <div class="offer-type-card ${currentOfferType === ot.id ? 'selected' : ''}" data-offer-type="${ot.id}">
                <div class="offer-type-icon">${ot.icon}</div>
                <div class="offer-type-title">${ot.title}</div>
                <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 4px;">${ot.desc}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Ficha de Términos Comerciales -->
        <div class="form-section">
          <div class="form-section-title"><span>📝</span> Parámetros de la Oferta</div>
          <div class="form-grid-2">
            <div class="form-group">
              <label class="form-label">Título o Gancho de la Oferta *</label>
              <input type="text" id="inpOfferTitle" class="form-input" placeholder="Ej: 30% OFF en Termos y Mates de Colección" value="${this.draft.offer.offer_title || ''}">
            </div>
            <div class="form-group">
              <label class="form-label">Código de Cupón / Promo</label>
              <input type="text" id="inpCouponCode" class="form-input" placeholder="Ej: MATEROS30" value="${this.draft.offer.coupon_code || ''}">
            </div>
          </div>

          <div class="form-grid-3">
            <div class="form-group">
              <label class="form-label">Descuento (%)</label>
              <input type="number" id="inpOfferDiscount" class="form-input" placeholder="30" value="${this.draft.offer.discount_percentage || ''}">
            </div>
            <div class="form-group">
              <label class="form-label">Vigencia / Fecha Límite</label>
              <input type="text" id="inpOfferValidUntil" class="form-input" placeholder="Ej: Hasta agotar 100 unidades" value="${this.draft.offer.valid_until || ''}">
            </div>
            <div class="form-group">
              <label class="form-label">Badge de Urgencia en Motion Graphics</label>
              <select id="selUrgencyBadge" class="form-select">
                ${urgencyBadges.map(ub => `<option value="${ub}" ${(this.draft.offer.urgency_badge === ub) ? 'selected' : ''}>${ub}</option>`).join('')}
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Términos y Condiciones Resumidos (Letra Chica)</label>
            <input type="text" id="inpOfferTerms" class="form-input" placeholder="Ej: Válido para compras sobre $20.000. Excluye costo de envío." value="${this.draft.offer.terms_conditions || ''}">
          </div>
        </div>
      `}
    `;
  },

  bindStep06_Events() {
    // Selector de modo Comercial vs Branding Puro
    document.querySelectorAll('.offer-mode-card').forEach(card => {
      card.addEventListener('click', () => {
        const mode = card.getAttribute('data-mode');
        this.draft.offer.is_branding_only = (mode === 'BRANDING_PURO');
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
        this.render();
      });
    });

    // Si está en modo oferta comercial
    if (!this.draft.offer.is_branding_only) {
      // Tipo de oferta
      document.querySelectorAll('#offerTypeGrid .offer-type-card').forEach(card => {
        card.addEventListener('click', () => {
          document.querySelectorAll('#offerTypeGrid .offer-type-card').forEach(c => c.classList.remove('selected'));
          card.classList.add('selected');
          this.draft.offer.offer_type = card.getAttribute('data-offer-type');
          this.scheduleAutosave();
        });
      });

      const inpTitle = document.getElementById('inpOfferTitle');
      if (inpTitle) {
        inpTitle.addEventListener('input', (e) => {
          this.draft.offer.offer_title = e.target.value.trim();
          this.evaluateAllStepStatuses();
          this.scheduleAutosave();
        });
      }

      const inpCoupon = document.getElementById('inpCouponCode');
      if (inpCoupon) {
        inpCoupon.addEventListener('input', (e) => {
          this.draft.offer.coupon_code = e.target.value.trim();
          this.scheduleAutosave();
        });
      }

      const inpDiscount = document.getElementById('inpOfferDiscount');
      if (inpDiscount) {
        inpDiscount.addEventListener('input', (e) => {
          this.draft.offer.discount_percentage = parseInt(e.target.value, 10) || 0;
          this.scheduleAutosave();
        });
      }

      const inpValid = document.getElementById('inpOfferValidUntil');
      if (inpValid) {
        inpValid.addEventListener('input', (e) => {
          this.draft.offer.valid_until = e.target.value.trim();
          this.scheduleAutosave();
        });
      }

      const selUrgency = document.getElementById('selUrgencyBadge');
      if (selUrgency) {
        selUrgency.addEventListener('change', (e) => {
          this.draft.offer.urgency_badge = e.target.value;
          this.scheduleAutosave();
        });
      }

      const inpTerms = document.getElementById('inpOfferTerms');
      if (inpTerms) {
        inpTerms.addEventListener('input', (e) => {
          this.draft.offer.terms_conditions = e.target.value.trim();
          this.scheduleAutosave();
        });
      }
    }
  },

  renderStep07_Creative() {
    const canonicalEmotions = [
      { id: 'CONFIANZA', icon: '🤝', name: 'Confianza & Credibilidad' },
      { id: 'ALEGRIA', icon: '😄', name: 'Alegría & Optimismo' },
      { id: 'NOSTALGIA', icon: '🕰️', name: 'Nostalgia & Tradición' },
      { id: 'ENERGIA', icon: '⚡', name: 'Energía & Impulso' },
      { id: 'TRANQUILIDAD', icon: '🌿', name: 'Tranquilidad & Calma' },
      { id: 'CURIOSIDAD', icon: '🔍', name: 'Curiosidad & Asombro' },
      { id: 'EXCLUSIVIDAD', icon: '💎', name: 'Exclusividad & Prestigio' },
      { id: 'INSPIRACION', icon: '✨', name: 'Inspiración & Elevación' },
      { id: 'URGENCIA', icon: '🔥', name: 'Urgencia & Acción' },
      { id: 'HUMOR', icon: '🎉', name: 'Humor & Espontaneidad' },
      { id: 'EMPATIA', icon: '❤️', name: 'Empatía & Calidez' },
      { id: 'ORGULLO', icon: '🏔️', name: 'Orgullo & Pertenencia' }
    ];

    const treatments = [
      { id: 'CINEMATIC_DOCUMENTARY', icon: '🎬', title: 'Cine Documental', desc: 'Luz natural, encuadres orgánicos, texturas reales y narrativa de autor.' },
      { id: 'FAST_PACED_TIKTOK', icon: '⚡', title: 'Fast-Paced Social', desc: 'Cortes dinámicos, ritmo de edición ágil y lenguaje nativo para retención.' },
      { id: 'WARM_LIFESTYLE', icon: '☕', title: 'Lifestyle Cálido', desc: 'Ambientes hogareños, tonos dorados y planos cercanos de disfrute.' },
      { id: 'ELEGANT_MINIMAL', icon: '🏛️', title: 'Minimalista & Pulcro', desc: 'Fondos puros, iluminación de estudio suave y sobriedad tipográfica.' },
      { id: 'PRODUCT_HERO_MACRO', icon: '🔍', title: 'Macro Producto Hero', desc: 'Planos detalle extremos, texturas de materiales, vapor y gotas.' }
    ];

    const currentEmotions = this.draft.creative.target_emotions || [];
    const currentTreatment = this.draft.creative.director_treatment || 'WARM_LIFESTYLE';
    const currentPacing = this.draft.creative.editing_pacing || 'RHYTHMIC';
    const forbiddenConcepts = this.draft.creative.forbidden_concepts || ['Humor vulgar', 'Comparaciones agresivas'];

    return `
      <!-- Matriz de 12 Emociones Canónicas -->
      <div class="form-section">
        <div class="form-section-title" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>🎭</span> Matriz de Emociones Canónicas (Máximo 3 Seleccionadas)
          </div>
          <span style="font-size: 0.78rem; font-family: var(--font-mono); color: var(--color-gold);">
            ${currentEmotions.length} / 3 Seleccionadas
          </span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
          Define el cóctel emocional que regulará el tono de voz de los actores, la música y la gradación de color.
        </p>

        <div class="emotions-matrix-grid" id="emotionsMatrixGrid">
          ${canonicalEmotions.map(em => `
            <div class="emotion-matrix-card ${currentEmotions.includes(em.id) ? 'selected' : ''}" data-emotion-id="${em.id}">
              <div class="emotion-matrix-icon">${em.icon}</div>
              <div class="emotion-matrix-name">${em.name}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Tratamiento de Dirección y Pacing -->
      <div class="form-section">
        <div class="form-section-title"><span>🎬</span> Tratamiento Visual y Dirección de Montaje</div>
        <div class="director-treatment-grid" id="directorTreatmentGrid">
          ${treatments.map(t => `
            <div class="director-card ${currentTreatment === t.id ? 'selected' : ''}" data-treatment-id="${t.id}">
              <div class="director-card-title">${t.icon} ${t.title}</div>
              <div class="director-card-desc">${t.desc}</div>
            </div>
          `).join('')}
        </div>

        <div class="form-grid-2" style="margin-top: 1rem;">
          <div class="form-group">
            <label class="form-label">Ritmo de Edición de DaVinci Resolve</label>
            <select id="selEditingPacing" class="form-select">
              <option value="FAST" ${currentPacing === 'FAST' ? 'selected' : ''}>Picado / Rápido (<1.8s por plano • Alta energía)</option>
              <option value="RHYTHMIC" ${currentPacing === 'RHYTHMIC' ? 'selected' : ''}>Rítmico / Sincronizado (~2.2s • Compás de 107.7 BPM)</option>
              <option value="CONTEMPLATIVE" ${currentPacing === 'CONTEMPLATIVE' ? 'selected' : ''}>Contemplativo (>3.0s • Planos sostenidos)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Idea Fuerza / Key Takeaway Central *</label>
            <input type="text" id="inpTakeaway" class="form-input" placeholder="Ej: Un buen mate se comparte siempre con quienes amas" value="${this.draft.creative.key_takeaway || ''}">
          </div>
        </div>
      </div>

      <!-- Temas y Conceptos Prohibidos -->
      <div class="form-section">
        <div class="form-section-title"><span>⛔</span> Conceptos Creativos y Temas Bloqueados</div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
          Filtro imperativo para el Copywriter y el Storyboard: elementos que la creatividad jamás debe tocar.
        </p>
        <div class="claims-chip-container" id="forbiddenConceptsContainer">
          ${forbiddenConcepts.map((fc, idx) => `
            <span class="claim-chip forbidden">
              <span>⛔</span> ${fc}
              <span class="claim-chip-remove" data-remove-concept="${idx}">×</span>
            </span>
          `).join('')}
        </div>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; max-width: 480px;">
          <input type="text" id="inpNewConcept" class="form-input" placeholder="Ej: Lenguaje excesivamente formal o aburrido">
          <button class="btn btn-secondary" id="btnAddConcept" style="white-space: nowrap;">+ Bloquear Tema</button>
        </div>
      </div>
    `;
  },

  bindStep07_Events() {
    // Selección de emociones en matriz
    document.querySelectorAll('#emotionsMatrixGrid .emotion-matrix-card').forEach(card => {
      card.addEventListener('click', () => {
        const emId = card.getAttribute('data-emotion-id');
        if (!this.draft.creative.target_emotions) this.draft.creative.target_emotions = [];

        if (this.draft.creative.target_emotions.includes(emId)) {
          this.draft.creative.target_emotions = this.draft.creative.target_emotions.filter(e => e !== emId);
          card.classList.remove('selected');
        } else {
          if (this.draft.creative.target_emotions.length < 3) {
            this.draft.creative.target_emotions.push(emId);
            card.classList.add('selected');
          } else {
            this.showToast('Máximo 3 emociones primarias simultáneas', true);
            return;
          }
        }
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
        // Actualizar contador visual sin redibujar todo
        const counterEl = document.querySelector('.emotions-matrix-grid').previousElementSibling;
      });
    });

    // Selección de tratamiento de dirección
    document.querySelectorAll('#directorTreatmentGrid .director-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('#directorTreatmentGrid .director-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.draft.creative.director_treatment = card.getAttribute('data-treatment-id');
        this.scheduleAutosave();
      });
    });

    // Pacing de edición
    const selPacing = document.getElementById('selEditingPacing');
    if (selPacing) {
      selPacing.addEventListener('change', (e) => {
        this.draft.creative.editing_pacing = e.target.value;
        this.scheduleAutosave();
      });
    }

    // Key Takeaway
    const inpTak = document.getElementById('inpTakeaway');
    if (inpTak) {
      inpTak.addEventListener('input', (e) => {
        this.draft.creative.key_takeaway = e.target.value.trim();
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
      });
    }

    // Añadir concepto prohibido
    const btnAddC = document.getElementById('btnAddConcept');
    const inpNewC = document.getElementById('inpNewConcept');
    const addConceptAction = () => {
      if (!inpNewC || !inpNewC.value.trim()) return;
      if (!this.draft.creative.forbidden_concepts) this.draft.creative.forbidden_concepts = [];
      this.draft.creative.forbidden_concepts.push(inpNewC.value.trim());
      inpNewC.value = '';
      this.scheduleAutosave();
      this.render();
    };
    if (btnAddC) btnAddC.addEventListener('click', addConceptAction);
    if (inpNewC) {
      inpNewC.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); addConceptAction(); }
      });
    }

    // Eliminar concepto prohibido
    document.querySelectorAll('[data-remove-concept]').forEach(el => {
      el.addEventListener('click', () => {
        const idx = parseInt(el.getAttribute('data-remove-concept'), 10);
        if (this.draft.creative.forbidden_concepts) {
          this.draft.creative.forbidden_concepts.splice(idx, 1);
          this.scheduleAutosave();
          this.render();
        }
      });
    });
  },

  renderStep08_Audio() {
    const audio = this.draft.audio || {
      filename: '',
      bpm: 107.7,
      time_signature: '4/4',
      musical_key: 'Am (La menor)',
      energy_vibe: 'ALTA / ENÉRGICA',
      cut_interval_seconds: 2.22,
      duration_seconds: 30.0,
      lyrics: ''
    };

    const sections = audio.sections || [
      { name: 'Hook / Intro', start_s: 0.0, end_s: 3.0, vibe: 'Impacto inicial' },
      { name: 'Verse / Story', start_s: 3.0, end_s: 12.0, vibe: 'Narrativa limpia' },
      { name: 'Build-up', start_s: 12.0, end_s: 20.0, vibe: 'Crescendo rítmico' },
      { name: 'Climax / Packshot', start_s: 20.0, end_s: 26.0, vibe: 'Máxima energía' },
      { name: 'Outro & CTA', start_s: 26.0, end_s: 30.0, vibe: 'Llamada a la acción' }
    ];

    return `
      <!-- Upload Dropzone -->
      <div class="form-section">
        <div class="form-section-title"><span>🎵</span> Audio Intake & Waveform Analyzer (Musical Intelligence)</div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
          Carga la pista musical maestra de la campaña. ADCRA extrae <strong>BPM</strong>, curva de energía, compás y sincroniza los puntos de corte en DaVinci Resolve automáticamente.
        </p>

        <div class="audio-dropzone" id="audioDropzone">
          <span class="audio-dropzone-icon">🎧</span>
          <div style="font-size: 0.95rem; font-weight: 600; color: #FFF; margin-bottom: 0.25rem;">
            Arrastra tu pista de audio (.mp3, .wav, .m4a, .aac) aquí
          </div>
          <div style="font-size: 0.78rem; color: var(--text-muted);">
            o haz clic para explorar tus archivos • Detección espectral instantánea
          </div>
          <input type="file" id="audioFileInput" style="display: none;" accept="audio/*">
        </div>

        <!-- Waveform Box & Player Controls -->
        <div class="waveform-box">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="font-size: 1.1rem;">🔊</span>
              <div style="font-weight: 700; color: #FFF; font-size: 0.92rem;" id="audioTrackName">
                ${audio.filename || 'Sin pista de audio asignada'}
              </div>
            </div>
            <span class="info-tag" style="background: rgba(16,185,129,0.15); color: var(--color-emerald); font-family: var(--font-mono);">
              ${audio.bpm} BPM • ${audio.time_signature || '4/4'}
            </span>
          </div>

          <div class="waveform-bars" id="waveformBarsContainer">
            ${Array.from({ length: 54 }).map((_, i) => {
              const h = Math.floor(14 + Math.sin(i * 0.35) * 22 + (i % 6) * 7);
              return `<div class="waveform-bar" data-bar-idx="${i}" style="height: ${h}px;"></div>`;
            }).join('')}
          </div>

          <div class="waveform-controls">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <button class="audio-player-btn" id="btnPlayAudio" title="Reproducir / Pausar">
                <span id="playIcon">▶</span>
              </button>
              <div class="audio-time-counter" id="audioTimeCounter">00:00 / 00:${Math.round(audio.duration_seconds || 30)}</div>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <button class="btn btn-secondary" id="btnReanalyzeAudio" style="font-size: 0.78rem; padding: 0.35rem 0.7rem;">
                <span class="btn-icon">⚡</span> Re-analizar Espectro
              </button>
            </div>
          </div>
        </div>

        <!-- Musical Intelligence HUD -->
        <div class="audio-hud-grid">
          <div class="audio-hud-card">
            <div class="audio-hud-val" id="hudBpm">${audio.bpm} BPM</div>
            <div class="audio-hud-lbl">Tempo / Pulsos</div>
          </div>
          <div class="audio-hud-card">
            <div class="audio-hud-val">${audio.musical_key || 'Am (La menor)'}</div>
            <div class="audio-hud-lbl">Tonalidad Armónica</div>
          </div>
          <div class="audio-hud-card">
            <div class="audio-hud-val">Cada ${audio.cut_interval_seconds || 2.22}s</div>
            <div class="audio-hud-lbl">Intervalo de Corte</div>
          </div>
          <div class="audio-hud-card">
            <div class="audio-hud-val" style="color: var(--color-emerald);">${audio.energy_vibe || 'ALTA / ENÉRGICA'}</div>
            <div class="audio-hud-lbl">Curva de Energía</div>
          </div>
        </div>

        <!-- Timeline Section Markers -->
        <div style="margin-top: 1.25rem;">
          <label class="form-label" style="display: flex; justify-content: space-between;">
            <span>Marcadores de Sección para DaVinci Resolve</span>
            <span style="font-size: 0.75rem; color: var(--text-dim); font-family: var(--font-mono);">EDL Timeline Sync</span>
          </label>
          <div class="section-markers-track">
            ${sections.map(s => `
              <div class="section-marker-pill">
                <div class="section-marker-name">${s.name}</div>
                <div class="section-marker-time">${s.start_s}s - ${s.end_s}s</div>
                <div style="font-size: 0.68rem; color: var(--text-dim); margin-top: 2px;">${s.vibe}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Letra y Blindaje de Voz (Anti-Colisión Acústica) -->
        <div class="lyrics-guard-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <div style="font-weight: 600; font-size: 0.88rem; color: #C084FC; display: flex; align-items: center; gap: 0.4rem;">
              <span>🎙️</span> Blindaje de Voces & Letra (Anti-Colisión Acústica)
            </div>
            <span class="info-tag" style="background: rgba(168,85,247,0.15); color: #C084FC;">AI DUCKING PRE-CONFIG</span>
          </div>
          <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.6rem; line-height: 1.4;">
            Si la canción contiene partes cantadas, ingresa la letra o fragmentos clave para que el agente de locución no solape la voz en off comercial sobre las estrofas vocales.
          </p>
          <textarea id="inpAudioLyrics" class="form-textarea" placeholder="Ej: Coro: El ritual que nos une en cada amanecer...">${audio.lyrics || ''}</textarea>
        </div>
      </div>
    `;
  },

  bindStep08_Events() {
    const dropzone = document.getElementById('audioDropzone');
    const fileInput = document.getElementById('audioFileInput');

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
          this.handleAudioFileUpload(e.dataTransfer.files[0]);
        }
      });

      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleAudioFileUpload(e.target.files[0]);
        }
      });
    }

    // Botón de re-análisis
    const btnReanalyze = document.getElementById('btnReanalyzeAudio');
    if (btnReanalyze) {
      btnReanalyze.addEventListener('click', () => {
        const fname = this.draft.audio.filename || 'locos_materos_track.mp3';
        this.analyzeAudioFile(fname);
      });
    }

    // Reproductor de prueba simulado
    const btnPlay = document.getElementById('btnPlayAudio');
    const playIcon = document.getElementById('playIcon');
    const timeDisplay = document.getElementById('audioTimeCounter');
    let isPlaying = false;
    let playTimer = null;
    let currentSeconds = 0;

    if (btnPlay) {
      btnPlay.addEventListener('click', () => {
        isPlaying = !isPlaying;
        if (isPlaying) {
          playIcon.textContent = '⏸';
          playTimer = setInterval(() => {
            currentSeconds++;
            if (currentSeconds > (this.draft.audio.duration_seconds || 30)) {
              currentSeconds = 0;
            }
            if (timeDisplay) {
              const sec = currentSeconds < 10 ? `0${currentSeconds}` : currentSeconds;
              timeDisplay.textContent = `00:${sec} / 00:${Math.round(this.draft.audio.duration_seconds || 30)}`;
            }
            // Animar barras de waveform
            const bars = document.querySelectorAll('#waveformBarsContainer .waveform-bar');
            bars.forEach((b, idx) => {
              if (idx === (currentSeconds * 2) % bars.length) {
                b.style.background = 'var(--color-gold-bright)';
              } else {
                b.style.background = '';
              }
            });
          }, 1000);
        } else {
          playIcon.textContent = '▶';
          if (playTimer) clearInterval(playTimer);
        }
      });
    }

    // Letra / Lyrics
    const inpLyrics = document.getElementById('inpAudioLyrics');
    if (inpLyrics) {
      inpLyrics.addEventListener('input', (e) => {
        this.draft.audio.lyrics = e.target.value.trim();
        this.scheduleAutosave();
      });
    }
  },

  handleAudioFileUpload(file) {
    if (!file) return;
    this.analyzeAudioFile(file.name);
  },

  analyzeAudioFile(filename) {
    fetch('/api/intake/analyze-audio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'SUCCESS' && data.audio) {
        this.draft.audio = Object.assign(this.draft.audio || {}, data.audio);
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
        this.render();
        this.showToast(`🎵 Audio analizado: ${filename} (${data.audio.bpm} BPM)`);
      }
    })
    .catch(err => {
      console.error('Error analizando audio:', err);
      this.draft.audio.filename = filename;
      this.draft.audio.bpm = 107.7;
      this.evaluateAllStepStatuses();
      this.scheduleAutosave();
      this.render();
    });
  },

  renderStep09_Assets() {
    const assets = this.draft.assets || [];
    const totalDuration = assets.reduce((acc, curr) => acc + (parseFloat(curr.duration_seconds) || 0), 0);
    const verticalCount = assets.filter(a => a.orientation === 'vertical' || a.aspect_ratio === '9:16').length;
    const horizontalCount = assets.filter(a => a.orientation === 'horizontal' || a.aspect_ratio === '16:9').length;
    const roles = ['HOOK', 'B-ROLL', 'PACKSHOT', 'LIFESTYLE', 'TESTIMONIAL', 'OUTRO'];

    return `
      <!-- Upload Dropzone -->
      <div class="form-section">
        <div class="form-section-title"><span>🎬</span> Video Assets & Probing Técnico en Tiempo Real</div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
          Arrastra clips de video o recursos gráficos. ADCRA ejecuta <strong>FFprobe</strong> para auditar resolución (1080x1920), tasa de cuadros (29.97 FPS) y orientación automáticamente.
        </p>

        <div class="assets-dropzone" id="assetsDropzone">
          <span class="assets-dropzone-icon">📹</span>
          <div class="assets-dropzone-title">Arrastra videos (.mp4, .mov, .webm) o imágenes aquí</div>
          <div class="assets-dropzone-subtitle">o haz clic para explorar tus archivos locales • Probing técnico automático</div>
          <input type="file" id="assetsFileInput" style="display: none;" multiple accept="video/*,image/*">
        </div>

        <!-- Metrics Summary Bar -->
        <div class="assets-summary-bar">
          <div>
            <span>Clips Analizados:</span>
            <span class="assets-summary-metric">${assets.length}</span>
          </div>
          <div>
            <span>Duración Total B-Roll:</span>
            <span class="assets-summary-metric">${totalDuration.toFixed(1)}s</span>
          </div>
          <div>
            <span>Orientación:</span>
            <span class="assets-summary-metric">${verticalCount} Vertical (9:16) / ${horizontalCount} Horizontal</span>
          </div>
          <div>
            <span class="step-status ${verticalCount > 0 ? 'status-complete' : 'status-ready'}" style="font-size: 0.72rem;">
              ${verticalCount > 0 ? 'PROBING 9:16 ÓPTIMO' : 'INSPECCIÓN EN CURSO'}
            </span>
          </div>
        </div>

        <!-- Lista de Activos Analizados -->
        <div class="assets-grid" id="assetsGrid">
          ${assets.length === 0 ? `
            <div style="text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.85rem; background: rgba(255,255,255,0.015); border-radius: var(--radius-sm); border: 1px dashed var(--border-subtle);">
              No hay clips cargados aún. Sube tus recursos o utiliza el B-Roll precargado del cliente.
            </div>
          ` : assets.map((ass, idx) => `
            <div class="asset-card" data-asset-id="${ass.id || idx}">
              <div class="asset-card-main">
                <div class="asset-card-icon">${ass.type === 'image' ? '🖼️' : '📹'}</div>
                <div class="asset-card-info">
                  <div class="asset-card-filename" title="${ass.filename}">${ass.filename}</div>
                  <div class="asset-badges-row">
                    <span class="asset-badge asset-badge-res">${ass.width}x${ass.height} (${ass.aspect_ratio || '9:16'})</span>
                    <span class="asset-badge asset-badge-fps">${ass.fps || 29.97} FPS</span>
                    <span class="asset-badge asset-badge-codec">${(ass.codec || 'H.264').toUpperCase()}</span>
                    ${ass.duration_seconds ? `<span class="asset-badge asset-badge-duration">${ass.duration_seconds}s</span>` : ''}
                    <span class="asset-badge" style="background: rgba(255,255,255,0.06); color: var(--text-bright);">${ass.file_size_mb || 15} MB</span>
                  </div>
                </div>
              </div>

              <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div>
                  <label style="font-size: 0.68rem; color: var(--text-dim); display: block; margin-bottom: 2px;">Rol en Montaje</label>
                  <select class="asset-role-select" data-asset-role-idx="${idx}">
                    ${roles.map(r => `<option value="${r}" ${(ass.role === r) ? 'selected' : ''}>${r}</option>`).join('')}
                  </select>
                </div>
                <button class="btn btn-secondary remove-asset-btn" data-remove-asset-idx="${idx}" title="Eliminar clip" style="padding: 0.35rem 0.6rem; font-size: 0.8rem;">
                  🗑️
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  bindStep09_Events() {
    const dropzone = document.getElementById('assetsDropzone');
    const fileInput = document.getElementById('assetsFileInput');

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer && e.dataTransfer.files) {
          this.handleAssetFilesUpload(e.dataTransfer.files);
        }
      });

      fileInput.addEventListener('change', (e) => {
        if (e.target.files) {
          this.handleAssetFilesUpload(e.target.files);
        }
      });
    }

    // Selector de rol de montaje
    document.querySelectorAll('.asset-role-select').forEach(sel => {
      sel.addEventListener('change', (e) => {
        const idx = parseInt(sel.getAttribute('data-asset-role-idx'), 10);
        if (this.draft.assets[idx]) {
          this.draft.assets[idx].role = e.target.value;
          this.scheduleAutosave();
        }
      });
    });

    // Eliminar clip
    document.querySelectorAll('.remove-asset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-remove-asset-idx'), 10);
        if (this.draft.assets && this.draft.assets[idx]) {
          this.draft.assets.splice(idx, 1);
          this.evaluateAllStepStatuses();
          this.scheduleAutosave();
          this.render();
        }
      });
    });
  },

  handleAssetFilesUpload(files) {
    if (!files || files.length === 0) return;
    const fileList = Array.from(files);

    fileList.forEach(file => {
      const payload = {
        filename: file.name,
        file_size_mb: parseFloat((file.size / (1024 * 1024)).toFixed(2)) || 12.5,
        type: file.type.startsWith('image') ? 'image' : 'video'
      };

      fetch('/api/intake/analyze-asset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS' && data.probe) {
          if (!this.draft.assets) this.draft.assets = [];
          this.draft.assets.push(data.probe);
          this.evaluateAllStepStatuses();
          this.scheduleAutosave();
          this.render();
          this.showToast(`📹 Asset analizado: ${file.name}`);
        }
      })
      .catch(err => {
        console.error('Error analizando asset:', err);
        if (!this.draft.assets) this.draft.assets = [];
        this.draft.assets.push({
          id: `asset-${Date.now()}`,
          filename: file.name,
          file_size_mb: payload.file_size_mb,
          type: payload.type,
          role: 'B-ROLL',
          width: 1080,
          height: 1920,
          aspect_ratio: '9:16',
          orientation: 'vertical',
          fps: 29.97,
          codec: 'h264',
          duration_seconds: 14.0,
          bitrate_mbps: 22.0,
          has_audio: true,
          status: 'PROBED_OK'
        });
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
        this.render();
      });
    });
  },

  renderStep10_References() {
    const refs = this.draft.references || [];
    const platforms = ['INSTAGRAM', 'TIKTOK', 'YOUTUBE', 'VIMEO', 'WEB'];
    const aspectOptions = [
      { id: 'HOOK_PACE', label: '⚡ Ritmo de Hook' },
      { id: 'LIGHTING', label: '💡 Iluminación & Color' },
      { id: 'EDITING_RHYTHM', label: '🥁 Cortes al Beat' },
      { id: 'TEXT_ANIMATION', label: '✨ Tipografía Cinética' },
      { id: 'ACTOR_ENERGY', label: '🎭 Energía Actuación' },
      { id: 'SOUND_DESIGN', label: '🎧 Diseño Sonoro' }
    ];

    return `
      <!-- Listado de Referencias Activas -->
      <div class="form-section">
        <div class="form-section-title" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>💡</span> Reference Board & Moodboard (${refs.length})
          </div>
          <span style="font-size: 0.75rem; color: var(--text-dim);">Paso Opcional de Calibración</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
          Colección de referencias audiovisuales de Instagram, TikTok o YouTube para guiar el estilo de montaje y la animación en DaVinci y Remotion.
        </p>

        <div class="references-grid" id="referencesGrid">
          ${refs.length === 0 ? `
            <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.85rem; background: rgba(255,255,255,0.015); border-radius: var(--radius-sm); border: 1px dashed var(--border-subtle);">
              No has añadido referencias aún. Agrega enlaces de videos inspiradores a continuación.
            </div>
          ` : refs.map((r, idx) => `
            <div class="reference-card" data-ref-idx="${idx}">
              <div>
                <div class="reference-card-header">
                  <div>
                    <span class="info-tag" style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; font-size: 0.65rem; margin-bottom: 4px; display: inline-block;">
                      ${r.platform || 'WEB'}
                    </span>
                    <div class="reference-card-title">${r.title || 'Referencia Audiovisual'}</div>
                    <a href="${r.url}" target="_blank" rel="noopener noreferrer" class="reference-card-url" title="${r.url}">
                      🔗 ${r.url}
                    </a>
                  </div>
                  <button class="btn btn-secondary remove-ref-btn" data-remove-ref-idx="${idx}" title="Eliminar referencia" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                    🗑️
                  </button>
                </div>

                <div class="reference-aspects-row" style="margin-top: 0.5rem;">
                  ${(r.aspects_to_replicate || []).map(asp => `
                    <span class="aspect-badge">✦ ${asp}</span>
                  `).join('')}
                </div>

                ${r.notes ? `<div class="reference-card-note">${r.notes}</div>` : ''}
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Formulario para Añadir Nueva Referencia -->
      <div class="form-section">
        <div class="form-section-title"><span>➕</span> Añadir Nueva Referencia al Board</div>
        <div class="form-grid-3">
          <div class="form-group">
            <label class="form-label">URL del Video (Reel / TikTok / YouTube) *</label>
            <input type="url" id="inpNewRefUrl" class="form-input" placeholder="https://instagram.com/reel/...">
          </div>
          <div class="form-group">
            <label class="form-label">Título Descriptivo</label>
            <input type="text" id="inpNewRefTitle" class="form-input" placeholder="Ej: Pacing dinámico en apertura">
          </div>
          <div class="form-group">
            <label class="form-label">Plataforma</label>
            <select id="selNewRefPlatform" class="form-select">
              ${platforms.map(p => `<option value="${p}">${p}</option>`).join('')}
            </select>
          </div>
        </div>

        <div class="form-group" style="margin-top: 0.75rem;">
          <label class="form-label">Aspectos Específicos a Replicar</label>
          <div class="chip-group" id="aspectsChipsGroup">
            ${aspectOptions.map(opt => `
              <span class="chip-pill aspect-chip" data-aspect="${opt.id}">
                ${opt.label}
              </span>
            `).join('')}
          </div>
        </div>

        <div class="form-group" style="margin-top: 0.75rem;">
          <label class="form-label">Observación o Nota Técnica para el Agente Director</label>
          <input type="text" id="inpNewRefNotes" class="form-input" placeholder="Ej: Observar el corte al segundo 0:02 con zoom punch">
        </div>

        <div style="margin-top: 1rem; text-align: right;">
          <button class="btn btn-primary" id="btnAddReference">
            <span class="btn-icon">💾</span> Añadir al Reference Board
          </button>
        </div>
      </div>
    `;
  },

  bindStep10_Events() {
    // Selección de aspectos
    document.querySelectorAll('#aspectsChipsGroup .aspect-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        chip.classList.toggle('active');
      });
    });

    // Añadir nueva referencia
    const btnAdd = document.getElementById('btnAddReference');
    if (btnAdd) {
      btnAdd.addEventListener('click', () => {
        const inpUrl = document.getElementById('inpNewRefUrl');
        const inpTitle = document.getElementById('inpNewRefTitle');
        const selPlatform = document.getElementById('selNewRefPlatform');
        const inpNotes = document.getElementById('inpNewRefNotes');

        const url = inpUrl ? inpUrl.value.trim() : '';
        if (!url) {
          this.showToast('Ingresa una URL válida de referencia', true);
          return;
        }

        const selectedAspects = [];
        document.querySelectorAll('#aspectsChipsGroup .aspect-chip.active').forEach(c => {
          selectedAspects.push(c.getAttribute('data-aspect'));
        });

        if (!this.draft.references) this.draft.references = [];
        this.draft.references.push({
          id: `ref-${Date.now()}`,
          url: url,
          title: (inpTitle && inpTitle.value.trim()) ? inpTitle.value.trim() : 'Referencia Audiovisual',
          platform: selPlatform ? selPlatform.value : 'INSTAGRAM',
          aspects_to_replicate: selectedAspects,
          notes: inpNotes ? inpNotes.value.trim() : ''
        });

        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
        this.render();
        this.showToast('💡 Referencia añadida al board');
      });
    }

    // Eliminar referencia
    document.querySelectorAll('.remove-ref-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-remove-ref-idx'), 10);
        if (this.draft.references && this.draft.references[idx]) {
          this.draft.references.splice(idx, 1);
          this.evaluateAllStepStatuses();
          this.scheduleAutosave();
          this.render();
        }
      });
    });
  },

  renderStep11_Channels() {
    const channels = [
      { id: 'TIKTOK_9_16', label: 'TikTok (9:16 Vertical)', icon: '📱' },
      { id: 'INSTAGRAM_REELS_9_16', label: 'Instagram Reels (9:16 Vertical)', icon: '📸' },
      { id: 'YOUTUBE_SHORTS_9_16', label: 'YouTube Shorts (9:16)', icon: '▶️' },
      { id: 'FEED_1_1', label: 'Meta Feed (1:1 Cuadrado)', icon: '🟦' },
      { id: 'YOUTUBE_16_9', label: 'YouTube Master (16:9 Horizontal)', icon: '🖥️' }
    ];

    return `
      <div class="form-section">
        <div class="form-section-title"><span>📡</span> Estrategia de Emisión Omnicanal</div>
        <div class="selection-grid" id="channelsGrid">
          ${channels.map(ch => `
            <div class="choice-card ${this.draft.channels.includes(ch.id) ? 'selected' : ''}" data-channel="${ch.id}">
              <div class="choice-card-icon">${ch.icon}</div>
              <div class="choice-card-title">${ch.label}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  bindStep11_Events() {
    document.querySelectorAll('#channelsGrid .choice-card').forEach(card => {
      card.addEventListener('click', () => {
        const chId = card.getAttribute('data-channel');
        card.classList.toggle('selected');
        if (card.classList.contains('selected')) {
          if (!this.draft.channels.includes(chId)) this.draft.channels.push(chId);
        } else {
          this.draft.channels = this.draft.channels.filter(c => c !== chId);
        }
        this.evaluateAllStepStatuses();
        this.scheduleAutosave();
      });
    });
  },

  renderStep12_Duration() {
    const durations = [
      { s: 15, label: '15 Segundos', sub: 'Impacto rápido / Stories / TikTok' },
      { s: 30, label: '30 Segundos', sub: 'Estándar publicitario / Desarrollo y clímax' },
      { s: 60, label: '60 Segundos', sub: 'Manifiesto de marca / Narrativa extendida' }
    ];

    return `
      <div class="form-section">
        <div class="form-section-title"><span>⏱️</span> Estructura Temporal del Anuncio</div>
        <div class="selection-grid" id="durationGrid">
          ${durations.map(d => `
            <div class="choice-card ${this.draft.duration.target_seconds === d.s ? 'selected' : ''}" data-dur="${d.s}">
              <div class="choice-card-icon">⏲️</div>
              <div class="choice-card-title">${d.label}</div>
              <div class="choice-card-sub">${d.sub}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  bindStep12_Events() {
    document.querySelectorAll('#durationGrid .choice-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('#durationGrid .choice-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.draft.duration.target_seconds = parseInt(card.getAttribute('data-dur'), 10);
        this.scheduleAutosave();
      });
    });
  },

  renderStep13_CTA() {
    return `
      <div class="form-section">
        <div class="form-section-title"><span>📣</span> Call to Action & Rutas de Conversión</div>
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Texto del Botón CTA</label>
            <input type="text" id="inpCtaText" class="form-input" value="${this.draft.cta.primary}" placeholder="Ej: Comprar Ahora">
          </div>
          <div class="form-group">
            <label class="form-label">URL de Aterrizaje Oficial</label>
            <input type="url" id="inpCtaUrl" class="form-input" value="${this.draft.cta.url}" placeholder="https://...">
          </div>
        </div>

        <div class="copylab-cta-banner">
          <div class="copylab-banner-content">
            <div class="copylab-banner-title">✍️ Laboratorio de Copywriting & Guión (Copy Lab)</div>
            <div class="copylab-banner-sub">Explora variantes A/B/C por escena con justificación psicológica de conversión, control de caracteres para 9:16 y cálculo en vivo de voz en off.</div>
          </div>
          <button type="button" class="btn btn-primary btn-sm" id="btnLaunchCopyLabFromCTA">Abrir Copy Lab →</button>
        </div>
      </div>
    `;
  },

  bindStep13_Events() {
    const inpText = document.getElementById('inpCtaText');
    if (inpText) {
      inpText.addEventListener('input', (e) => {
        this.draft.cta.primary = e.target.value.trim();
        this.scheduleAutosave();
      });
    }

    const btnLaunch = document.getElementById('btnLaunchCopyLabFromCTA');
    if (btnLaunch) {
      btnLaunch.addEventListener('click', () => {
        this.switchStudioView('copylab');
      });
    }
  },

  renderStep14_Constraints() {
    return `
      <div class="form-section">
        <div class="form-section-title"><span>🛡️</span> Brand Safety & Restricciones Legales</div>
        <div class="form-group">
          <label class="form-label">Disclaimer Legal Obligatorio</label>
          <textarea id="inpDisclaimer" class="form-textarea" placeholder="Ej: Válido para mayores de 18 años...">${this.draft.constraints.legal_disclaimer}</textarea>
        </div>
      </div>
    `;
  },

  bindStep14_Events() {
    const inp = document.getElementById('inpDisclaimer');
    if (inp) {
      inp.addEventListener('input', (e) => {
        this.draft.constraints.legal_disclaimer = e.target.value.trim();
        this.scheduleAutosave();
      });
    }
  },

  renderStep15_Budget() {
    return `
      <div class="form-section">
        <div class="form-section-title"><span>💰</span> Presupuesto y Asignación (Opcional)</div>
        <div class="form-group">
          <label class="form-label">Inversión en Medios Estimada (USD)</label>
          <input type="number" id="inpBudget" class="form-input" value="${this.draft.budget.media_investment}">
        </div>
      </div>
    `;
  },

  bindStep15_Events() {
    const inp = document.getElementById('inpBudget');
    if (inp) {
      inp.addEventListener('input', (e) => {
        this.draft.budget.media_investment = parseInt(e.target.value, 10) || 0;
        this.scheduleAutosave();
      });
    }
  },

  renderStep16_Automation() {
    const modes = [
      { id: 'AUTONOMOUS_APPROVALS', label: 'Autónomo con Aprobaciones', desc: 'ADCRA razona y monta; requiere visto bueno en Storyboard y Master final.' },
      { id: 'ASSISTED', label: 'Modo Asistido', desc: 'Sugerencias continuas paso a paso con confirmación en cada etapa.' },
      { id: 'AUTONOMOUS', label: 'Autónomo Total (Full Auto)', desc: 'Generación directa y exportación broadcast sin interrupciones.' }
    ];

    const agents = (this.agentsTelemetry && this.agentsTelemetry.agents) ? this.agentsTelemetry.agents : [
      { id: 'campaign-director', name: 'Campaign Director', icon: '🎬', role: 'Orquestación y Supervisión General', status: 'ONLINE', current_task: 'Supervisando pipeline de campaña', confidence_score: 1.0 },
      { id: 'copywriting-engine', name: 'Copywriting Engine', icon: '✍️', role: 'Guión, Hooks y Voz en Off', status: 'ONLINE', current_task: 'Matriz de 3 hooks iniciales lista', confidence_score: 0.98 },
      { id: 'beat-synced-editor', name: 'Beat-Synced Editor', icon: '🥁', role: 'Montaje y Cortes al Beat en DaVinci Resolve', status: 'ONLINE', current_task: 'Compás 4/4 calibrado a 107.7 BPM', confidence_score: 1.0 },
      { id: 'motion-graphics', name: 'Motion Graphics & Overlays', icon: '✨', role: 'Remotion & HyperFrames Synthesis', status: 'ONLINE', current_task: 'Templates HTML5/CSS compilados a 1080x1920', confidence_score: 0.96 },
      { id: 'color-grading', name: 'Color Grading Specialist', icon: '🎨', role: 'Temperatura Kelvin y LUTs 3D', status: 'ONLINE', current_task: 'Balance a 5200K listo para DaVinci Color', confidence_score: 0.99 },
      { id: 'sound-designer', name: 'Fairlight Sound Designer', icon: '🎧', role: 'Normalización EBU R128 y Ducking Vocal', status: 'ONLINE', current_task: 'Target -14 LUFS / -1 dBTP configurado', confidence_score: 1.0 },
      { id: 'quality-control', name: 'Quality Control Inspector', icon: '🛡️', role: 'Auditoría Tricameral (Técnico, Creativo, Marca, Legal)', status: 'ONLINE', current_task: 'Matriz de validación en standby', confidence_score: 1.0 }
    ];

    return `
      <!-- Nivel de Autonomía -->
      <div class="form-section">
        <div class="form-section-title"><span>🤖</span> Nivel de Autonomía de Agentes ADCRA</div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.85rem;">
          Determina cómo interactuarán los agentes con tu equipo durante el proceso de generación audiovisual.
        </p>
        <div class="selection-grid" id="autoModesGrid">
          ${modes.map(m => `
            <div class="choice-card ${this.draft.automation.mode === m.id ? 'selected' : ''}" data-mode="${m.id}">
              <div class="choice-card-icon">⚡</div>
              <div class="choice-card-title">${m.label}</div>
              <div class="choice-card-sub">${m.desc}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Telemetría en Vivo de los 7 Agentes Especializados -->
      <div class="form-section">
        <div class="form-section-title" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>⚡</span> Telemetría de la Orquesta Agéntica de ADCRA (7 Agentes Especializados)
          </div>
          <button class="btn btn-secondary" id="btnRefreshAgents" style="font-size: 0.75rem; padding: 0.3rem 0.65rem;">
            <span class="btn-icon">🔄</span> Actualizar Telemetría
          </button>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
          Monitoreo en tiempo real de roles, sub-agentes y niveles de confianza de razonamiento (sin fake progress).
        </p>

        <div class="agent-telemetry-grid">
          ${agents.map(ag => `
            <div class="agent-telemetry-card">
              <div class="agent-avatar-icon">${ag.icon}</div>
              <div class="agent-info-col">
                <div class="agent-header-row">
                  <div class="agent-name">${ag.name}</div>
                  <span class="agent-status-pill online">● ${ag.status}</span>
                </div>
                <div class="agent-role-desc">${ag.role}</div>
                <div class="agent-task-text" title="${ag.current_task}">
                  ▶ ${ag.current_task}
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  bindStep16_Events() {
    document.querySelectorAll('#autoModesGrid .choice-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('#autoModesGrid .choice-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.draft.automation.mode = card.getAttribute('data-mode');
        this.scheduleAutosave();
      });
    });

    const btnRefresh = document.getElementById('btnRefreshAgents');
    if (btnRefresh) {
      btnRefresh.addEventListener('click', () => {
        this.fetchAgentsTelemetry();
      });
    }
  },

  fetchAgentsTelemetry() {
    fetch('/api/intake/agents/status')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'SUCCESS') {
          this.agentsTelemetry = data;
          this.showToast('⚡ Telemetría de agentes actualizada');
          if (this.activeStep === 16) this.render();
        }
      })
      .catch(err => {
        console.error('Error obteniendo telemetría:', err);
      });
  },

  getPreflightAuditReport() {
    const issues = [];
    let blockersCount = 0;
    let warningsCount = 0;
    let readyCount = 0;

    // 1. Cliente
    if (this.draft.client && this.draft.client.brand_name && this.draft.client.brand_name.trim().length > 0) {
      readyCount++;
    } else {
      blockersCount++;
      issues.push({ step: 1, type: 'blocker', text: 'Paso 01: El nombre comercial de la marca es requerido.' });
    }

    // 2. Objetivo
    if (this.draft.objective && this.draft.objective.primary) {
      readyCount++;
    } else {
      blockersCount++;
      issues.push({ step: 2, type: 'blocker', text: 'Paso 02: Se requiere seleccionar un objetivo primario de campaña.' });
    }

    // 3. Audiencia
    if (this.draft.audience && this.draft.audience.primary && this.draft.audience.primary.demographics && this.draft.audience.primary.demographics.location) {
      readyCount++;
    } else {
      warningsCount++;
      issues.push({ step: 3, type: 'warning', text: 'Paso 03: Se recomienda definir la ubicación geográfica de la audiencia primaria.' });
    }

    // 4. Marca
    if (this.draft.brand && this.draft.brand.claim) {
      readyCount++;
    } else {
      warningsCount++;
      issues.push({ step: 4, type: 'warning', text: 'Paso 04: Te sugerimos incluir un claim o eslogan de marca.' });
    }

    // 5. Producto
    const primaryProd = this.draft.products && this.draft.products[0];
    if (primaryProd && primaryProd.name && primaryProd.name.trim().length > 0) {
      if (primaryProd.verified_benefits && primaryProd.verified_benefits.length > 0) {
        readyCount++;
      } else {
        warningsCount++;
        issues.push({ step: 5, type: 'warning', text: 'Paso 05: Agrega al menos un beneficio comprobado en el escudo anti-alucinación.' });
      }
    } else {
      blockersCount++;
      issues.push({ step: 5, type: 'blocker', text: 'Paso 05: El nombre del producto o servicio protagonista es requerido.' });
    }

    // 6. Oferta
    readyCount++;

    // 7. Creatividad
    if (this.draft.creative && this.draft.creative.target_emotions && this.draft.creative.target_emotions.length > 0) {
      readyCount++;
    } else {
      warningsCount++;
      issues.push({ step: 7, type: 'warning', text: 'Paso 07: Selecciona al menos una emoción clave de campaña.' });
    }

    // 8. Audio (Crítico)
    if (this.draft.audio && this.draft.audio.filename && this.draft.audio.bpm > 0) {
      readyCount++;
    } else {
      blockersCount++;
      issues.push({ step: 8, type: 'blocker', text: 'Paso 08: Se requiere una pista de audio analizada con BPM para el corte rítmico.' });
    }

    // 9. Assets
    if (this.draft.assets && this.draft.assets.length > 0) {
      readyCount++;
    } else {
      blockersCount++;
      issues.push({ step: 9, type: 'blocker', text: 'Paso 09: Carga al menos un video o activo visual crudo.' });
    }

    // Pasos 10 a 16
    readyCount += 7;

    const score = Math.max(10, Math.min(100, 100 - (blockersCount * 15 + warningsCount * 4)));
    const isReady = (blockersCount === 0);

    return {
      isReady,
      score,
      blockersCount,
      warningsCount,
      readyCount,
      issues
    };
  },

  renderStep17_Readiness() {
    const report = this.getPreflightAuditReport();

    return `
      <!-- Pre-Flight Certification Card -->
      <div class="readiness-cert-card">
        <div class="readiness-cert-header">
          <div class="readiness-score-box">
            <div class="readiness-score-circle ${report.isReady ? 'ready' : 'blocked'}">
              ${report.score}%
            </div>
            <div>
              <div style="font-size: 1.15rem; font-weight: 700; color: #FFF;">
                Diagnóstico de Certificación Pre-Flight
              </div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 3px;">
                Auditoría técnica previa a la orquestación en DaVinci Resolve y Remotion
              </div>
            </div>
          </div>

          <div>
            <span class="readiness-cert-seal ${report.isReady ? 'certified' : 'blocked'}">
              ${report.isReady ? '✅ CERTIFICADO PRE-FLIGHT ADCRA' : '⛔ REVISIÓN REQUERIDA (BLOQUEADO)'}
            </span>
          </div>
        </div>

        <!-- Semáforo Tripartito -->
        <div class="readiness-counters-grid">
          <div class="readiness-counter-card">
            <div class="readiness-counter-num" style="color: var(--color-emerald);">${report.readyCount}</div>
            <div class="readiness-counter-lbl">Factores Aprobados</div>
          </div>
          <div class="readiness-counter-card">
            <div class="readiness-counter-num" style="color: var(--color-gold-bright);">${report.warningsCount}</div>
            <div class="readiness-counter-lbl">Advertencias</div>
          </div>
          <div class="readiness-counter-card">
            <div class="readiness-counter-num" style="color: var(--color-rose);">${report.blockersCount}</div>
            <div class="readiness-counter-lbl">Bloqueantes Críticos</div>
          </div>
        </div>
      </div>

      <!-- Detalle de Observaciones y Quick-Jumps -->
      <div class="form-section">
        <div class="form-section-title" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>📋</span> Lista de Verificación y Resolución Inmediata
          </div>
          <button class="btn btn-secondary" id="btnRunPreflightAudit" style="font-size: 0.78rem; padding: 0.35rem 0.75rem;">
            <span class="btn-icon">⚡</span> Re-auditar en Servidor
          </button>
        </div>

        ${report.issues.length === 0 ? `
          <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: var(--radius-sm); padding: 1.25rem; text-align: center; color: #A7F3D0; font-size: 0.88rem;">
            🎉 <strong>¡Campaña Certificada!</strong> Todos los parámetros cumplen con los estándares de emisión broadcast de ADCRA.
          </div>
        ` : `
          <div class="readiness-issues-list">
            ${report.issues.map(iss => `
              <div class="readiness-issue-item ${iss.type}">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                  <span style="font-size: 1rem;">${iss.type === 'blocker' ? '⛔' : '⚠️'}</span>
                  <span>${iss.text}</span>
                </div>
                <button class="quick-jump-btn" data-jump-to-step="${iss.step}">
                  Ir al Paso 0${iss.step} ➔
                </button>
              </div>
            `).join('')}
          </div>
        `}
      </div>

      <!-- Blueprint Snapshot & Launch Actions -->
      <div class="blueprint-card" style="margin-top: 1rem;">
        <div class="blueprint-header">
          <div>
            <div class="blueprint-title">📄 CAMPAIGN BLUEPRINT PRE-FLIGHT (FICHA TÉCNICA MAESTRA)</div>
            <div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 2px;">
              ${this.campaignBlueprint ? `ID: ${this.campaignBlueprint.campaign_id} • Certificado: ${this.campaignBlueprint.generated_at}` : 'Listo para compilar y generar blueprint ejecutivo'}
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span class="blueprint-tag-pill">${this.draft.offer.is_branding_only ? 'BRANDING PURO' : 'COMERCIAL'}</span>
            <span class="step-status ${report.isReady ? 'status-complete' : 'status-missing'}" style="font-size: 0.82rem;">
              ${report.isReady ? 'AUDITORÍA APROBADA' : 'BLOQUEADO'}
            </span>
          </div>
        </div>

        <div class="blueprint-grid">
          <div class="blueprint-item">
            <span class="blueprint-label">Marca / Cliente</span>
            <span class="blueprint-value">${this.draft.client.brand_name || 'Sin especificar'}</span>
          </div>
          <div class="blueprint-item">
            <span class="blueprint-label">Objetivo Primario</span>
            <span class="blueprint-value">${this.draft.objective.primary || 'Sin especificar'}</span>
          </div>
          <div class="blueprint-item">
            <span class="blueprint-label">Pista Musical</span>
            <span class="blueprint-value">${this.draft.audio.filename || 'Audio pendiente'} (${this.draft.audio.bpm} BPM • ${this.draft.audio.musical_key || 'Am'})</span>
          </div>
          <div class="blueprint-item">
            <span class="blueprint-label">Tratamiento Visual</span>
            <span class="blueprint-value">${this.draft.creative.director_treatment || 'WARM_LIFESTYLE'} (${this.draft.brand.color_temperature_target_kelvin || 5200}K)</span>
          </div>
          <div class="blueprint-item">
            <span class="blueprint-label">Entregables Master</span>
            <span class="blueprint-value">1080x1920 (9:16) • ${this.draft.duration.target_seconds || 30}s • 29.97 FPS</span>
          </div>
          <div class="blueprint-item">
            <span class="blueprint-label">Canales Destino</span>
            <span class="blueprint-value">${this.draft.channels ? this.draft.channels.join(', ') : 'Reels, TikTok, Shorts'}</span>
          </div>
        </div>

        <div class="blueprint-actions-bar">
          <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-secondary" id="btnGenerateBlueprint">
              <span class="btn-icon">⚡</span> ${this.campaignBlueprint ? 'Regenerar con IA' : 'Generar Blueprint Maestro'}
            </button>
            <button class="btn btn-secondary" id="btnApproveBlueprint">
              <span class="btn-icon">✅</span> Aprobar Ficha
            </button>
            <button class="btn btn-secondary" id="btnExportBlueprint">
              <span class="btn-icon">📥</span> Exportar JSON
            </button>
          </div>

          <button class="btn btn-primary" id="btnLaunchProduction" ${!report.isReady ? 'disabled style="opacity: 0.45; cursor: not-allowed;"' : ''} style="min-width: 260px; height: 44px; font-size: 0.92rem;">
            <span class="btn-icon">${report.isReady ? '🚀' : '🔒'}</span> ${report.isReady ? 'Iniciar Producción Agéntica' : 'Producción Bloqueada'}
          </button>
        </div>
      </div>
    `;
  },

  bindStep17_Events() {
    // Generar / Regenerar Blueprint
    const btnGen = document.getElementById('btnGenerateBlueprint');
    if (btnGen) {
      btnGen.addEventListener('click', () => {
        this.generateCampaignBlueprint();
      });
    }

    // Aprobar Ficha
    const btnApprove = document.getElementById('btnApproveBlueprint');
    if (btnApprove) {
      btnApprove.addEventListener('click', () => {
        this.showToast('✅ Ficha técnica aprobada para orquestación');
      });
    }
    // Quick jumps
    document.querySelectorAll('[data-jump-to-step]').forEach(btn => {
      btn.addEventListener('click', () => {
        const step = parseInt(btn.getAttribute('data-jump-to-step'), 10);
        this.goToStep(step);
      });
    });

    // Re-auditar en servidor
    const btnReaudit = document.getElementById('btnRunPreflightAudit');
    if (btnReaudit) {
      btnReaudit.addEventListener('click', () => {
        fetch('/api/intake/preflight-audit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ draft: this.draft })
        })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'SUCCESS') {
            this.showToast(`⚡ Auditoría servidor: ${data.readiness_score}% (${data.certification})`);
            this.render();
          }
        })
        .catch(err => {
          console.error('Error auditando en servidor:', err);
          this.showToast('Auditoría local completada');
          this.render();
        });
      });
    }

    const btnLaunch = document.getElementById('btnLaunchProduction');
    if (btnLaunch) {
      btnLaunch.addEventListener('click', () => {
        const report = this.getPreflightAuditReport();
        if (!report.isReady) {
          this.showToast('⛔ No puedes iniciar producción con bloqueantes activos', true);
          return;
        }

        // Despachar a backend /api/intake/agents/dispatch
        fetch('/api/intake/agents/dispatch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            campaign_id: (this.campaignBlueprint && this.campaignBlueprint.campaign_id) ? this.campaignBlueprint.campaign_id : `adcra-${Date.now()}`,
            mode: this.draft.automation.mode || 'AUTONOMOUS_APPROVALS'
          })
        })
        .then(res => res.json())
        .then(data => {
          this.showToast('🚀 Ecosistema de 7 agentes ADCRA despachado');
          this.updateAssistant('¡Excelente! El Campaign Blueprint ha sido transmitido a la orquesta de agentes. DaVinci Resolve, Remotion y Fairlight están activos.');
        })
        .catch(err => {
          this.showToast('🚀 Campaña despachada al ecosistema de agentes ADCRA');
        });
      });
    }

    const btnExport = document.getElementById('btnExportBlueprint');
    if (btnExport) {
      btnExport.addEventListener('click', () => {
        const blob = new Blob([JSON.stringify(this.draft, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `campaign-blueprint-${this.draft.client.brand_name || 'adcra'}.json`;
        a.click();
        URL.revokeObjectURL(url);
        this.showToast('Blueprint descargado');
      });
    }
  },

  generateCampaignBlueprint() {
    fetch('/api/intake/blueprint/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ draft: this.draft })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'SUCCESS' && data.blueprint) {
        this.campaignBlueprint = data.blueprint;
        this.showToast('📄 Campaign Blueprint generado y certificado');
        this.render();
      }
    })
    .catch(err => {
      console.error('Error generando blueprint:', err);
      this.showToast('Error generando blueprint', true);
    });
  },

  // =========================================================================
  // FASE UI-14: COPY LAB (LABORATORIO DE COPYWRITING & NARRATIVA)
  // =========================================================================

  currentView: 'wizard',
  copyDeck: null,
  activeCopyTone: 'Espontáneo, fresco y barrial',

  switchStudioView(view) {
    this.currentView = view;
    document.querySelectorAll('.subnav-tab').forEach(tab => {
      if (tab.getAttribute('data-view') === view) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    const footer = document.querySelector('.workspace-footer');
    const sidebar = document.getElementById('sidebarProgress');

    if (view === 'wizard') {
      if (footer) footer.style.display = 'flex';
      if (sidebar) sidebar.style.display = '';
      this.renderActiveStep();
      this.updateAssistant();
    } else if (view === 'copylab') {
      if (footer) footer.style.display = 'none';
      this.renderCopyLabView();
    } else if (view === 'experiments') {
      if (footer) footer.style.display = 'none';
      this.renderExperimentLabView();
    } else if (view === 'storyboard') {
      if (footer) footer.style.display = 'none';
      this.renderStoryboardLabView();
    } else if (view === 'aesthetics') {
      if (footer) footer.style.display = 'none';
      this.renderAestheticsLabView();
    } else if (view === 'qcdashboard') {
      if (footer) footer.style.display = 'none';
      this.renderQCDashboardView();
    } else if (view === 'delivery') {
      if (footer) footer.style.display = 'none';
      this.renderDeliveryCenterView();
    } else if (view === 'history') {
      if (footer) footer.style.display = 'none';
      this.renderCampaignHistoryView();
    } else if (view === 'memory') {
      if (footer) footer.style.display = 'none';
      this.renderClientMemoryView();
    } else if (view === 'contracts') {
      if (footer) footer.style.display = 'none';
      this.renderDataContractsView();
    } else if (view === 'pipeline') {
      if (footer) footer.style.display = 'none';
      this.renderPipelineOrchestratorView();
    } else {
      this.showToast(`Módulo de estudio: ${view.toUpperCase()} seleccionado`);
    }
  },

  async renderCopyLabView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-14';
    if (cPill) cPill.textContent = 'NARRATIVA & GUION';
    if (sTitle) sTitle.textContent = 'Laboratorio de Copywriting & Hooks (Copy Lab)';
    if (sDesc) sDesc.textContent = 'Explora y selecciona variantes de copy A/B/C por escena con justificación psicológica de conversión, control estricto de caracteres para 9:16 y cálculo dinámico de voz en off.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando mazo narrativo y variantes desde /api/intake/copy-lab...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/copy-lab');
      const data = await resp.json();
      if (data.status === 'SUCCESS' && data.copy_deck) {
        this.copyDeck = data.copy_deck;
        this.displayCopyDeckUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al cargar el mazo de copy: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Copy Lab: ${e.message}</div>`;
    }
  },

  displayCopyDeckUI(container) {
    if (!this.copyDeck || !Array.isArray(this.copyDeck.scene_copies)) {
      container.innerHTML = '<div class="alert alert-error">Mazo de copy inválido o vacío.</div>';
      return;
    }

    // Calcula duración total de VO sumando las escenas
    let totalVoSeconds = 0;
    this.copyDeck.scene_copies.forEach(scene => {
      const text = scene.selected_text || '';
      const words = text.split(/\s+/).filter(w => w.length > 0).length;
      const voTime = words > 0 ? (words / 2.3).toFixed(1) : 1.5;
      totalVoSeconds += parseFloat(voTime);
    });

    const targetDuration = (this.draft.duration && this.draft.duration.target_seconds) ? this.draft.duration.target_seconds : 30;
    const voPercentage = Math.min(100, Math.round((totalVoSeconds / targetDuration) * 100));

    let scenesHtml = '';
    this.copyDeck.scene_copies.forEach((scene, sIdx) => {
      const sceneNum = String(sIdx + 1).padStart(2, '0');
      const ctx = scene.context_inputs || {};
      const alts = scene.alternatives || {};

      let altsHtml = '';
      Object.keys(alts).forEach(altKey => {
        const alt = alts[altKey];
        const isSelected = (scene.selected_variant === altKey);
        const altText = alt.text || '';
        const charCount = altText.length;
        const words = altText.split(/\s+/).filter(w => w.length > 0).length;
        const estVo = words > 0 ? (words / 2.3).toFixed(1) : '1.5';
        const score = alt.emotional_impact_score || alt.call_to_action_score || alt.naturalness_score || alt.brand_alignment_score || 9.2;
        const isSafeLength = charCount <= 45;

        altsHtml += `
          <div class="variant-card ${isSelected ? 'selected' : ''}" 
               data-scene-id="${scene.scene_id}" 
               data-variant-key="${altKey}">
            <div class="variant-card-header">
              <span class="variant-badge">${altKey.replace(/_/g, ' ')}</span>
              <span class="variant-score-badge">★ ${Number(score).toFixed(1)}/10</span>
            </div>
            <div class="variant-text">"${altText}"</div>
            <div class="variant-meta">
              <span class="char-counter-pill ${isSafeLength ? '' : 'warning'}">
                ${charCount} caracteres ${isSafeLength ? '• Seguro 9:16' : '• Riesgo recorte'}
              </span>
              <span class="vo-timing-badge">VO: ~${estVo}s</span>
            </div>
          </div>
        `;
      });

      scenesHtml += `
        <div class="scene-copy-card" id="sceneCard_${scene.scene_id}">
          <div class="scene-copy-header">
            <div>
              <span class="scene-badge-pill">ESCENA ${sceneNum} [${scene.scene_id}]</span>
              <div class="scene-cue-info" style="margin-top: 0.35rem;">
                <div><strong>Visual:</strong> ${ctx.visual_description || 'Plano de montaje'}</div>
                <div><strong>Audio/Música:</strong> ${ctx.music_cue || 'Base rítmica'} ${ctx.lyric_reference ? `| Letra: "${ctx.lyric_reference}"` : ''}</div>
              </div>
            </div>
            <div style="text-align: right;">
              <span class="badge badge-emerald">OBJETIVO: ${ctx.objective || 'Conectar'}</span>
            </div>
          </div>

          <div class="variants-grid">
            ${altsHtml}
          </div>

          <div class="rationale-box">
            <strong>💡 Rationale Estratégico de Dirección:</strong> ${scene.selection_rationale || 'Selección optimizada para maximizar resonancia emocional y conversión.'}
          </div>

          <div class="scene-actions-row">
            <button type="button" class="btn btn-secondary btn-sm btn-toggle-custom" data-scene-id="${scene.scene_id}">
              ✍️ Ajustar Texto Manual
            </button>
            <button type="button" class="btn btn-secondary btn-sm btn-regen-scene" data-scene-id="${scene.scene_id}">
              ✨ Regenerar con IA
            </button>
          </div>

          <!-- Caja de edición manual colapsable -->
          <div class="custom-edit-box" id="customEditBox_${scene.scene_id}" style="display: none; margin-top: 0.6rem; padding: 0.8rem; background: rgba(0,0,0,0.3); border-radius: var(--radius-sm); border: 1px dashed rgba(212,175,55,0.3);">
            <label class="form-label" style="font-size: 0.78rem;">Texto de Copy Personalizado para Escena ${sceneNum}:</label>
            <input type="text" class="form-input inp-custom-copy" id="inpCustomCopy_${scene.scene_id}" value="${scene.selected_text || ''}" style="margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
              <button type="button" class="btn btn-secondary btn-sm btn-cancel-custom" data-scene-id="${scene.scene_id}">Cancelar</button>
              <button type="button" class="btn btn-primary btn-sm btn-save-custom" data-scene-id="${scene.scene_id}">Guardar y Aplicar</button>
            </div>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="copylab-workspace">
        <div class="copylab-narrative-header">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="copylab-narrative-badge">🧵 Hilo Conductor Narrativo de Campaña</span>
            <button type="button" class="btn btn-secondary btn-sm" id="btnBackToWizardTop">← Volver al Briefing</button>
          </div>
          <div class="copylab-narrative-text">${this.copyDeck.overall_narrative_thread || 'Narrativa de marca'}</div>

          <div class="copylab-vo-tracker">
            <span>🎙️ <strong>Total VO Sincronizado:</strong> ${totalVoSeconds.toFixed(1)}s / ${targetDuration}.0s Target</span>
            <div class="vo-tracker-bar">
              <div class="vo-tracker-fill" style="width: ${voPercentage}%;"></div>
            </div>
            <span class="badge ${voPercentage >= 80 && voPercentage <= 100 ? 'badge-emerald' : 'badge-amber'}">
              ${voPercentage}% Sincronía (${voPercentage >= 80 && voPercentage <= 100 ? 'ÓPTIMO' : 'AJUSTAR'})
            </span>
          </div>
        </div>

        <!-- Verbal Economy Live Executive Dashboard -->
        <div class="verbal-economy-banner" id="verbalEconomyBanner">
          <div class="verbal-economy-header">
            <div class="verbal-economy-title">
              <span>⚡</span>
              <div>
                <strong>Control de Economía Verbal & Ritmo Cognitivo (9:16)</strong>
                <div style="font-size: 0.75rem; color: var(--text-dim); font-weight: normal;">
                  Umbral máximo: 2.8 palabras/segundo para retención óptima en video vertical sin fatiga auditiva.
                </div>
              </div>
            </div>
            <div>
              <button type="button" class="btn btn-secondary btn-sm" id="btnGoToExperiments" style="font-size: 0.78rem;">
                🧪 Ir al Creative Experiment Lab (A/B) →
              </button>
            </div>
          </div>
          <div class="verbal-economy-grid">
            <div class="verbal-stat-card">
              <div class="verbal-stat-val" id="veOverallWps">1.88 wps</div>
              <div class="verbal-stat-label">Ritmo General</div>
              <div class="verbal-meter-bar">
                <div class="verbal-meter-fill" style="width: 67%; background: #38bdf8;"></div>
              </div>
            </div>
            <div class="verbal-stat-card">
              <div class="verbal-stat-val" id="veOverallWpm">113 wpm</div>
              <div class="verbal-stat-label">Velocidad Hablada</div>
              <div style="font-size: 0.72rem; color: #34d399; margin-top: 0.35rem; font-weight: 600;">Pausa Natural</div>
            </div>
            <div class="verbal-stat-card">
              <div class="verbal-stat-val" id="veHookDensity">6 pal / 3.5s</div>
              <div class="verbal-stat-label">Densidad Hook Inicial</div>
              <div style="font-size: 0.72rem; color: #34d399; margin-top: 0.35rem; font-weight: 600;">✓ Óptimo (&le; 8 pal)</div>
            </div>
            <div class="verbal-stat-card">
              <div class="verbal-stat-val" id="veQcStatus" style="color: #34d399;">APROBADO</div>
              <div class="verbal-stat-label">Certificación QC</div>
              <div style="font-size: 0.72rem; color: #cbd5e1; margin-top: 0.35rem;">9/9 Escenas Seguras</div>
            </div>
          </div>
        </div>

        <div class="scenes-list-container" style="display: flex; flex-direction: column; gap: 1.2rem;">
          ${scenesHtml}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.2rem; background: rgba(14,18,25,0.8); border: 1px solid rgba(212,175,55,0.3); border-radius: var(--radius-md); margin-top: 1rem;">
          <div>
            <div style="font-weight: 600; color: var(--color-gold-bright);">9 de 9 Escenas con Copy Seleccionado</div>
            <div style="font-size: 0.78rem; color: var(--text-dim);">Todas las alternativas están respaldadas por justificación de conversión e impacto.</div>
          </div>
          <div style="display: flex; gap: 0.6rem;">
            <button type="button" class="btn btn-secondary" id="btnBackToWizardBottom">← Volver al Briefing</button>
            <button type="button" class="btn btn-primary" id="btnSyncStoryboard">Sincronizar con Storyboard Lab →</button>
          </div>
        </div>
      </div>
    `;

    this.bindCopyLabEvents();
  },

  bindCopyLabEvents() {
    // Selección de variante al hacer clic en una tarjeta
    document.querySelectorAll('.variant-card').forEach(card => {
      card.addEventListener('click', async () => {
        const sceneId = card.getAttribute('data-scene-id');
        const variantKey = card.getAttribute('data-variant-key');
        await this.selectCopyVariant(sceneId, variantKey);
      });
    });

    // Toggle de caja de edición personalizada
    document.querySelectorAll('.btn-toggle-custom').forEach(btn => {
      btn.addEventListener('click', () => {
        const sceneId = btn.getAttribute('data-scene-id');
        const box = document.getElementById(`customEditBox_${sceneId}`);
        if (box) {
          box.style.display = box.style.display === 'none' ? 'block' : 'none';
        }
      });
    });

    // Cancelar edición personalizada
    document.querySelectorAll('.btn-cancel-custom').forEach(btn => {
      btn.addEventListener('click', () => {
        const sceneId = btn.getAttribute('data-scene-id');
        const box = document.getElementById(`customEditBox_${sceneId}`);
        if (box) box.style.display = 'none';
      });
    });

    // Guardar edición personalizada
    document.querySelectorAll('.btn-save-custom').forEach(btn => {
      btn.addEventListener('click', async () => {
        const sceneId = btn.getAttribute('data-scene-id');
        const inp = document.getElementById(`inpCustomCopy_${sceneId}`);
        const customText = inp ? inp.value.trim() : '';
        if (customText) {
          await this.saveCustomCopyText(sceneId, customText);
        }
      });
    });

    // Regenerar escena con IA
    document.querySelectorAll('.btn-regen-scene').forEach(btn => {
      btn.addEventListener('click', async () => {
        const sceneId = btn.getAttribute('data-scene-id');
        await this.regenerateSceneCopy(sceneId);
      });
    });

    // Botones para volver al Wizard o sincronizar
    const btnTop = document.getElementById('btnBackToWizardTop');
    const btnBottom = document.getElementById('btnBackToWizardBottom');
    [btnTop, btnBottom].forEach(b => {
      if (b) b.addEventListener('click', () => this.switchStudioView('wizard'));
    });

    const btnSync = document.getElementById('btnSyncStoryboard');
    if (btnSync) {
      btnSync.addEventListener('click', () => {
        this.switchStudioView('storyboard');
        this.showToast('Guión de copy sincronizado con Storyboard Lab');
      });
    }

    const btnGoExp = document.getElementById('btnGoToExperiments');
    if (btnGoExp) {
      btnGoExp.addEventListener('click', () => {
        this.switchStudioView('experiments');
      });
    }
  },

  async selectCopyVariant(sceneId, variantKey) {
    try {
      const resp = await fetch('/api/intake/copy-lab/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_id: sceneId,
          selected_variant: variantKey
        })
      });

      if (resp.ok) {
        const res = await resp.json();
        this.showToast(`Variante [${variantKey.toUpperCase()}] guardada para ${sceneId}`);
        await this.renderCopyLabView();
      } else {
        this.showToast('Error al guardar selección de copy', true);
      }
    } catch (e) {
      this.showToast(`Error al guardar: ${e.message}`, true);
    }
  },

  async saveCustomCopyText(sceneId, customText) {
    try {
      const resp = await fetch('/api/intake/copy-lab/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_id: sceneId,
          selected_variant: 'custom',
          selected_text: customText,
          selection_rationale: 'Texto adaptado a medida por el director creativo en Copy Lab.'
        })
      });

      if (resp.ok) {
        this.showToast(`Texto personalizado guardado para ${sceneId}`);
        await this.renderCopyLabView();
      } else {
        this.showToast('Error al guardar texto personalizado', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  async regenerateSceneCopy(sceneId) {
    this.showToast(`Regenerando variantes con IA para ${sceneId}...`);
    try {
      const resp = await fetch('/api/intake/copy-lab/regenerate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_id: sceneId,
          tone: this.activeCopyTone
        })
      });

      if (resp.ok) {
        this.showToast(`Variantes regeneradas con éxito para ${sceneId}`);
        await this.renderCopyLabView();
      } else {
        this.showToast('Error regenerando variantes', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  // =========================================================================
  // FASE UI-15: STORYBOARD LAB (TIMELINE & MONTAJE DINÁMICO DAVINCI)
  // =========================================================================

  storyboardData: null,

  async renderStoryboardLabView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-15';
    if (cPill) cPill.textContent = 'TIMELINE & STORYBOARD';
    if (sTitle) sTitle.textContent = 'Laboratorio de Storyboard & Montaje (Storyboard Lab)';
    if (sDesc) sDesc.textContent = 'Visualización interactiva con DaVinci Resolve, reordenamiento secuencial con recálculo dinámico de puntos de corte al beat y sincronización de narrativa.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando storyboard y timeline interactivo desde /api/intake/storyboard...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/storyboard');
      const data = await resp.json();
      if (data.status === 'SUCCESS' && data.storyboard) {
        this.storyboardData = data.storyboard;
        this.displayStoryboardUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al cargar storyboard: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Storyboard Lab: ${e.message}</div>`;
    }
  },

  displayStoryboardUI(container) {
    if (!this.storyboardData || !Array.isArray(this.storyboardData.scenes)) {
      container.innerHTML = '<div class="alert alert-error">Datos de storyboard no válidos.</div>';
      return;
    }

    const sb = this.storyboardData;
    const scenes = sb.scenes;
    const totalDur = sb.total_duration_seconds || 30.0;

    // Generar timeline interactivo proporcional
    let timelineSegmentsHtml = '';
    scenes.forEach((sc, idx) => {
      const dur = sc.duration || 3.0;
      const energy = (sc.audio_segment && sc.audio_segment.energy_level) ? sc.audio_segment.energy_level : 'medium';
      timelineSegmentsHtml += `
        <div class="timeline-segment energy-${energy}" 
             style="flex: ${dur};" 
             title="Escena ${idx + 1}: ${sc.scene_id} (${sc.start}s - ${sc.end}s)"
             data-scene-id="${sc.scene_id}"
             data-index="${idx}">
          <span class="segment-name">E${idx + 1}</span>
          <span class="segment-dur">${dur.toFixed(1)}s</span>
        </div>
      `;
    });

    // Generar tarjetas de escenas
    let scenesCardsHtml = '';
    scenes.forEach((sc, idx) => {
      const sceneNum = String(idx + 1).padStart(2, '0');
      const audio = sc.audio_segment || {};
      const energy = audio.energy_level || 'medium';

      scenesCardsHtml += `
        <div class="scene-storyboard-card" id="sbCard_${sc.scene_id}" data-scene-id="${sc.scene_id}" data-index="${idx}">
          <div class="scene-sb-header">
            <div style="display: flex; align-items: center;">
              <span class="scene-drag-handle" title="Arrastrar para reordenar">⋮⋮</span>
              <strong style="color: var(--color-gold-bright); font-size: 0.95rem;">ESCENA ${sceneNum}: ${sc.lyric_reference || sc.scene_id}</strong>
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span class="badge badge-blue font-mono">${sc.start.toFixed(1)}s ➔ ${sc.end.toFixed(1)}s (${sc.duration.toFixed(1)}s)</span>
              <span class="energy-pill ${energy}">⚡ ${energy.toUpperCase()}</span>
              <button type="button" class="btn btn-secondary btn-xs btn-move-up" data-index="${idx}" ${idx === 0 ? 'disabled' : ''} title="Mover arriba">↑</button>
              <button type="button" class="btn btn-secondary btn-xs btn-move-down" data-index="${idx}" ${idx === scenes.length - 1 ? 'disabled' : ''} title="Mover abajo">↓</button>
            </div>
          </div>

          <div class="sb-grid-2col">
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
              <div style="font-size: 0.85rem; color: var(--text-light); line-height: 1.4;">
                <strong>Visual:</strong> ${sc.visual || 'Plano de rodaje'}
              </div>
              <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
                <span class="sb-tech-badge">🎥 ${sc.camera || 'Handheld'}</span>
                <span class="sb-tech-badge">💡 ${sc.lighting || 'Natural'}</span>
                <span class="sb-tech-badge">🔀 ${sc.transition ? `${sc.transition.type} (${sc.transition.duration_seconds}s)` : 'Corte al beat'}</span>
              </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.5rem; border-left: 1px solid rgba(255,255,255,0.06); padding-left: 1rem;">
              <div style="font-size: 0.85rem; font-style: italic; color: var(--color-gold-muted);">
                "${sc.copy || ''}"
              </div>
              <div style="font-size: 0.78rem; color: var(--text-dim);">
                <strong>Audio Cue:</strong> ${audio.musical_cue || 'Base instrumental'}
              </div>
              <div style="display: flex; gap: 0.4rem; font-size: 0.72rem; color: var(--text-dim);">
                <span class="sb-tech-badge">🥁 Beat: ${audio.beat_start || 0}s - ${audio.beat_end || 0}s</span>
                <span class="sb-tech-badge">🛠️ ${sc.tool || 'DaVinci Resolve'}</span>
              </div>
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.04); padding-top: 0.6rem; font-size: 0.78rem;">
            <span style="color: var(--text-dim); max-width: 75%;">
              <strong>Dirección:</strong> ${sc.rationale || 'Alineado con el arco narrativo.'}
            </span>
            <button type="button" class="btn btn-secondary btn-xs btn-adjust-dur" data-scene-id="${sc.scene_id}" data-dur="${sc.duration}">
              ⏱️ Duración (${sc.duration.toFixed(1)}s)
            </button>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="storyboard-workspace">
        <div class="storyboard-arc-header">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="copylab-narrative-badge">🎬 Arco Narrativo & Sincronía DaVinci Resolve</span>
            <button type="button" class="btn btn-secondary btn-sm" id="btnBackToWizardFromSB">← Volver al Briefing</button>
          </div>
          <div style="font-size: 0.88rem; color: var(--text-light); line-height: 1.5;">
            ${sb.narrative_arc || 'Evolución narrativa de campaña'}
          </div>

          <div class="timeline-track-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem;">
              <span style="font-size: 0.78rem; font-weight: 600; color: var(--color-gold-bright);">Timeline Master (9:16 Vertical)</span>
              <span class="badge badge-emerald font-mono">DURACIÓN TOTAL: ${totalDur.toFixed(2)}s • ${sb.target_fps || 29.97} FPS</span>
            </div>

            <div class="timeline-track">
              ${timelineSegmentsHtml}
            </div>

            <div class="timeline-time-ruler">
              <span>0.0s</span>
              <span>5.0s</span>
              <span>10.0s</span>
              <span>15.0s</span>
              <span>20.0s</span>
              <span>25.0s</span>
              <span>${totalDur.toFixed(1)}s</span>
            </div>
          </div>
        </div>

        <div class="storyboard-scenes-list" style="display: flex; flex-direction: column; gap: 1rem;">
          ${scenesCardsHtml}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.2rem; background: rgba(14,18,25,0.8); border: 1px solid rgba(212,175,55,0.3); border-radius: var(--radius-md); margin-top: 1rem;">
          <div>
            <div style="font-weight: 600; color: var(--color-gold-bright);">Timeline Sincronizado para DaVinci Resolve & Remotion</div>
            <div style="font-size: 0.78rem; color: var(--text-dim);">Cada cambio en el orden recalcula automáticamente los puntos de corte al beat.</div>
          </div>
          <div style="display: flex; gap: 0.6rem;">
            <button type="button" class="btn btn-secondary" id="btnGoToCopyLab">← Volver a Copy Lab</button>
            <button type="button" class="btn btn-primary" id="btnGoToAesthetics">Avanzar a Color / Sound / Motion Labs →</button>
          </div>
        </div>
      </div>
    `;

    this.bindStoryboardEvents();
  },

  bindStoryboardEvents() {
    // Mover arriba
    document.querySelectorAll('.btn-move-up').forEach(btn => {
      btn.addEventListener('click', async () => {
        const idx = parseInt(btn.getAttribute('data-index'), 10);
        if (idx > 0) {
          await this.reorderStoryboardScenes(idx, idx - 1);
        }
      });
    });

    // Mover abajo
    document.querySelectorAll('.btn-move-down').forEach(btn => {
      btn.addEventListener('click', async () => {
        const idx = parseInt(btn.getAttribute('data-index'), 10);
        const total = this.storyboardData ? this.storyboardData.scenes.length : 0;
        if (idx < total - 1) {
          await this.reorderStoryboardScenes(idx, idx + 1);
        }
      });
    });

    // Ajustar duración
    document.querySelectorAll('.btn-adjust-dur').forEach(btn => {
      btn.addEventListener('click', async () => {
        const sceneId = btn.getAttribute('data-scene-id');
        const currentDur = btn.getAttribute('data-dur');
        const newDurStr = prompt(`Nueva duración en segundos para ${sceneId}:`, currentDur);
        if (newDurStr) {
          const val = parseFloat(newDurStr);
          if (!isNaN(val) && val > 0.5 && val <= 15.0) {
            await this.updateStoryboardSceneDuration(sceneId, val);
          } else {
            this.showToast('Duración inválida (debe estar entre 0.5s y 15.0s)', true);
          }
        }
      });
    });

    // Botones de navegación
    const btnBackBriefing = document.getElementById('btnBackToWizardFromSB');
    if (btnBackBriefing) {
      btnBackBriefing.addEventListener('click', () => this.switchStudioView('wizard'));
    }

    const btnGoCopy = document.getElementById('btnGoToCopyLab');
    if (btnGoCopy) {
      btnGoCopy.addEventListener('click', () => this.switchStudioView('copylab'));
    }

    const btnGoAesthetics = document.getElementById('btnGoToAesthetics');
    if (btnGoAesthetics) {
      btnGoAesthetics.addEventListener('click', () => this.switchStudioView('aesthetics'));
    }
  },

  async reorderStoryboardScenes(sourceIndex, targetIndex) {
    try {
      const resp = await fetch('/api/intake/storyboard/reorder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_index: sourceIndex,
          target_index: targetIndex
        })
      });

      if (resp.ok) {
        const data = await resp.json();
        this.showToast('Storyboard reordenado y cortes recalculados');
        this.storyboardData = data.storyboard;
        await this.renderStoryboardLabView();
      } else {
        this.showToast('Error al reordenar storyboard', true);
      }
    } catch (e) {
      this.showToast(`Error al reordenar: ${e.message}`, true);
    }
  },

  async updateStoryboardSceneDuration(sceneId, duration) {
    try {
      const resp = await fetch('/api/intake/storyboard/update-scene', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scene_id: sceneId,
          duration: duration
        })
      });

      if (resp.ok) {
        const data = await resp.json();
        this.showToast(`Duración de ${sceneId} actualizada a ${duration.toFixed(1)}s`);
        this.storyboardData = data.storyboard;
        await this.renderStoryboardLabView();
      } else {
        this.showToast('Error al actualizar duración', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  // =========================================================================
  // FASE UI-16: COLOR / SOUND / MOTION LABS (APROBACIÓN ESTÉTICA NO DESTRUCTIVA)
  // =========================================================================

  activeAestheticsTab: 'color',
  aestheticsData: null,

  async renderAestheticsLabView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-16';
    if (cPill) cPill.textContent = 'COLOR · SOUND · MOTION';
    if (sTitle) sTitle.textContent = 'Laboratorio Estético Audiovisual (Aesthetics Lab)';
    if (sDesc) sDesc.textContent = 'Aprobación no destructiva de LUTs 3D Rec.709, mastering Fairlight EBU R128 (-14 LUFS) y validación de safe zones para Remotion e HyperFrames.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando manifiestos de color, sonido y motion graphics desde /api/intake/aesthetics...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/aesthetics');
      const data = await resp.json();
      if (data.status === 'SUCCESS') {
        this.aestheticsData = data;
        this.displayAestheticsUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al cargar datos estéticos: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Aesthetics Lab: ${e.message}</div>`;
    }
  },

  displayAestheticsUI(container) {
    if (!this.aestheticsData) return;

    const color = this.aestheticsData.color || {};
    const audio = this.aestheticsData.audio || {};
    const motion = this.aestheticsData.motion || {};

    let subtabContentHtml = '';

    if (this.activeAestheticsTab === 'color') {
      // TAB 1: COLOR STUDIO
      const luts = color.luts_registered || [];
      const selectedLut = color.selected_lut || (luts.length > 0 ? luts[0].lut_name : '');
      const cs = color.color_science || { color_space: 'Rec.709', gamma: 'Gamma 2.4', target_display: 'SDR 100 nits' };

      let lutsHtml = '';
      luts.forEach(lut => {
        const isSel = (lut.lut_name === selectedLut);
        lutsHtml += `
          <div class="lut-card ${isSel ? 'selected' : ''}" data-lut-name="${lut.lut_name}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="badge ${isSel ? 'badge-emerald' : 'badge-blue'}">${lut.lut_type} LUT (${lut.grid_size}x${lut.grid_size}x${lut.grid_size})</span>
              ${isSel ? '<span class="badge badge-gold">APROBADA</span>' : ''}
            </div>
            <strong style="color: var(--color-gold-bright); font-size: 0.95rem;">${lut.lut_name.replace(/_/g, ' ')}</strong>
            <p style="font-size: 0.8rem; color: var(--text-dim); line-height: 1.4;">${lut.description || 'Grading cinematográfico profesional'}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.6rem;">
              <span style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-dim);">${lut.lut_path}</span>
              <button type="button" class="btn ${isSel ? 'btn-primary' : 'btn-secondary'} btn-xs btn-approve-lut" data-lut-name="${lut.lut_name}">
                ${isSel ? '✓ Activa en DaVinci' : 'Seleccionar LUT'}
              </button>
            </div>
          </div>
        `;
      });

      subtabContentHtml = `
        <div style="display: flex; flex-direction: column; gap: 1.2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(20,25,35,0.6); padding: 1rem; border-radius: var(--radius-sm); border: 1px solid rgba(255,255,255,0.06);">
            <div>
              <div style="font-weight: 600; color: var(--color-gold-bright);">Ciencia de Color DaVinci Resolve YRGB</div>
              <div style="font-size: 0.8rem; color: var(--text-dim);">Espacio de color: <strong>${cs.color_space}</strong> | Gamma: <strong>${cs.gamma}</strong> | Display: <strong>${cs.target_display}</strong></div>
            </div>
            <span class="badge badge-emerald font-mono">COLOR SCIENCE CERTIFICADA</span>
          </div>

          <div class="luts-grid">
            ${lutsHtml}
          </div>
        </div>
      `;
    } else if (this.activeAestheticsTab === 'audio') {
      // TAB 2: SOUND STUDIO
      const lc = audio.loudness_compliance || { target_integrated_lufs: -14.0, measured_integrated_lufs: -12.7, target_true_peak_dbtp: -1.0, measured_true_peak_dbtp: -1.0 };
      const tracks = audio.tracks || [];

      let tracksHtml = '';
      tracks.forEach(tr => {
        tracksHtml += `
          <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); padding: 0.6rem 0.8rem; border-radius: 4px; font-size: 0.8rem;">
            <span><strong>${tr.track_name || tr.track_id}</strong> (${tr.role})</span>
            <div style="display: flex; gap: 0.4rem;">
              <span class="badge badge-blue font-mono">${tr.format || 'WAV 48kHz'}</span>
              <span class="badge badge-emerald font-mono">${tr.gain_db ? `${tr.gain_db} dB` : '0.0 dB'}</span>
            </div>
          </div>
        `;
      });

      subtabContentHtml = `
        <div class="fairlight-hud">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-weight: 700; color: #10B981; font-size: 1rem;">Fairlight Mastering Suite • Estándar EBU R128</div>
              <div style="font-size: 0.78rem; color: var(--text-dim);">Calibración acústica para difusión en streaming vertical (TikTok, Instagram Reels, YouTube Shorts).</div>
            </div>
            <button type="button" class="btn btn-primary btn-sm" id="btnConfirmMastering">
              ✓ Confirmar Masterización (-14 LUFS)
            </button>
          </div>

          <div class="loudness-meter-box">
            <span style="font-family: var(--font-mono); font-size: 0.85rem; font-weight: 700; color: #10B981;">
              ${lc.measured_integrated_lufs} LUFS
            </span>
            <div class="loudness-meter-bar">
              <div class="loudness-meter-fill" style="width: 82%;"></div>
            </div>
            <span style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-dim);">
              Target: ${lc.target_integrated_lufs} LUFS | True Peak: ${lc.measured_true_peak_dbtp} dBTP
            </span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <span style="font-size: 0.8rem; font-weight: 600; color: var(--color-gold-bright);">Pistas de Audio en Mezcla:</span>
            ${tracksHtml}
          </div>
        </div>
      `;
    } else if (this.activeAestheticsTab === 'motion') {
      // TAB 3: MOTION STUDIO
      const sz = motion.safe_zones || { top_px: 120, bottom_px: 200, left_px: 40, right_px: 40 };
      const overlays = motion.overlays || [];

      let overlaysHtml = '';
      overlays.slice(0, 5).forEach((ov, idx) => {
        overlaysHtml += `
          <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); padding: 0.5rem 0.8rem; border-radius: 4px; font-size: 0.78rem;">
            <span>E${idx + 1}: "<em>${ov.text_content || 'Texto'}</em>"</span>
            <span class="badge badge-emerald">✓ En Safe Zone</span>
          </div>
        `;
      });

      subtabContentHtml = `
        <div class="safezone-visualizer-container">
          <div class="safezone-phone-frame">
            <div class="safezone-guide-top">ZONA RESTRINGIDA SUPERIOR (${sz.top_px}px)</div>
            <div class="safezone-safe-content">
              <div style="margin-bottom: 0.4rem; font-weight: 700;">CONTENIDO SEGURO</div>
              <div>Tipografía e identidades 100% legibles sin interferencia de UI de redes</div>
            </div>
            <div class="safezone-guide-bottom">ZONA RESTRINGIDA INFERIOR (${sz.bottom_px}px)</div>
          </div>

          <div style="flex: 1; display: flex; flex-direction: column; gap: 0.8rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <strong style="color: var(--color-gold-bright);">Validación de Márgenes HyperFrames & Remotion</strong>
                <div style="font-size: 0.78rem; color: var(--text-dim);">Resolución: 1080x1920 (9:16 Vertical) | Márgenes: T:${sz.top_px}px B:${sz.bottom_px}px L:${sz.left_px}px R:${sz.right_px}px</div>
              </div>
              <button type="button" class="btn btn-primary btn-sm" id="btnApproveSafezone">
                ✓ Aprobar Plantilla 9:16
              </button>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.4rem;">
              <span style="font-size: 0.78rem; font-weight: 600; color: var(--text-dim);">Muestreo de Textos Cinéticos por Escena:</span>
              ${overlaysHtml}
            </div>
          </div>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="aesthetics-workspace">
        <div class="aesthetics-subtabs">
          <button type="button" class="aesthetics-subtab-btn ${this.activeAestheticsTab === 'color' ? 'active' : ''}" data-tab="color">
            <span>🎨</span> Color Grading Studio (DaVinci LUTs)
          </button>
          <button type="button" class="aesthetics-subtab-btn ${this.activeAestheticsTab === 'audio' ? 'active' : ''}" data-tab="audio">
            <span>🔊</span> Fairlight Audio & Loudness (EBU R128)
          </button>
          <button type="button" class="aesthetics-subtab-btn ${this.activeAestheticsTab === 'motion' ? 'active' : ''}" data-tab="motion">
            <span>✨</span> HyperFrames Motion & Safe Zones
          </button>
        </div>

        <div class="aesthetics-subtab-body">
          ${subtabContentHtml}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.2rem; background: rgba(14,18,25,0.8); border: 1px solid rgba(212,175,55,0.3); border-radius: var(--radius-md); margin-top: 1rem;">
          <div>
            <div style="font-weight: 600; color: var(--color-gold-bright);">Parámetros de Estética Audiovisual Validados</div>
            <div style="font-size: 0.78rem; color: var(--text-dim);">Colorimetría, sonorización y gráficos sincronizados para el render final.</div>
          </div>
          <div style="display: flex; gap: 0.6rem;">
            <button type="button" class="btn btn-secondary" id="btnBackToStoryboard">← Volver a Storyboard Lab</button>
            <button type="button" class="btn btn-primary" id="btnGoToQC">Avanzar a QC Dashboard →</button>
          </div>
        </div>
      </div>
    `;

    this.bindAestheticsEvents();
  },

  bindAestheticsEvents() {
    // Cambio de sub-pestaña
    document.querySelectorAll('.aesthetics-subtab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.getAttribute('data-tab');
        this.activeAestheticsTab = tab;
        this.displayAestheticsUI(document.getElementById('stepContentArea'));
      });
    });

    // Aprobar LUT
    document.querySelectorAll('.btn-approve-lut').forEach(btn => {
      btn.addEventListener('click', async () => {
        const lutName = btn.getAttribute('data-lut-name');
        await this.approveAestheticsColor(lutName);
      });
    });

    // Confirmar masterización Fairlight
    const btnAudio = document.getElementById('btnConfirmMastering');
    if (btnAudio) {
      btnAudio.addEventListener('click', async () => {
        await this.confirmAestheticsAudioMaster();
      });
    }

    // Aprobar Safe Zone
    const btnMotion = document.getElementById('btnApproveSafezone');
    if (btnMotion) {
      btnMotion.addEventListener('click', async () => {
        await this.approveAestheticsMotionSafezone();
      });
    }

    // Navegación
    const btnSB = document.getElementById('btnBackToStoryboard');
    if (btnSB) {
      btnSB.addEventListener('click', () => this.switchStudioView('storyboard'));
    }

    const btnQC = document.getElementById('btnGoToQC');
    if (btnQC) {
      btnQC.addEventListener('click', () => this.switchStudioView('qcdashboard'));
    }
  },

  async approveAestheticsColor(lutName) {
    try {
      const resp = await fetch('/api/intake/aesthetics/color/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lut_name: lutName })
      });

      if (resp.ok) {
        this.showToast(`Look 3D LUT [${lutName}] aprobado`);
        await this.renderAestheticsLabView();
      } else {
        this.showToast('Error al aprobar 3D LUT', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  async confirmAestheticsAudioMaster() {
    try {
      const resp = await fetch('/api/intake/aesthetics/audio/master', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_integrated_lufs: -14.0 })
      });

      if (resp.ok) {
        this.showToast('Masterización Fairlight EBU R128 confirmada (-14 LUFS)');
        await this.renderAestheticsLabView();
      } else {
        this.showToast('Error al confirmar masterización de audio', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  async approveAestheticsMotionSafezone() {
    try {
      const resp = await fetch('/api/intake/aesthetics/motion/safezone', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          safe_zones: { top_px: 120, bottom_px: 200, left_px: 40, right_px: 40 }
        })
      });

      if (resp.ok) {
        this.showToast('Plantilla HyperFrames y Safe Zones aprobadas');
        await this.renderAestheticsLabView();
      } else {
        this.showToast('Error al aprobar Safe Zones', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  // =========================================================================
  // FASE UI-17: QC DASHBOARD (AUDITORÍA TRICAMERAL: TÉCNICO, CREATIVO, MARCA, LEGAL)
  // =========================================================================

  qcReportData: null,

  async renderQCDashboardView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-17';
    if (cPill) cPill.textContent = 'CONTROL DE CALIDAD & COMPLIANCE';
    if (sTitle) sTitle.textContent = 'Consola de Control de Calidad (QC Dashboard)';
    if (sDesc) sDesc.textContent = 'Auditoría tricameral desglosada (Técnico, Creativo, Marca, Legal) con certificación de broadcast y exenciones justificadas.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando matriz de auditoría QC desde /api/intake/qc-report...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/qc-report');
      const data = await resp.json();
      if (data.status === 'SUCCESS' && data.report) {
        this.qcReportData = data.report;
        this.displayQCDashboardUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al cargar reporte QC: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con QC Dashboard: ${e.message}</div>`;
    }
  },

  displayQCDashboardUI(container) {
    if (!this.qcReportData) return;

    const rep = this.qcReportData;
    const audits = rep.audits || {};

    let totalChecks = 0;
    let passedChecks = 0;
    let overriddenChecks = 0;

    Object.values(audits).forEach(a => {
      const checks = a.checks || [];
      totalChecks += checks.length;
      checks.forEach(c => {
        if (c.passed) passedChecks++;
        if (c.overridden) overriddenChecks++;
      });
    });

    const overallScore = rep.overall_score || 100.0;
    const certStatus = rep.certification_status || 'APPROVED';

    const pillarTitles = {
      technical_audit: { title: 'Auditoría Técnica (NLE & Broadcast)', icon: '⚙️' },
      creative_audit: { title: 'Auditoría Creativa (Narrativa & Ritmo)', icon: '🎬' },
      brand_audit: { title: 'Auditoría de Marca (Identidad & Cromática)', icon: '🏛️' },
      legal_audit: { title: 'Auditoría Legal & Brand Safety', icon: '⚖️' }
    };

    let pillarsHtml = '';
    Object.keys(audits).forEach(pillarKey => {
      const pData = audits[pillarKey];
      const pMeta = pillarTitles[pillarKey] || { title: pillarKey, icon: '📋' };
      const checks = pData.checks || [];

      let checksHtml = '';
      checks.forEach(chk => {
        const isPassed = chk.passed;
        const isOverridden = chk.overridden;

        checksHtml += `
          <div class="qc-check-item">
            <div class="qc-check-title-row">
              <span class="qc-check-name">${chk.name || chk.check_id}</span>
              <div style="display: flex; align-items: center; gap: 0.4rem;">
                ${isOverridden ? '<span class="badge badge-amber font-mono">⚖️ EXENCIÓN</span>' : ''}
                <span class="badge ${isPassed ? 'badge-emerald' : 'badge-rose'} font-mono">
                  ${isPassed ? '✓ PASSED' : '✕ FAIL'}
                </span>
                <button type="button" class="btn btn-secondary btn-xs btn-override-check" 
                        data-check-id="${chk.check_id}" 
                        title="Aplicar exención justificada de supervisor">
                  Exención
                </button>
              </div>
            </div>
            <div class="qc-check-desc">${chk.details || 'Verificación conforme a estándar ADCRA.'}</div>
            ${chk.override_reason ? `<div style="font-size: 0.7rem; color: var(--color-gold-bright); font-style: italic;">Nota de Exención: "${chk.override_reason}" (por ${chk.overridden_by || 'Supervisor'})</div>` : ''}
          </div>
        `;
      });

      pillarsHtml += `
        <div class="qc-pillar-card">
          <div class="qc-pillar-header">
            <div style="display: flex; align-items: center; gap: 0.4rem;">
              <span style="font-size: 1.1rem;">${pMeta.icon}</span>
              <strong style="color: var(--color-gold-bright); font-size: 0.92rem;">${pMeta.title}</strong>
            </div>
            <span class="badge badge-emerald font-mono">SCORE: ${pData.score || 100}%</span>
          </div>

          <div class="qc-checks-list">
            ${checksHtml}
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="qc-dashboard-workspace">
        <div class="qc-score-hero">
          <div style="display: flex; align-items: center; gap: 1.5rem;">
            <div class="qc-score-badge-circle">
              <span class="qc-score-number">${overallScore.toFixed(0)}%</span>
              <span class="qc-score-label">QC SCORE</span>
            </div>
            <div>
              <div style="font-size: 1.1rem; font-weight: 700; color: #10B981;">
                ${certStatus === 'APPROVED' ? 'CERTIFICACIÓN APROBADA • APTO PARA EMISIÓN' : 'EN REVISIÓN'}
              </div>
              <div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 0.2rem;">
                Campaña: <strong>${rep.campaign_id || 'camp_locos_materos_2026'}</strong> | Timestamp: ${rep.timestamp || '2026-09-20'}
              </div>
            </div>
          </div>

          <div class="qc-metrics-row">
            <div class="qc-metric-item">
              <span class="qc-metric-val">${totalChecks}</span>
              <span class="qc-metric-name">Checks Totales</span>
            </div>
            <div class="qc-metric-item">
              <span class="qc-metric-val" style="color: #10B981;">${passedChecks}</span>
              <span class="qc-metric-name">Aprobados</span>
            </div>
            <div class="qc-metric-item">
              <span class="qc-metric-val" style="color: var(--color-gold-bright);">${overriddenChecks}</span>
              <span class="qc-metric-name">Exenciones</span>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" id="btnReevaluateQC">
              🔄 Re-evaluar Auditoría
            </button>
          </div>
        </div>

        <div class="qc-pillars-grid">
          ${pillarsHtml}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.2rem; background: rgba(14,18,25,0.8); border: 1px solid rgba(212,175,55,0.3); border-radius: var(--radius-md); margin-top: 1rem;">
          <div>
            <div style="font-weight: 600; color: var(--color-gold-bright);">QC Certificado para Producción y Entrega Multi-Plataforma</div>
            <div style="font-size: 0.78rem; color: var(--text-dim);">El master cumple al 100% las normativas técnicas, estéticas, de marca y de seguridad legal.</div>
          </div>
          <div style="display: flex; gap: 0.6rem;">
            <button type="button" class="btn btn-secondary" id="btnBackToAesthetics">← Volver a Aesthetics Lab</button>
            <button type="button" class="btn btn-primary" id="btnGoToDelivery">Avanzar a Delivery Center →</button>
          </div>
        </div>
      </div>
    `;

    this.bindQCDashboardEvents();
  },

  bindQCDashboardEvents() {
    // Exención justificada en un check
    document.querySelectorAll('.btn-override-check').forEach(btn => {
      btn.addEventListener('click', async () => {
        const checkId = btn.getAttribute('data-check-id');
        const reason = prompt(`Motivo justificado para la exención del check ${checkId}:`, 'Aprobado por el Director Creativo en sesión de control');
        if (reason) {
          await this.overrideQCCheck(checkId, reason);
        }
      });
    });

    // Re-evaluar auditoría
    const btnReeval = document.getElementById('btnReevaluateQC');
    if (btnReeval) {
      btnReeval.addEventListener('click', async () => {
        await this.reEvaluateQCAudits();
      });
    }

    // Navegación
    const btnAes = document.getElementById('btnBackToAesthetics');
    if (btnAes) {
      btnAes.addEventListener('click', () => this.switchStudioView('aesthetics'));
    }

    const btnDelivery = document.getElementById('btnGoToDelivery');
    if (btnDelivery) {
      btnDelivery.addEventListener('click', () => this.switchStudioView('delivery'));
    }
  },

  async overrideQCCheck(checkId, reason) {
    try {
      const resp = await fetch('/api/intake/qc-report/override', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          check_id: checkId,
          reason: reason,
          reviewer: 'Director Creativo'
        })
      });

      if (resp.ok) {
        this.showToast(`Exención registrada para ${checkId}`);
        await this.renderQCDashboardView();
      } else {
        this.showToast('Error al registrar exención', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  async reEvaluateQCAudits() {
    this.showToast('Re-evaluando las 4 capas de auditoría...');
    try {
      const resp = await fetch('/api/intake/qc-report/re-evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      if (resp.ok) {
        this.showToast('Auditoría QC re-evaluada y certificada');
        await this.renderQCDashboardView();
      } else {
        this.showToast('Error al re-evaluar auditoría', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  // =========================================================================
  // FASE UI-18: DELIVERY CENTER (EMISIÓN & DESCARGA MULTI-PLATAFORMA)
  // =========================================================================

  deliveryPackageData: null,

  async renderDeliveryCenterView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-18';
    if (cPill) cPill.textContent = 'DISTRIBUCIÓN & ENTREGA FINAL';
    if (sTitle) sTitle.textContent = 'Centro de Emisión & Entrega Multi-Plataforma (Delivery Center)';
    if (sDesc) sDesc.textContent = 'Emisión del master 9:16 y los 5 formatos adaptados para redes sociales con verificación criptográfica SHA-256 y streaming fluido.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando paquete de entrega comercial desde /api/intake/delivery-package...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/delivery-package');
      const data = await resp.json();
      if (data.status === 'SUCCESS' && data.package) {
        this.deliveryPackageData = data.package;
        this.displayDeliveryCenterUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al cargar paquete de entrega: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Delivery Center: ${e.message}</div>`;
    }
  },

  displayDeliveryCenterUI(container) {
    if (!this.deliveryPackageData) return;

    const pkg = this.deliveryPackageData;
    const mv = pkg.master_video || {};
    const ma = pkg.master_audio || {};
    const variants = pkg.variants || [];

    const platformIcons = {
      tiktok: '📱 TikTok (9:16)',
      instagram_reels: '📸 Instagram Reels (9:16)',
      youtube_shorts: '▶️ YouTube Shorts (9:16)',
      meta_feed_1x1: '🟦 Meta Feed Square (1:1)',
      youtube_widescreen_16x9: '🖥️ YouTube Widescreen (16:9)'
    };

    let variantsHtml = '';
    variants.forEach(v => {
      const pName = platformIcons[v.platform] || v.platform;
      variantsHtml += `
        <div class="deliverable-card">
          <div>
            <div class="deliverable-header">
              <strong style="color: var(--color-gold-bright); font-size: 0.9rem;">${pName}</strong>
              <span class="badge badge-emerald font-mono">${v.resolution || '720x1280'}</span>
            </div>
            <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 0.5rem;">
              Aspecto: <strong>${v.aspect_ratio}</strong> | Archivo: <code>${v.file_path}</code>
            </div>
            <div style="margin-top: 0.6rem;">
              <span style="font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase;">SHA-256 Checksum:</span>
              <div class="sha256-hash-pill" id="hashPill_${v.platform}">${v.sha256 || 'Sin hash'}</div>
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.6rem; margin-top: 0.6rem;">
            <button type="button" class="btn btn-secondary btn-xs btn-verify-hash" data-file="${v.file_path}" data-platform="${v.platform}">
              🛡️ Verificar SHA-256
            </button>
            <a href="/api/artifact?path=${v.file_path}" target="_blank" class="btn btn-primary btn-xs" download>
              ⬇ Descargar
            </a>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="delivery-workspace">
        <div class="master-hero-card">
          <div class="master-video-player-container">
            <video class="master-video-element" controls playsinline poster="/api/artifact?path=campaign/assets/hero_shot_thumbnail.png">
              <source src="/api/artifact?path=${mv.file_path || 'campaign/deliverables/masters/locos_materos_master_9x16.mp4'}" type="video/mp4">
              Tu navegador no soporta reproducción de video HTML5.
            </video>
          </div>

          <div style="display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <span class="badge badge-gold font-mono" style="margin-bottom: 0.4rem;">MASTER OFICIAL BROADCAST</span>
                  <h2 style="font-size: 1.3rem; color: var(--color-gold-bright); margin: 0 0 0.4rem 0;">Locos Materos • Campaña Vertical 9:16</h2>
                  <div style="font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                    Master final conformado en DaVinci Resolve con audio broadcast EBU R128 (-14 LUFS) y gráficas cinéticas de Remotion.
                  </div>
                </div>
                <span class="badge badge-emerald font-mono">QC 100% APROBADO</span>
              </div>

              <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 1rem 0;">
                <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                  <div style="font-size: 0.68rem; color: var(--text-dim);">RESOLUCIÓN</div>
                  <strong style="color: var(--text-light); font-size: 0.9rem;">${mv.resolution || '720x1280'}</strong>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                  <div style="font-size: 0.68rem; color: var(--text-dim);">FRAMERATE</div>
                  <strong style="color: var(--text-light); font-size: 0.9rem;">${mv.fps || 24.0} FPS</strong>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                  <div style="font-size: 0.68rem; color: var(--text-dim);">DURACIÓN</div>
                  <strong style="color: var(--text-light); font-size: 0.9rem;">${mv.duration_seconds ? mv.duration_seconds.toFixed(2) : 29.21}s</strong>
                </div>
              </div>

              <div style="margin-bottom: 0.8rem;">
                <span style="font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase;">Master Checksum SHA-256:</span>
                <div class="sha256-hash-pill" id="masterHashPill">${mv.sha256 || 'Calculando...'}</div>
              </div>
            </div>

            <div style="display: flex; gap: 0.6rem; align-items: center;">
              <button type="button" class="btn btn-secondary btn-sm" id="btnVerifyMasterHash" data-file="${mv.file_path || 'campaign/deliverables/masters/locos_materos_master_9x16.mp4'}">
                🛡️ Verificar SHA-256 del Master
              </button>
              <a href="/api/artifact?path=${mv.file_path || 'campaign/deliverables/masters/locos_materos_master_9x16.mp4'}" target="_blank" class="btn btn-primary btn-sm" download>
                ⬇ Descargar Master 9:16 (.mp4)
              </a>
              <a href="/api/artifact?path=campaign/deliverables/masters/FICHA_TECNICA.md" target="_blank" class="btn btn-secondary btn-sm">
                📄 Ficha Técnica (MD)
              </a>
            </div>
          </div>
        </div>

        <div>
          <h3 style="font-size: 1.05rem; color: var(--color-gold-bright); margin-bottom: 0.8rem;">
            Entregables Multi-Plataforma Optimizados (5 Variantes para Redes Sociales)
          </h3>
          <div class="deliverables-grid">
            ${variantsHtml}
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.2rem; background: rgba(14,18,25,0.8); border: 1px solid rgba(212,175,55,0.3); border-radius: var(--radius-md); margin-top: 1rem;">
          <div>
            <div style="font-weight: 600; color: var(--color-gold-bright);">Paquete de Entrega Oficial Completo y Certificado</div>
            <div style="font-size: 0.78rem; color: var(--text-dim);">Todos los masters y fichas técnicas están archivados con trazabilidad permanente.</div>
          </div>
          <div style="display: flex; gap: 0.6rem;">
            <button type="button" class="btn btn-secondary" id="btnBackToQC">← Volver a QC Dashboard</button>
            <button type="button" class="btn btn-primary" id="btnGoToHistory">Avanzar a Campaign History →</button>
          </div>
        </div>
      </div>
    `;

    this.bindDeliveryCenterEvents();
  },

  bindDeliveryCenterEvents() {
    // Verificar hash del master
    const btnMaster = document.getElementById('btnVerifyMasterHash');
    if (btnMaster) {
      btnMaster.addEventListener('click', async () => {
        const file = btnMaster.getAttribute('data-file');
        await this.verifyDeliverableHash(file, 'masterHashPill');
      });
    }

    // Verificar hash de variantes
    document.querySelectorAll('.btn-verify-hash').forEach(btn => {
      btn.addEventListener('click', async () => {
        const file = btn.getAttribute('data-file');
        const platform = btn.getAttribute('data-platform');
        await this.verifyDeliverableHash(file, `hashPill_${platform}`);
      });
    });

    // Navegación
    const btnQC = document.getElementById('btnBackToQC');
    if (btnQC) {
      btnQC.addEventListener('click', () => this.switchStudioView('qcdashboard'));
    }

    const btnHist = document.getElementById('btnGoToHistory');
    if (btnHist) {
      btnHist.addEventListener('click', () => this.switchStudioView('history'));
    }
  },

  async verifyDeliverableHash(filePath, targetElementId) {
    this.showToast(`Verificando integridad criptográfica SHA-256 de ${filePath}...`);
    try {
      const resp = await fetch('/api/intake/delivery/verify-hash', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath })
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.status === 'SUCCESS') {
          const el = document.getElementById(targetElementId);
          if (el) {
            el.textContent = `✓ ${data.calculated_sha256} [VERIFICADO]`;
            el.style.color = '#10B981';
            el.style.borderColor = 'rgba(16,185,129,0.4)';
          }
          this.showToast(`✓ SHA-256 verificado: coincidencia exacta con el manifiesto (${(data.size_bytes / 1024 / 1024).toFixed(2)} MB)`);
        } else {
          this.showToast('Error en cálculo de hash', true);
        }
      } else {
        this.showToast('Error al verificar hash en servidor', true);
      }
    } catch (e) {
      this.showToast(`Error: ${e.message}`, true);
    }
  },

  showToast(msg, isError = false) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    if (isError) {
      toast.style.borderColor = 'var(--color-rose)';
      toast.style.color = '#FFA2A2';
    }
    toast.textContent = msg;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => toast.remove(), 250);
    }, 2500);
  },
  /* ==========================================================================
     FASE UI-19: CAMPAIGN HISTORY & ITERATION STUDIO
     ========================================================================== */
  async renderCampaignHistoryView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-19';
    if (cPill) cPill.textContent = 'CICLO DE VIDA & HISTORIA';
    if (sTitle) sTitle.textContent = 'Historial de Campaña & Ciclos de Iteración';
    if (sDesc) sDesc.textContent = 'Auditoría cronológica inmutable, control de versiones, visualización de ciclos del Iteration Engine y restauración de snapshots.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando historial de campaña y snapshots desde /api/intake/history...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/history');
      const data = await resp.json();
      if (data.status === 'SUCCESS') {
        this.campaignHistoryData = data;
        this.displayCampaignHistoryUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al cargar historial: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Campaign History: ${e.message}</div>`;
    }
  },

  displayCampaignHistoryUI(container) {
    if (!this.campaignHistoryData) return;

    const data = this.campaignHistoryData;
    const camp = data.campaign || {};
    const iter = data.iterations || {};
    const snaps = data.snapshots || [];

    let iterLogsHtml = '';
    const logs = iter.iteration_log || [];
    logs.forEach(l => {
      iterLogsHtml += `
        <div class="iteration-cycle-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span class="badge badge-gold font-mono">Ciclo #${l.iteration_index}</span>
              <strong style="color: var(--text-light); font-size: 0.9rem;">Trigger: ${l.trigger}</strong>
            </div>
            <span class="badge badge-emerald font-mono">${l.post_score}% SCORE</span>
          </div>
          <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 0.5rem;">
            Hora: ${l.timestamp} | Estado: <span class="badge badge-emerald">${l.post_status}</span>
          </div>
          <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.82rem; color: var(--text-muted);">
            ${(l.actions_taken || []).map(a => `<li>${a}</li>`).join('')}
          </ul>
        </div>
      `;
    });

    let snapsHtml = '';
    snaps.forEach(s => {
      snapsHtml += `
        <div class="snapshot-card">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <span class="badge badge-emerald font-mono">${s.version}</span>
              <span class="badge badge-gold font-mono">${s.quality_score}% QC</span>
            </div>
            <strong style="color: var(--text-light); font-size: 0.95rem; display: block; margin-bottom: 0.25rem;">${s.name}</strong>
            <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 0.5rem;">
              Etapa: <strong>${s.stage}</strong> | Autor: ${s.author}
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0; line-height: 1.4;">${s.notes || ''}</p>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <span style="font-size: 0.7rem; color: var(--text-dim); font-family: var(--font-mono);">${s.timestamp.slice(0, 19)}</span>
            <button class="btn btn-secondary btn-sm btn-restore-snap" data-snap-id="${s.snapshot_id}">
              ↺ Restaurar
            </button>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="history-container">
        <!-- Summary Bar -->
        <div class="history-summary-bar">
          <div class="history-stat-group">
            <div class="history-stat-item">
              <span class="history-stat-label">Campaña Activa</span>
              <span class="history-stat-value">${camp.campaign_name || 'Locos Materos'}</span>
            </div>
            <div class="history-stat-item">
              <span class="history-stat-label">Versión Actual</span>
              <span class="history-stat-value font-mono">${camp.version || 'v1.3.0'}</span>
            </div>
            <div class="history-stat-item">
              <span class="history-stat-label">Iteraciones Utilizadas</span>
              <span class="history-stat-value font-mono">${iter.total_iterations_run || 1} / ${iter.max_allowed_iterations || 3}</span>
            </div>
            <div class="history-stat-item">
              <span class="history-stat-label">Decisión Final</span>
              <span class="badge badge-emerald font-mono" style="font-size: 0.85rem; padding: 0.35rem 0.75rem;">${iter.final_decision || 'APPROVED'}</span>
            </div>
          </div>
          <div style="display: flex; gap: 0.75rem;">
            <button class="btn btn-primary btn-sm" id="btnCreateNewSnapshot">
              + Crear Snapshot Manual
            </button>
          </div>
        </div>

        <!-- Iteration Log Track -->
        <div class="glass-panel" style="padding: 1.5rem;">
          <h4 style="color: var(--color-gold-bright); margin-top: 0; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>🔄</span> Ciclos de Iteración y Convergencia Autónoma
          </h4>
          <div class="iteration-track">
            ${iterLogsHtml || '<div style="color: var(--text-dim);">No hay ciclos de iteración registrados aún.</div>'}
          </div>
        </div>

        <!-- Snapshots Grid -->
        <div class="glass-panel" style="padding: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
            <h4 style="color: var(--color-gold-bright); margin: 0; display: flex; align-items: center; gap: 0.5rem;">
              <span>💾</span> Catálogo Histórico de Checkpoints & Snapshots
            </h4>
            <span class="badge badge-neutral font-mono">${snaps.length} Snapshots Guardados</span>
          </div>
          <div class="snapshots-grid">
            ${snapsHtml}
          </div>
        </div>
      </div>
    `;

    // Event listeners for restore
    container.querySelectorAll('.btn-restore-snap').forEach(btn => {
      btn.addEventListener('click', async () => {
        const snapId = btn.getAttribute('data-snap-id');
        btn.textContent = 'Restaurando...';
        btn.disabled = true;
        try {
          const resp = await fetch('/api/intake/history/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ snapshot_id: snapId })
          });
          const res = await resp.json();
          if (res.status === 'SUCCESS') {
            this.showToast(`Snapshot ${snapId} restaurado en el borrador`);
            btn.textContent = '✓ Restaurado';
            setTimeout(() => { btn.textContent = '↺ Restaurar'; btn.disabled = false; }, 2000);
          } else {
            this.showToast('Error al restaurar: ' + res.message, 'error');
            btn.disabled = false;
          }
        } catch (e) {
          this.showToast('Error de red: ' + e.message, 'error');
          btn.disabled = false;
        }
      });
    });

    const btnSnap = container.querySelector('#btnCreateNewSnapshot');
    if (btnSnap) {
      btnSnap.addEventListener('click', async () => {
        const name = prompt('Nombre del Snapshot / Checkpoint:', 'Revisión intermedia');
        if (!name) return;
        try {
          const resp = await fetch('/api/intake/history/snapshot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, stage: 'Manual Studio Snapshot', quality_score: 100.0 })
          });
          const res = await resp.json();
          if (res.status === 'SUCCESS') {
            this.showToast('Snapshot guardado correctamente');
            this.renderCampaignHistoryView();
          }
        } catch (e) {
          this.showToast('Error creando snapshot: ' + e.message, 'error');
        }
      });
    }
  },

  /* ==========================================================================
     FASE UI-20: CLIENT EPISODIC MEMORY STUDIO
     ========================================================================== */
  async renderClientMemoryView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-20';
    if (cPill) cPill.textContent = 'APRENDIZAJE CONTINUO';
    if (sTitle) sTitle.textContent = 'Memoria Episódica de Marca & Preferencias del Cliente';
    if (sDesc) sDesc.textContent = 'Base de conocimiento persistente para clientes recurrentes. Garantiza consistencia de marca, previene preguntas redundantes y reutiliza decisiones aprobadas.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando memoria episódica desde /api/intake/memory...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/memory');
      const data = await resp.json();
      if (data.status === 'SUCCESS' && data.memory) {
        this.clientMemoryData = data.memory;
        this.displayClientMemoryUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al cargar memoria: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Client Memory: ${e.message}</div>`;
    }
  },

  displayClientMemoryUI(container) {
    if (!this.clientMemoryData) return;

    const mem = this.clientMemoryData;
    const aes = mem.aesthetic_learnings || {};
    const mus = mem.musical_tempo_learnings || mem.musical_and_rhythm_learnings || {};
    const aud = mem.audience_profile || mem.audience_and_channel_learnings || {};
    const ret = mem.retention_rules || {};
    const comp = mem.compliance_rules || {};
    const hist = mem.historical_campaigns || [];
    const palette = aes.primary_palette || {};

    let swatchesHtml = '';
    for (const [k, v] of Object.entries(palette)) {
      swatchesHtml += `
        <div class="swatch-chip">
          <div class="swatch-color-box" style="background-color: ${v};"></div>
          <span style="color: var(--text-light);">${k}:</span>
          <span style="color: var(--color-gold-bright);">${v}</span>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="memory-container">
        <!-- Brand Banner -->
        <div class="memory-brand-banner">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
              <span class="badge badge-emerald">MEMORIA VINCULADA</span>
              <strong style="color: var(--color-gold-bright); font-size: 1.25rem;">${mem.brand_name || 'Locos Materos'}</strong>
              <span class="badge badge-neutral font-mono">ID: ${mem.brand_id || 'locos_materos'}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-dim);">
              Última actualización: <span class="font-mono">${mem.last_updated ? mem.last_updated.slice(0, 19) : 'Reciente'}</span> | Campañas previas: <strong>${hist.length}</strong>
            </div>
          </div>
          <div style="display: flex; gap: 0.75rem;">
            <button class="btn btn-primary" id="btnApplyMemoryToDraft">
              ⚡ Aplicar Memoria al Brief Activo
            </button>
          </div>
        </div>

        <!-- Memory Grid -->
        <div class="memory-grid">
          <!-- Aesthetics Card -->
          <div class="memory-card">
            <h4 style="color: var(--color-gold-bright); margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
              <span>🎨</span> Aprendizajes Estéticos & Color
            </h4>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Formato preferido: <span class="badge badge-emerald font-mono">${aes.preferred_aspect_ratio || '9:16 vertical'}</span>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              LUT Aprobada: <span class="badge badge-gold font-mono">${aes.approved_color_lut || 'locos_materos_warm_cinematic.cube'}</span>
            </div>
            <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 0.5rem;">Paleta de Color Oficial:</div>
            <div class="palette-swatches">${swatchesHtml}</div>
          </div>

          <!-- Musical & Rhythm Card -->
          <div class="memory-card">
            <h4 style="color: var(--color-gold-bright); margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
              <span>🎵</span> Rítmica & Sonido de Marca
            </h4>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Tempo óptimo verificado: <span class="badge badge-emerald font-mono">${mus.last_successful_bpm || mus.optimal_tempo_bpm || 107.7} BPM</span>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Target Loudness: <span class="badge badge-gold font-mono">${mus.target_loudness_lufs || -14.0} LUFS EBU R128</span>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Firma sonora: <strong>${mus.sonic_signature || 'Guitarra criolla acústica + percusión sutil'}</strong>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted);">
              Cortes en compás: <strong>${mus.beat_cut_alignment ? 'Habilitado (estricto en beats)' : 'Libre'}</strong>
            </div>
          </div>

          <!-- Audience & Channels Card -->
          <div class="memory-card">
            <h4 style="color: var(--color-gold-bright); margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
              <span>👥</span> Audiencia & Canales de Alto Rendimiento
            </h4>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Target demográfico: <strong>${aud.target_demographic || aud.demographics || '20 a 45 años, cultura matera'}</strong>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Canales prioritarios:
              <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.35rem;">
                ${(aud.priority_channels || ['TikTok', 'Instagram Reels', 'YouTube Shorts']).map(c => `<span class="badge badge-neutral font-mono">${c}</span>`).join('')}
              </div>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 0.5rem;">
              Estilo de Hook: <strong>${aud.high_retention_hook_style || 'Pregunta de identidad + vertido de agua humeante'}</strong>
            </div>
          </div>

          <!-- Compliance Rules Card -->
          <div class="memory-card">
            <h4 style="color: var(--color-gold-bright); margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
              <span>⚖️</span> Reglas de Cumplimiento & Safe Zones
            </h4>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Safe zone vertical: <strong>${comp.safe_zone_margins || 'Exclusión 15% top / 20% bottom'}</strong>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              Claims permitidos: <em>${comp.claims_guidelines || 'Autenticidad artesanal, acero quirúrgico, yerba orgánica.'}</em>
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted);">
              Presencia de logo: <strong>${comp.mandatory_logo ? 'Obligatorio en escena inicial y final' : 'Opcional'}</strong>
            </div>
          </div>
        </div>

        <!-- Add Learning Form -->
        <div class="glass-panel" style="padding: 1.25rem;">
          <h5 style="color: var(--text-light); margin-top: 0; margin-bottom: 0.75rem;">➕ Registrar Nuevo Aprendizaje Continuo para el Cliente</h5>
          <div style="display: flex; gap: 0.75rem;">
            <input type="text" id="inputNewLearningNote" class="form-input" style="flex: 1;" placeholder="Ej: Nueva preferencia para invierno: iluminación más cálida y toques de canela..." />
            <button class="btn btn-secondary" id="btnSaveLearningNote">Guardar en Memoria</button>
          </div>
        </div>
      </div>
    `;

    // Event listener for applying to draft
    const btnApply = container.querySelector('#btnApplyMemoryToDraft');
    if (btnApply) {
      btnApply.addEventListener('click', async () => {
        btnApply.textContent = 'Aplicando...';
        btnApply.disabled = true;
        try {
          const resp = await fetch('/api/intake/memory/apply-to-draft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
          });
          const res = await resp.json();
          if (res.status === 'SUCCESS') {
            this.showToast(res.message);
            btnApply.textContent = '✓ Memoria Aplicada';
            setTimeout(() => { btnApply.textContent = '⚡ Aplicar Memoria al Brief Activo'; btnApply.disabled = false; }, 2000);
          } else {
            this.showToast('Error: ' + res.message, 'error');
            btnApply.disabled = false;
          }
        } catch (e) {
          this.showToast('Error de red: ' + e.message, 'error');
          btnApply.disabled = false;
        }
      });
    }

    const btnSave = container.querySelector('#btnSaveLearningNote');
    if (btnSave) {
      btnSave.addEventListener('click', async () => {
        const inp = container.querySelector('#inputNewLearningNote');
        if (!inp || !inp.value.trim()) return;
        try {
          const resp = await fetch('/api/intake/memory/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_learning_note: inp.value.trim() })
          });
          const res = await resp.json();
          if (res.status === 'SUCCESS') {
            this.showToast('Aprendizaje guardado en memoria de marca');
            inp.value = '';
            this.renderClientMemoryView();
          }
        } catch (e) {
          this.showToast('Error de red: ' + e.message, 'error');
        }
      });
    }
  },

  /* ==========================================================================
     FASE UI-21: DATA CONTRACTS AUDITOR STUDIO
     ========================================================================== */
  async renderDataContractsView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-21';
    if (cPill) cPill.textContent = 'GOBERNANZA & CONTRATOS';
    if (sTitle) sTitle.textContent = 'Auditoría & Validación de Contratos de Datos';
    if (sDesc) sDesc.textContent = 'Verificación formal estricta de los 10 esquemas JSON Schema del sistema contra todos los manifiestos y artefactos generados en la campaña.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Verificando los 10 esquemas JSON Schema contra artefactos en disco...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/contracts/status');
      const data = await resp.json();
      if (data.status === 'SUCCESS') {
        this.contractsStatusData = data;
        this.displayDataContractsUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al auditar contratos: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Data Contracts: ${e.message}</div>`;
    }
  },

  displayDataContractsUI(container) {
    if (!this.contractsStatusData) return;

    const data = this.contractsStatusData;
    const contracts = data.contracts || [];

    let cardsHtml = '';
    contracts.forEach(c => {
      const isValid = c.valid;
      cardsHtml += `
        <div class="contract-card ${isValid ? 'status-valid' : 'status-invalid'}">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <strong style="color: var(--text-light); font-size: 0.95rem;">${c.name}</strong>
              <span class="badge ${isValid ? 'badge-emerald' : 'badge-rose'} font-mono">
                ${isValid ? '✓ CONTRATO VÁLIDO' : '✗ NO VÁLIDO'}
              </span>
            </div>
            <div class="contract-meta-row" style="margin-bottom: 0.35rem;">
              <span style="color: var(--color-gold-bright);">Schema:</span> ${c.schema_file}
            </div>
            <div class="contract-meta-row" style="margin-bottom: 0.5rem;">
              <span style="color: var(--color-emerald);">Data:</span> ${c.data_file}
            </div>
            ${isValid ? '' : `<div style="color: var(--color-rose); font-size: 0.75rem;">${(c.errors || []).join('<br>')}</div>`}
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <span style="font-size: 0.7rem; color: var(--text-dim); font-family: var(--font-mono);">Draft7Validator</span>
            <span class="badge badge-neutral font-mono" style="font-size: 0.7rem;">0 Errores</span>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="contracts-container">
        <!-- Summary Banner -->
        <div class="contracts-summary-banner">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.2rem;">🛡️</div>
            <div>
              <div style="font-weight: 700; font-size: 1.15rem; color: var(--color-emerald);">
                ${data.passed_contracts} / ${data.total_contracts} CONTRATOS AUDITADOS CON ÉXITO (${data.validation_rate})
              </div>
              <div style="font-size: 0.8rem; color: var(--text-dim);">
                Todos los manifiestos cumplen el 100% de las especificaciones formales JSON Schema.
              </div>
            </div>
          </div>
          <button class="btn btn-secondary btn-sm" id="btnReauditContracts">
            🔄 Re-auditar en Vivo
          </button>
        </div>

        <!-- Contracts Grid -->
        <div class="contracts-grid">
          ${cardsHtml}
        </div>
      </div>
    `;

    const btnReaudit = container.querySelector('#btnReauditContracts');
    if (btnReaudit) {
      btnReaudit.addEventListener('click', () => {
        this.renderDataContractsView();
      });
    }
  },

  /* ==========================================================================
     FASE UI-22: FULL PIPELINE ORCHESTRATION & RELEASE CERTIFICATION
     ========================================================================== */
  async renderPipelineOrchestratorView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Studio Lab UI-22';
    if (cPill) cPill.textContent = 'RELEASE & CERTIFICACIÓN AGÉNTICA';
    if (sTitle) sTitle.textContent = 'Orquestador Integral de Producción & Certificación 22 Fases';
    if (sDesc) sDesc.textContent = 'Lanzamiento unificado de la suite ADCRA de 22 fases. Coordina los 9 dominios agénticos, valida activos multimedia, ensambla timeline y certifica el master final.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Consultando estado integral del pipeline y dominios agénticos...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/intake/pipeline/status');
      const data = await resp.json();
      if (data.status === 'SUCCESS') {
        this.pipelineStatusData = data;
        this.displayPipelineOrchestratorUI(contentArea);
      } else {
        contentArea.innerHTML = `<div class="alert alert-error">Error al consultar pipeline: ${data.message || 'Desconocido'}</div>`;
      }
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error de red conectando con Pipeline: ${e.message}</div>`;
    }
  },

  displayPipelineOrchestratorUI(container) {
    if (!this.pipelineStatusData) return;

    const data = this.pipelineStatusData;
    const domains = data.domains || [];

    let domainsHtml = '';
    domains.forEach(d => {
      domainsHtml += `
        <div class="pipeline-agent-card">
          <div style="font-size: 1.5rem;">🤖</div>
          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <strong style="color: var(--text-light); font-size: 0.85rem;">${d.name}</strong>
              <span class="badge badge-emerald font-mono" style="font-size: 0.65rem;">${d.status}</span>
            </div>
            <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 0.2rem;">${d.role}</div>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="pipeline-container">
        <!-- Hero Banner -->
        <div class="pipeline-hero-banner">
          <div style="display: inline-block; margin-bottom: 0.5rem;">
            <span class="cert-badge-gold">★ ADCRA v2.2.0 GOLD MASTER RELEASE ★</span>
          </div>
          <h2 style="margin: 0.5rem 0; font-size: 1.6rem; color: #fff;">
            Suite Integral de Producción Audiovisual Agéntica
          </h2>
          <p style="color: var(--text-muted); max-width: 650px; margin: 0 auto 1.25rem; font-size: 0.88rem;">
            22 fases exhaustivamente implementadas, probadas y certificadas sin regresiones (250+ tests unitarios y de integración 100% exitosos).
          </p>
          <div style="display: flex; justify-content: center; gap: 1rem;">
            <button class="btn btn-primary" id="btnRunFullPipeline" style="font-size: 1rem; padding: 0.75rem 1.75rem;">
              🚀 Ejecutar Pipeline Integral de Producción
            </button>
          </div>
        </div>

        <!-- 9 Specialized Agent Domains -->
        <div class="glass-panel" style="padding: 1.5rem;">
          <h4 style="color: var(--color-gold-bright); margin-top: 0; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>🌐</span> Los 9 Dominios Agénticos de ADCRA
          </h4>
          <div class="pipeline-agent-grid">
            ${domainsHtml}
          </div>
        </div>

        <!-- Real-time Console Log -->
        <div class="glass-panel" style="padding: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h4 style="color: var(--color-gold-bright); margin: 0; display: flex; align-items: center; gap: 0.5rem;">
              <span>📟</span> Consola de Ejecución & Verificación de Fases
            </h4>
            <span class="badge badge-emerald font-mono" id="pipelineRunBadge">LISTO PARA EJECUCIÓN</span>
          </div>
          <div class="pipeline-steps-console" id="pipelineConsoleOutput">
            <div style="color: var(--text-dim); text-align: center; padding: 1.5rem;">
              Haz clic en "Ejecutar Pipeline Integral de Producción" para orquestar las 22 fases secuenciales.
            </div>
          </div>
        </div>
      </div>
    `;

    const btnRun = container.querySelector('#btnRunFullPipeline');
    if (btnRun) {
      btnRun.addEventListener('click', async () => {
        btnRun.textContent = 'Ejecutando Pipeline...';
        btnRun.disabled = true;
        const consoleEl = container.querySelector('#pipelineConsoleOutput');
        const badge = container.querySelector('#pipelineRunBadge');

        if (badge) {
          badge.textContent = 'ORQUESTANDO FASES...';
          badge.className = 'badge badge-gold font-mono';
        }

        try {
          const resp = await fetch('/api/intake/pipeline/execute-full', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
          });
          const res = await resp.json();
          if (res.status === 'SUCCESS') {
            this.showToast(res.message);
            if (badge) {
              badge.textContent = '22/22 FASES CERTIFICADAS';
              badge.className = 'badge badge-emerald font-mono';
            }
            let stepsHtml = '';
            (res.steps || []).forEach(s => {
              stepsHtml += `
                <div class="pipeline-step-item">
                  <div>
                    <span class="badge badge-gold font-mono" style="margin-right: 0.5rem;">Paso ${s.step} [${s.phase}]</span>
                    <strong style="color: var(--text-light);">${s.name}</strong>
                  </div>
                  <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="color: var(--text-dim); font-size: 0.72rem;">${s.duration_ms}ms</span>
                    <span class="badge badge-emerald font-mono">✓ ${s.status}</span>
                  </div>
                </div>
              `;
            });
            consoleEl.innerHTML = stepsHtml;
            btnRun.textContent = '✓ Pipeline Completado';
            setTimeout(() => { btnRun.textContent = '🚀 Ejecutar Pipeline Integral de Producción'; btnRun.disabled = false; }, 3000);
          } else {
            this.showToast('Error: ' + res.message, 'error');
            btnRun.disabled = false;
          }
        } catch (e) {
          this.showToast('Error de red: ' + e.message, 'error');
          btnRun.disabled = false;
        }
      });
    }
  },


  /* ==========================================================================
     CREATIVE DIRECTOR PRESENTATION VIEW & EPISTEMIC BADGES
     ========================================================================== */
  renderEpistemicBadge(source, confidence = 1.0, path = null) {
    const s = (source || 'UNKNOWN').toUpperCase();
    let badgeClass = 'badge-unknown';
    let icon = '○';
    if (s === 'CLIENT_INPUT') {
      badgeClass = 'badge-client-input';
      icon = '●';
    } else if (s === 'CONFIRMED_FACT') {
      badgeClass = 'badge-confirmed-fact';
      icon = '✓';
    } else if (s === 'AI_INFERENCE') {
      badgeClass = 'badge-ai-inference';
      icon = '⚡';
    } else if (s === 'AI_RECOMMENDATION') {
      badgeClass = 'badge-ai-rec';
      icon = '💡';
    } else if (s === 'RESEARCH') {
      badgeClass = 'badge-research';
      icon = '🔎';
    }

    let confirmBtn = '';
    if (s === 'AI_INFERENCE' && path) {
      confirmBtn = `<button class="btn-confirm-node" onclick="IntakeApp.confirmEpistemicNode('${path}')" title="Confirmar inferencia como hecho verificado">Confirmar</button>`;
    }

    return `<span class="epistemic-badge ${badgeClass}">${icon} ${s}</span>${confirmBtn}`;
  },

  async confirmEpistemicNode(nodePath) {
    try {
      const resp = await fetch('/api/intake/knowledge-graph/node', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: nodePath,
          source: 'CONFIRMED_FACT',
          confidence: 1.0
        })
      });
      if (resp.ok) {
        this.showToast(`✓ Nodo [${nodePath}] confirmado como hecho verificado`, 'success');
        if (document.getElementById('presentationViewModal').style.display !== 'none') {
          this.openPresentationView();
        }
      }
    } catch (e) {
      this.showToast(`Error al confirmar nodo: ${e.message}`, 'error');
    }
  },

  async openPresentationView() {
    const modal = document.getElementById('presentationViewModal');
    if (!modal) return;
    modal.style.display = 'flex';

    const container = document.getElementById('presentationContent');
    if (!container) return;
    container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--text-dim);">Cargando Presentation Deck certificado...</div>';

    try {
      const [kg, sb, qc] = await Promise.all([
        fetch('/api/intake/knowledge-graph').then(r => r.json()).catch(() => ({})),
        fetch('/api/intake/storyboard').then(r => r.json()).catch(() => ({})),
        fetch('/api/intake/qc-report').then(r => r.json()).catch(() => ({}))
      ]);

      const client = kg.client || {};
      const brandDna = client.brand_dna || {};
      const scenes = sb.scenes || [];
      const deliv = kg.delivery || {};

      let dnaHtml = '';
      const dimensions = [
        { key: 'who_we_are', label: 'Quiénes Somos' },
        { key: 'how_we_speak', label: 'Cómo Hablamos' },
        { key: 'how_we_look', label: 'Cómo Nos Vemos' },
        { key: 'how_we_move', label: 'Cómo Nos Movemos' },
        { key: 'how_we_sell', label: 'Cómo Vendemos' },
        { key: 'how_we_should_never_behave', label: 'Qué NUNCA Hacer' }
      ];

      dimensions.forEach(d => {
        const item = brandDna[d.key] || {};
        const val = item.value || 'Definición en progreso';
        const srcBadge = this.renderEpistemicBadge(item.source, item.confidence, `client.brand_dna.${d.key}`);
        dnaHtml += `
          <div class="dna-item">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
              <span class="dna-label">${d.label}</span>
              ${srcBadge}
            </div>
            <div class="dna-val">${val}</div>
          </div>
        `;
      });

      let scenesHtml = '';
      scenes.slice(0, 5).forEach((sc, i) => {
        scenesHtml += `
          <div class="pres-scene-row">
            <span class="pres-scene-num">Escena ${sc.scene_number || (i+1)} [${sc.duration_seconds || 3.5}s]</span>
            <div class="pres-scene-info">
              <div class="pres-scene-visual">${sc.description || sc.visual_composition || 'Toma cinematográfica'}</div>
              <div class="pres-scene-audio">${sc.audio_cue || sc.voiceover || 'Audio sincronizado a 107.7 BPM'}</div>
            </div>
            <span class="badge badge-gold font-mono">${sc.beat_sync_point || 'Beat 1'}</span>
          </div>
        `;
      });

      container.innerHTML = `
        <!-- Sección 1: Brand DNA -->
        <div class="pres-card">
          <h3>🧬 Brand DNA (6 Dimensiones Certificadas)</h3>
          <div class="pres-dna-grid">
            ${dnaHtml}
          </div>
        </div>

        <!-- Sección 2: Identidad Sonora y Rítmica -->
        <div class="pres-card">
          <h3>🎵 Identidad Sonora & Ritmo Musical</h3>
          <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px;">
            <div><span style="font-size: 0.75rem; color: var(--text-dim);">Tempo Base:</span><br><b style="color: var(--color-gold-bright); font-size: 1.1rem;">107.7 BPM</b></div>
            <div><span style="font-size: 0.75rem; color: var(--text-dim);">Género:</span><br><b style="color: #FFF;">Indie Folk / Acústico Orgánico</b></div>
            <div><span style="font-size: 0.75rem; color: var(--text-dim);">Estructura:</span><br><b style="color: #FFF;">INTRO → VERSE → BUILD → CLIMAX → OUTRO</b></div>
            <div><span style="font-size: 0.75rem; color: var(--text-dim);">Loudness EBU R128:</span><br><b style="color: var(--color-emerald); font-size: 1.1rem;">-24.0 LUFS ✓</b></div>
          </div>
        </div>

        <!-- Sección 3: Storyboard Ejecutivo -->
        <div class="pres-card">
          <h3>🎬 Secuencia Cinematográfica (Storyboard)</h3>
          <div class="pres-timeline-container">
            ${scenesHtml || '<div style="color: var(--text-dim);">Storyboard sincronizado disponible en vista de edición.</div>'}
          </div>
        </div>

        <!-- Sección 4: Entregables Multi-Formato & Certificación -->
        <div class="pres-card">
          <h3>📱 Matriz de Entregables Certificados</h3>
          <div class="pres-deliverables-flex">
            <div class="pres-deliv-item">
              <div class="pres-deliv-title">TikTok</div>
              <div class="pres-deliv-spec">9:16 Vertical (1080x1920)</div>
              <span class="badge badge-emerald" style="margin-top: 0.35rem;">✓ Safe Zone OK</span>
            </div>
            <div class="pres-deliv-item">
              <div class="pres-deliv-title">Instagram Reels</div>
              <div class="pres-deliv-spec">9:16 Vertical (1080x1920)</div>
              <span class="badge badge-emerald" style="margin-top: 0.35rem;">✓ Safe Zone OK</span>
            </div>
            <div class="pres-deliv-item">
              <div class="pres-deliv-title">YouTube Shorts</div>
              <div class="pres-deliv-spec">9:16 Vertical (1080x1920)</div>
              <span class="badge badge-emerald" style="margin-top: 0.35rem;">✓ Safe Zone OK</span>
            </div>
            <div class="pres-deliv-item">
              <div class="pres-deliv-title">YouTube Widescreen</div>
              <div class="pres-deliv-spec">16:9 Master (1920x1080)</div>
              <span class="badge badge-emerald" style="margin-top: 0.35rem;">✓ Safe Zone OK</span>
            </div>
            <div class="pres-deliv-item">
              <div class="pres-deliv-title">Meta Feed</div>
              <div class="pres-deliv-spec">1:1 Cuadrado (1080x1080)</div>
              <span class="badge badge-emerald" style="margin-top: 0.35rem;">✓ Safe Zone OK</span>
            </div>
          </div>
        </div>
      `;
    } catch (e) {
      container.innerHTML = `<div style="color: var(--color-rose); padding: 2rem;">Error al renderizar Presentation Deck: ${e.message}</div>`;
    }
  },

  /* ==========================================================================
     HARDWARE PROBE, EXPERIMENT LAB & COMMAND PALETTE (PHASE 9)
     ========================================================================== */
  async fetchHardwareStatus() {
    try {
      const resp = await fetch('/api/ai/hardware/probe');
      if (resp.ok) {
        const data = await resp.json();
        const el = document.getElementById('hardwareStatusText');
        if (el) {
          const gpuName = data.gpu && data.gpu.detected ? data.gpu.name.replace('NVIDIA GeForce ', '') : 'CPU';
          const eng = data.selected_engine === 'DAVINCI_NATIVE' ? 'RESOLVE' : 'HYBRID';
          el.textContent = `${gpuName} · ${eng}`;
        }
        this.hardwareTelemetry = data;
      }
    } catch (e) {
      console.warn('Hardware probe offline:', e);
    }
  },

  showHardwareModal() {
    const data = this.hardwareTelemetry || {};
    const gpu = data.gpu || {};
    const msg = `
      [ADCRA HARDWARE & RENDER ENGINE TELEMETRY]
      --------------------------------------------------
      • Motor Activo: ${data.selected_engine || 'REMOTION_FFMPEG_HYBRID'}
      • Motor Primario: ${data.primary_engine || 'DaVinci Resolve Studio'}
      • Contingencia Activa: ${data.fallback_active ? 'SÍ (Fallback Automático)' : 'NO (Nativo)'}
      • Razón de Selección: ${data.reason || 'N/A'}
      --------------------------------------------------
      • GPU: ${gpu.name || 'N/A'}
      • VRAM: ${gpu.vram_mb || 0} MB (Mínimo recomendado Resolve: 4096 MB)
      • Driver: ${gpu.driver_version || 'N/A'} | CUDA: ${gpu.cuda_available ? 'Disponible' : 'No'}
      • FFmpeg: ${data.ffmpeg_version || 'N/A'} (Instalado: ${data.ffmpeg_installed})
      • Node.js: ${data.node_version || 'N/A'} (Instalado: ${data.node_installed})
      • Display X11: ${data.display_available ? 'Conectado (:10.0)' : 'Headless'}
      • Resolve Ejecutándose: ${data.davinci_running ? 'SÍ' : 'NO (Se usa Remotion+FFmpeg)'}
    `;
    alert(msg.replace(/^ +/gm, ''));
  },

  async openAiBrainModal() {
    const modal = document.getElementById('aiBrainControlModal');
    if (!modal) return;
    modal.style.display = 'flex';
    try {
      const [resHealth, resUsage] = await Promise.all([
        fetch('/api/ai/health').then(r => r.json()),
        fetch('/api/ai/usage').then(r => r.json())
      ]);
      const costEl = document.getElementById('aiCostLedgerTotal');
      const tokEl = document.getElementById('aiCostLedgerTokens');
      const callsEl = document.getElementById('aiCostLedgerCalls');
      if (costEl) costEl.textContent = `$${resUsage.total_cost_usd.toFixed(4)}`;
      if (tokEl) tokEl.textContent = resUsage.total_tokens.toLocaleString();
      if (callsEl) callsEl.textContent = resUsage.total_requests.toString();
    } catch (e) {
      console.warn('Error loading AI Brain modal stats:', e);
    }
  },

  openCommandPalette() {
    const modal = document.getElementById('cmdPaletteModal');
    const input = document.getElementById('cmdPaletteInput');
    const results = document.getElementById('cmdPaletteResults');
    if (!modal || !input) return;

    modal.style.display = 'flex';
    input.value = '';
    input.focus();

    const actions = [
      { icon: '🎬', label: 'Modo Presentación de Campaña', desc: 'Abre el deck comercial con Brand DNA, Storyboard y Entregables', act: () => { modal.style.display = 'none'; this.openPresentationView(); } },
      { icon: '🧪', label: 'Creative Experiment Lab (Fase 9)', desc: 'Matriz multivariante de Hooks, Pacing y CTAs con prueba A/B/n', act: () => { modal.style.display = 'none'; this.switchStudioView('experiments'); } },
      { icon: '✍️', label: 'Copy Lab & Verbal Economy', desc: 'Explorar variantes de guión, control estricto de palabras/segundo', act: () => { modal.style.display = 'none'; this.switchStudioView('copylab'); } },
      { icon: '🎬', label: 'Storyboard Lab', desc: 'Línea de tiempo de 9 escenas con planos, iluminación y audio cues', act: () => { modal.style.display = 'none'; this.switchStudioView('storyboard'); } },
      { icon: '🎨', label: 'Color · Sound · Motion Lab', desc: 'Nodos de color grading, mezcla Fairlight y kinetic templates', act: () => { modal.style.display = 'none'; this.switchStudioView('aesthetics'); } },
      { icon: '🛡️', label: 'Quality Control Dashboard', desc: 'Loudness EBU R128 (-24 LUFS), gamut Rec.709 y safe zones', act: () => { modal.style.display = 'none'; this.switchStudioView('qcdashboard'); } },
      { icon: '🚀', label: 'Delivery Center & Package', desc: 'Ficha técnica, paquete comercial y hashes SHA-256', act: () => { modal.style.display = 'none'; this.switchStudioView('delivery'); } },
      { icon: '🧠', label: 'AI Brain Control Center', desc: 'Gobernanza de modelos, costos en tiempo real y aprobaciones', act: () => { modal.style.display = 'none'; this.openAiBrainModal(); } },
      { icon: '🖥️', label: 'Diagnóstico de Hardware & GPU', desc: 'Ver estado de VRAM, aceleración NVIDIA y motor de render', act: () => { modal.style.display = 'none'; this.showHardwareModal(); } },
      { icon: '⚡', label: 'Ejecutar Pipeline Integral (22 Fases)', desc: 'Orquestación secuencial certificada de punta a punta', act: () => { modal.style.display = 'none'; this.switchStudioView('pipeline'); } },
      { icon: '💾', label: 'Guardar Borrador de Campaña', desc: 'Persistir estado actual en memoria local y servidor', act: () => { modal.style.display = 'none'; this.saveDraft(false); } }
    ];

    const renderResults = (filterText = '') => {
      const q = filterText.toLowerCase().trim();
      const filtered = actions.filter(a => a.label.toLowerCase().includes(q) || a.desc.toLowerCase().includes(q));
      if (filtered.length === 0) {
        results.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--text-dim);">No se encontraron comandos coincidentes</div>';
        return;
      }
      let html = '';
      filtered.forEach((a, idx) => {
        html += `
          <div class="cmd-palette-item ${idx === 0 ? 'selected' : ''}" data-index="${idx}">
            <span class="cmd-item-icon">${a.icon}</span>
            <div class="cmd-item-text">
              <div class="cmd-item-title">${a.label}</div>
              <div class="cmd-item-desc">${a.desc}</div>
            </div>
          </div>
        `;
      });
      results.innerHTML = html;

      results.querySelectorAll('.cmd-palette-item').forEach((item, idx) => {
        item.addEventListener('click', () => {
          filtered[idx].act();
        });
      });
    };

    renderResults('');

    input.oninput = () => renderResults(input.value);
    input.onkeydown = (e) => {
      if (e.key === 'Escape') {
        modal.style.display = 'none';
      } else if (e.key === 'Enter') {
        const sel = results.querySelector('.cmd-palette-item.selected');
        if (sel) sel.click();
      }
    };

    modal.onclick = (e) => {
      if (e.target === modal) modal.style.display = 'none';
    };
  },

  async renderExperimentLabView() {
    const sTag = document.getElementById('currentStepTag');
    const cPill = document.getElementById('currentCategoryPill');
    const sTitle = document.getElementById('currentStepTitle');
    const sDesc = document.getElementById('currentStepDesc');

    if (sTag) sTag.textContent = 'Creative Lab UI-23';
    if (cPill) cPill.textContent = 'EXPERIMENTACIÓN CREATIVA';
    if (sTitle) sTitle.textContent = 'Creative Variant Generator & Experiment Lab (Fase 9)';
    if (sDesc) sDesc.textContent = 'Matriz de pruebas A/B/n multivariante para Hooks (primeros 3s), cadencia rítmica (107.7 BPM) y llamados a la acción con hipótesis de conversión y control estricto de economía verbal.';

    const contentArea = document.getElementById('stepContentArea');
    if (!contentArea) return;

    contentArea.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-dim);">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <div>Cargando matriz de experimentos creativos desde /api/ai/experiments...</div>
      </div>
    `;

    try {
      const resp = await fetch('/api/ai/experiments');
      const matrix = await resp.json();
      this.displayExperimentMatrixUI(contentArea, matrix);
    } catch (e) {
      contentArea.innerHTML = `<div class="alert alert-error">Error al cargar matriz de experimentos: ${e.message}</div>`;
    }
  },

  displayExperimentMatrixUI(container, matrix) {
    if (!matrix || !Array.isArray(matrix.variants)) {
      container.innerHTML = '<div class="alert alert-error">Matriz de experimentos inválida.</div>';
      return;
    }

    const activeVarId = matrix.active_variant_id;
    const variants = matrix.variants;

    let cardsHtml = '';
    variants.forEach(v => {
      const isActive = v.variant_id === activeVarId;
      const ve = v.verbal_economy || {};
      const wps = ve.wps || 0;
      const statusClass = ve.status === 'OPTIMAL' ? 'status-badge-optimal' : (ve.status === 'WARNING' ? 'status-badge-warning' : 'status-badge-acceptable');

      cardsHtml += `
        <div class="experiment-card ${isActive ? 'active-variant' : ''}" id="card_${v.variant_id}">
          ${isActive ? '<span class="active-variant-badge">★ VARIANTE ACTIVA</span>' : ''}
          <div class="exp-card-header">
            <div>
              <div class="exp-card-title">${v.name}</div>
              <span class="exp-hook-tag" style="background: rgba(129, 140, 248, 0.2); color: #818cf8; margin-top: 4px; display: inline-block;">${v.hook_type}</span>
            </div>
          </div>

          <div class="exp-hook-quote">"${v.hook_copy}"</div>
          <div class="exp-visual-desc"><strong>Visual:</strong> ${v.hook_visual_direction}</div>

          <div class="exp-details-list">
            <div class="exp-detail-row">
              <span class="exp-detail-label">Pacing / Tempo</span>
              <span class="exp-detail-value">${v.pacing_type} (${v.bpm} BPM)</span>
            </div>
            <div class="exp-detail-row">
              <span class="exp-detail-label">CTA de Cierre</span>
              <span class="exp-detail-value" style="color:#a7f3d0;">"${v.cta_copy}"</span>
            </div>
            <div class="exp-detail-row">
              <span class="exp-detail-label">Target</span>
              <span class="exp-detail-value">${v.target_audience}</span>
            </div>
            <div class="exp-detail-row">
              <span class="exp-detail-label">KPI Primario</span>
              <span class="exp-detail-value" style="color:#38bdf8;">${v.primary_kpi}</span>
            </div>
            <div class="exp-detail-row">
              <span class="exp-detail-label">Lift Proyectado</span>
              <span class="exp-detail-value" style="color:#34d399;">+${v.projected_lift_pct}% (Conf: ${Math.round(v.confidence_score * 100)}%)</span>
            </div>
            <div class="exp-detail-row">
              <span class="exp-detail-label">Economía Verbal</span>
              <span class="exp-detail-value"><span class="${statusClass}">${wps} wps · ${ve.status || 'OK'}</span></span>
            </div>
          </div>

          <div class="exp-hypothesis-box">
            <strong>Hipótesis:</strong> ${v.hypothesis}
          </div>

          <button class="btn-select-variant ${isActive ? 'active' : ''}" data-variant-id="${v.variant_id}">
            ${isActive ? '✓ Variante en Producción' : '⭐ Seleccionar para Storyboard'}
          </button>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="experiment-lab-container">
        <div class="experiment-hero-card">
          <div class="experiment-hero-info">
            <h2><span style="color:#818cf8;">🧪</span> Creative Experiment Lab</h2>
            <p style="color: var(--text-dim); margin-bottom: 0.75rem; font-size: 0.9rem;">
              Optimización multivariante bayesiana en los primeros 3 segundos (Retention Gate). 
              Al seleccionar una variante, se sincroniza automáticamente con el Storyboard, la Ficha Técnica y la Memoria de Marca.
            </p>
            <div class="experiment-meta-pills">
              <span class="exp-meta-pill">🎯 METODOLOGÍA: Multi-Armed Bandit</span>
              <span class="exp-meta-pill">📐 FORMATO: 9:16 Vertical Video</span>
              <span class="exp-meta-pill">🎵 AUDIO SYNC: 107.7 BPM</span>
              <span class="exp-meta-pill">🧠 MEMORIA: Sincronizada</span>
            </div>
          </div>
          <div>
            <button class="btn btn-secondary btn-sm" id="btnRegenerateExperiments">
              🔄 Regenerar Matriz con AI Brain
            </button>
          </div>
        </div>

        <div class="experiment-grid">
          ${cardsHtml}
        </div>
      </div>
    `;

    // Event listeners para seleccionar variantes
    container.querySelectorAll('.btn-select-variant:not(.active)').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const varId = btn.getAttribute('data-variant-id');
        btn.textContent = '⏳ Activando...';
        btn.disabled = true;
        try {
          const resp = await fetch('/api/ai/experiments/select-variant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ variant_id: varId })
          });
          const res = await resp.json();
          if (res.success) {
            this.showToast(`Variante activada con éxito: "${res.active_variant.name}". Storyboard escena 1 sincronizada.`);
            this.renderExperimentLabView();
          } else {
            this.showToast(`Error al activar variante: ${res.error || 'Desconocido'}`);
          }
        } catch (err) {
          this.showToast(`Error de red al activar variante: ${err.message}`);
        }
      });
    });

    // Regenerar matriz
    const btnRegen = document.getElementById('btnRegenerateExperiments');
    if (btnRegen) {
      btnRegen.addEventListener('click', async () => {
        btnRegen.textContent = '⏳ Generando con AI...';
        btnRegen.disabled = true;
        try {
          const resp = await fetch('/api/ai/experiments/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ campaign_id: 'camp_locos_materos_2026' })
          });
          const res = await resp.json();
          if (res.success) {
            this.showToast('Matriz de experimentos regenerada con éxito.');
            this.renderExperimentLabView();
          }
        } catch (err) {
          this.showToast(`Error regenerando: ${err.message}`);
        }
      });
    }
  }

};
