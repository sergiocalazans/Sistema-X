import { state } from "../core/state.js";
import { mount, setHtml, setText, template } from "../ui/dom.js";
import { emptyState, recBadge, sexLabel } from "../ui/formatters.js";

export function renderDashboardPage(el) {
  const fragment = template("tpl-dashboard");
  const referrals = state.assessments.filter(
    (a) => a.rec === "encaminhar",
  ).length;

  setText(fragment, "total-patients", state.patients.length);
  setText(fragment, "total-assessments", state.assessments.length);
  setText(fragment, "total-referrals", referrals);
  setHtml(fragment, "recent-assessments", recentAssessmentsTable());

  mount(el, fragment);
}

function recentAssessmentsTable() {
  if (!state.assessments.length) {
    return emptyState("Nenhuma avaliação registrada ainda.");
  }

  return `<table class="table table-hover align-middle">
    <thead><tr><th>Paciente</th><th>Sexo</th><th>Score</th><th>Resultado</th><th>Data</th></tr></thead>
    <tbody>${state.assessments.slice(0, 6).map(recentAssessmentRow).join("")}</tbody>
  </table>`;
}

function recentAssessmentRow(assessment) {
  return `<tr>
    <td class="name">${assessment.patientName}</td>
    <td>${sexLabel(assessment.sex)}</td>
    <td class="score">${assessment.score}</td>
    <td>${recBadge(assessment.rec)}</td>
    <td>${assessment.date}</td>
  </tr>`;
}
