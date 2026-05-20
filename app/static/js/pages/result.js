import { navigate } from "../core/router.js";
import { mount, setText, slot, template } from "../ui/dom.js";

export function renderResult(el, result) {
  const fragment = template("tpl-result");
  const shouldRefer = result.rec === "encaminhar";
  const statusBox = slot(fragment, "status-box");
  const scoreBar = slot(fragment, "score-bar");

  setText(fragment, "patient-name", result.patientName);
  setText(fragment, "assessment-date", `Avaliação realizada em ${result.date}`);
  setText(fragment, "score", result.score);
  setText(fragment, "threshold", result.threshold);
  setText(fragment, "status-title", statusTitle(shouldRefer));

  statusBox.classList.add(shouldRefer ? "encaminhar" : "nao-prioritario");
  scoreBar.style.width = `${Math.min(result.score * 100, 100)}%`;

  mount(el, fragment);
  document
    .getElementById("new-assessment")
    .addEventListener("click", () => navigate("triagem"));
  document
    .getElementById("go-history")
    .addEventListener("click", () => navigate("avaliacoes"));
}

function statusTitle(shouldRefer) {
  return shouldRefer
    ? "Encaminhar para teste genético confirmatório"
    : "Não prioritário para investigação neste momento";
}
