import { state } from "../core/state.js";
import { mount, setHtml, template } from "../ui/dom.js";
import { emptyState, recBadge, sexLabel } from "../ui/formatters.js";

export function renderAssessmentsPage(el) {
  const fragment = template("tpl-assessments");
  setHtml(fragment, "assessments-table", assessmentsTable());
  mount(el, fragment);
  bindAssessmentExport();
}

function assessmentsTable() {
  if (!state.assessments.length) {
    return emptyState("Nenhuma avaliação registrada ainda.");
  }

  return `<table class="table table-hover align-middle">
    <thead><tr><th>ID</th><th>Paciente</th><th>Sexo</th><th>Score</th><th>Limiar</th><th>Resultado</th><th>Data</th></tr></thead>
    <tbody>${state.assessments.map(assessmentRow).join("")}</tbody>
  </table>`;
}

function assessmentRow(assessment) {
  return `<tr>
    <td>#${assessment.id}</td>
    <td class="name">${assessment.patientName}</td>
    <td>${sexLabel(assessment.sex)}</td>
    <td class="score">${assessment.score}</td>
    <td class="score">${assessment.threshold}</td>
    <td>${recBadge(assessment.rec)}</td>
    <td>${assessment.date}</td>
  </tr>`;
}

function bindAssessmentExport() {
  document.getElementById("export-assessments").addEventListener("click", () => {
    window.location.href = "/api/avaliacoes/export";
  });
}
