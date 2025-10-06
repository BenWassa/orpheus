const mappingFields = [
  { id: "timestamp", label: "Play timestamp" },
  { id: "track", label: "Track title" },
  { id: "artist", label: "Artist" },
  { id: "album", label: "Album" },
  { id: "duration_ms", label: "Duration (ms)" },
  { id: "valence", label: "Valence" },
  { id: "energy", label: "Energy" },
  { id: "danceability", label: "Danceability" },
];

const state = {
  file: null,
};

function setupMappingGrid(columns) {
  const mappingGrid = document.getElementById("mapping-grid");
  const content = document.getElementById("mapping-grid-content");
  if (!mappingGrid || !content) return;

  content.innerHTML = "";

  mappingFields.forEach((field) => {
    const wrapper = document.createElement("label");
    wrapper.className = "mapping-field";

    const name = document.createElement("span");
    name.textContent = field.label;

    const select = document.createElement("select");
    select.name = field.id;

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = "Select column";
    select.appendChild(placeholderOption);

    columns.forEach((column) => {
      const option = document.createElement("option");
      option.value = column;
      option.textContent = column;
      select.appendChild(option);
    });

    wrapper.appendChild(name);
    wrapper.appendChild(select);
    content.appendChild(wrapper);
  });

  mappingGrid.hidden = false;
}

function showSummaryPlaceholder(filename) {
  const summarySection = document.getElementById("summary-section");
  const summaryMetrics = document.getElementById("summary-metrics");
  if (!summarySection || !summaryMetrics) return;

  summarySection.hidden = false;
  summaryMetrics.innerHTML = `
    <p class="placeholder">
      Parsing <strong>${filename}</strong>… detailed metrics will populate here once Sprint B3 adds the data transforms.
    </p>
  `;
}

function showChartsPlaceholder() {
  const chartsSection = document.getElementById("charts-section");
  if (!chartsSection) return;
  chartsSection.hidden = false;
}

function handleFileChange(event) {
  const [file] = event.target.files || [];
  if (!file) {
    return;
  }

  state.file = file;

  // Papaparse will be wired in Sprint B2/B3. For now, mock column detection.
  setupMappingGrid(["timestamp", "track", "artist", "album", "duration_ms"]);
  showSummaryPlaceholder(file.name);
  showChartsPlaceholder();
}

function initialize() {
  const csvInput = document.getElementById("csv-input");
  if (!csvInput) return;

  csvInput.addEventListener("change", handleFileChange);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialize);
} else {
  initialize();
}
