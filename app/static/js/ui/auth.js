import { state } from "../core/state.js";
import { navigate } from "../core/router.js";
import { api } from "../services/api.js";
import { appRoot, mount, showToast, template } from "./dom.js";
import { buildShell } from "./shell.js";
import { bindThemeToggle } from "./theme.js";

export function renderLogin() {
  const fragment = template("tpl-login");
  mount(appRoot(), fragment);
  bindThemeToggle();
  bindAuthTabs();
  bindAuthForm();
}

function bindAuthTabs() {
  let mode = "login";
  const submitButton = document.getElementById("btn-auth");
  const registerFields = document.querySelector(".register-only");

  document.querySelectorAll(".auth-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      mode = tab.dataset.mode;
      document.querySelectorAll(".auth-tab").forEach((el) => {
        el.classList.toggle("active", el === tab);
      });

      registerFields.classList.toggle("hidden", mode !== "register");
      submitButton.textContent = mode === "register" ? "Cadastrar" : "Entrar";
      document.getElementById("auth-form").dataset.mode = mode;
    });
  });
}

function bindAuthForm() {
  document.getElementById("auth-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;
    const mode = form.dataset.mode || "login";
    const button = document.getElementById("btn-auth");

    button.disabled = true;
    button.textContent = mode === "register" ? "Cadastrando..." : "Entrando...";

    try {
      state.currentUser = await api(mode === "register" ? "/api/auth/register" : "/api/auth/login", {
        method: "POST",
        body: JSON.stringify(authPayload()),
      });

      buildShell();
      navigate("dashboard");
    } catch (err) {
      showToast(err.message, "error");
      button.disabled = false;
      button.textContent = mode === "register" ? "Cadastrar" : "Entrar";
    }
  });
}

function authPayload() {
  return {
    email: document.getElementById("auth-email").value,
    senha: document.getElementById("auth-password").value,
    nome: document.getElementById("auth-name").value,
    especialidade: document.getElementById("auth-specialty").value,
  };
}
