const THEME_KEY = "sxf-theme";
const DARK_QUERY = "(prefers-color-scheme: dark)";

export function initTheme() {
  applyTheme(getStoredTheme() || getPreferredTheme());
}

export function bindThemeToggle() {
  const button = document.getElementById("btn-theme-toggle");
  if (!button) return;

  syncThemeButton(button);
  button.addEventListener("click", () => {
    const nextTheme = currentTheme() === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_KEY, nextTheme);
    applyTheme(nextTheme);
    syncThemeButton(button);
    window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: nextTheme } }));
  });
}

export function currentTheme() {
  return document.documentElement.dataset.theme || "light";
}

export function themeColors() {
  const styles = getComputedStyle(document.documentElement);
  return {
    surface: styles.getPropertyValue("--surface").trim(),
    textPrimary: styles.getPropertyValue("--text-primary").trim(),
    textMuted: styles.getPropertyValue("--text-muted").trim(),
    border: styles.getPropertyValue("--border-light").trim(),
  };
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
}

function getStoredTheme() {
  const theme = localStorage.getItem(THEME_KEY);
  return theme === "dark" || theme === "light" ? theme : null;
}

function getPreferredTheme() {
  return window.matchMedia?.(DARK_QUERY).matches ? "dark" : "light";
}

function syncThemeButton(button) {
  const dark = currentTheme() === "dark";
  button.setAttribute("aria-label", dark ? "Ativar modo claro" : "Ativar modo escuro");
  button.setAttribute("title", dark ? "Ativar modo claro" : "Ativar modo escuro");
  button.querySelector("[data-theme-label]").textContent = dark ? "Modo claro" : "Modo escuro";
}
