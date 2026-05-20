import { state } from "../core/state.js";
import { mount, setHtml, setText, template } from "../ui/dom.js";
import { emptyState } from "../ui/formatters.js";

export function renderReportsPage(el) {
  const fragment = template("tpl-reports");
  const reports = state.reports || emptyReports();
  const indicators = reports.indicators;

  setText(fragment, "total-assessments", indicators.totalAssessments);
  setText(fragment, "referral-rate", `${indicators.referralRate}%`);
  setText(fragment, "average-score", indicators.averageScore);
  setText(fragment, "most-frequent-symptom", indicators.mostFrequentSymptom);
  setHtml(fragment, "by-sex-table", bySexTable(reports.tables.bySex));
  setHtml(fragment, "top-symptoms-table", topSymptomsTable(reports.tables.topSymptoms));

  mount(el, fragment);
  renderCharts(reports.charts);
}

function renderCharts(charts) {
  renderPlot("chart-recommendations", charts.recommendations);
  renderPlot("chart-score-sex", charts.scoreBySex);
  renderPlot("chart-monthly", charts.assessmentsByMonth);
  renderPlot("chart-symptoms", charts.topSymptoms);
}

function renderPlot(elementId, figure) {
  const el = document.getElementById(elementId);
  if (!el || !figure) return;

  if (!window.Plotly) {
    el.innerHTML = `<div class="empty-state"><p>Plotly não carregou. Verifique a conexão com a internet.</p></div>`;
    return;
  }

  window.Plotly.react(el, figure.data, figure.layout, {
    responsive: true,
    displayModeBar: false,
  });
}

function bySexTable(rows) {
  if (!rows.length) {
    return emptyState("Sem avaliações para agrupar por sexo.");
  }

  return `<table>
    <thead>
      <tr>
        <th>Sexo</th>
        <th>Total</th>
        <th>Encaminhamentos</th>
        <th>Taxa</th>
        <th>Score médio</th>
        <th>Idade média</th>
      </tr>
    </thead>
    <tbody>
      ${rows.map((row) => `
        <tr>
          <td class="name">${row.sex}</td>
          <td>${row.total}</td>
          <td>${row.referrals}</td>
          <td>${row.referralRate}%</td>
          <td class="score">${row.averageScore}</td>
          <td>${row.averageAge}</td>
        </tr>
      `).join("")}
    </tbody>
  </table>`;
}

function topSymptomsTable(rows) {
  if (!rows.length) {
    return emptyState("Sem sintomas marcados nas avaliações.");
  }

  return `<table>
    <thead>
      <tr>
        <th>Sintoma</th>
        <th>Categoria</th>
        <th>Ocorrências</th>
      </tr>
    </thead>
    <tbody>
      ${rows.map((row) => `
        <tr>
          <td class="name">${row.symptom}</td>
          <td>${row.category}</td>
          <td class="score">${row.count}</td>
        </tr>
      `).join("")}
    </tbody>
  </table>`;
}

function emptyReports() {
  return {
    indicators: {
      totalAssessments: 0,
      referralRate: 0,
      averageScore: 0,
      mostFrequentSymptom: "Sem dados",
    },
    tables: {
      bySex: [],
      topSymptoms: [],
    },
    charts: {},
  };
}
