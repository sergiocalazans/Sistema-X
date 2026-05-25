import { navigate } from "../core/router.js";
import { state } from "../core/state.js";
import { api } from "../services/api.js";
import { mount, setHtml, setText, showToast, template } from "../ui/dom.js";
import { emptyState, sexLabel } from "../ui/formatters.js";

export function renderPatientsPage(el) {
  state.editingPatientId = null;

  const fragment = template("tpl-patients");
  setHtml(fragment, "patients-table", patientsTable());

  mount(el, fragment);
  bindPatientListActions();
}

export function renderPatientFormPage(el) {
  const fragment = template("tpl-patient-form");
  const patient = state.patients.find((item) => item.id === state.editingPatientId);

  if (patient) {
    setText(fragment, "form-title", "Editar Paciente");
    fillPatientForm(fragment, patient);
  }

  mount(el, fragment);
  bindPatientForm();
}

function patientsTable() {
  if (!state.patients.length) {
    return emptyState("Cadastre o primeiro paciente para iniciar a triagem.");
  }

  return `<table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Nome</th>
        <th>CPF</th>
        <th>E-mail</th>
        <th>Telefone</th>
        <th>Sexo</th>
        <th>Idade</th>
        <th>Ultimo score</th>
        <th></th>
      </tr>
    </thead>
    <tbody>${state.patients.map(patientRow).join("")}</tbody>
  </table>`;
}

function patientRow(patient) {
  return `<tr>
    <td>#${patient.id}</td>
    <td class="name">${patient.name}</td>
    <td>${patient.cpf || "-"}</td>
    <td>${patient.email || "-"}</td>
    <td>${patient.telefone || "-"}</td>
    <td>${sexLabel(patient.sex)}</td>
    <td>${patient.age}</td>
    <td class="score">${patient.score}</td>
    <td><button class="btn btn-secondary btn-sm edit-patient" data-id="${patient.id}">Editar</button></td>
  </tr>`;
}

function bindPatientListActions() {
  document.getElementById("new-patient").addEventListener("click", () => {
    state.editingPatientId = null;
    navigate("paciente-cadastro");
  });

  document.querySelectorAll(".edit-patient").forEach((button) => {
    button.addEventListener("click", () => {
      state.editingPatientId = Number(button.dataset.id);
      navigate("paciente-cadastro");
    });
  });

  document.getElementById("export-patients").addEventListener("click", () => {
    window.location.href = "/api/pacientes/export";
  });
}

function bindPatientForm() {
  document.getElementById("back-to-patients").addEventListener("click", () => {
    navigate("historico");
  });

  document.getElementById("patient-clear").addEventListener("click", clearPatientForm);

  document.getElementById("patient-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    await savePatient();
  });
}

function fillPatientForm(root, patient) {
  root.querySelector("#patient-id").value = patient.id;
  root.querySelector("#patient-name").value = patient.name;
  root.querySelector("#patient-cpf").value = patient.cpf || "";
  root.querySelector("#patient-email").value = patient.email || "";
  root.querySelector("#patient-phone").value = patient.telefone || "";
  root.querySelector("#patient-birth").value = patient.birthDate;
  root.querySelector("#patient-sex").value = patient.sexo;
}

function clearPatientForm() {
  document.getElementById("patient-form").reset();
  document.getElementById("patient-id").value = "";
  state.editingPatientId = null;
}

async function savePatient() {
  const id = document.getElementById("patient-id").value;
  const payload = {
    nome: document.getElementById("patient-name").value,
    cpf: document.getElementById("patient-cpf").value,
    email: document.getElementById("patient-email").value,
    telefone: document.getElementById("patient-phone").value,
    data_nascimento: document.getElementById("patient-birth").value,
    sexo: document.getElementById("patient-sex").value,
  };

  await api(id ? `/api/pacientes/${id}` : "/api/pacientes", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });

  showToast(id ? "Paciente atualizado." : "Paciente cadastrado.");
  state.editingPatientId = null;
  await navigate("historico");
}
