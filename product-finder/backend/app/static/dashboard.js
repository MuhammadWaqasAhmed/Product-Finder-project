const chartColors = {
  primary: "#34495e",
  accent: "#f5a623",
  gray: "#95a5a6",
  light: "#d5dbe1",
};

let charts = [];

function destroyCharts() {
  charts.forEach((chart) => chart.destroy());
  charts = [];
}

function makeChart(canvasId, config) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  charts.push(new Chart(canvas, config));
}

function renderKpis(kpis) {
  const container = document.getElementById("kpi-grid");
  container.innerHTML = kpis
    .map(
      (kpi) => `
        <article class="card kpi-card">
          <p class="label">${kpi.label}</p>
          <p class="value">${kpi.value}</p>
          <p class="change ${kpi.trend === "down" ? "down" : ""}">${kpi.change}</p>
        </article>
      `,
    )
    .join("");
}

function renderLeaderboard(entries) {
  const top = document.getElementById("leaderboard-top");
  const list = document.getElementById("leaderboard-list");
  const podium = entries.slice(0, 3);
  const rest = entries.slice(3);

  top.innerHTML = podium
    .map(
      (entry, index) => `
        <div class="leader ${index === 0 ? "first" : ""}">
          <div class="avatar" style="background:${entry.avatar_color}">#${entry.rank}</div>
          <strong>${entry.name.slice(0, 28)}${entry.name.length > 28 ? "…" : ""}</strong>
          <div>${entry.value}</div>
        </div>
      `,
    )
    .join("");

  list.innerHTML = rest
    .map(
      (entry) => `
        <li>
          <span>#${entry.rank} ${entry.name.slice(0, 34)}</span>
          <strong>${entry.score}</strong>
        </li>
      `,
    )
    .join("");
}

function renderProviderTable(statuses) {
  const tbody = document.querySelector("#provider-table tbody");
  tbody.innerHTML = statuses
    .map(
      (item) => `
        <tr>
          <td>${item.label}</td>
          <td><span class="badge ${item.mode}">${item.mode}</span></td>
          <td>${item.product_count}</td>
        </tr>
      `,
    )
    .join("");
}

function renderDashboard(data) {
  renderKpis(data.kpis);
  renderLeaderboard(data.top_products);
  renderProviderTable(data.provider_status);
  destroyCharts();

  makeChart("search-volume-chart", {
    type: "bar",
    data: {
      labels: data.search_volume.labels,
      datasets: data.search_volume.series.map((series, index) => ({
        label: series.label,
        data: series.data,
        backgroundColor: index === 0 ? chartColors.primary : chartColors.accent,
        borderRadius: 6,
      })),
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
  });

  makeChart("provider-mix-chart", {
    type: "bar",
    data: {
      labels: data.provider_mix.labels,
      datasets: data.provider_mix.series.map((series, index) => ({
        label: series.label,
        data: series.data,
        backgroundColor: index === 0 ? chartColors.primary : chartColors.accent,
        borderRadius: 6,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { stacked: false }, y: { beginAtZero: true } },
      plugins: { legend: { position: "bottom" } },
    },
  });

  makeChart("category-chart", {
    type: "bar",
    data: {
      labels: data.category_breakdown.labels,
      datasets: [{
        label: data.category_breakdown.series[0].label,
        data: data.category_breakdown.series[0].data,
        backgroundColor: chartColors.accent,
        borderRadius: 6,
      }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
  });

  makeChart("price-trend-chart", {
    type: "line",
    data: {
      labels: data.price_trends.labels,
      datasets: data.price_trends.series.map((series, index) => ({
        label: series.label,
        data: series.data,
        borderColor: index === 0 ? chartColors.primary : chartColors.accent,
        backgroundColor: index === 0 ? "rgba(52,73,94,0.12)" : "rgba(245,166,35,0.18)",
        fill: true,
        tension: 0.35,
      })),
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
  });

  makeChart("engagement-chart", {
    type: "doughnut",
    data: {
      labels: data.provider_engagement.labels,
      datasets: [{
        data: data.provider_engagement.series[0].data,
        backgroundColor: [chartColors.primary, chartColors.accent, chartColors.gray, chartColors.light, "#bdc3c7"],
      }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
  });
}

async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  const data = await response.json();
  renderDashboard(data);
}

document.addEventListener("DOMContentLoaded", loadDashboard);
