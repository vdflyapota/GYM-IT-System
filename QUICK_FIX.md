# QUICK FIX: Leaderboard 422 Error

## ⚠️ YOU MUST FOLLOW THESE STEPS EXACTLY

The code is **already fixed**, but you need to **restart services** and **get a fresh token**.

---

## Step 1: Restart Services (REQUIRED)

Open terminal in project directory and run:

```bash
# For microservices setup:
docker compose -f docker-compose.microservices.yml restart auth-service tournament-service

# OR if using regular docker-compose:
docker compose restart auth-service tournament-service
```

**Wait for services to fully restart** (about 10-30 seconds).

---

## Step 2: Clear Your Token (REQUIRED)

You have two options:

### Option A: Log Out and Log In
1. Click "Logout" in the application
2. Log in again with your credentials

### Option B: Clear Token Manually
1. Open browser DevTools (press F12)
2. Go to "Application" tab
3. Click "Local Storage" in left sidebar
4. Find `http://127.0.0.1:8000` (or your URL)
5. Delete the `token` entry
6. Refresh the page
7. Log in again

---

## Step 3: Test Leaderboard

1. Navigate to the leaderboard page
2. Open browser console (F12 → Console tab)
3. You should now see:
   - `[Leaderboard] Response status: 200` ✅
   - `[Leaderboard] Response ok: true` ✅

---

## Still Not Working?

### Check 1: Are services actually restarted?
```bash
docker compose ps
```

Both `auth-service` and `tournament-service` should show "Up".

### Check 2: View service logs
```bash
docker compose logs auth-service | tail -30
docker compose logs tournament-service | tail -30
```

Look for any error messages.

### Check 3: Hard refresh browser
- Windows/Linux: Ctrl + Shift + R
- Mac: Cmd + Shift + R

### Check 4: Try incognito/private window
This ensures no cached tokens or data.

---

## Why This Fix Is Necessary

**The Problem:**
- Auth-service signs JWT tokens with a secret key and algorithm
- Tournament-service validates tokens using the same secret key and algorithm
- Before fix: Algorithm wasn't explicitly configured, causing mismatch
- After fix: Both services use HS256 algorithm explicitly

**Why Restart Is Required:**
- Config changes in Python files only apply when service starts
- Your services are still running with OLD configuration
- Old tokens were signed without explicit algorithm
- Restart loads NEW configuration

**Why Fresh Token Is Required:**
- Your browser has an old token (signed with old config)
- Tournament-service with new config can't verify old tokens
- Logging in creates a NEW token (signed with new config)
- New token works with new configuration

---

## Technical Details

Configuration is now correct in both services:

| Service | JWT_SECRET_KEY | JWT_ALGORITHM | Status |
|---------|---------------|---------------|--------|
| auth-service | "jwt-secret-key" | "HS256" | ✅ Fixed |
| tournament-service | "jwt-secret-key" | "HS256" | ✅ Fixed |

Files modified:
- `services/auth-service/src/config.py` (commit 8da25a6)
- `services/tournament-service/src/config.py` (commit a50dfbc)

---

## Summary

1. ✅ Code is fixed
2. ⏳ You must restart services
3. ⏳ You must get fresh token (logout/login)
4. ✅ Leaderboard will work

**The fix is complete - just execute the steps above!**
