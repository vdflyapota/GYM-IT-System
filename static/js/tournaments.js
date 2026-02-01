/**
 * Tournament Management JavaScript
 * Handles tournament creation, participant assignment, and bracket visualization
 */

// API base URL
const API_BASE = '/api/tournaments';

// State management
let currentTournaments = [];
let currentTournament = null;
let userRole = null;

/**
 * Initialize the tournaments page
 */
async function initTournaments() {
    // Get user role first
    userRole = await getUserRole();
    
    // Setup UI based on role
    setupRoleBasedUI();
    
    await loadTournaments();
    setupEventListeners();
}

/**
 * Get current user's role
 */
async function getUserRole() {
    try {
        // First try from auth.js helper
        if (typeof getRole === 'function') {
            const role = getRole();
            if (role) return role;
        }
        
        // Fallback: fetch from API
        const res = await authFetch('/api/users/me');
        if (res.ok) {
            const me = await res.json();
            return me.role || 'member';
        }
    } catch (e) {
        console.warn('Could not determine user role:', e);
    }
    return 'member'; // default to member
}

/**
 * Setup UI elements based on user role
 */
function setupRoleBasedUI() {
    const newTournamentBtn = document.getElementById('newTournamentBtn');
    
    // Only admin and trainer can create tournaments
    // Members cannot see the "New Tournament" button
    if (userRole === 'admin' || userRole === 'trainer') {
        if (newTournamentBtn) {
            newTournamentBtn.classList.remove('d-none');
        }
    }
    // For members, button stays hidden (default d-none in HTML)
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
        // Use authFetch from auth.js if available, otherwise fall back to manual token
        const fetchFn = typeof authFetch !== 'undefined' ? authFetch : fetch;
        const headers = typeof authFetch !== 'undefined' ? {} : {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
        };
        
        const response = await fetchFn(API_BASE + '/', {
            method: 'GET',
            headers: headers
        });

        if (response.ok) {
            const data = await response.json();
            currentTournaments = data.tournaments || [];
            renderTournaments();
        } else {
            console.error('Failed to load tournaments:', response.status, response.statusText);
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
    const startDate = document.getElementById('tStartDate').value;
    const deadline = document.getElementById('tDeadline').value;
    const maxParticipants = parseInt(document.getElementById('tMax').value);
    const tournamentType = document.getElementById('tType') ? document.getElementById('tType').value : 'single_elimination';

    if (!name) {
        alert('Please enter a tournament name');
        return;
    }

    if (!startDate) {
        alert('Please select a tournament start date');
        return;
    }

    try {
        // Prepare request body
        const requestBody = {
            name: name,
            start_date: new Date(startDate).toISOString(),
            max_participants: maxParticipants,
            tournament_type: tournamentType
        };

        // Add registration_deadline if provided
        if (deadline) {
            requestBody.registration_deadline = new Date(deadline).toISOString();
        }

        // Use authFetch from auth.js if available, otherwise fall back to manual token
        const fetchFn = typeof authFetch !== 'undefined' ? authFetch : fetch;
        const headers = typeof authFetch !== 'undefined' ? {} : {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
        };
        
        const response = await fetchFn(API_BASE + '/', {
            method: 'POST',
            headers: headers,
            body: typeof authFetch !== 'undefined' ? requestBody : JSON.stringify(requestBody)
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
            let errorMessage = 'Failed to create tournament';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.error || errorData.message || errorData.msg || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText || errorMessage;
            }
            
            // Show specific error message based on status
            if (response.status === 401) {
                errorMessage = 'Please log in to create tournaments';
            } else if (response.status === 403) {
                errorMessage = 'You need trainer or admin privileges to create tournaments';
            }
            
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error creating tournament:', error);
        alert('Network error: Unable to create tournament. Please check your connection.');
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
    
    // Check if registration deadline has passed
    const now = new Date();
    const deadlinePassed = tournament.registration_deadline && new Date(tournament.registration_deadline) < now;
    
    // Format deadline for display
    let deadlineDisplay = '';
    if (tournament.registration_deadline) {
        const deadline = new Date(tournament.registration_deadline);
        const timeLeft = deadline - now;
        
        if (deadlinePassed) {
            deadlineDisplay = `
                <div class="alert alert-danger py-1 px-2 mb-2 small">
                    <i class="fas fa-clock"></i> Registration Closed
                </div>
            `;
        } else {
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            
            let timeText = '';
            if (days > 0) {
                timeText = `${days}d ${hours}h left`;
            } else if (hours > 0) {
                timeText = `${hours}h left`;
            } else {
                const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                timeText = `${minutes}m left`;
            }
            
            deadlineDisplay = `
                <div class="alert alert-info py-1 px-2 mb-2 small">
                    <i class="fas fa-clock"></i> Register by: ${deadline.toLocaleString()} (${timeText})
                </div>
            `;
        }
    }
    
    // Only trainers and admins can add participants
    const canAddParticipants = (userRole === 'admin' || userRole === 'trainer') && !isFull;
    
    // Members can request to join (if tournament is not full, in setup status, and deadline hasn't passed)
    const canRequestJoin = (userRole === 'member') && !isFull && tournament.status === 'setup' && !deadlinePassed;
    
    // Trainers and admins can generate bracket when status is setup
    const canGenerateBracket = (userRole === 'admin' || userRole === 'trainer') && tournament.status === 'setup' && tournament.participant_count >= 2;
    
    // Trainers and admins can delete tournaments
    const canDelete = (userRole === 'admin' || userRole === 'trainer');

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
                ${deadlineDisplay}
                <div class="d-grid gap-2 mt-4">
                    ${canAddParticipants ? `
                        <button class="btn btn-primary btn-sm" onclick="openParticipantModal(${tournament.id})">
                            <i class="fas fa-user-plus"></i> Add Participants
                        </button>
                    ` : ''}
                    ${canRequestJoin ? `
                        <button class="btn btn-success btn-sm" onclick="requestToJoin(${tournament.id})">
                            <i class="fas fa-hand-paper"></i> Request to Join
                        </button>
                    ` : ''}
                    ${deadlinePassed && userRole === 'member' && tournament.status === 'setup' ? `
                        <button class="btn btn-secondary btn-sm" disabled>
                            <i class="fas fa-ban"></i> Registration Closed
                        </button>
                    ` : ''}
                    ${canGenerateBracket ? `
                        <button class="btn btn-warning btn-sm" onclick="generateBracket(${tournament.id})">
                            <i class="fas fa-sitemap"></i> Generate Bracket
                        </button>
                    ` : ''}
                    ${tournament.participant_count > 0 ? `
                        <button class="btn btn-outline-dark btn-sm" onclick="viewBracket(${tournament.id})">
                            <i class="fas fa-sitemap"></i> View Bracket
                        </button>
                    ` : ''}
                    ${canDelete ? `
                        <button class="btn btn-danger btn-sm" onclick="deleteTournament(${tournament.id}, '${escapeHtml(tournament.name)}')">
                            <i class="fas fa-trash"></i> Delete
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

    // Load pending requests and available users
    await loadPendingParticipants();
    await loadAvailableUsers();

    const modal = new bootstrap.Modal(document.getElementById('participantModal'));
    modal.show();
}

/**
 * Load pending participants for tournament
 */
async function loadPendingParticipants() {
    const pendingList = document.getElementById('pendingList');
    if (!pendingList || !currentTournament) return;

    try {
        const response = await authFetch(`${API_BASE}/${currentTournament.id}/participants`);
        
        if (response.ok) {
            const participants = await response.json();
            const pending = participants.filter(p => p.status === 'pending');
            
            if (pending.length === 0) {
                pendingList.innerHTML = '<p class="text-muted">No pending requests</p>';
                return;
            }

            pendingList.innerHTML = pending.map(participant => `
                <div class="card mb-2">
                    <div class="card-body py-2 px-3">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${escapeHtml(participant.name)}</strong>
                                <small class="text-muted d-block">Requested: ${new Date(participant.created_at).toLocaleDateString()}</small>
                            </div>
                            <button class="btn btn-sm btn-success" onclick="approveParticipant(${participant.id})">
                                <i class="fas fa-check"></i> Approve
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            pendingList.innerHTML = '<p class="text-danger">Failed to load pending requests</p>';
        }
    } catch (error) {
        console.error('Error loading pending participants:', error);
        pendingList.innerHTML = '<p class="text-danger">Error loading pending requests</p>';
    }
}

/**
 * Approve a pending participant
 */
async function approveParticipant(participantId) {
    if (!currentTournament) return;
    
    try {
        const response = await authFetch(`${API_BASE}/${currentTournament.id}/participants/${participantId}/approve`, {
            method: 'PATCH'
        });
        
        if (response.ok) {
            showMessage('Participant approved successfully!', 'success');
            await loadPendingParticipants();
            await loadTournaments();
        } else {
            let errorMessage = 'Failed to approve participant';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.error || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error approving participant:', error);
        alert('Network error: Unable to approve participant. Please check your connection.');
    }
}

/**
 * Load available users for tournament
 */
async function loadAvailableUsers() {
    const usersList = document.getElementById('usersList');
    if (!usersList) return;

    try {
        const fetchFn = typeof authFetch !== 'undefined' ? authFetch : fetch;
        const headers = typeof authFetch !== 'undefined' ? {} : {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
        };

        const response = await fetchFn(`${API_BASE}/available-users`, {
            method: 'GET',
            headers: headers
        });

        if (response.ok) {
            const data = await response.json();
            const users = data.users || [];
            
            if (users.length === 0) {
                usersList.innerHTML = '<p class="text-muted">No users available</p>';
                return;
            }

            usersList.innerHTML = users.map(user => `
                <div class="form-check mb-2">
                    <input class="form-check-input user-checkbox" type="checkbox" value="${user.id}" 
                           id="user-${user.id}" data-name="${escapeHtml(user.name)}">
                    <label class="form-check-label" for="user-${user.id}">
                        ${escapeHtml(user.name)} <small class="text-muted">(${escapeHtml(user.email)})</small>
                    </label>
                </div>
            `).join('');
        } else {
            usersList.innerHTML = '<p class="text-danger">Failed to load users</p>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        usersList.innerHTML = '<p class="text-danger">Error loading users</p>';
    }
}

/**
 * Add selected users to tournament
 */
async function addSelectedUsers() {
    if (!currentTournament) return;

    const checkboxes = document.querySelectorAll('.user-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('Please select at least one user');
        return;
    }

    const participants = Array.from(checkboxes).map(cb => ({
        user_id: parseInt(cb.value),
        name: cb.dataset.name
    }));

    try {
        const fetchFn = typeof authFetch !== 'undefined' ? authFetch : fetch;
        const headers = typeof authFetch !== 'undefined' ? {} : {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
        };

        const response = await fetchFn(`${API_BASE}/${currentTournament.id}/participants`, {
            method: 'PUT',
            headers: headers,
            body: typeof authFetch !== 'undefined' ? { participants } : JSON.stringify({ participants })
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('participantModal'));
            if (modal) modal.hide();
            
            await loadTournaments();
            showMessage('Users added to tournament successfully!', 'success');
        } else {
            let errorMessage = 'Failed to add users';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.error || errorData.message || errorData.msg || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            
            if (response.status === 401) {
                errorMessage = 'Please log in to add participants';
            } else if (response.status === 403) {
                errorMessage = 'You need trainer or admin privileges to add participants';
            }
            
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error adding users:', error);
        alert('Network error: Unable to add users. Please check your connection.');
    }
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
        // Use authFetch from auth.js if available, otherwise fall back to manual token
        const fetchFn = typeof authFetch !== 'undefined' ? authFetch : fetch;
        const headers = typeof authFetch !== 'undefined' ? {} : {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
        };
        
        const response = await fetchFn(`${API_BASE}/${currentTournament.id}/participants`, {
            method: 'PUT',
            headers: headers,
            body: typeof authFetch !== 'undefined' ? { participants } : JSON.stringify({ participants })
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
            let errorMessage = 'Failed to add participants';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorData.msg || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            
            // Show specific error message based on status
            if (response.status === 401) {
                errorMessage = 'Please log in to add participants';
            } else if (response.status === 403) {
                errorMessage = 'You need trainer or admin privileges to add participants';
            }
            
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error adding participants:', error);
        alert('Network error: Unable to add participants. Please check your connection.');
    }
}

/**
 * Request to join a tournament (for members)
 */
async function requestToJoin(tournamentId) {
    try {
        const res = await authFetch('/api/users/me');
        if (!res.ok) {
            alert('Please log in to request to join a tournament');
            return;
        }
        
        const me = await res.json();
        const myName = me.full_name || me.email || 'Unknown';
        
        const confirmed = confirm(`Request to join this tournament as "${myName}"?\n\nYour request will be pending until approved by a trainer or admin.`);
        if (!confirmed) return;
        
        const response = await authFetch(`${API_BASE}/${tournamentId}/participants`, {
            method: 'PUT',
            body: {
                participants: [{ 
                    user_id: me.id,
                    name: myName 
                }]
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            await loadTournaments();
            showMessage(data.message || 'Join request submitted successfully! Waiting for approval.', 'success');
        } else {
            let errorMessage = 'Failed to submit join request';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.error || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error requesting to join tournament:', error);
        alert('Network error: Unable to submit join request. Please check your connection.');
    }
}

/**
 * Delete a tournament
 */
async function deleteTournament(tournamentId, tournamentName) {
    // Confirm deletion
    const confirmed = confirm(`Are you sure you want to delete the tournament "${tournamentName}"?\n\nThis will permanently delete:\n- The tournament\n- All participants\n- All bracket matches\n\nThis action cannot be undone.`);
    
    if (!confirmed) return;
    
    try {
        const response = await authFetch(`${API_BASE}/${tournamentId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showMessage('Tournament deleted successfully!', 'success');
            await loadTournaments();
        } else {
            let errorMessage = 'Failed to delete tournament';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.error || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error deleting tournament:', error);
        alert('Network error: Unable to delete tournament. Please check your connection.');
    }
}

/**
 * Generate tournament bracket
 */
async function generateBracket(tournamentId) {
    if (!confirm('Generate tournament bracket? This will create all matches for the tournament.')) {
        return;
    }
    
    try {
        const response = await authFetch(`${API_BASE}/${tournamentId}/generate-bracket`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showMessage(data.message || 'Bracket generated successfully!', 'success');
            await loadTournaments();
        } else {
            let errorMessage = 'Failed to generate bracket';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.error || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error generating bracket:', error);
        alert('Network error: Unable to generate bracket. Please check your connection.');
    }
}

/**
 * View tournament bracket
 */
async function viewBracket(tournamentId) {
    try {
        // Use authFetch to include JWT token
        const response = await authFetch(`${API_BASE}/${tournamentId}/bracket`, {
            method: 'GET'
        });

        if (response.ok) {
            const data = await response.json();
            await renderBracket(data.tournament, data.bracket);
            
            const modal = new bootstrap.Modal(document.getElementById('bracketModal'));
            modal.show();
        } else {
            let errorMessage = 'Failed to load bracket';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorData.msg || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }
            
            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error loading bracket:', error);
        alert('Network error: Unable to load bracket. Please check your connection.');
    }
}

/**
 * Render bracket visualization
 */
async function renderBracket(tournament, bracket) {
    const container = document.getElementById('bracketContainer');
    if (!container) return;

    // Ensure userRole is set
    if (!userRole) {
        userRole = await getUserRole();
    }

    // Set tournament name in modal
    const title = document.querySelector('#bracketModal .modal-title');
    if (title) {
        title.textContent = `${tournament.name} - Bracket`;
    }

    // Add pause/resume controls for admins
    let controlsHtml = '';
    if (userRole === 'admin') {
        if (tournament.is_paused) {
            controlsHtml = `
                <div class="alert alert-warning mb-3 d-flex justify-content-between align-items-center">
                    <span><i class="fas fa-pause-circle"></i> <strong>Tournament is PAUSED</strong> - Results cannot be recorded</span>
                    <button class="btn btn-sm btn-success" onclick="resumeTournament(${tournament.id})">
                        <i class="fas fa-play"></i> Resume Tournament
                    </button>
                </div>`;
        } else {
            controlsHtml = `
                <div class="mb-3 text-end">
                    <button class="btn btn-sm btn-warning" onclick="pauseTournament(${tournament.id})">
                        <i class="fas fa-pause"></i> Pause Tournament
                    </button>
                </div>`;
        }
    } else if (tournament.is_paused) {
        // Show info to non-admins
        controlsHtml = `
            <div class="alert alert-warning mb-3">
                <i class="fas fa-pause-circle"></i> <strong>Tournament is currently paused</strong>
            </div>`;
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
    let html = controlsHtml + '<div class="bracket-container d-flex justify-content-around align-items-center gap-4" style="overflow-x: auto; min-height: 400px;">';

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
            const canRecordResult = match.participant1 && match.participant2 && !isDecided && !tournament.is_paused;
            const winner = isDecided ? (match.winner?.name || '') : null;
            
            // Only trainers and admins can record match results
            const canRecordAsRole = (userRole === 'admin' || userRole === 'trainer');
            // Only admins can clear results
            const canClearResult = (userRole === 'admin' && isDecided);
            
            const matchDescription = `${escapeHtml(p1Name)} vs ${escapeHtml(p2Name)}`;
            
            console.log('Match:', match.id, 'userRole:', userRole, 'canRecordResult:', canRecordResult, 'canRecordAsRole:', canRecordAsRole);

            html += `<div class="bracket-match border rounded p-2 bg-white shadow-sm" style="min-width: 200px;">
                <div class="match-participant ${match.winner_id === match.participant1?.id ? 'fw-bold text-success' : ''}">
                    ${escapeHtml(p1Name)}
                </div>
                <div class="text-center text-muted small">vs</div>
                <div class="match-participant ${match.winner_id === match.participant2?.id ? 'fw-bold text-success' : ''}">
                    ${escapeHtml(p2Name)}
                </div>
                ${match.score ? `<div class="text-center small text-muted mt-1">${escapeHtml(match.score)}</div>` : ''}
                ${(canRecordResult && canRecordAsRole) ? `<button class="btn btn-sm btn-outline-primary mt-2 w-100 record-result-btn" 
                    data-tournament-id="${tournament.id}" 
                    data-bracket-id="${match.id}"
                    data-p1-id="${match.participant1?.id || 0}"
                    data-p1-name="${escapeHtml(match.participant1?.name || '')}"
                    data-p2-id="${match.participant2?.id || 0}"
                    data-p2-name="${escapeHtml(match.participant2?.name || '')}">
                    <i class="fas fa-trophy"></i> Record Result
                </button>` : ''}
                ${isDecided ? `<div class="text-center small text-success mt-1"><i class="fas fa-check-circle"></i> Winner: ${escapeHtml(winner)}</div>` : ''}
                ${canClearResult ? `<button class="btn btn-sm btn-outline-danger mt-2 w-100" 
                    onclick="clearMatchResult(${tournament.id}, ${match.id}, '${matchDescription}')">
                    <i class="fas fa-undo"></i> Clear Result
                </button>` : ''}
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
    
    // Add event delegation for Record Result buttons
    container.querySelectorAll('.record-result-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tournamentId = parseInt(this.dataset.tournamentId);
            const bracketId = parseInt(this.dataset.bracketId);
            const participant1 = {
                id: parseInt(this.dataset.p1Id),
                name: this.dataset.p1Name
            };
            const participant2 = {
                id: parseInt(this.dataset.p2Id),
                name: this.dataset.p2Name
            };
            openResultModal(tournamentId, bracketId, participant1, participant2);
        });
    });
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

// Global state for current match
let currentMatch = null;

/**
 * Open result recording modal
 */
function openResultModal(tournamentId, bracketId, participant1, participant2) {
    currentMatch = {
        tournamentId: tournamentId,
        bracketId: bracketId,
        participant1: participant1,
        participant2: participant2
    };

    const winnerSelection = document.getElementById('winnerSelection');
    if (!winnerSelection) return;

    winnerSelection.innerHTML = `
        <div class="form-check mb-2">
            <input class="form-check-input" type="radio" name="winner" value="${participant1.id}" id="winner1" required>
            <label class="form-check-label" for="winner1">
                ${escapeHtml(participant1.name)}
            </label>
        </div>
        <div class="form-check mb-2">
            <input class="form-check-input" type="radio" name="winner" value="${participant2.id}" id="winner2" required>
            <label class="form-check-label" for="winner2">
                ${escapeHtml(participant2.name)}
            </label>
        </div>
    `;

    // Clear score field
    const scoreField = document.getElementById('matchScore');
    if (scoreField) scoreField.value = '';

    // Setup form submission
    const form = document.getElementById('resultForm');
    if (form) {
        form.onsubmit = async (e) => {
            e.preventDefault();
            await recordMatchResult();
        };
    }

    const modal = new bootstrap.Modal(document.getElementById('resultModal'));
    modal.show();
}

/**
 * Record match result
 */
async function recordMatchResult() {
    if (!currentMatch) return;

    const winnerRadio = document.querySelector('input[name="winner"]:checked');
    if (!winnerRadio) {
        alert('Please select a winner');
        return;
    }

    const winnerId = parseInt(winnerRadio.value);
    const score = document.getElementById('matchScore').value;

    try {
        const fetchFn = typeof authFetch !== 'undefined' ? authFetch : fetch;
        const headers = typeof authFetch !== 'undefined' ? {} : {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
        };

        const body = { winner_id: winnerId };
        if (score) body.score = score;

        const response = await fetchFn(
            `${API_BASE}/${currentMatch.tournamentId}/bracket/${currentMatch.bracketId}/result`,
            {
                method: 'PUT',
                headers: headers,
                body: typeof authFetch !== 'undefined' ? body : JSON.stringify(body)
            }
        );

        if (response.ok) {
            // Close result modal
            const resultModal = bootstrap.Modal.getInstance(document.getElementById('resultModal'));
            if (resultModal) resultModal.hide();

            // Refresh bracket
            await viewBracket(currentMatch.tournamentId);

            showMessage('Match result recorded successfully!', 'success');
        } else {
            let errorMessage = 'Failed to record result';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorData.msg || errorMessage;
            } catch (e) {
                errorMessage = response.statusText || errorMessage;
            }

            if (response.status === 401) {
                errorMessage = 'Please log in to record results';
            } else if (response.status === 403) {
                errorMessage = 'You need trainer or admin privileges to record results';
            }

            alert(errorMessage);
        }
    } catch (error) {
        console.error('Error recording result:', error);
        alert('Network error: Unable to record result. Please check your connection.');
    }
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

/**
 * Pause tournament (Admin only)
 */
async function pauseTournament(tournamentId) {
    if (!confirm('Are you sure you want to PAUSE this tournament?\n\nThis will prevent recording any new match results until resumed.')) {
        return;
    }

    try {
        const response = await authFetch(`${API_BASE}/${tournamentId}/pause`, {
            method: 'PATCH'
        });

        if (response.ok) {
            showToast('Tournament paused successfully', 'success');
            // Reload bracket view if open
            if (currentTournamentId === tournamentId) {
                viewBracket(tournamentId);
            }
        } else {
            const errorData = await response.json();
            showToast(errorData.detail || 'Failed to pause tournament', 'error');
        }
    } catch (error) {
        console.error('Error pausing tournament:', error);
        showToast('Failed to pause tournament', 'error');
    }
}

/**
 * Resume tournament (Admin only)
 */
async function resumeTournament(tournamentId) {
    if (!confirm('Resume this tournament?\n\nMatch results can be recorded again.')) {
        return;
    }

    try {
        const response = await authFetch(`${API_BASE}/${tournamentId}/resume`, {
            method: 'PATCH'
        });

        if (response.ok) {
            showToast('Tournament resumed successfully', 'success');
            // Reload bracket view if open
            if (currentTournamentId === tournamentId) {
                viewBracket(tournamentId);
            }
        } else {
            const errorData = await response.json();
            showToast(errorData.detail || 'Failed to resume tournament', 'error');
        }
    } catch (error) {
        console.error('Error resuming tournament:', error);
        showToast('Failed to resume tournament', 'error');
    }
}

/**
 * Clear match result (Admin only)
 */
async function clearMatchResult(tournamentId, bracketId, matchDescription) {
    if (!confirm(`Clear result for ${matchDescription}?\n\nWARNING: This will also clear any dependent matches in later rounds.\n\nThis action allows re-recording the correct result.`)) {
        return;
    }

    try {
        const response = await authFetch(`${API_BASE}/${tournamentId}/bracket/${bracketId}/result`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Match result cleared successfully', 'success');
            // Reload bracket view
            viewBracket(tournamentId);
        } else {
            const errorData = await response.json();
            showToast(errorData.detail || 'Failed to clear result', 'error');
        }
    } catch (error) {
        console.error('Error clearing result:', error);
        showToast('Failed to clear result', 'error');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTournaments);
} else {
    initTournaments();
}
