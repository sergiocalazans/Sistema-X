import { state } from "../core/state.js";
import { navigate } from "../core/router.js";
import { api } from "../services/api.js";
import { appRoot, mount, setText, template } from "./dom.js";
import { bindThemeToggle } from "./theme.js";

let authRenderer = () => {};

export function setAuthRenderer(renderFn) {
  authRenderer = renderFn;
}

export function buildShell() {
  const fragment = template("tpl-shell");
  setText(fragment, "user-name", state.currentUser?.nome || "Sistema Clínico");
  mount(appRoot(), fragment);

  document.querySelectorAll(".nav-item[data-page]").forEach((el) => {
    el.addEventListener("click", () => {
      closeMobileMenu();
      navigate(el.dataset.page);
    });
  });

  bindMobileMenu();
  bindThemeToggle();

  document.getElementById("btn-logout").addEventListener("click", async () => {
    await api("/api/auth/logout", { method: "POST", body: "{}" });
    state.currentUser = null;
    authRenderer();
  });
}

function bindMobileMenu() {
  document.getElementById("btn-mobile-menu")?.addEventListener("click", () => {
    document.querySelector(".sidebar")?.classList.add("open");
    document.querySelector(".sidebar-backdrop")?.classList.add("show");
  });

  document.getElementById("sidebar-backdrop")?.addEventListener("click", closeMobileMenu);
  window.addEventListener("resize", () => {
    if (window.matchMedia("(min-width: 1181px)").matches) {
      closeMobileMenu();
    }
  });
}

function closeMobileMenu() {
  document.querySelector(".sidebar")?.classList.remove("open");
  document.querySelector(".sidebar-backdrop")?.classList.remove("show");
}
