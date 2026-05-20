import { icons } from "../core/icons.js";

export function appRoot() {
  return document.getElementById("app");
}

export function template(id) {
  const tpl = document.getElementById(id);
  if (!tpl) {
    throw new Error(`Template não encontrado: ${id}`);
  }

  const fragment = tpl.content.cloneNode(true);
  hydrateIcons(fragment);
  return fragment;
}

export function mount(target, fragment) {
  target.replaceChildren(fragment);
}

export function hydrateIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    el.innerHTML = icons[el.dataset.icon] || "";
  });
}

export function slot(root, name) {
  return root.querySelector(`[data-slot="${name}"]`);
}

export function setText(root, name, value) {
  const el = slot(root, name);
  if (el) {
    el.textContent = value ?? "";
  }
}

export function setHtml(root, name, value) {
  const el = slot(root, name);
  if (el) {
    el.innerHTML = value ?? "";
  }
}

export function showToast(message, type = "success") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}
