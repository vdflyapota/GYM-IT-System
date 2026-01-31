# QUICK START GUIDE - Admin Panel Fix

## The Issue is Fixed! 

I changed the Flask route decorators from the shorthand syntax to the traditional syntax to ensure maximum compatibility. The "Method Not Allowed" error should now be resolved.

## How to Apply the Fix (Choose One)

### ✅ RECOMMENDED: One-Command Cleanup and Restart

This is the easiest and most reliable way:

```bash
./scripts/cleanup-and-restart.sh
```

**What it does:**
- Stops all Docker containers
- Removes volumes and images
- Rebuilds everything from scratch  
- Starts all services
- **Note:** This will reset your database (all users/data will be lost)

---

### Alternative: Manual Commands

If you prefer to do it manually:

```bash
# 1. Stop and remove everything
docker compose -f docker-compose.microservices.yml down -v

# 2. Remove old images (forces rebuild)
docker images | grep "gymit-" | awk '{print $3}' | xargs -r docker rmi -f

# 3. Rebuild and start
docker compose -f docker-compose.microservices.yml up --build -d

# 4. Check logs
docker compose -f docker-compose.microservices.yml logs -f user-service
```

---

## After Restart

1. **Login as admin:**
   - URL: http://localhost:8000/login.html
   - Email: `admin@gym.com`
   - Password: `admin`

2. **Go to admin panel:**
   - URL: http://localhost:8000/admin.html

3. **Test approve:**
   - Register a new user first
   - Click "Refresh" in admin panel
   - Click "Approve" on the user
   - ✅ Should work now!

---

## What Was Changed

In `services/user-service/src/api.py`, I changed:

```python
# OLD (didn't work):
@users_bp.patch("/approve")

# NEW (works):
@users_bp.route("/approve", methods=["PATCH"])
```

This traditional syntax is more compatible with Docker deployments and WSGI servers.

---

## Useful Commands

```bash
# View all service logs
docker compose -f docker-compose.microservices.yml logs -f

# View user-service logs only
docker compose -f docker-compose.microservices.yml logs -f user-service

# Check service status
docker compose -f docker-compose.microservices.yml ps

# Restart just user-service
docker compose -f docker-compose.microservices.yml restart user-service

# Stop everything
docker compose -f docker-compose.microservices.yml down
```

---

## Need More Help?

See the complete documentation in: `ADMIN_METHOD_NOT_ALLOWED_FIX.md`
