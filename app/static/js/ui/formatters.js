import { icons } from "../core/icons.js";

export function sexLabel(sex) {
  return sex === "M" ? "Masculino" : "Feminino";
}

export function recBadge(recommendation) {
  return recommendation === "encaminhar"
    ? `<span class="badge encaminhar">Encaminhar</span>`
    : `<span class="badge nao-prio">Nao prioritario</span>`;
}

export function emptyState(text) {
  return `<div class="empty-state">${icons.clipboard}<p>${text}</p></div>`;
}
