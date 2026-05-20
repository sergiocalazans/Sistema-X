// estado atual da pag
const SXF = {
  currentPage: null,

  // dados gerais
  patients: [
    { id: 1, name: 'Ana Silva Santos',    age: 8,  sex: 'F', score: 0.62, rec: 'encaminhar',   date: '01/05/2026' },
    { id: 2, name: 'Pedro Oliveira Costa',age: 12, sex: 'M', score: 0.71, rec: 'encaminhar',   date: '30/04/2026' },
    { id: 3, name: 'Maria Souza Lima',    age: 6,  sex: 'F', score: 0.48, rec: 'nao-prio',     date: '29/04/2026' },
    { id: 4, name: 'João Ferreira Alves', age: 9,  sex: 'M', score: 0.59, rec: 'encaminhar',   date: '28/04/2026' },
    { id: 5, name: 'Beatriz Mendes Rocha',age: 7,  sex: 'F', score: 0.53, rec: 'nao-prio',     date: '27/04/2026' },
    { id: 6, name: 'Carlos Eduardo Silva',age: 11, sex: 'M', score: 0.68, rec: 'encaminhar',   date: '26/04/2026' },
    { id: 7, name: 'Juliana Costa Almeida',age:5,  sex: 'F', score: 0.45, rec: 'nao-prio',     date: '25/04/2026' },
    { id: 8, name: 'Rafael Santos Moreira',age:10, sex: 'M', score: 0.52, rec: 'nao-prio',     date: '24/04/2026' },
    { id: 9, name: 'Fernanda Lima Pereira',age:8,  sex: 'F', score: 0.59, rec: 'encaminhar',   date: '23/04/2026' },
    { id:10, name: 'Lucas Martins Rocha', age: 14, sex: 'M', score: 0.63, rec: 'encaminhar',   date: '22/04/2026' },
  ],

  nextId: 11,
  lastResult: null,
};

// sintomas
const SYMPTOMS = [
  { id: 'defIntelectual',  label: 'Deficiência intelectual',       pesoM: 0.14, pesoF: 0.13 },
  { id: 'difAprendizagem', label: 'Dificuldades de aprendizagem',  pesoM: 0.10, pesoF: 0.10 },
  { id: 'defAtencao',      label: 'Déficit de atenção',            pesoM: 0.08, pesoF: 0.07 },
  { id: 'atrasoFala',      label: 'Atraso na fala',                pesoM: 0.09, pesoF: 0.08 },
  { id: 'hiperatividade',  label: 'Hiperatividade',                pesoM: 0.07, pesoF: 0.06 },
  { id: 'movRepetitivos',  label: 'Movimentos repetitivos',        pesoM: 0.08, pesoF: 0.08 },
  { id: 'evitaContato',    label: 'Evita contato visual',          pesoM: 0.06, pesoF: 0.06 },
  { id: 'evitaFisico',     label: 'Evita contato físico',          pesoM: 0.05, pesoF: 0.05 },
  { id: 'agressividade',   label: 'Agressividade',                 pesoM: 0.05, pesoF: 0.04 },
  { id: 'faceAlongada',    label: 'Face alongada / orelhas proeminentes', pesoM: 0.10, pesoF: 0.09 },
  { id: 'macroorquidismo', label: 'Macroorquidismo',               pesoM: 0.09, pesoF: 0.00 },
  { id: 'hiperMobil',      label: 'Hipermobilidade articular',     pesoM: 0.05, pesoF: 0.09 },
];

const THRESHOLD = { M: 0.56, F: 0.55 };

function calcScore(sex, symptoms) {
  const key = sex === 'M' ? 'pesoM' : 'pesoF';
  return symptoms.reduce((sum, sid) => {
    const s = SYMPTOMS.find(s => s.id === sid);
    return s ? sum + s[key] : sum;
  }, 0);
}

function getRecommendation(sex, score) {
  return score >= THRESHOLD[sex] ? 'encaminhar' : 'nao-prio';
}

const pages = {};

function registerPage(id, renderFn) {
  pages[id] = renderFn;
}

function navigate(pageId, params = {}) {
  SXF.currentPage = pageId;

  // atualizar a nav
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === pageId);
  });

  const content = document.getElementById('page-content');
  if (!content) return;

  content.innerHTML = '';
  content.className = 'fade-in';

  const fn = pages[pageId];
  if (fn) fn(content, params);

  void content.offsetWidth;
}

// barra lateral
function buildShell() {
  const sidebarHTML = `
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-brand">
        <div class="sidebar-logo">
          ${icons.pulse}
        </div>
        <div class="sidebar-brand-text">
          <div class="brand-name">Triagem SXF</div>
          <div class="brand-sub">Sistema Clínico</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <a class="nav-item" data-page="dashboard">
          ${icons.dashboard} Dashboard
        </a>
        <a class="nav-item" data-page="cadastro">
          ${icons.userPlus} Cadastrar Paciente
        </a>
        <a class="nav-item" data-page="historico">
          ${icons.clipboard} Histórico de Avaliações
        </a>
        <a class="nav-item" data-page="relatorios">
          ${icons.chart} Relatórios
        </a>
      </nav>
      <div class="sidebar-footer">
        <a class="nav-item danger" id="logout-btn">
          ${icons.logout} Sair
        </a>
      </div>
    </aside>
    <div class="main-content">
      <div id="page-content"></div>
    </div>
    <div class="toast-container" id="toast-container"></div>
  `;

  document.body.innerHTML = `<div class="app-shell">${sidebarHTML}</div>`;

  // botões de nav
  document.querySelectorAll('.nav-item[data-page]').forEach(el => {
    el.addEventListener('click', () => navigate(el.dataset.page));
  });

  document.getElementById('logout-btn').addEventListener('click', () => {
    showToast('Sessão encerrada.', 'success');
    setTimeout(() => renderLogin(), 800);
  });
}

// ícones
const icons = {
  pulse:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
  dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>`,
  userPlus:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="16" y1="11" x2="22" y2="11"/></svg>`,
  users:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  clipboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>`,
  chart:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
  arrow:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`,
  logout:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
  check:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
  back:      `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>`,
  search:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
  alert:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  checkCircle:`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
  filter:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>`,
  barChart:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>`,
  save:      `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>`,
  refresh:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>`,
};

// toast (avisos)
function showToast(msg, type = '') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const icon = type === 'success' ? icons.checkCircle : type === 'error' ? icons.alert : icons.check;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `${icon}<span>${msg}</span>`;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function sexLabel(s)  { return s === 'M' ? 'Masculino' : 'Feminino'; }
function recBadge(r)  {
  return r === 'encaminhar'
    ? `<span class="badge encaminhar">Encaminhar</span>`
    : `<span class="badge nao-prio">Não prioritário</span>`;
}

// Dashboard/página principal
registerPage('dashboard', (el) => {
  const total    = SXF.patients.length;
  const triagens = SXF.patients.filter(p => p.score !== null).length;
  const encamin  = SXF.patients.filter(p => p.rec === 'encaminhar').length;
  const recent   = SXF.patients.slice(0, 6);

  el.innerHTML = `
    <div class="page-header">
      <div class="page-title">Dashboard</div>
      <div class="page-subtitle">Visão geral do sistema de triagem</div>
    </div>
    <div class="page-body">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">${icons.users}</div>
          <div class="stat-label">Total de Pacientes</div>
          <div class="stat-value">${total}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">${icons.clipboard}</div>
          <div class="stat-label">Triagens Realizadas</div>
          <div class="stat-value">${triagens}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">${icons.arrow}</div>
          <div class="stat-label">Encaminhamentos Recomendados</div>
          <div class="stat-value">${encamin}</div>
        </div>
      </div>

      <div class="table-card">
        <div class="table-header">
          <span class="table-title">Pacientes Recentes</span>
          <button class="btn btn-secondary btn-sm" onclick="navigate('historico')">
            Ver todos ${icons.arrow}
          </button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Idade</th>
                <th>Sexo</th>
                <th>Score</th>
                <th>Recomendação</th>
              </tr>
            </thead>
            <tbody>
              ${recent.map(p => `
                <tr>
                  <td class="name">${p.name}</td>
                  <td>${p.age}</td>
                  <td>${sexLabel(p.sex)}</td>
                  <td class="score">${p.score.toFixed(2)}</td>
                  <td>${recBadge(p.rec)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
});

// pagina de cadastro
registerPage('cadastro', (el) => {
  let selectedSex = 'M';

  el.innerHTML = `
    <div class="page-header">
      <a class="back-link" onclick="navigate('dashboard')">${icons.back} Voltar ao Dashboard</a>
      <div class="page-title">Cadastro de Paciente</div>
      <div class="page-subtitle">Preencha as informações do paciente</div>
    </div>
    <div class="page-body">
      <div class="form-section" style="max-width:560px">
        <div class="form-group">
          <label class="form-label">Nome Completo</label>
          <input id="inp-name" class="form-input" type="text" placeholder="Digite o nome completo">
          <div class="field-error" id="err-name">Campo obrigatório</div>
        </div>
        <div class="form-group">
          <label class="form-label">Idade</label>
          <input id="inp-age" class="form-input" type="number" min="0" max="120" placeholder="Digite a idade">
          <div class="field-error" id="err-age">Informe uma idade válida</div>
        </div>
        <div class="form-group">
          <label class="form-label">Sexo</label>
          <div class="radio-group">
            <div class="radio-option selected" id="opt-M" data-sex="M">
              <div class="radio-dot"></div>
              <span class="radio-label">Masculino</span>
            </div>
            <div class="radio-option" id="opt-F" data-sex="F">
              <div class="radio-dot"></div>
              <span class="radio-label">Feminino</span>
            </div>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" id="btn-save">
            ${icons.arrow} Salvar e Iniciar Avaliação
          </button>
          <button class="btn btn-secondary" onclick="navigate('dashboard')">Cancelar</button>
        </div>
      </div>
    </div>
  `;

  // interação dos botoes
  el.querySelectorAll('.radio-option').forEach(opt => {
    opt.addEventListener('click', () => {
      el.querySelectorAll('.radio-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      selectedSex = opt.dataset.sex;
    });
  });

  // salvar
  el.querySelector('#btn-save').addEventListener('click', () => {
    const name = el.querySelector('#inp-name').value.trim();
    const age  = parseInt(el.querySelector('#inp-age').value);
    let valid  = true;

    const errName = el.querySelector('#err-name');
    const errAge  = el.querySelector('#err-age');
    const inpName = el.querySelector('#inp-name');
    const inpAge  = el.querySelector('#inp-age');

    if (!name) {
      inpName.classList.add('error'); errName.classList.add('show'); valid = false;
    } else {
      inpName.classList.remove('error'); errName.classList.remove('show');
    }
    if (isNaN(age) || age < 0 || age > 120) {
      inpAge.classList.add('error'); errAge.classList.add('show'); valid = false;
    } else {
      inpAge.classList.remove('error'); errAge.classList.remove('show');
    }
    if (!valid) return;

    const patient = { id: SXF.nextId++, name, age, sex: selectedSex, score: null, rec: null, date: new Date().toLocaleDateString('pt-BR') };
    SXF.patients.unshift(patient);
    navigate('avaliacao', { patient });
  });
});

// pagina de avaiação 
registerPage('avaliacao', (el, { patient }) => {
  el.innerHTML = `
    <div class="page-header">
      <a class="back-link" onclick="navigate('dashboard')">${icons.back} Voltar ao Dashboard</a>
      <div class="page-title">Avaliação Clínica — Checklist SXF</div>
      <div class="page-subtitle">Paciente: <strong>${patient.name}</strong> · ${sexLabel(patient.sex)} · ${patient.age} anos</div>
    </div>
    <div class="page-body">
      <div class="form-section" style="max-width:720px">
        <div class="form-section-title">Sintomas Clínicos</div>
        <div class="symptoms-grid" id="symptoms-grid">
          ${SYMPTOMS.filter(s => patient.sex === 'M' ? true : s.id !== 'macroorquidismo').map(s => `
            <div class="symptom-item" data-id="${s.id}">
              <div class="symptom-checkbox">${icons.check}</div>
              <span class="symptom-name">${s.label}</span>
            </div>
          `).join('')}
        </div>
        <div class="form-actions" style="margin-top:28px">
          <button class="btn btn-primary btn-lg" id="btn-calc">
            ${icons.pulse} Calcular Score
          </button>
          <button class="btn btn-secondary" onclick="navigate('cadastro')">Cancelar</button>
        </div>
      </div>
    </div>
  `;

  el.querySelectorAll('.symptom-item').forEach(item => {
    item.addEventListener('click', () => item.classList.toggle('checked'));
  });

  el.querySelector('#btn-calc').addEventListener('click', () => {
    const checked = [...el.querySelectorAll('.symptom-item.checked')].map(el => el.dataset.id);
    const score   = Math.min(calcScore(patient.sex, checked), 1);
    const rec     = getRecommendation(patient.sex, score);

    // atualizar paciente salvo
    const p = SXF.patients.find(p => p.id === patient.id);
    if (p) { p.score = score; p.rec = rec; }

    SXF.lastResult = { patient: { ...patient, score, rec }, checkedSymptoms: checked };
    navigate('resultado', { patient: { ...patient, score, rec } });
  });
});

//  pagina de resultado 
registerPage('resultado', (el, { patient }) => {
  const isEnc    = patient.rec === 'encaminhar';
  const threshold = THRESHOLD[patient.sex];
  const barPct   = Math.round(patient.score * 100);

  el.innerHTML = `
    <div class="page-header">
      <a class="back-link" onclick="navigate('dashboard')">${icons.back} Voltar ao Dashboard</a>
      <div class="page-title">Resultado da Triagem</div>
      <div class="page-subtitle">Análise clínica baseada nos sintomas avaliados</div>
    </div>
    <div class="page-body">
      <div class="result-card">
        <div class="result-header">
          <h2>Resultado da Triagem</h2>
          <p>Análise clínica baseada nos sintomas avaliados</p>
        </div>
        <div class="result-body">
          <div class="result-grid">
            <div class="result-field">
              <label>Nome do Paciente</label>
              <div class="value">${patient.name}</div>
            </div>
            <div class="result-field">
              <label>Sexo</label>
              <div class="value">${sexLabel(patient.sex)}</div>
            </div>
            <div class="result-field">
              <label>Score Calculado</label>
              <div class="value score-val" id="score-display">0.00</div>
            </div>
            <div class="result-field">
              <label>Limiar Aplicável</label>
              <div class="value">${threshold.toFixed(2)}</div>
            </div>
          </div>

          <div class="score-bar-wrap">
            <div class="score-bar-track">
              <div class="score-bar-fill" id="score-bar" style="width:0%"></div>
            </div>
            <div class="score-bar-labels">
              <span>0.00</span>
              <span>Limiar ${threshold.toFixed(2)}</span>
              <span>1.00</span>
            </div>
          </div>

          <div class="result-status ${isEnc ? 'encaminhar' : 'nao-prioritario'}">
            <div class="status-icon">${isEnc ? icons.alert : icons.checkCircle}</div>
            <div class="status-content">
              <h3>${isEnc ? 'Encaminhar para Teste Genético' : 'Paciente Não Prioritário'}</h3>
              <p>${isEnc
                ? `Score de ${patient.score.toFixed(2)} está acima do limiar de ${threshold} para pacientes do sexo ${sexLabel(patient.sex).toLowerCase()}. Recomenda-se encaminhamento para teste genético confirmatório (PCR / Southern Blot).`
                : `Score de ${patient.score.toFixed(2)} está abaixo do limiar de ${threshold} para pacientes do sexo ${sexLabel(patient.sex).toLowerCase()}. Paciente não é prioritário para investigação genética neste momento. Continue o acompanhamento clínico regular.`
              }</p>
            </div>
          </div>

          <div class="result-actions">
            <button class="btn btn-primary" id="btn-save-res">
              ${icons.save} Salvar Avaliação
            </button>
            <button class="btn btn-secondary" onclick="navigate('cadastro')">
              ${icons.refresh} Nova Avaliação
            </button>
            <button class="btn btn-ghost" onclick="navigate('dashboard')">
              Voltar ao Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  // animação do contador de score
  const scoreEl = el.querySelector('#score-display');
  const barEl   = el.querySelector('#score-bar');
  let current   = 0;
  const target  = patient.score;
  const steps   = 60;
  let i = 0;
  const interval = setInterval(() => {
    i++;
    current = target * (i / steps);
    scoreEl.textContent = current.toFixed(2);
    barEl.style.width   = (current * 100) + '%';
    if (i >= steps) clearInterval(interval);
  }, 14);

  el.querySelector('#btn-save-res').addEventListener('click', () => {
    showToast('Avaliação salva com sucesso!', 'success');
    setTimeout(() => navigate('historico'), 800);
  });
});

// pagina de historico
registerPage('historico', (el) => {
  let filtered = [...SXF.patients];

  function renderTable() {
    const query  = el.querySelector('#search-input')?.value.toLowerCase() || '';
    const sexF   = el.querySelector('#filter-sex')?.value  || '';
    const recF   = el.querySelector('#filter-rec')?.value  || '';

    filtered = SXF.patients.filter(p => {
      const matchName = p.name.toLowerCase().includes(query);
      const matchSex  = !sexF || p.sex === sexF;
      const matchRec  = !recF || p.rec === recF;
      return matchName && matchSex && matchRec;
    });

    const tbody = el.querySelector('#hist-tbody');
    if (!tbody) return;

    tbody.innerHTML = filtered.length === 0
      ? `<tr><td colspan="6" style="text-align:center;padding:48px;color:var(--text-muted)">Nenhum resultado encontrado.</td></tr>`
      : filtered.map(p => `
        <tr>
          <td class="name">${p.name}</td>
          <td>${p.date || '—'}</td>
          <td>${sexLabel(p.sex)}</td>
          <td class="score">${p.score !== null ? p.score.toFixed(2) : '—'}</td>
          <td>${p.score !== null ? recBadge(p.rec) : '—'}</td>
        </tr>
      `).join('');
  }

  el.innerHTML = `
    <div class="page-header">
      <div class="page-title">Histórico de Avaliações</div>
      <div class="page-subtitle">Visualize e filtre todas as avaliações realizadas</div>
    </div>
    <div class="page-body">
      <div class="table-card">
        <div class="table-header">
          <div class="filter-row">
            <div class="search-wrap">
              ${icons.search}
              <input id="search-input" class="form-input search-input" placeholder="Buscar por nome do paciente...">
            </div>
            <select class="filter-select" id="filter-sex">
              <option value="">Todos os sexos</option>
              <option value="M">Masculino</option>
              <option value="F">Feminino</option>
            </select>
            <select class="filter-select" id="filter-rec">
              <option value="">Todas recomendações</option>
              <option value="encaminhar">Encaminhar</option>
              <option value="nao-prio">Não prioritário</option>
            </select>
          </div>
          <button class="btn btn-primary btn-sm" onclick="navigate('cadastro')">
            ${icons.userPlus} Novo Paciente
          </button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nome do Paciente</th>
                <th>Data da Avaliação</th>
                <th>Sexo</th>
                <th>Score</th>
                <th>Recomendação</th>
              </tr>
            </thead>
            <tbody id="hist-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  renderTable();

  el.querySelector('#search-input').addEventListener('input', renderTable);
  el.querySelector('#filter-sex').addEventListener('change', renderTable);
  el.querySelector('#filter-rec').addEventListener('change', renderTable);
});

// pagina de relatorios
registerPage('relatorios', (el) => {
  const total   = SXF.patients.length;
  const encamin = SXF.patients.filter(p => p.rec === 'encaminhar').length;
  const naoPrio = SXF.patients.filter(p => p.rec === 'nao-prio').length;
  const encPct  = total ? Math.round((encamin / total) * 100) : 0;
  const femEnc  = SXF.patients.filter(p => p.sex === 'F' && p.rec === 'encaminhar').length;
  const mascEnc = SXF.patients.filter(p => p.sex === 'M' && p.rec === 'encaminhar').length;
  const avgScore = total ? (SXF.patients.reduce((s, p) => s + (p.score || 0), 0) / total).toFixed(2) : '—';

  el.innerHTML = `
    <div class="page-header">
      <div class="page-title">Relatórios</div>
      <div class="page-subtitle">Estatísticas e análises do sistema de triagem</div>
    </div>
    <div class="page-body">
      <div style="background:var(--warning-bg);border:1px solid var(--warning-light);border-radius:var(--radius);padding:16px 20px;margin-bottom:28px;display:flex;gap:12px;align-items:center">
        <span style="color:var(--warning)">${icons.alert}</span>
        <span style="font-size:.875rem;color:var(--warning)">página de relatórios, ainda não definida 100%.</span>
      </div>

      <div class="stats-grid" style="margin-bottom:24px">
        <div class="stat-card">
          <div class="stat-icon blue">${icons.barChart}</div>
          <div class="stat-label">Score Médio</div>
          <div class="stat-value" style="font-size:1.6rem;font-family:var(--mono)">${avgScore}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">${icons.arrow}</div>
          <div class="stat-label">Taxa de Encaminhamento</div>
          <div class="stat-value">${encPct}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">${icons.users}</div>
          <div class="stat-label">Total Avaliados</div>
          <div class="stat-value">${total}</div>
        </div>
      </div>

      <div class="card" style="margin-bottom:20px">
        <div class="card-body">
          <div style="font-weight:600;margin-bottom:20px;font-size:.95rem">Distribuição de Recomendações</div>
          <div style="display:flex;gap:32px;align-items:center">
            <div style="flex:1">
              <div style="display:flex;justify-content:space-between;font-size:.8rem;color:var(--text-muted);margin-bottom:6px">
                <span>Encaminhar</span><span>${encamin} (${encPct}%)</span>
              </div>
              <div style="height:10px;background:var(--surface-2);border-radius:99px;overflow:hidden;margin-bottom:14px">
                <div style="height:100%;width:${encPct}%;background:#F97316;border-radius:99px;transition:width 1s cubic-bezier(.34,1.56,.64,1)" class="bar-anim"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:.8rem;color:var(--text-muted);margin-bottom:6px">
                <span>Não prioritário</span><span>${naoPrio} (${100-encPct}%)</span>
              </div>
              <div style="height:10px;background:var(--surface-2);border-radius:99px;overflow:hidden">
                <div style="height:100%;width:${100-encPct}%;background:var(--success);border-radius:99px;transition:width 1s cubic-bezier(.34,1.56,.64,1)" class="bar-anim"></div>
              </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:12px;min-width:160px">
              <div style="display:flex;justify-content:space-between;font-size:.85rem">
                <span style="color:var(--text-muted)">Masc. encaminhar</span>
                <strong>${mascEnc}</strong>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:.85rem">
                <span style="color:var(--text-muted)">Fem. encaminhar</span>
                <strong>${femEnc}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
});

// pagina de login
function renderLogin() {
  document.body.innerHTML = `
    <div class="login-page">
      <div class="login-card fade-in">
        <div class="login-brand">
          <div class="login-logo">${icons.pulse}</div>
          <div class="login-title">Sistema de Triagem Clínica</div>
          <div class="login-subtitle">Síndrome do X Frágil</div>
        </div>
        <div class="login-form">
          <div class="form-group">
            <label class="form-label">E-mail</label>
            <input id="login-email" class="form-input" type="email" placeholder="seu@email.com">
            <div class="field-error" id="err-email">Informe um e-mail válido</div>
          </div>
          <div class="form-group">
            <label class="form-label">Senha</label>
            <input id="login-senha" class="form-input" type="password" placeholder="••••••••">
            <div class="field-error" id="err-senha">Senha obrigatória</div>
          </div>
          <button class="btn btn-primary btn-login" id="btn-login">Entrar</button>
          <a class="forgot-link">Esqueci minha senha</a>
        </div>
      </div>
      <div class="toast-container" id="toast-container"></div>
    </div>
  `;

  document.getElementById('btn-login').addEventListener('click', () => {
    const email = document.getElementById('login-email').value.trim();
    const senha = document.getElementById('login-senha').value;
    let valid = true;

    if (!email || !email.includes('@')) {
      document.getElementById('login-email').classList.add('error');
      document.getElementById('err-email').classList.add('show');
      valid = false;
    } else {
      document.getElementById('login-email').classList.remove('error');
      document.getElementById('err-email').classList.remove('show');
    }
    if (!senha) {
      document.getElementById('login-senha').classList.add('error');
      document.getElementById('err-senha').classList.add('show');
      valid = false;
    } else {
      document.getElementById('login-senha').classList.remove('error');
      document.getElementById('err-senha').classList.remove('show');
    }
    if (!valid) return;

    const btn = document.getElementById('btn-login');
    btn.textContent = 'Entrando…';
    btn.disabled = true;

    setTimeout(() => {
      buildShell();
      navigate('dashboard');
    }, 900);
  });

  // clicar no enter
  document.addEventListener('keydown', function handler(e) {
    if (e.key === 'Enter') {
      document.getElementById('btn-login')?.click();
      document.removeEventListener('keydown', handler);
    }
  });
}

// iniciar
document.addEventListener('DOMContentLoaded', () => {
  renderLogin();
});
