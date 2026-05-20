import { icons } from "../core/icons.js";
import { state } from "../core/state.js";
import { api } from "../services/api.js";
import { mount, setHtml, template } from "../ui/dom.js";
import { emptyState, sexLabel } from "../ui/formatters.js";
import { renderResult } from "./result.js";

export function renderTriagePage(el) {
  const fragment = template("tpl-triage");
  const patientSelect = fragment.querySelector("#assessment-patient");

  patientSelect.innerHTML += patientOptions();
  setHtml(fragment, "symptoms", symptomsChecklist());

  mount(el, fragment);
  bindAssessmentForm(el);
}

function patientOptions() {
  return state.patients
    .map((p) => `<option value="${p.id}">${p.name} - ${sexLabel(p.sex)}, ${p.age} anos</option>`)
    .join("");
}

function symptomsChecklist() {
  if (!state.symptoms.length) {
    return emptyState("Nenhum sintoma cadastrado no banco.");
  }

  return `<div class="symptoms-grid">
    ${state.symptoms.map(symptomItem).join("")}
  </div>`;
}

function symptomItem(symptom) {
  return `<label class="symptom-item">
    <input type="checkbox" class="symptom-input" value="${symptom.id}">
    <span class="symptom-checkbox">${icons.check}</span>
    <span><span class="symptom-name">${symptom.description}</span><small>${symptom.category}</small></span>
  </label>`;
}

function bindAssessmentForm(el) {
  document.querySelectorAll(".symptom-input").forEach((input) => {
    input.addEventListener("change", () => {
      input.closest(".symptom-item").classList.toggle("checked", input.checked);
    });
  });

  document.getElementById("assessment-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const result = await api("/api/avaliacoes", {
      method: "POST",
      body: JSON.stringify(assessmentPayload()),
    });
    renderResult(el, result);
  });
}

function assessmentPayload() {
  return {
    paciente_id: Number(document.getElementById("assessment-patient").value),
    sintomas: [...document.querySelectorAll(".symptom-input:checked")].map((input) => Number(input.value)),
    observacao: document.getElementById("assessment-note").value,
  };
}
