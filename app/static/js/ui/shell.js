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
    el.addEventListener("click", () => navigate(el.dataset.page));
  });

  bindThemeToggle();

  document.getElementById("btn-logout").addEventListener("click", async () => {
    await api("/api/auth/logout", { method: "POST", body: "{}" });
    state.currentUser = null;
    authRenderer();
  });
}
