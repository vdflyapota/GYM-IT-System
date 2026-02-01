// Leaderboard functionality
const API_BASE = '/api/tournaments';

let leaderboardData = [];
let currentSort = 'points'; // Default sort by points
let currentOrder = 'desc';
let searchQuery = '';
let roleFilter = 'all';

// Fetch leaderboard data from API
async function fetchLeaderboard() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login.html';
            return;
        }

        const response = await fetch(`${API_BASE}/leaderboard`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login.html';
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to fetch leaderboard data');
        }

        const data = await response.json();
        leaderboardData = data.leaderboard || [];
        
        updateStats(data);
        renderLeaderboard();
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        showToast('Failed to load leaderboard', 'error');
    }
}

// Update statistics cards
function updateStats(data) {
    const totalPlayers = data.total_players || 0;
    const activePlayers = leaderboardData.filter(p => p.tournaments_played > 0).length;
    const totalTournaments = Math.max(...leaderboardData.map(p => p.tournaments_played), 0);
    const totalMatches = leaderboardData.reduce((sum, p) => sum + p.total_wins + p.total_losses, 0);

    document.getElementById('totalPlayers').textContent = totalPlayers;
    document.getElementById('activePlayers').textContent = activePlayers;
    document.getElementById('totalTournaments').textContent = totalTournaments;
    document.getElementById('totalMatches').textContent = totalMatches;
}

// Render leaderboard table
function renderLeaderboard() {
    const tbody = document.getElementById('leaderboardBody');
    if (!tbody) return;

    // Filter data
    let filteredData = leaderboardData.filter(player => {
        // Search filter
        const matchesSearch = player.user_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            player.email.toLowerCase().includes(searchQuery.toLowerCase());
        
        // Role filter
        const matchesRole = roleFilter === 'all' || player.role === roleFilter;
        
        return matchesSearch && matchesRole;
    });

    // Sort data
    filteredData.sort((a, b) => {
        let aVal = a[currentSort];
        let bVal = b[currentSort];
        
        if (currentSort === 'user_name') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        if (currentOrder === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    // Render rows
    tbody.innerHTML = '';
    
    if (filteredData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="fas fa-search fa-2x mb-2"></i>
                    <p>No players found matching your criteria</p>
                </td>
            </tr>
        `;
        return;
    }

    filteredData.forEach((player, index) => {
        const row = createLeaderboardRow(player, index + 1);
        tbody.appendChild(row);
    });
}

// Create a leaderboard table row
function createLeaderboardRow(player, displayRank) {
    const tr = document.createElement('tr');
    
    // Add highlight for top 3
    if (player.rank === 1) tr.classList.add('table-warning');
    else if (player.rank === 2) tr.classList.add('table-secondary');
    else if (player.rank === 3) tr.classList.add('table-light');
    
    // Medal for top 3
    let medal = '';
    if (player.rank === 1) medal = '🥇';
    else if (player.rank === 2) medal = '🥈';
    else if (player.rank === 3) medal = '🥉';
    
    // Role badge
    let roleBadge = '';
    if (player.role === 'admin') {
        roleBadge = '<span class="badge bg-danger ms-2">Admin</span>';
    } else if (player.role === 'trainer') {
        roleBadge = '<span class="badge bg-primary ms-2">Trainer</span>';
    } else {
        roleBadge = '<span class="badge bg-secondary ms-2">Member</span>';
    }
    
    tr.innerHTML = `
        <td class="text-center fw-bold">${displayRank} ${medal}</td>
        <td>
            ${escapeHtml(player.user_name)}${roleBadge}
            <br><small class="text-muted">${escapeHtml(player.email)}</small>
        </td>
        <td class="text-center">${player.points}</td>
        <td class="text-center">${player.tournaments_played}</td>
        <td class="text-center">
            <span class="badge bg-success">${player.tournament_wins}</span>
        </td>
        <td class="text-center">${player.total_wins}</td>
        <td class="text-center">${player.total_losses}</td>
        <td class="text-center">
            <div class="progress" style="height: 20px;">
                <div class="progress-bar ${player.win_rate >= 50 ? 'bg-success' : 'bg-warning'}" 
                     role="progressbar" 
                     style="width: ${player.win_rate}%"
                     aria-valuenow="${player.win_rate}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${player.win_rate}%
                </div>
            </div>
        </td>
    `;
    
    return tr;
}

// Sort by column
function sortBy(column) {
    if (currentSort === column) {
        // Toggle order
        currentOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort = column;
        currentOrder = 'desc';
    }
    
    updateSortIndicators();
    renderLeaderboard();
}

// Update sort indicators in table headers
function updateSortIndicators() {
    // Remove all existing sort indicators
    document.querySelectorAll('th.sortable i').forEach(icon => {
        icon.className = 'fas fa-sort ms-1 text-muted';
    });
    
    // Add indicator to current sort column
    const currentHeader = document.querySelector(`th.sortable[data-sort="${currentSort}"] i`);
    if (currentHeader) {
        currentHeader.className = currentOrder === 'asc' 
            ? 'fas fa-sort-up ms-1' 
            : 'fas fa-sort-down ms-1';
    }
}

// Search functionality
function searchLeaderboard() {
    const searchInput = document.getElementById('searchInput');
    searchQuery = searchInput ? searchInput.value : '';
    renderLeaderboard();
}

// Filter by role
function filterByRole() {
    const roleSelect = document.getElementById('roleFilter');
    roleFilter = roleSelect ? roleSelect.value : 'all';
    renderLeaderboard();
}

// Refresh leaderboard
async function refreshLeaderboard() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Refreshing...';
    }
    
    await fetchLeaderboard();
    
    if (refreshBtn) {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
    }
    
    showToast('Leaderboard refreshed', 'success');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '11';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login.html';
        return;
    }
    
    // Load leaderboard
    fetchLeaderboard();
    
    // Set up event listeners
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', searchLeaderboard);
    }
    
    const roleFilter = document.getElementById('roleFilter');
    if (roleFilter) {
        roleFilter.addEventListener('change', filterByRole);
    }
    
    // Make sortable headers clickable
    document.querySelectorAll('th.sortable').forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const sortColumn = header.getAttribute('data-sort');
            if (sortColumn) {
                sortBy(sortColumn);
            }
        });
    });
});
