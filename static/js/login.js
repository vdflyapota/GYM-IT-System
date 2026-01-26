// Stores token + role on successful login and redirects appropriately.
// Requires /js/auth.js to be loaded first.

(function initLogin() {
  const form = document.getElementById("loginForm");
  const submitBtn = document.getElementById("loginSubmit");
  const msg = document.getElementById("msg");

  if (!form) {
    console.error("loginForm not found. Ensure #loginForm exists.");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.textContent = "";
    if (submitBtn) submitBtn.disabled = true;

    const email = document.getElementById("email")?.value?.trim() || "";
    const password = document.getElementById("password")?.value || "";

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Login failed");
      }

      // Persist token + role for RBAC
      setToken(data.access_token, data.role);

      // Redirect by role
      if (data.role === "admin") {
        window.location.href = "/admin.html";
      } else {
        window.location.href = "/dashboard.html";
      }
    } catch (err) {
      console.error(err);
      msg.innerHTML = `<span class="text-danger">${err.message || "Server error"}</span>`;
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
})();
