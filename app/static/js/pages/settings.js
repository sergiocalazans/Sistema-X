import { state } from "../core/state.js";
import { api } from "../services/api.js";
import { mount, showToast, template } from "../ui/dom.js";

export function renderSettingsPage(el) {
  const fragment = template("tpl-settings");
  fillProfileForm(fragment);
  mount(el, fragment);
  bindProfileForm();
  bindPasswordForm();
}

function fillProfileForm(root) {
  root.querySelector("#settings-name").value = state.currentUser?.nome || "";
  root.querySelector("#settings-email").value = state.currentUser?.email || "";
  root.querySelector("#settings-specialty").value = state.currentUser?.especialidade || "";
}

function bindProfileForm() {
  document.getElementById("profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const user = await api("/api/auth/profile", {
      method: "PUT",
      body: JSON.stringify({
        nome: document.getElementById("settings-name").value,
        email: document.getElementById("settings-email").value,
        especialidade: document.getElementById("settings-specialty").value,
      }),
    });

    state.currentUser = { ...state.currentUser, ...user };
    const nameSlot = document.querySelector('[data-slot="user-name"]');
    if (nameSlot) {
      nameSlot.textContent = user.nome;
    }
    showToast("Login atualizado.");
  });
}

function bindPasswordForm() {
  document.getElementById("password-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    await api("/api/auth/password", {
      method: "PUT",
      body: JSON.stringify({
        senha_atual: document.getElementById("current-password").value,
        nova_senha: document.getElementById("new-password").value,
        confirmar_senha: document.getElementById("confirm-password").value,
      }),
    });

    event.currentTarget.reset();
    showToast("Senha alterada.");
  });
}
