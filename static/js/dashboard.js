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

  // Try to load the current user info for display
  try {
    const res = await authFetch("/api/users/me");
    if (res.ok) {
      const me = await res.json();
      if (userDisplay) userDisplay.textContent = me.full_name || me.email || "Unknown";
      const userRole = me.role || role || "member";
      if (roleBadge) roleBadge.textContent = userRole;
      
      // Only show Admin Panel button for admin users (not for trainers or members)
      if (userRole === "admin" && adminLink) {
        adminLink.classList.remove("d-none");
      }
    } else {
      // Fallback to role from token
      if (role === "admin" && adminLink) {
        adminLink.classList.remove("d-none");
      }
    }
  } catch (e) {
    // Not logged in or request failed; use role from token
    console.warn("Could not load /api/users/me", e);
    if (role === "admin" && adminLink) {
      adminLink.classList.remove("d-none");
    }
  }
});
