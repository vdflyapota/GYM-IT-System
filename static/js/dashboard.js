// Enhanced Dashboard with Real-time Features and Notifications

// Variables for WebSocket and notifications
let socket = null;
let notificationRefreshInterval = null;

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
      window.currentUserName = me.full_name || me.email || "";
      window.currentUserId = me.id;
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
    console.warn("Could not load /api/users/me", e);
    if (role === "admin" && adminLink) {
      adminLink.classList.remove("d-none");
    }
  }

  // Initialize features
  await loadDashboardStats();
  await loadNotifications();
  await loadRecentNotifications();
  await loadLatestBlogPosts();
  initializeRealTimeUpdates();
  
  // Refresh notifications periodically
  notificationRefreshInterval = setInterval(loadNotifications, 30000); // Every 30 seconds
});

// Load dashboard statistics (and optionally update live leaderboard widget from real-time data)
async function loadDashboardStats(leaderboardData = null) {
  try {
    let data = null;
    if (leaderboardData && Array.isArray(leaderboardData)) {
      data = { leaderboard: leaderboardData };
    } else {
      const leaderboardRes = await authFetch("/api/tournaments/leaderboard");
      if (leaderboardRes.ok) data = await leaderboardRes.json();
    }
    if (data && data.leaderboard) {
      const currentUserEmail = getEmail();
      const currentUserName = window.currentUserName || "";
      const userEntry = data.leaderboard.find(
        entry => entry.email === currentUserEmail || entry.user_name === currentUserEmail || entry.user_name === currentUserName
      );
      if (userEntry) {
        const rankEl = document.getElementById("userRank");
        const pointsEl = document.getElementById("userPoints");
        if (rankEl) rankEl.textContent = "#" + (userEntry.rank != null ? userEntry.rank : "—");
        if (pointsEl) pointsEl.textContent = String(userEntry.points != null ? userEntry.points : 0);
      }
      updateLiveLeaderboard(data.leaderboard);
    }

    if (!leaderboardData) {
      const tournamentsRes = await authFetch("/api/tournaments");
      if (tournamentsRes.ok) {
        const json = await tournamentsRes.json();
        const list = Array.isArray(json) ? json : (json.tournaments || []);
        const activeTournaments = list.filter(t => t.status === "active").length;
        const el = document.getElementById("activeTournaments");
        if (el) el.textContent = activeTournaments;
      }
    }
  } catch (e) {
    console.error("Error loading dashboard stats:", e);
  }
}

// Update the "Live leaderboard" / "Who is scoring" widget
function updateLiveLeaderboard(leaderboard) {
  const container = document.getElementById("liveLeaderboard");
  if (!container) return;
  if (!leaderboard || leaderboard.length === 0) {
    container.innerHTML = '<p class="text-muted small mb-0">No scores yet. Scores update in real time.</p>';
    return;
  }
  const currentUserName = window.currentUserName || "";
  const currentUserEmail = getEmail();
  let html = "";
  leaderboard.slice(0, 10).forEach((entry, i) => {
    const rank = entry.rank != null ? entry.rank : i + 1;
    const name = entry.user_name || entry.name || "—";
    const points = entry.points != null ? entry.points : 0;
    const isYou = name === currentUserName || entry.email === currentUserEmail;
    html += `
      <div class="d-flex justify-content-between align-items-center py-2 border-bottom border-light ${isYou ? "bg-light rounded px-2" : ""}">
        <span class="fw-bold">#${rank}</span>
        <span>${escapeHtml(name)}${isYou ? ' <span class="badge bg-primary">You</span>' : ""}</span>
        <span class="text-success fw-bold">${points} pts</span>
      </div>`;
  });
  container.innerHTML = html;
}

// Load notifications for dropdown
async function loadNotifications() {
  const dropdown = document.getElementById("notificationDropdown");
  const badge = document.getElementById("notificationBadge");
  
  if (!dropdown) return;
  
  try {
    const res = await authFetch("/api/users/notifications?limit=10");
    if (res.ok) {
      const notifications = await res.json();
      
      // Update badge
      const unreadCount = notifications.filter(n => !n.is_read).length;
      if (badge) {
        if (unreadCount > 0) {
          badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
          badge.style.display = 'flex';
        } else {
          badge.style.display = 'none';
        }
      }
      
      // Update dropdown
      if (notifications.length === 0) {
        dropdown.innerHTML = `
          <li><h6 class="dropdown-header">Notifications</h6></li>
          <li><hr class="dropdown-divider"></li>
          <li class="px-3 py-2 text-center text-muted">No notifications</li>
        `;
      } else {
        let html = `
          <li><h6 class="dropdown-header">Notifications (${unreadCount} unread)</h6></li>
          <li><hr class="dropdown-divider"></li>
        `;
        
        notifications.forEach(notif => {
          const typeIcon = getNotificationIcon(notif.type);
          const timeAgo = getTimeAgo(new Date(notif.created_at));
          html += `
            <li>
              <a class="dropdown-item ${notif.is_read ? '' : 'fw-bold'}" href="#" onclick="markNotificationRead(${notif.id}); return false;">
                <div class="d-flex align-items-start">
                  <span class="me-2">${typeIcon}</span>
                  <div class="flex-grow-1">
                    <div class="small">${escapeHtml(notif.title)}</div>
                    <div class="text-muted" style="font-size: 0.75rem;">${timeAgo}</div>
                  </div>
                </div>
              </a>
            </li>
          `;
        });
        
        dropdown.innerHTML = html;
      }
    } else {
      // API error - show friendly message
      dropdown.innerHTML = `
        <li><h6 class="dropdown-header">Notifications</h6></li>
        <li><hr class="dropdown-divider"></li>
        <li class="px-3 py-2 text-center text-muted">No notifications</li>
      `;
      if (badge) badge.style.display = 'none';
    }
  } catch (e) {
    console.error("Error loading notifications:", e);
    // On error, show friendly message instead of leaving "Loading..."
    dropdown.innerHTML = `
      <li><h6 class="dropdown-header">Notifications</h6></li>
      <li><hr class="dropdown-divider"></li>
      <li class="px-3 py-2 text-center text-muted">No notifications</li>
    `;
    if (badge) badge.style.display = 'none';
  }
}

// Load recent notifications for dashboard widget
async function loadRecentNotifications() {
  const container = document.getElementById("recentNotifications");
  if (!container) return;
  
  try {
    const res = await authFetch("/api/users/notifications?limit=5");
    if (res.ok) {
      const notifications = await res.json();
      
      if (notifications.length === 0) {
        container.innerHTML = '<p class="text-muted text-center py-3">No notifications yet</p>';
      } else {
        let html = '';
        notifications.forEach(notif => {
          const typeIcon = getNotificationIcon(notif.type);
          const timeAgo = getTimeAgo(new Date(notif.created_at));
          html += `
            <div class="notification-item ${notif.is_read ? '' : 'unread'} ${notif.type}" onclick="markNotificationRead(${notif.id})">
              <div class="d-flex align-items-start">
                <span class="me-2">${typeIcon}</span>
                <div class="flex-grow-1">
                  <strong class="d-block small">${escapeHtml(notif.title)}</strong>
                  <small class="text-muted">${timeAgo}</small>
                </div>
              </div>
            </div>
          `;
        });
        container.innerHTML = html;
      }
    } else {
      // API error - show friendly message
      container.innerHTML = '<p class="text-muted text-center py-3">No notifications yet</p>';
    }
  } catch (e) {
    console.error("Error loading recent notifications:", e);
    // On error, show friendly message instead of leaving "Loading..."
    container.innerHTML = '<p class="text-muted text-center py-3">No notifications yet</p>';
  }
}

// Load latest blog posts
async function loadLatestBlogPosts() {
  const container = document.getElementById("latestBlogPosts");
  if (!container) return;
  
  try {
    const res = await fetch("/api/users/blog/posts?limit=3");
    if (res.ok) {
      const posts = await res.json();
      
      if (posts.length === 0) {
        container.innerHTML = '<p class="text-muted text-center py-3">No blog posts yet</p>';
      } else {
        let html = '';
        posts.forEach(post => {
          const date = new Date(post.published_at || post.created_at).toLocaleDateString();
          html += `
            <div class="blog-preview mb-2" onclick="window.location.href='/blog-post.html?slug=${post.slug}'">
              <strong class="d-block">${escapeHtml(post.title)}</strong>
              <small class="text-muted">
                <i class="fas fa-calendar me-1"></i> ${date} • 
                <i class="fas fa-user me-1"></i> ${post.author ? escapeHtml(post.author.full_name) : 'HealthGYM'}
              </small>
            </div>
          `;
        });
        container.innerHTML = html;
      }
    } else {
      // API error - show friendly message
      container.innerHTML = '<p class="text-muted text-center py-3">No blog posts yet</p>';
    }
  } catch (e) {
    console.error("Error loading blog posts:", e);
    // On error, show friendly message instead of leaving "Loading..."
    container.innerHTML = '<p class="text-muted text-center py-3">No blog posts yet</p>';
  }
}

// Mark notification as read
async function markNotificationRead(notificationId) {
  try {
    const res = await authFetch(`/api/users/notifications/${notificationId}/read`, {
      method: "PUT",
    });
    if (res.ok) {
      // Reload notifications
      await loadNotifications();
      await loadRecentNotifications();
    }
  } catch (e) {
    console.error("Error marking notification as read:", e);
  }
}

// Initialize real-time updates with WebSocket
function initializeRealTimeUpdates() {
  // Only initialize if Socket.IO is available
  if (typeof io === 'undefined') {
    console.log("Socket.IO not available, skipping real-time updates");
    return;
  }
  
  try {
    socket = io();
    
    socket.on('connect', () => {
      console.log('Connected to real-time updates');
    });
    
    socket.on('leaderboard_update', (data) => {
      console.log('Leaderboard update received:', data);
      const list = data && data.leaderboard ? data.leaderboard : null;
      loadDashboardStats(list);
    });

    socket.on('new_notification', (notification) => {
      const forUser = notification.user_id == null || notification.user_id === window.currentUserId;
      if (!forUser) return;
      showToast(notification.title || "Notification", notification.message || "", notification.type);
      loadNotifications();
      loadRecentNotifications();
    });
    
    socket.on('tournament_update', (data) => {
      console.log('Tournament update:', data);
      loadDashboardStats();
    });
  } catch (e) {
    console.error("Error initializing real-time updates:", e);
  }
}

// Show toast notification
function showToast(title, message, type = 'info') {
  const toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) return;
  
  const bgClass = type === 'success' ? 'bg-success' : 
                  type === 'warning' ? 'bg-warning' : 
                  type === 'error' ? 'bg-danger' : 'bg-info';
  
  const toastHTML = `
    <div class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${escapeHtml(title)}</strong><br>
          ${escapeHtml(message)}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHTML);
  const toastEl = toastContainer.lastElementChild;
  const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 });
  toast.show();
  
  // Remove from DOM after hidden
  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}

// Helper functions
function getNotificationIcon(type) {
  switch (type) {
    case 'success': return '✅';
    case 'warning': return '⚠️';
    case 'error': return '❌';
    case 'info':
    default: return 'ℹ️';
  }
}

function getTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  
  return date.toLocaleDateString();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function getEmail() {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub;
  } catch (e) {
    return null;
  }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (socket) socket.disconnect();
  if (notificationRefreshInterval) clearInterval(notificationRefreshInterval);
});
