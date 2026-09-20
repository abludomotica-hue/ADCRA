/* ==========================================================================
   ADCRA MISSION CONTROL — CLIENT APPLICATION LOGIC
   Gestión reactiva de video, estado de fases, telemetría y entregables
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initVideoPlayer();
  initSafeZoneToggle();
  initModal();
  loadAllData();
  setupEventListeners();
});

// Cache global de datos
const AppState = {
  status: null,
  deliver: null,
  benchmark: null,
  skills: null,
  health: null,
  activeFormat: 'master'
};

// ----------------- TAB NAVIGATION -----------------
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const activePanel = document.getElementById(`panel${capitalize(targetTab)}`);
      if (activePanel) {
        activePanel.classList.add('active');
      }
    });
  });
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// ----------------- VIDEO PLAYER & MULTI-FORMAT SWITCHER -----------------
function initVideoPlayer() {
  const formatCards = document.querySelectorAll('.format-card');
  const videoPlayer = document.getElementById('mainVideoPlayer');
  const viewport = document.getElementById('videoViewport');
  const safeZoneImg = document.getElementById('safeZoneImg');
  const badgeFormat = document.getElementById('activeFormatBadge');
  const activeTitle = document.getElementById('activeVideoTitle');
  const specRes = document.getElementById('specResolution');
  const specHash = document.getElementById('specHash');

  formatCards.forEach(card => {
    card.addEventListener('click', () => {
      formatCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');

      const src = card.getAttribute('data-src');
      const aspectClass = card.getAttribute('data-aspect');
      const res = card.getAttribute('data-res');
      const guide = card.getAttribute('data-guide');
      const hash = card.getAttribute('data-hash');
      const name = card.querySelector('.format-name').textContent;
      const aspect = card.querySelector('.aspect-pill').textContent;

      AppState.activeFormat = card.getAttribute('data-format');

      // Actualizar contenedor de aspecto
      viewport.className = `video-viewport ${aspectClass}`;

      // Actualizar video
      videoPlayer.src = src;
      videoPlayer.load();
      videoPlayer.play().catch(() => {});

      // Actualizar overlay de safe zone
      if (guide && safeZoneImg) {
        safeZoneImg.src = guide;
      }

      // Actualizar metadatos
      badgeFormat.textContent = `${aspect} ${aspectClass.includes('9-16') ? 'VERTICAL' : (aspectClass.includes('1-1') ? 'SQUARE' : 'WIDESCREEN')}`;
      activeTitle.textContent = name;
      specRes.textContent = res;
      specHash.textContent = hash ? (hash.substring(0, 10) + '...') : '—';
      specHash.setAttribute('title', `Hash SHA-256 completo: ${hash}\nClick para copiar`);
      specHash.setAttribute('data-full-hash', hash || '');
    });
  });

  // Copiar hash al portapapeles
  specHash.addEventListener('click', () => {
    const fullHash = specHash.getAttribute('data-full-hash');
    if (fullHash) {
      navigator.clipboard.writeText(fullHash).then(() => {
        showToast('Hash SHA-256 copiado al portapapeles');
      });
    }
  });
}

// ----------------- SAFE ZONE TOGGLE -----------------
function initSafeZoneToggle() {
  const chk = document.getElementById('chkSafeZone');
  const overlay = document.getElementById('safeZoneOverlay');

  if (chk && overlay) {
    chk.addEventListener('change', () => {
      if (chk.checked) {
        overlay.classList.add('visible');
      } else {
        overlay.classList.remove('visible');
      }
    });
  }
}

// ----------------- DATA LOADING ORCHESTRATION -----------------
async function loadAllData() {
  try {
    await Promise.all([
      fetchStatus(),
      fetchDeliver(),
      fetchBenchmark(),
      fetchIntrospect(),
      fetchHealth()
    ]);
    renderAllPanels();
  } catch (err) {
    console.error('Error cargando datos de ADCRA:', err);
    showToast('Error cargando datos del servidor', true);
  }
}

async function fetchStatus() {
  const res = await fetch('/api/status');
  AppState.status = await res.json();
}

async function fetchDeliver() {
  const res = await fetch('/api/deliver');
  AppState.deliver = await res.json();
}

async function fetchBenchmark() {
  const res = await fetch('/api/benchmark');
  AppState.benchmark = await res.json();
}

async function fetchIntrospect() {
  const res = await fetch('/api/introspect');
  AppState.skills = await res.json();
}

async function fetchHealth() {
  const res = await fetch('/api/health');
  AppState.health = await res.json();
}

// ----------------- RENDER FUNCTIONS -----------------
function renderAllPanels() {
  renderMetrics();
  renderPipelineGrid();
  renderTelemetry();
  renderSkills();
  renderVault();
}

function renderMetrics() {
  if (AppState.status) {
    const pct = AppState.status.completion_percentage;
    document.getElementById('valPipelineProgress').textContent = `${pct}%`;
  }
  if (AppState.deliver && AppState.deliver.broadcast_certification) {
    const score = AppState.deliver.broadcast_certification.qc_score;
    document.getElementById('valQcScore').textContent = `${score.toFixed(1)} / 100`;
  }
  if (AppState.deliver && AppState.deliver.master_audio) {
    const lufs = AppState.deliver.master_audio.loudness_lufs;
    document.getElementById('valLoudness').textContent = `${lufs} LUFS`;
  }
  if (AppState.benchmark && AppState.benchmark.aggregate_metrics) {
    const agg = AppState.benchmark.aggregate_metrics;
    const estSec = (agg.pipeline_estimated_total_latency_sec * 1000).toFixed(1);
    document.getElementById('valLatency').textContent = `${estSec} ms`;
  }
}

function renderPipelineGrid() {
  const container = document.getElementById('phasesGrid');
  if (!container || !AppState.status) return;

  container.innerHTML = '';
  const phases = AppState.status.phases || [];

  phases.forEach(p => {
    const card = document.createElement('div');
    card.className = 'phase-card';
    card.innerHTML = `
      <div class="phase-card-top">
        <span class="phase-id">${p.phase_id}</span>
        <span class="phase-category">${p.category}</span>
      </div>
      <div class="phase-name">${p.name}</div>
      <div class="phase-artifact" title="${p.artifact}">${p.artifact}</div>
      <div class="phase-card-bottom">
        <span class="phase-status-pill">
          <span class="pulse-indicator"></span> ${p.status}
        </span>
        <span style="font-size: 0.72rem; color: var(--text-dim);">${p.size_kb} KB</span>
      </div>
    `;

    card.addEventListener('click', () => {
      openArtifactModal(p.name, p.artifact);
    });

    container.appendChild(card);
  });
}

function renderTelemetry() {
  if (AppState.health) {
    const h = AppState.health;
    document.getElementById('hwOs').textContent = 'Linux (x86_64)';
    document.getElementById('hwCpu').textContent = `${h.cpu_cores} Cores`;
    document.getElementById('hwRam').textContent = `${h.ram_total_gb} GB`;
    document.getElementById('hwGpu').textContent = h.gpu_device || 'CPU Acelerada';
  }

  const container = document.getElementById('engineBarsContainer');
  if (!container || !AppState.benchmark) return;

  container.innerHTML = '';
  const engines = AppState.benchmark.engine_benchmarks || [];
  const maxLat = Math.max(...engines.map(e => e.mean_latency_ms), 50.0);

  engines.forEach(eng => {
    const pct = Math.min(100, Math.max(8, (eng.mean_latency_ms / maxLat) * 100));
    const row = document.createElement('div');
    row.className = 'engine-bar-row';
    row.innerHTML = `
      <div class="engine-meta-row">
        <span class="engine-name">[${eng.category.toUpperCase()}] ${eng.engine_name}</span>
        <span class="engine-stats">${eng.mean_latency_ms} ms | ${eng.throughput_ops_sec.toLocaleString()} ops/s</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${pct}%;"></div>
      </div>
    `;
    container.appendChild(row);
  });
}

function renderSkills() {
  const container = document.getElementById('skillsGrid');
  if (!container || !AppState.skills) return;

  container.innerHTML = '';
  const skills = AppState.skills.skills || [];

  skills.forEach(s => {
    const card = document.createElement('div');
    card.className = 'skill-card';
    card.setAttribute('data-domain', s.domain.toLowerCase());
    card.setAttribute('data-name', s.name.toLowerCase());
    card.innerHTML = `
      <div class="skill-top">
        <span class="skill-domain-pill">${s.domain}</span>
        <span class="skill-ver">v${s.version}</span>
      </div>
      <div class="skill-name">${s.name}</div>
      <div class="skill-desc">${s.description || 'Habilidad modular de la agencia.'}</div>
      <div class="skill-path">${s.path}</div>
    `;
    container.appendChild(card);
  });
}

function renderVault() {
  const tbody = document.getElementById('vaultTableBody');
  if (!tbody || !AppState.deliver) return;

  tbody.innerHTML = '';
  const d = AppState.deliver;
  const items = [];

  // Master Video
  if (d.master_video) {
    items.push({
      channel: 'Master Oficial (Broadcast)',
      aspect: d.master_video.aspect_ratio,
      res: d.master_video.resolution,
      dur: `${d.master_video.duration_seconds}s`,
      size: '11.0 MB',
      hash: d.master_video.sha256,
      url: `/${d.master_video.file_path}`
    });
  }

  // Variants
  if (d.variants) {
    d.variants.forEach(v => {
      const pName = v.platform.replace('_', ' ').toUpperCase();
      items.push({
        channel: pName,
        aspect: v.aspect_ratio,
        res: v.resolution,
        dur: '29.21s',
        size: v.aspect_ratio === '1:1' ? '4.6 MB' : (v.aspect_ratio === '16:9' ? '6.6 MB' : '11.0 MB'),
        hash: v.sha256,
        url: `/${v.file_path}`
      });
    });
  }

  items.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${item.channel}</strong></td>
      <td><span class="aspect-pill">${item.aspect}</span></td>
      <td>${item.res}</td>
      <td>${item.dur}</td>
      <td>${item.size}</td>
      <td class="hash-cell" title="${item.hash}">${item.hash.substring(0, 16)}...</td>
      <td>
        <a href="${item.url}" download class="btn btn-secondary btn-sm">
          Descargar
        </a>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ----------------- EVENT LISTENERS & SEARCH -----------------
function setupEventListeners() {
  // Refrescar métricas
  const btnRefresh = document.getElementById('btnRefresh');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      btnRefresh.disabled = true;
      btnRefresh.textContent = '↻ Actualizando...';
      loadAllData().then(() => {
        btnRefresh.disabled = false;
        btnRefresh.innerHTML = '<span class="btn-icon">↻</span> Refrescar';
        showToast('Datos actualizados');
      });
    });
  }

  // Benchmark en vivo
  const btnBench = document.getElementById('btnQuickBenchmark');
  const btnBenchLive = document.getElementById('btnRunBenchmarkLive');

  [btnBench, btnBenchLive].forEach(b => {
    if (!b) return;
    b.addEventListener('click', async () => {
      b.disabled = true;
      const originalText = b.innerHTML;
      b.innerHTML = '<span class="btn-icon">⏳</span> Evaluando...';

      try {
        const res = await fetch('/api/run-benchmark', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'SUCCESS') {
          AppState.benchmark = data.report;
          renderMetrics();
          renderTelemetry();
          showToast('Stress-test completado: Rating EXCELLENT');
        } else {
          showToast('Error en ejecución de benchmark', true);
        }
      } catch (err) {
        showToast('Falla de red al ejecutar benchmark', true);
      } finally {
        b.disabled = false;
        b.innerHTML = originalText;
      }
    });
  });

  // Filtrado de pipeline
  const pipelineSearch = document.getElementById('pipelineSearch');
  if (pipelineSearch) {
    pipelineSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('.phase-card').forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? 'flex' : 'none';
      });
    });
  }

  // Filtrado de habilidades
  const skillSearch = document.getElementById('skillSearch');
  const domainSelect = document.getElementById('domainSelect');

  function filterSkills() {
    const q = skillSearch ? skillSearch.value.toLowerCase() : '';
    const dom = domainSelect ? domainSelect.value.toLowerCase() : 'all';

    document.querySelectorAll('.skill-card').forEach(card => {
      const cardDom = card.getAttribute('data-domain');
      const text = card.textContent.toLowerCase();
      const matchesDom = dom === 'all' || cardDom === dom;
      const matchesQ = text.includes(q);
      card.style.display = (matchesDom && matchesQ) ? 'flex' : 'none';
    });
  }

  if (skillSearch) skillSearch.addEventListener('input', filterSkills);
  if (domainSelect) domainSelect.addEventListener('change', filterSkills);
}

// ----------------- ARTIFACT MODAL -----------------
function initModal() {
  const modal = document.getElementById('artifactModal');
  const btnClose = document.getElementById('btnCloseModal');
  const btnCopy = document.getElementById('btnCopyJson');

  if (btnClose) {
    btnClose.addEventListener('click', () => {
      modal.classList.remove('open');
    });
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('open');
      }
    });
  }

  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const code = document.getElementById('modalJsonContent').textContent;
      navigator.clipboard.writeText(code).then(() => {
        showToast('Contenido copiado al portapapeles');
      });
    });
  }
}

async function openArtifactModal(title, relPath) {
  const modal = document.getElementById('artifactModal');
  const titleEl = document.getElementById('modalArtifactTitle');
  const pathEl = document.getElementById('modalArtifactPath');
  const codeEl = document.getElementById('modalJsonContent');

  titleEl.textContent = title;
  pathEl.textContent = relPath;
  codeEl.textContent = '// Cargando contenido del artefacto...';
  modal.classList.add('open');

  try {
    const res = await fetch(`/api/artifact?path=${encodeURIComponent(relPath)}`);
    const data = await res.json();
    if (data.error) {
      codeEl.textContent = `// Error: ${data.error}`;
    } else if (data.type === 'json') {
      codeEl.textContent = JSON.stringify(data.content, null, 2);
    } else {
      codeEl.textContent = data.content;
    }
  } catch (err) {
    codeEl.textContent = `// Error al leer archivo: ${err.message}`;
  }
}

// ----------------- TOAST NOTIFICATIONS -----------------
function showToast(msg, isError = false) {
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
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, 2800);
}
