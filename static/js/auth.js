// Lightweight client-side auth helpers for JWT in localStorage

const TOKEN_KEY = "access_token";
const ROLE_KEY = "role";

function setToken(token, role) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
    if (role) localStorage.setItem(ROLE_KEY, role);
  } catch (e) {
    console.error("Failed to store token", e);
  }
}

function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function getRole() {
  try {
    const explicit = localStorage.getItem(ROLE_KEY);
    if (explicit) return explicit;
    const token = getToken();
    if (!token) return null;
    const payload = parseJwt(token);
    return payload?.role || null;
  } catch {
    return null;
  }
}

function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
  } catch {}
}

function logout() {
  clearToken();
  window.location.href = "/login.html";
}

// Basic JWT payload decode (no signature verification; for UI only)
function parseJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

// Require any authenticated user; redirect to login if missing
function requireAuth(redirect = "/login.html") {
  const token = getToken();
  if (!token) {
    window.location.replace(redirect);
    return false;
  }
  return true;
}

// Require a specific role; redirect if missing or not authorized
function requireRole(role, redirect = "/login.html") {
  if (!requireAuth(redirect)) return false;
  const userRole = getRole();
  if (userRole !== role) {
    // Not authorized; send to home or login
    window.location.replace("/");
    return false;
  }
  return true;
}

// Wrapper around fetch that automatically adds Authorization header
async function authFetch(url, options = {}) {
  const token = getToken();
  const headers = new Headers(options.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  // default to JSON when body is an object
  if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
    options.body = JSON.stringify(options.body);
  }
  return fetch(url, { ...options, headers });
}
