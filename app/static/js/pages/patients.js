import { state } from "../core/state.js";
import { navigate } from "../core/router.js";
import { api } from "../services/api.js";
import { mount, setHtml, showToast, template } from "../ui/dom.js";
import { emptyState, sexLabel } from "../ui/formatters.js";

export function renderPatientsPage(el) {
  const fragment = template("tpl-patients");
  setHtml(fragment, "patients-table", patientsTable());

  mount(el, fragment);
  bindPatientForm();
}

function patientsTable() {
  if (!state.patients.length) {
    return emptyState("Cadastre o primeiro paciente para iniciar a triagem.");
  }

  return `<table>
    <thead><tr><th>ID</th><th>Nome</th><th>Sexo</th><th>Idade</th><th>Ultimo score</th><th></th></tr></thead>
    <tbody>${state.patients.map(patientRow).join("")}</tbody>
  </table>`;
}

function patientRow(patient) {
  return `<tr>
    <td>#${patient.id}</td>
    <td class="name">${patient.name}</td>
    <td>${sexLabel(patient.sex)}</td>
    <td>${patient.age}</td>
    <td class="score">${patient.score}</td>
    <td><button class="btn btn-secondary btn-sm edit-patient" data-id="${patient.id}">Editar</button></td>
  </tr>`;
}

function bindPatientForm() {
  const form = document.getElementById("patient-form");
  document.getElementById("patient-clear").addEventListener("click", clearPatientForm);

  document.querySelectorAll(".edit-patient").forEach((button) => {
    button.addEventListener("click", () => fillPatientForm(Number(button.dataset.id)));
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await savePatient();
  });
}

function clearPatientForm() {
  document.getElementById("patient-form").reset();
  document.getElementById("patient-id").value = "";
  document.getElementById("patient-form-title").textContent = "Cadastrar paciente";
}

function fillPatientForm(patientId) {
  const patient = state.patients.find((p) => p.id === patientId);
  if (!patient) return;

  document.getElementById("patient-id").value = patient.id;
  document.getElementById("patient-name").value = patient.name;
  document.getElementById("patient-birth").value = patient.birthDate;
  document.getElementById("patient-sex").value = patient.sexo;
  document.getElementById("patient-form-title").textContent = "Editar paciente";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function savePatient() {
  const id = document.getElementById("patient-id").value;
  const payload = {
    nome: document.getElementById("patient-name").value,
    data_nascimento: document.getElementById("patient-birth").value,
    sexo: document.getElementById("patient-sex").value,
  };

  await api(id ? `/api/pacientes/${id}` : "/api/pacientes", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });

  showToast(id ? "Paciente atualizado." : "Paciente cadastrado.");
  await navigate("historico");
}
