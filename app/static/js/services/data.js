import { state } from "../core/state.js";
import { api } from "./api.js";

export async function loadPatients() {
  state.patients = await api("/api/pacientes");
}

export async function loadSymptoms() {
  state.symptoms = await api("/api/sintomas");
}

export async function loadAssessments() {
  state.assessments = await api("/api/avaliacoes");
}

export async function loadReports() {
  state.reports = await api("/api/relatorios");
}
