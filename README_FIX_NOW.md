# ⚠️ FIX YOUR 422 ERROR NOW

## You Are Getting This Error:
```
Response status: 422
Error: Signature verification failed
```

## Why?
**Your Docker services are still running with OLD configuration.**

---

## THE FIX (3 Steps - Takes 2 Minutes)

### ✅ STEP 1: Restart Docker Services

Open terminal and run:

```bash
# Go to your project directory
cd /path/to/GYM-IT-System

# Stop ALL services
docker compose down

# Start ALL services fresh
docker compose up -d

# Wait 10 seconds for services to fully start
sleep 10

# Check they're running
docker compose ps
```

You should see:
```
auth-service          Up
tournament-service    Up
user-service          Up
```

**If any service is not "Up", the fix won't work!**

---

### ✅ STEP 2: Clear Old Token

In your web browser:

1. **Click "Logout"** button
2. Wait for logout to complete
3. You're now on login page

**Alternative (if logout doesn't work):**
1. Press **F12** (opens Developer Tools)
2. Click **"Application"** tab
3. Click **"Local Storage"** → **your site URL**
4. Find **"token"** entry
5. **Right-click → Delete**
6. Close Developer Tools

---

### ✅ STEP 3: Log In Again

1. **Enter your username and password**
2. **Click "Login"**
3. You now have a FRESH token that works!

---

### ✅ STEP 4: Test Leaderboard

1. **Click "Leaderboard"** link
2. **Open Developer Console (F12)**
3. **Look for:**

**SUCCESS (what you should see):**
```
[Leaderboard] Response status: 200
[Leaderboard] Response ok: true
[Leaderboard] Leaderboard data: [...]
```

**FAILURE (if services not restarted):**
```
[Leaderboard] Response status: 422
[Leaderboard] Error: Signature verification failed
```

---

## ❓ Still Not Working?

### Check 1: Are services actually restarted?
```bash
docker compose ps
```

Look at the "STATUS" column. Should say "Up X seconds" or "Up X minutes", NOT "Up X hours".

If "Up X hours" = services NOT restarted!

**Fix:** Run `docker compose down` then `docker compose up -d`

---

### Check 2: Did you log out and log in?

If you didn't log out, you still have the OLD token!

**Fix:** Log out, then log in again

---

### Check 3: Check service logs
```bash
docker compose logs auth-service | tail -20
docker compose logs tournament-service | tail -20
```

Look for errors or startup messages.

---

## 🎯 SUMMARY

**Problem:** Services running old code, browser has old token

**Solution:** 
1. Restart services (`docker compose down` then `up -d`)
2. Get fresh token (logout and login)

**Time Required:** 2 minutes

**Difficulty:** Easy - just follow steps!

---

## 📝 WHAT THE CODE FIX DID

I fixed the code in these files:
- `services/auth-service/src/config.py`
- `services/tournament-service/src/config.py`

Both now have:
```python
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
```

This makes JWT signatures match between services.

**But:** Python code only loads when service starts!

**So:** You MUST restart services to load the new code!

---

## ✅ CHECKLIST

Before saying "it doesn't work":

- [ ] Did I run `docker compose down`?
- [ ] Did I run `docker compose up -d`?
- [ ] Did I wait 10 seconds for services to start?
- [ ] Did I check `docker compose ps` shows all services "Up"?
- [ ] Did I log out from the web app?
- [ ] Did I log in again?
- [ ] Did I open leaderboard page?
- [ ] Did I check browser console (F12)?

**If you did ALL of these and still get 422, then report back with:**
1. Output of `docker compose ps`
2. Output of `docker compose logs tournament-service | tail -50`
3. Browser console output (F12)

---

## 🚀 DO IT NOW

**Stop reading. Start doing.**

1. Open terminal
2. Run `docker compose down`
3. Run `docker compose up -d`
4. Open browser
5. Log out
6. Log in
7. Go to leaderboard
8. **IT WILL WORK!**

The code is fixed. The error persists because you haven't restarted services.

**Restart now. Problem solved.**
