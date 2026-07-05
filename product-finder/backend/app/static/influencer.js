const preferenceOptions = [
  { key: "auto_product_research", label: "Automated product research" },
  { key: "content_generation", label: "AI content and caption generation" },
  { key: "price_alerts", label: "Price drop alerts" },
  { key: "affiliate_links", label: "Affiliate link automation" },
];

function renderPreferences() {
  const container = document.getElementById("workflow-preferences");
  container.innerHTML = preferenceOptions
    .map(
      (item) => `
        <label>
          <input type="checkbox" data-pref="${item.key}" checked />
          ${item.label}
        </label>
      `,
    )
    .join("");
}

function readPreferences() {
  return Object.fromEntries(
    [...document.querySelectorAll("[data-pref]")].map((input) => [input.dataset.pref, input.checked]),
  );
}

function renderIntegrations(items) {
  const list = document.getElementById("integration-list");
  if (!items.length) {
    list.innerHTML = "<li>No connected accounts yet.</li>";
    return;
  }
  list.innerHTML = items
    .map(
      (item) => `
        <li>
          <strong>${item.platform}</strong> · ${item.account_handle}
          <div class="card__subtitle">Status: ${item.status} · AI: ${item.ai_workflow_enabled ? "enabled" : "disabled"}</div>
        </li>
      `,
    )
    .join("");
}

function renderWorkflows(items) {
  const list = document.getElementById("workflow-list");
  if (!items.length) {
    list.innerHTML = "<li>No workflows created yet.</li>";
    return;
  }
  list.innerHTML = items
    .map(
      (item) => `
        <li>
          <strong>${item.name}</strong>
          <div class="card__subtitle">${item.trigger} · ${item.schedule} · ${item.enabled ? "active" : "paused"}</div>
          <div>${item.actions.join(", ")}</div>
        </li>
      `,
    )
    .join("");
}

async function loadInfluencerDashboard() {
  if (!getToken()) return;
  const data = await authFetch("/api/influencer/dashboard");
  if (data.profile) {
    document.getElementById("display-name").value = data.profile.display_name;
    document.getElementById("niche").value = data.profile.niche;
    document.getElementById("audience-size").value = data.profile.audience_size;
    document.getElementById("bio").value = data.profile.bio;
  }

  const platformSelect = document.getElementById("platform");
  const platforms = data?.available_platforms || [
    "TikTok", "Instagram", "YouTube", "Amazon Associates", "eBay Partner Network",
    "AliExpress Portals", "Alibaba Seller", "Shopify", "Pinterest",
  ];
  platformSelect.innerHTML = platforms
    .map((platform) => `<option value="${platform}">${platform}</option>`)
    .join("");

  document.getElementById("ai-capabilities").innerHTML = data.ai_capabilities
    .map((item) => `<li>${item}</li>`)
    .join("");

  renderIntegrations(data.integrations);
  renderWorkflows(data.workflows);
}

document.addEventListener("DOMContentLoaded", () => {
  renderPreferences();

  document.getElementById("profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!getToken()) return alert("Sign in first.");
    await authFetch("/api/influencer/profile", {
      method: "POST",
      body: JSON.stringify({
        display_name: document.getElementById("display-name").value,
        niche: document.getElementById("niche").value,
        audience_size: Number(document.getElementById("audience-size").value || 0),
        bio: document.getElementById("bio").value,
      }),
    });
    alert("Profile saved.");
    loadInfluencerDashboard();
  });

  document.getElementById("integration-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!getToken()) return alert("Sign in first.");
    await authFetch("/api/influencer/integrations", {
      method: "POST",
      body: JSON.stringify({
        platform: document.getElementById("platform").value,
        account_handle: document.getElementById("account-handle").value,
        account_id: document.getElementById("account-id").value,
        access_token: document.getElementById("access-token").value,
        ai_workflow_enabled: document.getElementById("ai-enabled").checked,
        workflow_preferences: readPreferences(),
      }),
    });
    event.target.reset();
    document.getElementById("ai-enabled").checked = true;
    renderPreferences();
    alert("Account connected.");
    loadInfluencerDashboard();
  });

  document.getElementById("workflow-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!getToken()) return alert("Sign in first.");
    const actions = document
      .getElementById("workflow-actions")
      .value.split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    await authFetch("/api/influencer/workflows", {
      method: "POST",
      body: JSON.stringify({
        name: document.getElementById("workflow-name").value,
        trigger: document.getElementById("workflow-trigger").value,
        schedule: document.getElementById("workflow-schedule").value,
        actions,
        enabled: true,
      }),
    });
    event.target.reset();
    alert("Workflow created.");
    loadInfluencerDashboard();
  });

  document.addEventListener("auth:changed", loadInfluencerDashboard);
  loadInfluencerDashboard();
});
