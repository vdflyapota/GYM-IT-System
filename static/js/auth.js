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

// Require authentication for protected pages
// If allowedRoles is provided, also check if user has the required role
function requireAuth(allowedRoles = null) {
  const token = getToken();
  
  // If no token, redirect to login
  if (!token) {
    const currentUrl = window.location.pathname + window.location.search;
    const returnUrl = encodeURIComponent(currentUrl);
    window.location.href = `/login.html?returnUrl=${returnUrl}`;
    return false;
  }
  
  // If specific roles are required, check user's role
  if (allowedRoles) {
    const userRole = getRole();
    const rolesArray = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    
    if (!rolesArray.includes(userRole)) {
      alert('Access Denied: You do not have permission to access this page.');
      window.location.href = '/dashboard.html';
      return false;
    }
  }
  
  return true;
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
