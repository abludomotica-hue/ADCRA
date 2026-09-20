/* ==========================================================================
   ADCRA CAMPAIGN INTAKE STUDIO — JAVASCRIPT APP (FASE UI-01)
   Lógica del Layout Tripartito, Navegación Progresiva y Asistente Agéntico
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  IntakeApp.init();
});

const IntakeApp = {
  activeStep: 1,
  totalSteps: 17,
  clientMode: 'NEW_CLIENT', // 'NEW_CLIENT' | 'EXISTING_CLIENT'
  lastSavedAt: new Date(),

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
      secondary: [],
      desired_outcome: 'recordar_marca'
    },
    audience: {
      primary: { age_min: 20, age_max: 45, location: '', interests: [] }
    },
    brand: {
      claim: '',
      values: [],
      primary_color: '#0D5C3A',
      secondary_color: '#D4AF37',
      accent_color: '#10B981'
    }
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

  init() {
    this.setupEventListeners();
    this.renderActiveStep();
    this.updateAssistant();
    this.setupAutosave();
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
        this.updateAssistant();
        this.showToast('Modo: Nuevo Cliente activado');
      });

      btnExist.addEventListener('click', () => {
        this.clientMode = 'EXISTING_CLIENT';
        btnExist.classList.add('active');
        btnNew.classList.remove('active');
        this.renderActiveStep();
        this.updateAssistant();
        this.showToast('Modo: Cliente Existente (Memoria precargada)');
      });
    }

    // Navegación de pasos por la barra lateral
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
          this.showToast('¡Has llegado al Campaign Readiness Center!');
        }
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
  },

  goToStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > this.totalSteps) return;
    this.activeStep = stepNumber;

    // Actualizar sidebar activo
    document.querySelectorAll('.step-item').forEach(el => {
      const s = parseInt(el.getAttribute('data-step'), 10);
      if (s === this.activeStep) {
        el.classList.add('active');
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

    this.renderActiveStep();
    this.updateAssistant();
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

    // Renderizar según el paso activo
    if (this.activeStep === 1) {
      contentArea.innerHTML = this.renderStep01Client();
      this.bindStep01Events();
    } else {
      contentArea.innerHTML = `
        <div class="form-section">
          <div class="form-section-title">
            <span>⚙️</span> Configuración de ${sMeta.title}
          </div>
          <p style="font-size: 0.88rem; color: var(--text-muted);">
            Esta sección formará parte de la fase correspondiente del intake progresivo. Puedes navegar libremente entre los 17 pasos para comprobar la fluidez y coherencia del sistema agéntico.
          </p>
          <div style="padding: 2rem; background: rgba(255,255,255,0.02); border: 1px dashed var(--border-subtle); border-radius: 12px; text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">✦</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: var(--color-gold-bright);">${sMeta.title}</div>
            <div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 0.35rem;">Dominio: ${sMeta.category} | Estado: READY PARA CONFIGURACIÓN</div>
          </div>
        </div>
      `;
    }
  },

  renderStep01Client() {
    if (this.clientMode === 'EXISTING_CLIENT') {
      return `
        <div class="form-section">
          <div class="form-section-title">
            <span>🏛️</span> Cliente Existente Seleccionado
          </div>
          <p style="font-size: 0.85rem; color: var(--text-muted);">
            Se ha detectado el perfil histórico de <strong>Locos Materos</strong> en la memoria episódica de ADCRA. Su identidad visual, tono y audiencia han sido precargados automáticamente.
          </p>
          <div style="display: flex; gap: 1rem; align-items: center; padding: 1.25rem; background: rgba(212,175,55,0.08); border: 1px solid var(--border-gold); border-radius: 12px;">
            <div style="font-size: 2.5rem;">🧉</div>
            <div>
              <div style="font-weight: 800; font-size: 1.1rem; color: #FFF;">Locos Materos</div>
              <div style="font-size: 0.82rem; color: var(--color-gold-bright);">Yerba Mate / Alimentos y Bebidas • Quality Score previo: 100.0/100</div>
              <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.25rem;">Paleta: Verde Mate (#0D5C3A), Dorado (#D4AF37) • Claim: "¿Dónde estás tú? Está tu mate"</div>
            </div>
          </div>
        </div>
      `;
    }

    return `
      <div class="form-section">
        <div class="form-section-title">
          <span>🏢</span> Datos de la Marca y Empresa
        </div>
        
        <!-- Smart Website Auto-Analysis Row -->
        <div style="display: flex; gap: 0.75rem; align-items: flex-end; padding: 1rem; background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); border-radius: 10px;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Sitio Web Oficial (Opcional pero recomendado)</label>
            <input type="url" id="inpClientWeb" class="form-input" placeholder="https://www.tu-marca.com" value="${this.draft.client.website_url}">
          </div>
          <button class="btn btn-primary" id="btnAnalyzeWeb" style="height: 40px;">
            <span class="btn-icon">⚡</span> Analizar Sitio Web
          </button>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Nombre Comercial de la Marca <span class="required">*</span></label>
            <input type="text" id="inpBrandName" class="form-input" placeholder="Ej: Café de la Sierra" value="${this.draft.client.brand_name}">
          </div>
          <div class="form-group">
            <label class="form-label">Sector o Industria <span class="required">*</span></label>
            <input type="text" id="inpIndustry" class="form-input" placeholder="Ej: Café de Especialidad / Gastronomía" value="${this.draft.client.industry}">
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Tipo de Negocio</label>
          <select id="selBusinessType" class="form-select">
            <option value="producto" ${this.draft.client.business_type === 'producto' ? 'selected' : ''}>Producto Físico / Bien de Consumo</option>
            <option value="servicio" ${this.draft.client.business_type === 'servicio' ? 'selected' : ''}>Servicio Profesional / Consultoría</option>
            <option value="ecommerce" ${this.draft.client.business_type === 'ecommerce' ? 'selected' : ''}>E-commerce / Tienda Online</option>
            <option value="restaurante" ${this.draft.client.business_type === 'restaurante' ? 'selected' : ''}>Gastronomía / Restaurante</option>
            <option value="startup" ${this.draft.client.business_type === 'startup' ? 'selected' : ''}>Startup / Tecnología / SaaS</option>
            <option value="institucion" ${this.draft.client.business_type === 'institucion' ? 'selected' : ''}>Organización / Institución</option>
            <option value="otro" ${this.draft.client.business_type === 'otro' ? 'selected' : ''}>Otro</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Descripción Breve de la Propuesta de Valor</label>
          <textarea id="inpDescription" class="form-textarea" placeholder="Describe brevemente qué hace único a tu negocio, qué problema resuelve o qué ritual celebra...">${this.draft.client.description}</textarea>
        </div>
      </div>

      <div class="form-section">
        <div class="form-section-title">
          <span>📱</span> Presencia Digital y Canales Oficiales
        </div>
        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">Instagram (@usuario)</label>
            <input type="text" id="inpInstagram" class="form-input" placeholder="@cafedelasierra" value="${this.draft.client.social_channels.instagram}">
          </div>
          <div class="form-group">
            <label class="form-label">TikTok (@usuario)</label>
            <input type="text" id="inpTiktok" class="form-input" placeholder="@cafedelasierra" value="${this.draft.client.social_channels.tiktok}">
          </div>
        </div>
      </div>
    `;
  },

  bindStep01Events() {
    const inpBrand = document.getElementById('inpBrandName');
    if (inpBrand) {
      inpBrand.addEventListener('input', (e) => {
        this.draft.client.brand_name = e.target.value.trim();
        this.updateStepStatus(1, this.draft.client.brand_name ? 'COMPLETE' : 'READY');
        this.updateAssistant();
      });
    }

    const btnAnalyze = document.getElementById('btnAnalyzeWeb');
    if (btnAnalyze) {
      btnAnalyze.addEventListener('click', () => {
        const url = document.getElementById('inpClientWeb').value.trim();
        if (!url) {
          this.showToast('Introduce una URL para analizar', true);
          return;
        }
        btnAnalyze.disabled = true;
        btnAnalyze.textContent = 'Analizando...';
        setTimeout(() => {
          btnAnalyze.disabled = false;
          btnAnalyze.innerHTML = '<span class="btn-icon">⚡</span> Analizar Sitio Web';
          this.showToast('Análisis web completado: Paleta y propuesta inferidas');
          this.updateAssistant('He analizado la web proporcionada: se detectaron colores predominantes y un tono aspiracional. Revisa la Ficha de Marca en el Paso 04.');
        }, 800);
      });
    }
  },

  updateStepStatus(stepNum, status) {
    const badge = document.getElementById(`stepBadge${stepNum}`);
    if (badge) {
      badge.className = `step-status status-${status.toLowerCase().replace('_', '-')}`;
      badge.textContent = status;
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

    // Mensajes dinámicos contextuales según el paso
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
        if (badgeStatus) badgeStatus.textContent = 'OBJETIVO PENDIENTE';
        break;
      case 8:
        textEl.textContent = 'Paso 08 (Audio): Carga una pista musical en MP3 o WAV. El motor de audio extraerá el BPM, los compases rítmicos y los puntos de corte de forma autónoma.';
        if (badgeStatus) badgeStatus.textContent = 'AUDIO REQUERIDO';
        break;
      case 17:
        textEl.textContent = 'Paso 17 (Readiness Center): Diagnóstico pre-flight. El sistema auditará si existen inconsistencias o bloqueantes antes de activar el pipeline de producción.';
        if (badgeStatus) badgeStatus.textContent = 'AUDITORÍA PRE-FLIGHT';
        break;
      default:
        textEl.textContent = `Paso ${this.activeStep} (${this.steps[this.activeStep - 1].name}): Configura los parámetros necesarios. El asistente supervisa en tiempo real la coherencia con la identidad de marca.`;
        if (badgeStatus) badgeStatus.textContent = 'MONITOREANDO';
    }
  },

  setupAutosave() {
    // Simulación de auto-guardado cada 10 segundos
    setInterval(() => {
      const autoText = document.getElementById('autosaveText');
      if (autoText) {
        autoText.textContent = 'Guardado ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      }
    }, 10000);
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
  }
};
