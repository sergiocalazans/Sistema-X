import { icons } from "./core/icons.js";

const THEME_KEY = "sxf-theme";

function currentTheme() {
  return document.documentElement.dataset.theme || "light";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.bsTheme = theme;
}

function initTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  const preferred = window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  applyTheme(stored === "dark" || stored === "light" ? stored : preferred);
  syncThemeButtons();
}

function syncThemeButtons() {
  const dark = currentTheme() === "dark";
  document.querySelectorAll(".theme-toggle").forEach((button) => {
    button.setAttribute("aria-label", dark ? "Ativar modo claro" : "Ativar modo escuro");
    button.setAttribute("title", dark ? "Ativar modo claro" : "Ativar modo escuro");
    button.querySelector("[data-theme-label]").textContent = dark ? "Modo claro" : "Modo escuro";
  });
}

function bindTheme() {
  document.querySelectorAll(".theme-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const nextTheme = currentTheme() === "dark" ? "light" : "dark";
      localStorage.setItem(THEME_KEY, nextTheme);
      applyTheme(nextTheme);
      syncThemeButtons();
      renderCharts();
    });
  });
}

function hydrateIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    el.innerHTML = icons[el.dataset.icon] || "";
  });
}

function bindShell() {
  const sidebar = document.querySelector(".sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");
  document.getElementById("btn-mobile-menu")?.addEventListener("click", () => {
    sidebar?.classList.add("open");
    backdrop?.classList.add("show");
  });
  backdrop?.addEventListener("click", () => {
    sidebar?.classList.remove("open");
    backdrop.classList.remove("show");
  });
}

function bindSymptoms() {
  document.querySelectorAll(".symptom-input").forEach((input) => {
    input.addEventListener("change", () => {
      input.closest(".symptom-item").classList.toggle("checked", input.checked);
    });
  });
}

function themeColors() {
  const styles = getComputedStyle(document.documentElement);
  return {
    surface: styles.getPropertyValue("--surface").trim(),
    textPrimary: styles.getPropertyValue("--text-primary").trim(),
    textMuted: styles.getPropertyValue("--text-muted").trim(),
    border: styles.getPropertyValue("--border-light").trim(),
  };
}

function renderCharts() {
  if (!window.Plotly || !window.SXF_CHARTS) return;

  const map = {
    "chart-recommendations": window.SXF_CHARTS.recommendations,
    "chart-score-sex": window.SXF_CHARTS.scoreBySex,
    "chart-monthly": window.SXF_CHARTS.assessmentsByMonth,
    "chart-symptoms": window.SXF_CHARTS.topSymptoms,
  };

  Object.entries(map).forEach(([id, figure]) => {
    const el = document.getElementById(id);
    if (!el || !figure) return;
    window.Plotly.react(el, figure.data, themedLayout(figure.layout || {}), {
      responsive: true,
      displayModeBar: false,
    });
  });
}

function themedLayout(layout) {
  const colors = themeColors();
  return {
    ...layout,
    paper_bgcolor: colors.surface,
    plot_bgcolor: colors.surface,
    font: { ...(layout.font || {}), color: colors.textPrimary },
  };
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  hydrateIcons();
  bindTheme();
  bindShell();
  bindSymptoms();
  renderCharts();
});
