const form = document.querySelector("#upload-form");
const fileInput = document.querySelector("#pdf-file");
const dropzone = document.querySelector("#dropzone");
const dropTitle = document.querySelector("#drop-title");
const dropSubtitle = document.querySelector("#drop-subtitle");
const submitButton = document.querySelector("#submit-button");
const buttonLabel = document.querySelector("#button-label");
const copyButton = document.querySelector("#copy-button");
const summaryPanel = document.querySelector(".summary-panel");
const emptyState = document.querySelector("#empty-state");
const loadingState = document.querySelector("#loading-state");
const loadingMessage = document.querySelector("#loading-message");
const errorState = document.querySelector("#error-state");
const summaryResult = document.querySelector("#summary-result");
const summaryText = document.querySelector("#summary-text");
const documentMeta = document.querySelector("#document-meta");

function setFile(file) {
  if (!file) return;
  fileInput.files = createFileList(file);
  dropTitle.textContent = file.name;
  dropSubtitle.textContent = `${(file.size / (1024 * 1024)).toFixed(1)} MB · ready to summarize`;
  submitButton.disabled = false;
  dropzone.classList.add("has-file");
  showState("empty");
}

function createFileList(file) {
  const transfer = new DataTransfer();
  transfer.items.add(file);
  return transfer.files;
}

function showState(state) {
  emptyState.hidden = state !== "empty";
  loadingState.hidden = state !== "loading";
  errorState.hidden = state !== "error";
  summaryResult.hidden = state !== "result";
  copyButton.disabled = state !== "result";
  summaryPanel.setAttribute("aria-busy", String(state === "loading"));
}

fileInput.addEventListener("change", () => setFile(fileInput.files[0]));

for (const eventName of ["dragenter", "dragover"]) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-over");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-over");
  });
}

dropzone.addEventListener("drop", (event) => setFile(event.dataTransfer.files[0]));

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  const payload = new FormData();
  payload.append("file", file);
  submitButton.disabled = true;
  buttonLabel.textContent = "Working…";
  loadingMessage.textContent = "Reading your document…";
  showState("loading");

  const progressTimer = window.setTimeout(() => {
    loadingMessage.textContent = "Building your summary…";
  }, 1400);

  try {
    const response = await fetch("/api/summarize", { method: "POST", body: payload });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "The document could not be summarized.");

    summaryText.textContent = result.summary;
    documentMeta.textContent = `${result.filename}  /  ${result.page_count} ${result.page_count === 1 ? "page" : "pages"}`;
    showState("result");
  } catch (error) {
    errorState.textContent = error.message || "Something went wrong. Please try again.";
    showState("error");
  } finally {
    window.clearTimeout(progressTimer);
    submitButton.disabled = false;
    buttonLabel.textContent = "Summarize document";
  }
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(summaryText.textContent);
    copyButton.textContent = "COPIED";
    window.setTimeout(() => { copyButton.textContent = "COPY"; }, 1400);
  } catch {
    copyButton.textContent = "UNAVAILABLE";
    window.setTimeout(() => { copyButton.textContent = "COPY"; }, 1800);
  }
});
