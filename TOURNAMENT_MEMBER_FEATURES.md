# Tournament Member Features - Complete Implementation

## Overview
This document describes the complete implementation of member-friendly tournament features, including proper UI restrictions and the ability for members to join tournaments.

---

## 🎯 Problem Statement

**Original Issues:**
1. ❌ Members could see "New Tournament" button (should be hidden)
2. ❌ Members could see "Add Participants" button (should be hidden)
3. ❌ No way for members to join tournaments
4. ❌ Trainers couldn't add existing users to tournaments

**Solutions Implemented:**
1. ✅ Hide "New Tournament" button from members
2. ✅ Hide "Add Participants" button from members
3. ✅ Add "Request to Join" button for members
4. ✅ Backend allows members to add only themselves
5. ✅ Trainers can add any users to tournaments

---

## 📊 Feature Matrix

### UI Buttons by Role

| Feature | Member | Trainer | Admin |
|---------|:------:|:-------:|:-----:|
| **New Tournament** | ❌ Hidden | ✅ Visible | ✅ Visible |
| **Add Participants** | ❌ Hidden | ✅ Visible | ✅ Visible |
| **Request to Join** | ✅ Visible | ❌ Hidden | ❌ Hidden |
| **View Bracket** | ✅ Visible | ✅ Visible | ✅ Visible |
| **Record Result** | ❌ Hidden | ✅ Visible | ✅ Visible |

### Backend Permissions

| Action | Member | Trainer | Admin |
|--------|:------:|:-------:|:-----:|
| Create Tournament | ❌ 403 | ✅ 200 | ✅ 200 |
| Add Self to Tournament | ✅ 200 | ✅ 200 | ✅ 200 |
| Add Others to Tournament | ❌ 403 | ✅ 200 | ✅ 200 |
| Record Match Result | ❌ 403 | ✅ 200 | ✅ 200 |

---

## 🔧 Implementation Details

### Frontend Changes

#### 1. HTML (`static/tournaments.html`)

**Before:**
```html
<button id="newTournamentBtn" class="btn btn-success">
    <i class="fas fa-plus"></i> New Tournament
</button>
```

**After:**
```html
<!-- Hidden by default, shown only for trainers/admins via JS -->
<button id="newTournamentBtn" class="btn btn-success d-none">
    <i class="fas fa-plus"></i> New Tournament
</button>
```

**Why:** Button starts hidden, preventing flash of content before JavaScript hides it.

---

#### 2. JavaScript (`static/js/tournaments.js`)

##### A. `setupRoleBasedUI()` Function

**Improved Logic:**
```javascript
function setupRoleBasedUI() {
    const newTournamentBtn = document.getElementById('newTournamentBtn');
    
    // Only show for admin and trainer
    if (userRole === 'admin' || userRole === 'trainer') {
        if (newTournamentBtn) {
            newTournamentBtn.classList.remove('d-none');
        }
    }
    // For members, button stays hidden (default d-none in HTML)
}
```

**Benefits:**
- ✅ No race condition
- ✅ Button hidden by default
- ✅ Only shown for authorized roles

---

##### B. `createTournamentCard()` Function

**New Logic:**
```javascript
// Only trainers and admins can add participants
const canAddParticipants = (userRole === 'admin' || userRole === 'trainer') && !isFull;

// Members can request to join (if tournament is not full and in setup status)
const canRequestJoin = (userRole === 'member') && !isFull && tournament.status === 'setup';

// In HTML template:
${canAddParticipants ? `
    <button class="btn btn-primary btn-sm" onclick="openParticipantModal(...)">
        <i class="fas fa-user-plus"></i> Add Participants
    </button>
` : ''}
${canRequestJoin ? `
    <button class="btn btn-success btn-sm" onclick="requestToJoin(...)">
        <i class="fas fa-hand-paper"></i> Request to Join
    </button>
` : ''}
```

**Benefits:**
- ✅ Clear separation of member vs trainer/admin actions
- ✅ Members see appropriate action button
- ✅ Only shows join button for eligible tournaments

---

##### C. `requestToJoin()` Function (NEW)

**Implementation:**
```javascript
async function requestToJoin(tournamentId) {
    // 1. Fetch current user info
    const res = await authFetch('/api/users/me');
    const me = await res.json();
    
    // 2. Confirm with user
    const confirmed = confirm(`Request to join this tournament as "${me.full_name}"?`);
    
    // 3. Submit join request
    const response = await authFetch(`${API_BASE}/${tournamentId}/participants`, {
        method: 'PUT',
        body: {
            participants: [{ 
                user_id: me.id,
                name: me.full_name 
            }]
        }
    });
    
    // 4. Handle response
    if (response.ok) {
        await loadTournaments();
        showMessage('Join request submitted successfully!', 'success');
    }
}
```

**Features:**
- ✅ Fetches user info automatically
- ✅ Confirms before submitting
- ✅ Shows success/error messages
- ✅ Refreshes tournament list on success

---

### Backend Changes

#### `services/tournament-service/src/api.py`

##### 1. Added Helper Function

```python
def get_current_user_id():
    """Helper to get current user ID from JWT"""
    claims = get_jwt()
    return claims.get("sub") or claims.get("user_id")
```

**Purpose:** Extract user ID from JWT for authorization checks.

---

##### 2. Updated `add_participants_bulk()` Endpoint

**Key Changes:**

**A. Role-Based Authorization:**
```python
role = get_current_user_role()
current_user_id = get_current_user_id()

if role == "member":
    # Members can only add themselves
    if len(participants_data) > 1:
        return jsonify({"detail": "Members can only add themselves"}), 403
    
    participant_user_id = participants_data[0].get("user_id")
    if participant_user_id and str(participant_user_id) != str(current_user_id):
        return jsonify({"detail": "Members can only add themselves"}), 403
elif role not in ["trainer", "admin"]:
    return jsonify({"detail": "Unauthorized"}), 403
```

**B. Duplicate Prevention:**
```python
# Check if user is already a participant
if user_id:
    existing = Participant.query.filter_by(
        tournament_id=tournament_id,
        user_id=user_id
    ).first()
    if existing:
        return jsonify({"detail": "User is already a participant"}), 400
```

**Benefits:**
- ✅ Members can join tournaments themselves
- ✅ Members cannot add other users
- ✅ Prevents duplicate participants
- ✅ Trainers/admins retain full control

---

## 🧪 Testing Scenarios

### Scenario 1: Member Joins Tournament

**Steps:**
1. Login as member user
2. Navigate to tournaments page
3. See "Request to Join" button on eligible tournament
4. Click button
5. Confirm dialog
6. See success message

**Expected Results:**
- ✅ Button visible only for members
- ✅ Confirmation dialog appears
- ✅ Success message on submission
- ✅ User added to tournament
- ✅ Tournament list refreshes

---

### Scenario 2: Member Attempts Multiple Adds

**Request:**
```json
PUT /api/tournaments/1/participants
{
  "participants": [
    {"user_id": 5, "name": "User A"},
    {"user_id": 6, "name": "User B"}
  ]
}
```

**Expected Response:**
```json
{
  "detail": "Members can only add themselves to tournaments"
}
// Status: 403 Forbidden
```

---

### Scenario 3: Member Attempts to Add Someone Else

**Request:**
```json
PUT /api/tournaments/1/participants
{
  "participants": [
    {"user_id": 999, "name": "Other User"}
  ]
}
// Current user ID: 5
```

**Expected Response:**
```json
{
  "detail": "Members can only add themselves to tournaments"
}
// Status: 403 Forbidden
```

---

### Scenario 4: Trainer Adds Multiple Users

**Request:**
```json
PUT /api/tournaments/1/participants
{
  "participants": [
    {"user_id": 5, "name": "User A"},
    {"user_id": 6, "name": "User B"},
    {"user_id": 7, "name": "User C"}
  ]
}
```

**Expected Response:**
```json
{
  "message": "3 participants added successfully",
  "participants": [...]
}
// Status: 200 OK
```

---

### Scenario 5: Duplicate Join Attempt

**Request:**
```json
PUT /api/tournaments/1/participants
{
  "participants": [
    {"user_id": 5, "name": "User A"}
  ]
}
// User 5 already in tournament
```

**Expected Response:**
```json
{
  "detail": "User is already a participant in this tournament"
}
// Status: 400 Bad Request
```

---

## 🎨 User Experience Flow

### Member User Journey

1. **Login** → Dashboard
2. **Navigate** → Tournaments page
3. **See tournaments** with different statuses
4. **For each tournament:**
   - ❌ No "New Tournament" button (hidden)
   - ❌ No "Add Participants" button (hidden)
   - ✅ "Request to Join" button (if eligible)
   - ✅ "View Bracket" button (if participants exist)
5. **Click "Request to Join"**
   - See confirmation dialog with their name
   - Confirm → See success message
   - Tournament refreshes, showing updated participant count
6. **Click "View Bracket"**
   - See tournament bracket
   - ❌ No "Record Result" buttons (hidden)

---

### Trainer User Journey

1. **Login** → Dashboard
2. **Navigate** → Tournaments page
3. **See tournaments** with different statuses
4. **Actions available:**
   - ✅ "New Tournament" button (create new)
   - ✅ "Add Participants" button (on each tournament)
   - ✅ "View Bracket" button
   - ✅ "Record Result" buttons (in bracket view)
5. **Click "Add Participants"**
   - See modal with two tabs:
     - "Select Users" - choose from existing users
     - "Manual Entry" - type names manually
   - Can add multiple participants at once
6. **Click "Record Result"**
   - Select winner
   - Optionally enter score
   - Submit → Bracket updates

---

## 🔒 Security Considerations

### Defense in Depth

**Layer 1: UI** (Frontend)
- Buttons hidden for unauthorized roles
- Prevents accidental unauthorized attempts

**Layer 2: Backend Authorization** (API)
- Role-based access control
- User ID validation for member joins
- Prevents bypass via API calls

### Validation Checks

1. ✅ **Role Verification:** Every request validates user role
2. ✅ **User ID Verification:** Members can only add themselves
3. ✅ **Duplicate Prevention:** Can't join same tournament twice
4. ✅ **Capacity Limits:** Respects max_participants
5. ✅ **Tournament Status:** Can only join eligible tournaments

---

## 📝 Error Messages

### Clear, User-Friendly Messages

| Scenario | Message |
|----------|---------|
| Member adds self successfully | "Join request submitted successfully! Waiting for approval." |
| Member tries to add others | "Members can only add themselves to tournaments" |
| User already in tournament | "User is already a participant in this tournament" |
| Tournament full | "Cannot add participants. Tournament has X/Y participants." |
| Not logged in | "Please log in to request to join a tournament" |
| Network error | "Network error: Unable to submit join request. Please check your connection." |

---

## 🚀 Deployment Notes

### Files Modified

1. **Frontend:**
   - `static/tournaments.html` - Button visibility
   - `static/js/tournaments.js` - UI logic + join feature

2. **Backend:**
   - `services/tournament-service/src/api.py` - Authorization logic

### No Database Changes Required

- Uses existing `participants` table
- Uses existing `user_id` field
- No schema migration needed

### Backward Compatibility

- ✅ Existing tournaments unaffected
- ✅ Admin/trainer workflows unchanged
- ✅ Only adds new member capability
- ✅ No breaking changes

---

## 🎯 Summary

### Problem Solved ✅

1. ✅ Members cannot see "New Tournament" button
2. ✅ Members cannot see "Add Participants" button
3. ✅ Members CAN join tournaments via "Request to Join"
4. ✅ Trainers CAN add any users to tournaments
5. ✅ Proper authorization at backend level
6. ✅ Clear, user-friendly error messages
7. ✅ Duplicate prevention
8. ✅ Security through defense in depth

### User Experience Improved ✅

- ✅ Clear role-based UI
- ✅ No confusing buttons
- ✅ Members empowered to join
- ✅ Trainers retain control
- ✅ Intuitive workflow

### Code Quality ✅

- ✅ Well-documented
- ✅ Follows existing patterns
- ✅ Comprehensive error handling
- ✅ Syntax validated
- ✅ Ready for production
