# Tournament Display Fix

## Problem
Tournaments created by trainers or admins were not appearing on the tournaments page.

## Root Causes

### 1. API Response Format Mismatch
**Backend (`services/tournament-service/src/api.py`)**:
- Was returning: `[{tournament1}, {tournament2}, ...]` (plain array)

**Frontend (`static/js/tournaments.js`)**:
- Was expecting: `{tournaments: [{tournament1}, {tournament2}, ...]}`

This caused the JavaScript to receive `data.tournaments = undefined`, resulting in an empty array.

### 2. Missing Authentication
**Backend**: Required JWT authentication via `@jwt_required()` decorator
**Frontend**: Was not including JWT token in the request headers

The `loadTournaments()` function was making unauthenticated requests, which would fail with 401 Unauthorized.

## Fixes Applied

### Backend Changes
**File**: `services/tournament-service/src/api.py`

Changed line 63 from:
```python
return jsonify([t.to_dict() for t in tournaments]), 200
```

To:
```python
return jsonify({"tournaments": [t.to_dict() for t in tournaments]}), 200
```

### Frontend Changes
**File**: `static/js/tournaments.js`

Updated `loadTournaments()` function to:
1. Use `authFetch` helper (which automatically adds JWT token)
2. Fall back to manual token inclusion if `authFetch` is not available
3. Added better error logging

## Testing

To verify the fix works:

1. **Start the microservices**:
   ```bash
   ./scripts/start-microservices.sh
   ```

2. **Login as admin**:
   - Navigate to http://localhost:8000/login.html
   - Login with: admin@gym.com / admin

3. **Create a tournament**:
   - Go to http://localhost:8000/tournaments.html
   - Click "New Tournament"
   - Enter name, select max participants, and tournament type
   - Click "Create Tournament"

4. **Verify**:
   - Tournament should appear in the grid immediately after creation
   - No longer see "No tournaments yet" message
   - Tournament card shows correct status, participant count, etc.

## Additional Notes

The fix ensures that:
- All tournament-related API calls include proper authentication
- Response format matches what the frontend expects
- Error messages are more descriptive for debugging
- The system is consistent with other microservices
