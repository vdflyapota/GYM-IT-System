# Database Migrations

This folder contains database migration scripts for the GYM-IT System.

## Current Migration

### add_is_active_column.sql

**Purpose:** Adds the `is_active` column to the users table

**Why needed:** Fixes the error "column users.is_active does not exist" on profile page

**How to run:**

From project root directory:

```bash
# Option 1: Automated script (easiest)
./run_migration.sh

# Option 2: Direct SQL
docker exec -i gym-it-user-db psql -U postgres -d user_service < services/user-service/migrations/add_is_active_column.sql

# Option 3: Python migration
cd services/user-service && python migrate_db.py
```

**After running:**
```bash
docker-compose restart user-service
```

## What Gets Fixed

- ✅ Profile page loads correctly
- ✅ Admin panel user management works
- ✅ User reports generate without errors

## Safe to Run

All migrations are safe to run multiple times. They check if changes already exist before applying them.
