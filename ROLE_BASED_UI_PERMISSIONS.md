# Role-Based UI and Permissions Implementation

## Overview
This document describes the role-based UI and permission improvements implemented for the GYM IT System.

## Changes Made

### 1. Dashboard - Admin Panel Button
**File:** `static/js/dashboard.js`

**Behavior:**
- **Admin users**: Can see the "Admin Panel" button
- **Trainer users**: Cannot see the "Admin Panel" button (hidden)
- **Member users**: Cannot see the "Admin Panel" button (hidden)

**Implementation:**
- Enhanced the user role detection to fetch the actual role from `/api/users/me`
- The Admin Panel button (`#adminLink`) is only shown when `userRole === "admin"`
- Default state is hidden (`d-none` class)

### 2. Tournaments - New Tournament Button
**Files:** `static/tournaments.html`, `static/js/tournaments.js`

**Behavior:**
- **Admin users**: Can see "New Tournament" button and create tournaments
- **Trainer users**: Can see "New Tournament" button and create tournaments
- **Member users**: Cannot see "New Tournament" button (hidden)

**Implementation:**
- Added `id="newTournamentBtn"` to the button in `tournaments.html`
- Added `getUserRole()` function to fetch user role on page load
- Added `setupRoleBasedUI()` function to hide/show button based on role
- Button is hidden (`display: none`) for members only

### 3. Tournament Participant Management
**File:** `static/js/tournaments.js`

**Behavior:**
- **Admin users**: Can add participants to tournaments
- **Trainer users**: Can add participants to tournaments
- **Member users**: Cannot add participants (button not shown)

**Implementation:**
- Modified `createTournamentCard()` function to check user role
- "Add Participants" button only shown when `userRole === 'admin' || userRole === 'trainer'`
- Backend already has proper authorization via `require_trainer_or_admin()`

### 4. Match Result Recording
**File:** `static/js/tournaments.js`

**Behavior:**
- **Admin users**: Can record match results (decide winners/losers)
- **Trainer users**: Can record match results (decide winners/losers)
- **Member users**: Cannot record match results (button not shown)

**Implementation:**
- Modified `renderBracket()` function to check user role
- "Record Result" button only shown when `userRole === 'admin' || userRole === 'trainer'`
- Backend already has proper authorization via `require_trainer_or_admin()`

## User Roles Summary

| Feature | Member | Trainer | Admin |
|---------|--------|---------|-------|
| View Dashboard | ✅ | ✅ | ✅ |
| View Tournaments | ✅ | ✅ | ✅ |
| Create Tournament | ❌ | ✅ | ✅ |
| Add Participants | ❌ | ✅ | ✅ |
| Record Match Results | ❌ | ✅ | ✅ |
| View Bracket | ✅ | ✅ | ✅ |
| Access Admin Panel | ❌ | ❌ | ✅ |

## Backend Permissions

The backend already has proper authorization checks in place:

**Tournament Service** (`services/tournament-service/src/api.py`):
- `require_trainer_or_admin()` - Used for:
  - Creating tournaments (`POST /`)
  - Adding participants in bulk (`PUT /{id}/participants`)
  - Recording match results (`PUT /{id}/bracket/{bid}/result`)

**User Service** (`services/user-service/src/api.py`):
- `require_admin()` - Used for:
  - Listing all users (`GET /`)
  - Approving users (`PATCH /approve`)
  - Banning users (`PATCH /ban`)
  - Deleting users (`DELETE /{id}`)

## Testing

To test the role-based UI:

1. **Login as Member:**
   - Should NOT see "Admin Panel" button in dashboard
   - Should NOT see "New Tournament" button in tournaments page
   - Should NOT see "Add Participants" buttons on tournament cards
   - Should NOT see "Record Result" buttons in bracket view
   - CAN view tournaments and brackets

2. **Login as Trainer:**
   - Should NOT see "Admin Panel" button in dashboard
   - SHOULD see "New Tournament" button in tournaments page
   - SHOULD see "Add Participants" buttons on tournament cards
   - SHOULD see "Record Result" buttons in bracket view

3. **Login as Admin:**
   - SHOULD see "Admin Panel" button in dashboard
   - SHOULD see "New Tournament" button in tournaments page
   - SHOULD see "Add Participants" buttons on tournament cards
   - SHOULD see "Record Result" buttons in bracket view

## Future Enhancements

Potential improvements:
1. Add visual feedback when members try to perform unauthorized actions
2. Add "Join Tournament" feature for members (with approval workflow)
3. Show different tournament cards for different roles
4. Add statistics/leaderboard updates when match results are recorded
