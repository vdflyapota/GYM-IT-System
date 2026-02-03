# Fix for Leaderboard 422 "Signature Verification Failed" Error

## Problem
Getting error when accessing leaderboard:
```
Response status: 422
Error: "Signature verification failed"
```

## Root Cause
JWT configuration mismatch between auth-service (creates tokens) and tournament-service (validates tokens).

## Status
✅ **Configuration is now FIXED in code!**

Both services now have matching JWT settings:
- JWT_SECRET_KEY: "jwt-secret-key"
- JWT_ALGORITHM: "HS256"

## Solution: Restart Services and Get Fresh Token

### Step 1: Restart Services

**Option A - Using docker-compose.microservices.yml:**
```bash
cd /path/to/GYM-IT-System
docker compose -f docker-compose.microservices.yml restart auth-service tournament-service
```

**Option B - Using regular docker-compose.yml:**
```bash
cd /path/to/GYM-IT-System
docker compose restart auth-service tournament-service
```

**Verify services restarted:**
```bash
docker compose ps
```
Both services should show status "Up".

### Step 2: Clear Old Token and Log In Again

**Why?** Your browser has an old JWT token signed with the old configuration. You need a fresh token.

**How to clear token:**

**Option A - Log out:**
1. Open the application in browser
2. Click logout
3. Log in again with your credentials

**Option B - Clear localStorage manually:**
1. Open Developer Tools (F12)
2. Go to "Application" tab
3. Left sidebar: Local Storage → Your site URL
4. Find and delete the `token` entry
5. Refresh page and log in again

### Step 3: Test Leaderboard

1. Navigate to leaderboard page
2. Open Developer Console (F12)
3. Check console output

**Expected (success):**
```
[Leaderboard] Response status: 200
[Leaderboard] Response ok: true
[Leaderboard] Leaderboard data: [...]
```

**If still seeing 422:**
- Services not restarted properly
- Old token still in browser
- See troubleshooting below

## Troubleshooting

### Check Services Are Running
```bash
docker compose ps
```
Look for:
- `auth-service` - Status: Up
- `tournament-service` - Status: Up

### Check Service Logs
```bash
# View last 20 lines of each service
docker compose logs auth-service | tail -20
docker compose logs tournament-service | tail -20

# OR follow logs in real-time
docker compose logs -f auth-service tournament-service
```

### Verify Configuration
```bash
# Check if environment variables are set
docker compose config | grep JWT
```

### Force Clean Restart
If services still won't work:
```bash
# Stop services
docker compose down

# Restart services
docker compose up -d

# Check status
docker compose ps
```

### Browser Issues

**Hard refresh:**
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

**Try incognito/private window:**
- Ensures no cached tokens or cookies

**Clear all site data:**
1. Developer Tools (F12)
2. Application tab
3. Storage → Clear site data

## Quick Checklist

- [ ] Restarted auth-service
- [ ] Restarted tournament-service  
- [ ] Verified both services are "Up"
- [ ] Logged out from application
- [ ] Logged back in (fresh token)
- [ ] Tested leaderboard page
- [ ] Checked browser console for status 200

## Technical Details

**What changed:**
1. Added `JWT_ALGORITHM = "HS256"` to auth-service config
2. Added `JWT_ALGORITHM = "HS256"` to tournament-service config

**Why it matters:**
- Auth-service signs JWT tokens using SECRET_KEY + ALGORITHM
- Tournament-service validates tokens using same SECRET_KEY + ALGORITHM
- If algorithm differs, signature verification fails
- Both services must use identical JWT configuration

**Modified files:**
- `services/auth-service/src/config.py`
- `services/tournament-service/src/config.py`

## Still Having Issues?

If you've followed all steps and still see 422 error:

1. Check that you committed and pulled latest changes
2. Verify both config.py files have `JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")`
3. Rebuild containers if needed: `docker compose build auth-service tournament-service`
4. Check for any environment variable overrides in docker-compose.yml
5. Share service logs for further debugging

## Success Indicators

✅ Browser console shows: `Response status: 200`
✅ Browser console shows: `Response ok: true`  
✅ Leaderboard displays player names and statistics
✅ No "Signature verification failed" errors
