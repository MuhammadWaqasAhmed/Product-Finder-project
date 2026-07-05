const AUTH_KEY = "pf_access_token";
const USER_KEY = "pf_user";

function getToken() {
  return localStorage.getItem(AUTH_KEY);
}

function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setAuth(token, user) {
  localStorage.setItem(AUTH_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  updateAuthUi();
}

function clearAuth() {
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(USER_KEY);
  updateAuthUi();
}

async function authFetch(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json();
}

function updateAuthUi() {
  const user = getUser();
  const authUser = document.getElementById("auth-user");
  const loginOpen = document.getElementById("login-open");
  const logoutBtn = document.getElementById("logout-btn");
  if (!authUser) return;
  authUser.textContent = user ? `Signed in as ${user.username}` : "Guest mode";
  loginOpen?.classList.toggle("hidden", Boolean(user));
  logoutBtn?.classList.toggle("hidden", !user);
}

function bindAuthModal() {
  const modal = document.getElementById("login-modal");
  const loginOpen = document.getElementById("login-open");
  const loginClose = document.getElementById("login-close");
  const loginSubmit = document.getElementById("login-submit");
  const logoutBtn = document.getElementById("logout-btn");

  loginOpen?.addEventListener("click", () => modal?.classList.remove("hidden"));
  loginClose?.addEventListener("click", () => modal?.classList.add("hidden"));
  logoutBtn?.addEventListener("click", clearAuth);

  loginSubmit?.addEventListener("click", async () => {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    const body = new URLSearchParams({ username, password });
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!response.ok) {
      alert("Login failed. Try demo / demo1234");
      return;
    }
    const payload = await response.json();
    setAuth(payload.access_token, payload.user);
    modal?.classList.add("hidden");
    document.dispatchEvent(new CustomEvent("auth:changed"));
  });

  updateAuthUi();
}

document.addEventListener("DOMContentLoaded", bindAuthModal);
