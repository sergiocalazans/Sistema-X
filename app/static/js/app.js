import { state } from "./core/state.js";
import { navigate, registerPage, setUnauthenticatedRenderer } from "./core/router.js";
import { api } from "./services/api.js";
import { renderLogin } from "./ui/auth.js";
import { buildShell, setAuthRenderer } from "./ui/shell.js";

import { renderAssessmentsPage } from "./pages/assessments.js";
import { renderDashboardPage } from "./pages/dashboard.js";
import { renderPatientsPage } from "./pages/patients.js";
import { renderReportsPage } from "./pages/reports.js";
import { renderTriagePage } from "./pages/triage.js";

registerPage("dashboard", renderDashboardPage);
registerPage("historico", renderPatientsPage);
registerPage("triagem", renderTriagePage);
registerPage("avaliacoes", renderAssessmentsPage);
registerPage("relatorios", renderReportsPage);

setAuthRenderer(renderLogin);
setUnauthenticatedRenderer(renderLogin);

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const user = await api("/api/auth/me");
    if (!user.authenticated) {
      renderLogin();
      return;
    }

    state.currentUser = user;
    buildShell();
    navigate("dashboard");
  } catch {
    renderLogin();
  }
});
