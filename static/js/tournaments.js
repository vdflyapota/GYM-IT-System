/**
 * Tournament Management JavaScript
 * Handles tournament creation, participant assignment, and bracket visualization
 */

// API base URL
const API_BASE = '/api/tournaments';

// State management
let currentTournaments = [];
let currentTournament = null;

/**
 * Initialize the tournaments page
 */
async function initTournaments() {
    await loadTournaments();
    setupEventListeners();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Create tournament form
    const createForm = document.getElementById('createForm');
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await createTournament();
        });
    }

    // Participant form
    const participantForm = document.getElementById('participantForm');
    if (participantForm) {
        participantForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await addParticipants();
        });
    }
}

/**
 * Load all tournaments from API
 */
async function loadTournaments() {
    try {
        const response = await fetch(API_BASE + '/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            currentTournaments = data.tournaments || [];
            renderTournaments();
        } else {
            console.error('Failed to load tournaments');
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading tournaments:', error);
        showEmptyState();
    }
}

/**
 * Create a new tournament
 */
async function createTournament() {
    const name = document.getElementById('tName').value;
    const maxParticipants = parseInt(document.getElementById('tMax').value);
    const tournamentType = document.getElementById('tType') ? document.getElementById('tType').value : 'single_elimination';

    if (!name) {
        alert('Please enter a tournament name');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(API_BASE + '/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                start_date: new Date().toISOString(),
                max_participants: maxParticipants,
                tournament_type: tournamentType
            })
        });

        if (response.ok) {
            const data = await response.json();
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createModal'));
            if (modal) modal.hide();
            
            // Clear form
            document.getElementById('createForm').reset();
            
            // Reload tournaments
            await loadTournaments();
            
            // Show success message
            showMessage('Tournament created successfully!', 'success');
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to create tournament');
        }
    } catch (error) {
        console.error('Error creating tournament:', error);
        alert('Failed to create tournament');
    }
}

/**
 * Render tournaments grid
 */
function renderTournaments() {
    const grid = document.getElementById('tournamentGrid');
    const emptyState = document.getElementById('emptyState');

    if (!currentTournaments || currentTournaments.length === 0) {
        showEmptyState();
        return;
    }

    grid.innerHTML = '';
    emptyState?.classList.add('d-none');

    currentTournaments.forEach(tournament => {
        const card = createTournamentCard(tournament);
        grid.appendChild(card);
    });
}

/**
 * Create a tournament card element
 */
function createTournamentCard(tournament) {
    const col = document.createElement('div');
    col.className = 'col-md-4';

    const statusBadge = getStatusBadge(tournament.status);
    const participantText = `${tournament.participant_count}/${tournament.max_participants}`;
    const isFull = tournament.participant_count >= tournament.max_participants;

    col.innerHTML = `
        <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
                <div class="d-flex justify-content-between mb-3">
                    <span class="badge ${statusBadge.class}">${statusBadge.text}</span>
                    <small class="text-muted">
                        <i class="fas fa-users"></i> ${participantText} ${isFull ? 'Full' : ''}
                    </small>
                </div>
                <h4 class="card-title fw-bold">${escapeHtml(tournament.name)}</h4>
                <p class="text-muted small">
                    ${tournament.tournament_type.replace('_', ' ').toUpperCase()} • 
                    ${tournament.max_participants} Participants
                </p>
                <div class="d-grid gap-2 mt-4">
                    ${!isFull ? `
                        <button class="btn btn-primary btn-sm" onclick="openParticipantModal(${tournament.id})">
                            <i class="fas fa-user-plus"></i> Add Participants
                        </button>
                    ` : ''}
                    ${tournament.participant_count > 0 ? `
                        <button class="btn btn-outline-dark btn-sm" onclick="viewBracket(${tournament.id})">
                            <i class="fas fa-sitemap"></i> View Bracket
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;

    return col;
}

/**
 * Get status badge configuration
 */
function getStatusBadge(status) {
    const badges = {
        'setup': { class: 'bg-warning', text: 'SETUP' },
        'active': { class: 'bg-success', text: 'ACTIVE' },
        'completed': { class: 'bg-secondary', text: 'COMPLETED' }
    };
    return badges[status] || { class: 'bg-secondary', text: status.toUpperCase() };
}

/**
 * Open participant assignment modal
 */
async function openParticipantModal(tournamentId) {
    currentTournament = currentTournaments.find(t => t.id === tournamentId);
    if (!currentTournament) return;

    const modal = new bootstrap.Modal(document.getElementById('participantModal'));
    modal.show();
}

/**
 * Add participants to tournament
 */
async function addParticipants() {
    if (!currentTournament) return;

    const participantNames = document.getElementById('participantNames').value;
    if (!participantNames) {
        alert('Please enter participant names');
        return;
    }

    // Split by newlines and filter empty
    const names = participantNames.split('\n')
        .map(name => name.trim())
        .filter(name => name.length > 0);

    if (names.length === 0) {
        alert('Please enter at least one participant name');
        return;
    }

    const participants = names.map(name => ({ name }));

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/${currentTournament.id}/participants`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ participants })
        });

        if (response.ok) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('participantModal'));
            if (modal) modal.hide();
            
            // Clear form
            document.getElementById('participantForm').reset();
            
            // Reload tournaments
            await loadTournaments();
            
            showMessage('Participants added successfully!', 'success');
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to add participants');
        }
    } catch (error) {
        console.error('Error adding participants:', error);
        alert('Failed to add participants');
    }
}

/**
 * View tournament bracket
 */
async function viewBracket(tournamentId) {
    try {
        const response = await fetch(`${API_BASE}/${tournamentId}/bracket`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            renderBracket(data.tournament, data.bracket);
            
            const modal = new bootstrap.Modal(document.getElementById('bracketModal'));
            modal.show();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to load bracket');
        }
    } catch (error) {
        console.error('Error loading bracket:', error);
        alert('Failed to load bracket');
    }
}

/**
 * Render bracket visualization
 */
function renderBracket(tournament, bracket) {
    const container = document.getElementById('bracketContainer');
    if (!container) return;

    // Set tournament name in modal
    const title = document.querySelector('#bracketModal .modal-title');
    if (title) {
        title.textContent = `${tournament.name} - Bracket`;
    }

    // Group brackets by round
    const rounds = {};
    bracket.forEach(match => {
        if (!rounds[match.round]) {
            rounds[match.round] = [];
        }
        rounds[match.round].push(match);
    });

    // Build bracket HTML
    let html = '<div class="bracket-container d-flex justify-content-around align-items-center gap-4" style="overflow-x: auto; min-height: 400px;">';

    Object.keys(rounds).sort((a, b) => parseInt(a) - parseInt(b)).forEach(roundNum => {
        const matches = rounds[roundNum];
        const roundName = getRoundName(roundNum, Object.keys(rounds).length);

        html += `<div class="bracket-round">
            <h6 class="text-center mb-3 text-muted">${roundName}</h6>
            <div class="d-flex flex-column gap-4">`;

        matches.forEach(match => {
            const p1Name = match.participant1 ? match.participant1.name : 'TBD';
            const p2Name = match.participant2 ? match.participant2.name : 'TBD';
            const isDecided = match.winner_id !== null;
            const winner = isDecided ? (match.winner?.name || '') : null;

            html += `<div class="bracket-match border rounded p-2 bg-white shadow-sm" style="min-width: 200px;">
                <div class="match-participant ${match.winner_id === match.participant1?.id ? 'fw-bold text-success' : ''}">
                    ${escapeHtml(p1Name)}
                </div>
                <div class="text-center text-muted small">vs</div>
                <div class="match-participant ${match.winner_id === match.participant2?.id ? 'fw-bold text-success' : ''}">
                    ${escapeHtml(p2Name)}
                </div>
                ${match.score ? `<div class="text-center small text-muted mt-1">${escapeHtml(match.score)}</div>` : ''}
            </div>`;
        });

        html += `</div></div>`;

        // Add arrow between rounds
        if (parseInt(roundNum) < Object.keys(rounds).length) {
            html += '<div class="display-4 text-muted">&rarr;</div>';
        }
    });

    html += '</div>';

    container.innerHTML = html;
}

/**
 * Get round name based on round number
 */
function getRoundName(roundNum, totalRounds) {
    const round = parseInt(roundNum);
    const total = parseInt(totalRounds);

    if (round === total) return 'Final';
    if (round === total - 1) return 'Semi-Finals';
    if (round === total - 2) return 'Quarter-Finals';
    return `Round ${round}`;
}

/**
 * Show empty state
 */
function showEmptyState() {
    const grid = document.getElementById('tournamentGrid');
    const emptyState = document.getElementById('emptyState');

    if (grid) grid.innerHTML = '';
    if (emptyState) emptyState.classList.remove('d-none');
}

/**
 * Show message toast
 */
function showMessage(message, type = 'info') {
    // Create a simple toast notification
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : 'info'} alert-dismissible fade show`;
    toast.setAttribute('role', 'alert');
    toast.style.cssText = 'position: relative; margin-bottom: 10px;';
    
    toast.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 150);
    }, 3000);
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
    document.body.appendChild(container);
    return container;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTournaments);
} else {
    initTournaments();
}
