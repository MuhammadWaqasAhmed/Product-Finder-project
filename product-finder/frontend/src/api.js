const API_BASE = "/api";

async function request(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`, window.location.origin);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      url.searchParams.set(key, String(value));
    }
  });

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export function fetchDashboard() {
  return request("/dashboard");
}

export function searchProducts(filters) {
  return request("/search", filters);
}
