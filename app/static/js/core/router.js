import { state } from "./state.js";
import { loadAssessments, loadPatients, loadSymptoms } from "../services/data.js";
import { showToast } from "../ui/dom.js";

const pages = {};
let unauthenticatedRenderer = () => {};

export function registerPage(id, renderFn) {
  pages[id] = renderFn;
}

export function setUnauthenticatedRenderer(renderFn) {
  unauthenticatedRenderer = renderFn;
}

export async function navigate(pageId) {
  state.currentPage = pageId;
  updateActiveNavigation(pageId);

  const content = document.getElementById("page-content");
  if (!content) return;

  content.innerHTML = "";
  content.className = "fade-in";

  try {
    await loadPageData(pageId);
    pages[pageId]?.(content);
  } catch (err) {
    showToast(err.message, "error");
    unauthenticatedRenderer();
  }
}

function updateActiveNavigation(pageId) {
  document.querySelectorAll(".nav-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.page === pageId);
  });
}

async function loadPageData(pageId) {
  if (["dashboard", "historico", "triagem"].includes(pageId)) {
    await loadPatients();
  }

  if (pageId === "triagem") {
    await loadSymptoms();
  }

  if (["dashboard", "avaliacoes"].includes(pageId)) {
    await loadAssessments();
  }
}
