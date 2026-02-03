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
      
      // Only show Admin Panel button for admin users
      if (userRole === "admin" && adminLink) {
        adminLink.classList.remove("d-none");
      }
      
      // Store user ID for real-time updates
      window.currentUserId = me.id;
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

// Load dashboard statistics
async function loadDashboardStats() {
  try {
    // Load leaderboard to get user's rank and points
    const leaderboardRes = await authFetch("/api/tournaments/leaderboard");
    if (leaderboardRes.ok) {
      const data = await leaderboardRes.json();
      const currentUserEmail = getEmail();
      
      // Find current user in leaderboard
      const userEntry = data.leaderboard.find(entry => entry.user_name === currentUserEmail || entry.email === currentUserEmail);
      
      if (userEntry) {
        document.getElementById("userRank").textContent = `#${userEntry.rank || '—'}`;
        document.getElementById("userPoints").textContent = userEntry.points || '0';
      }
    }
    
    // Load active tournaments count
    const tournamentsRes = await authFetch("/api/tournaments");
    if (tournamentsRes.ok) {
      const tournaments = await tournamentsRes.json();
      const activeTournaments = tournaments.filter(t => t.status === 'active').length;
      document.getElementById("activeTournaments").textContent = activeTournaments;
    }
  } catch (e) {
    console.error("Error loading dashboard stats:", e);
  }
}

// Load notifications for dropdown
async function loadNotifications() {
  try {
    const res = await authFetch("/api/users/notifications?limit=10");
    if (res.ok) {
      const notifications = await res.json();
      
      // Update badge
      const unreadCount = notifications.filter(n => !n.is_read).length;
      const badge = document.getElementById("notificationBadge");
      if (unreadCount > 0) {
        badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
        badge.style.display = 'flex';
      } else {
        badge.style.display = 'none';
      }
      
      // Update dropdown
      const dropdown = document.getElementById("notificationDropdown");
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
    }
  } catch (e) {
    console.error("Error loading notifications:", e);
  }
}

// Load recent notifications for dashboard widget
async function loadRecentNotifications() {
  try {
    const res = await authFetch("/api/users/notifications?limit=5");
    if (res.ok) {
      const notifications = await res.json();
      
      const container = document.getElementById("recentNotifications");
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
    }
  } catch (e) {
    console.error("Error loading recent notifications:", e);
  }
}

// Load latest blog posts
async function loadLatestBlogPosts() {
  try {
    const res = await fetch("/api/users/blog/posts?limit=3");
    if (res.ok) {
      const posts = await res.json();
      
      const container = document.getElementById("latestBlogPosts");
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
    }
  } catch (e) {
    console.error("Error loading blog posts:", e);
  }
}

// Mark notification as read
async function markNotificationRead(notificationId) {
  try {
    const res = await authFetch(`/api/users/notifications/${notificationId}/read`, {
      method: 'PUT'
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
      // Update stats if user's position changed
      loadDashboardStats();
    });
    
    socket.on('new_notification', (notification) => {
      console.log('New notification received:', notification);
      // Show toast
      showToast(notification.title, notification.message, notification.type);
      // Reload notifications
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
