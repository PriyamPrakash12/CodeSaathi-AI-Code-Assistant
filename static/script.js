const modeTabs = document.querySelectorAll(".mode-tab");
const runBtn = document.getElementById("runBtn");
const runBtnLabel = document.getElementById("runBtnLabel");
const outputBody = document.getElementById("outputBody");
const inputHeader = document.getElementById("inputHeader");

const skillLevelRow = document.getElementById("skillLevelRow");
const descriptionRow = document.getElementById("descriptionRow");
const errorRow = document.getElementById("errorRow");
const goalRow = document.getElementById("goalRow");
const codeRow = document.getElementById("codeRow");
const codeInput = document.getElementById("codeInput");

const ALL_ROWS = [skillLevelRow, descriptionRow, errorRow, goalRow, codeRow];

let currentMode = "explain";

const MODE_CONFIG = {
  explain: {
    header: "Paste your code",
    button: "Explain code",
    visibleRows: [skillLevelRow, codeRow],
    placeholder: "def example():\n    pass",
  },
  generate: {
    header: "Generate new code",
    button: "Generate code",
    visibleRows: [descriptionRow],
    placeholder: "",
  },
  fix: {
    header: "Paste the broken code",
    button: "Fix code",
    visibleRows: [errorRow, codeRow],
    placeholder: "def divide(a, b):\n    return a / b",
  },
  refactor: {
    header: "Paste the code to refactor",
    button: "Refactor code",
    visibleRows: [goalRow, codeRow],
    placeholder: "def process(data):\n    result = []\n    for i in range(len(data)):\n        result.append(data[i] * 2)\n    return result",
  },
};

function applyMode(mode) {
  currentMode = mode;
  const cfg = MODE_CONFIG[mode];

  modeTabs.forEach(tab => tab.classList.toggle("active", tab.dataset.mode === mode));

  inputHeader.textContent = cfg.header;
  runBtnLabel.textContent = cfg.button;

  // Hide every row first, then show only the ones this mode needs.
  // This avoids any row being left visible from a previous mode.
  ALL_ROWS.forEach(row => row.classList.add("hidden"));
  cfg.visibleRows.forEach(row => row.classList.remove("hidden"));

  codeInput.placeholder = cfg.placeholder;
}

modeTabs.forEach(tab => {
  tab.addEventListener("click", () => applyMode(tab.dataset.mode));
});

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function renderExplain(data) {
  const issues = (data.potential_issues || []).map(i => `<li>${escapeHtml(i)}</li>`).join("");
  const suggestions = (data.suggestions || []).map(s => `<li>${escapeHtml(s)}</li>`).join("");
  const lines = (data.line_by_line || []).map(l => `<li>${escapeHtml(l)}</li>`).join("");

  return `
    <div class="result-block">
      <div class="result-label">Summary</div>
      <div class="result-text">${escapeHtml(data.summary || "")}</div>
    </div>
    <div class="result-block">
      <div class="result-label">Line by line</div>
      <ul class="result-list">${lines}</ul>
    </div>
    ${issues ? `<div class="result-block"><div class="result-label">Potential issues</div><ul class="result-list issues">${issues}</ul></div>` : ""}
    ${suggestions ? `<div class="result-block"><div class="result-label">Suggestions</div><ul class="result-list suggestions">${suggestions}</ul></div>` : ""}
  `;
}

function renderGenerate(data) {
  const assumptions = (data.assumptions || []).map(a => `<li>${escapeHtml(a)}</li>`).join("");
  return `
    <div class="result-block">
      <div class="result-label">Generated code</div>
      <pre class="code-block">${escapeHtml(data.code || "")}</pre>
    </div>
    <div class="result-block">
      <div class="result-label">Approach</div>
      <div class="result-text">${escapeHtml(data.explanation || "")}</div>
    </div>
    ${assumptions ? `<div class="result-block"><div class="result-label">Assumptions</div><ul class="result-list">${assumptions}</ul></div>` : ""}
  `;
}

function renderFix(data) {
  const changes = (data.what_changed || []).map(c => `<li>${escapeHtml(c)}</li>`).join("");
  return `
    <div class="result-block">
      <div class="result-label">Diagnosis</div>
      <div class="result-text">${escapeHtml(data.diagnosis || "")}</div>
    </div>
    <div class="result-block">
      <div class="result-label">Fixed code</div>
      <pre class="code-block">${escapeHtml(data.fixed_code || "")}</pre>
    </div>
    ${changes ? `<div class="result-block"><div class="result-label">What changed</div><ul class="result-list">${changes}</ul></div>` : ""}
  `;
}

function renderRefactor(data) {
  const changes = (data.changes || [])
    .map(c => `<div class="change-item"><div>${escapeHtml(c.change || "")}</div><div class="why">${escapeHtml(c.why || "")}</div></div>`)
    .join("");
  return `
    <div class="result-block">
      <div class="result-label">Refactored code</div>
      <pre class="code-block">${escapeHtml(data.refactored_code || "")}</pre>
    </div>
    <div class="result-block">
      <div class="result-label">Changes</div>
      ${changes}
    </div>
  `;
}

const RENDERERS = {
  explain: renderExplain,
  generate: renderGenerate,
  fix: renderFix,
  refactor: renderRefactor,
};

async function runAssist() {
  const language = document.getElementById("language").value;
  //const provider = document.getElementById("provider").value;
  const payload = { mode: currentMode, language};

  if (currentMode === "explain") {
    payload.code = codeInput.value;
    payload.skill_level = document.getElementById("skillLevel").value;
  } else if (currentMode === "generate") {
    payload.description = document.getElementById("description").value;
  } else if (currentMode === "fix") {
    payload.code = codeInput.value;
    payload.error_message = document.getElementById("errorMessage").value;
  } else if (currentMode === "refactor") {
    payload.code = codeInput.value;
    payload.goal = document.getElementById("goal").value;
  }

  runBtn.disabled = true;
  outputBody.innerHTML = `<div class="loading">Thinking…</div>`;

  try {
    const res = await fetch("/api/assist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok || data.error) {
      outputBody.innerHTML = `<div class="error-box">${escapeHtml(data.error || "Something went wrong.")}</div>`;
      return;
    }

    outputBody.innerHTML = RENDERERS[currentMode](data);
  } catch (err) {
    outputBody.innerHTML = `<div class="error-box">Request failed: ${escapeHtml(err.message)}</div>`;
  } finally {
    runBtn.disabled = false;
  }
}

runBtn.addEventListener("click", runAssist);

applyMode("explain");
