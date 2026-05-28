import { icons } from "../core/icons.js";

export function sexLabel(sex) {
  return sex === "M" ? "Masculino" : "Feminino";
}

export function recBadge(recommendation) {
  return recommendation === "encaminhar"
    ? `<span class="badge rounded-pill encaminhar">Encaminhar</span>`
    : `<span class="badge rounded-pill nao-prio">Não prioritário</span>`;
}

export function emptyState(text) {
  return `<div class="empty-state">${icons.clipboard}<p>${text}</p></div>`;
}
