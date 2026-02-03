// Reports variables - declared at top to avoid temporal dead zone issues
let reportData = null;
let roleChart = null;
let trendChart = null;

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
      const res = await authFetch("/api/auth/create_admin", {
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
    const res = await authFetch("/api/users/");
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Failed: ${res.status}`);
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
      // Handle is_active field gracefully - it might not exist in older databases
      const isActive = u.is_active !== undefined ? u.is_active : true;
      tr.innerHTML = `
        <td>${u.id}</td>
        <td>${u.email}</td>
        <td>${u.full_name}</td>
        <td><span class="badge ${badgeClass(u.role)}">${u.role}</span></td>
        <td>${u.is_approved ? "✅" : "❌"}</td>
        <td>${isActive ? "✅" : "❌"}</td>
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
  const ban = u.is_banned
    ? `<button class="btn btn-sm btn-outline-secondary" ${disabled} disabled>Banned</button>`
    : `<button class="btn btn-sm btn-outline-danger" onclick="banUser(${u.id})" ${disabled}>Ban</button>`;
  const del = `<button class="btn btn-sm btn-outline-dark" onclick="deleteUser(${u.id})" ${disabled}>Delete</button>`;
  return [approve, ban, del].join(" ");
}

async function approveUser(userId) {
  const res = await authFetch("/api/users/approve", { 
    method: "PATCH", 
    body: { user_id: userId } 
  });
  await handleResponse(res, "User approved");
}

async function banUser(userId) {
  const res = await authFetch("/api/users/ban", { 
    method: "PATCH", 
    body: { user_id: userId } 
  });
  await handleResponse(res, "User banned");
}

async function deleteUser(userId) {
  const ok = confirm("Are you sure you want to delete this user?");
  if (!ok) return;
  const res = await authFetch(`/api/users/${userId}`, { method: "DELETE" });
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

// ============================================
// REPORTS FUNCTIONALITY
// ============================================

async function loadReports() {
  const alert = document.getElementById("alert");
  const tbody = document.getElementById("reportsTbody");
  const wrapper = document.getElementById("reportsTableWrapper");
  const empty = document.getElementById("reportsEmptyState");

  alert.className = "alert d-none";
  tbody.innerHTML = "";

  // Get filter values
  const startDate = document.getElementById("startDate")?.value || '';
  const endDate = document.getElementById("endDate")?.value || '';
  const role = document.getElementById("roleFilter")?.value || 'all';

  // Build query string
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate + 'T00:00:00');
  if (endDate) params.append('end_date', endDate + 'T23:59:59');
  if (role && role !== 'all') params.append('role', role);

  try {
    const res = await authFetch(`/api/users/reports/statistics?${params.toString()}`);
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Failed: ${res.status} ${errText}`);
    }
    
    reportData = await res.json();
    
    // Update statistics cards
    document.getElementById('statTotalUsers').textContent = reportData.total_users || 0;
    document.getElementById('statApproved').textContent = reportData.approved_users || 0;
    document.getElementById('statPending').textContent = reportData.pending_users || 0;
    document.getElementById('statBanned').textContent = reportData.banned_users || 0;

    // Update charts
    updateRoleChart(reportData.by_role || {});
    updateTrendChart(reportData.registrations_by_date || {});

    // Update user table
    const users = reportData.users || [];
    if (users.length === 0) {
      wrapper.classList.add("d-none");
      empty.classList.remove("d-none");
      empty.textContent = "No users match the selected filters.";
      return;
    }

    empty.classList.add("d-none");
    wrapper.classList.remove("d-none");

    for (const u of users) {
      const tr = document.createElement("tr");
      // Handle created_at gracefully - it might be null or undefined
      const createdDate = u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A';
      tr.innerHTML = `
        <td>${u.id}</td>
        <td>${u.email || 'N/A'}</td>
        <td>${u.full_name || 'N/A'}</td>
        <td><span class="badge ${badgeClass(u.role)}">${u.role || 'member'}</span></td>
        <td>${u.is_approved ? "✅" : "❌"}</td>
        <td>${u.is_banned ? "🚫" : "✅"}</td>
        <td>${createdDate}</td>
      `;
      tbody.appendChild(tr);
    }
  } catch (e) {
    console.error(e);
    alert.textContent = e.message || "Error loading reports";
    alert.className = "alert alert-danger";
  }
}

function updateRoleChart(byRole) {
  const ctx = document.getElementById('roleChart');
  if (!ctx) return;

  const roles = ['member', 'trainer', 'admin'];
  const counts = roles.map(role => byRole[role] || 0);
  const colors = ['#6c757d', '#0d6efd', '#dc3545'];

  if (roleChart) {
    roleChart.destroy();
  }

  roleChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: roles.map(r => r.charAt(0).toUpperCase() + r.slice(1)),
      datasets: [{
        data: counts,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

function updateTrendChart(registrationsByDate) {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;

  // Sort dates and get values
  const dates = Object.keys(registrationsByDate).sort();
  const counts = dates.map(date => registrationsByDate[date]);

  // Format dates for display
  const labels = dates.map(date => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  });

  if (trendChart) {
    trendChart.destroy();
  }

  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'New Registrations',
        data: counts,
        borderColor: '#0d6efd',
        backgroundColor: 'rgba(13, 110, 253, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  });
}

function exportToCSV() {
  if (!reportData || !reportData.users || reportData.users.length === 0) {
    alert('No data to export. Please generate a report first.');
    return;
  }

  const users = reportData.users;
  const headers = ['ID', 'Email', 'Full Name', 'Role', 'Approved', 'Banned', 'Root Admin', 'Created At'];
  
  let csv = headers.join(',') + '\n';
  
  for (const user of users) {
    const row = [
      user.id,
      `"${user.email}"`,
      `"${user.full_name}"`,
      user.role,
      user.is_approved ? 'Yes' : 'No',
      user.is_banned ? 'Yes' : 'No',
      user.is_root_admin ? 'Yes' : 'No',
      user.created_at ? new Date(user.created_at).toISOString() : 'N/A'
    ];
    csv += row.join(',') + '\n';
  }

  downloadFile(csv, 'user-report.csv', 'text/csv');
}

function exportToJSON() {
  if (!reportData) {
    alert('No data to export. Please generate a report first.');
    return;
  }

  const jsonStr = JSON.stringify(reportData, null, 2);
  downloadFile(jsonStr, 'user-report.json', 'application/json');
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
