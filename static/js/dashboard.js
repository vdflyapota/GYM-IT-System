// Requires /js/auth.js

document.addEventListener("DOMContentLoaded", async () => {
  // Show/hide Admin button based on role
  const adminLink = document.getElementById("adminLink");
  const roleBadge = document.getElementById("userRole");
  const userDisplay = document.getElementById("userDisplay");

  // Default hidden
  if (adminLink) adminLink.classList.add("d-none");

  // If not logged in, do nothing
  const role = getRole();
  if (roleBadge) roleBadge.textContent = role || "guest";

  if (role === "admin" && adminLink) {
    adminLink.classList.remove("d-none");
  }

  // Try to load the current user info for display
  try {
    const res = await authFetch("/users/me");
    if (res.ok) {
      const me = await res.json();
      if (userDisplay) userDisplay.textContent = me.full_name || me.email || "Unknown";
      if (roleBadge) roleBadge.textContent = me.role || role || "member";
    }
  } catch (e) {
    // Not logged in or request failed; leave defaults
    console.warn("Could not load /users/me", e);
  }
});
