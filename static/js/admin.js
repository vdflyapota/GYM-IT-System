// Guard page for admin role
if (!requireRole("admin")) {
  // requireRole handles redirect
} else {
  wireCreateAdminForm();
  loadUsers();
}

function wireCreateAdminForm() {
  const form = document.getElementById("createAdminForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("newAdminEmail").value.trim().toLowerCase();
    const full_name = document.getElementById("newAdminName").value.trim();
    const password = document.getElementById("newAdminPassword").value;
    try {
      const res = await authFetch("/users/create_admin", {
        method: "POST",
        body: { email, full_name, password },
      });
      await handleResponse(res, "Admin created");
      form.reset();
    } catch (e) {
      const alert = document.getElementById("alert");
      alert.textContent = e.message || "Error creating admin";
      alert.className = "alert alert-danger";
    }
  });
}

async function loadUsers() {
  const alert = document.getElementById("alert");
  const tbody = document.getElementById("usersTbody");
  const wrapper = document.getElementById("usersTableWrapper");
  const empty = document.getElementById("emptyState");

  alert.className = "alert d-none";
  tbody.innerHTML = "";

  try {
    const res = await authFetch("/users/");
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Failed: ${res.status} ${errText}`);
    }
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      wrapper.classList.add("d-none");
      empty.classList.remove("d-none");
      return;
    }

    empty.classList.add("d-none");
    wrapper.classList.remove("d-none");

    for (const u of data) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${u.id}</td>
        <td>${u.email}</td>
        <td>${u.full_name}</td>
        <td><span class="badge ${badgeClass(u.role)}">${u.role}</span></td>
        <td>${u.is_approved ? "✅" : "❌"}</td>
        <td>${u.is_active ? "✅" : "❌"}</td>
        <td>${u.is_banned ? "🚫" : "—"}</td>
        <td>${u.is_root_admin ? "👑" : "—"}</td>
        <td class="d-flex flex-wrap gap-1">
          ${actionButtons(u)}
        </td>
      `;
      tbody.appendChild(tr);
    }
  } catch (e) {
    console.error(e);
    alert.textContent = e.message || "Error loading users";
    alert.className = "alert alert-danger";
  }
}

function badgeClass(role) {
  switch (role) {
    case "admin": return "bg-danger";
    case "trainer": return "bg-primary";
    default: return "bg-secondary";
  }
}

function actionButtons(u) {
  const disabled = u.is_root_admin ? "disabled" : "";
  const approve = `<button class="btn btn-sm btn-success" onclick="approveUser(${u.id})" ${u.is_approved ? "disabled" : ""}>Approve</button>`;
  const deactivate = `<button class="btn btn-sm btn-outline-warning" onclick="deactivateUser(${u.id})" ${disabled}>Deactivate</button>`;
  const ban = u.is_banned
    ? `<button class="btn btn-sm btn-outline-secondary" onclick="unbanUser(${u.id})" ${disabled}>Unban</button>`
    : `<button class="btn btn-sm btn-outline-danger" onclick="banUser(${u.id})" ${disabled}>Ban</button>`;
  const del = `<button class="btn btn-sm btn-outline-dark" onclick="deleteUser(${u.id})" ${disabled}>Delete</button>`;
  return [approve, deactivate, ban, del].join(" ");
}

async function approveUser(userId) {
  await postJSON("/users/approve", { user_id: userId }, "User approved");
}
async function deactivateUser(userId) {
  await postJSON("/users/deactivate", { user_id: userId }, "User deactivated");
}
async function banUser(userId) {
  await postJSON("/users/ban", { user_id: userId }, "User banned");
}
async function unbanUser(userId) {
  await postJSON("/users/unban", { user_id: userId }, "User unbanned");
}
async function deleteUser(userId) {
  const ok = confirm("Are you sure you want to delete this user?");
  if (!ok) return;
  const res = await authFetch(`/users/${userId}`, { method: "DELETE" });
  await handleResponse(res, "User deleted");
}

async function postJSON(url, body, successMsg) {
  const res = await authFetch(url, { method: "POST", body });
  await handleResponse(res, successMsg);
}

async function handleResponse(res, successMsg) {
  const alert = document.getElementById("alert");
  if (!res.ok) {
    const text = await res.text();
    alert.textContent = text || `Error (${res.status})`;
    alert.className = "alert alert-danger";
  } else {
    alert.textContent = successMsg;
    alert.className = "alert alert-success";
    loadUsers();
  }
}
