 # Backend Improvements (Jan 2026)

## What was fixed

1) Safer DB schema bootstrap
- Use a transaction context for schema tweaks.
- Prevent leaked connections if an error occurs.

2) Root admin safety
- If ADMIN_EMAIL exists, ensure it stays active and unbanned unless force reset is off.
- Prevent accidental lockout of the bootstrap admin.

3) User API input validation
- `user_id` is now parsed and validated as an integer for admin actions.
- Returns clear 400 errors on invalid/missing `user_id`.

4) SocketIO emit reliability
- Emits from HTTP routes now use the initialized SocketIO extension.
- If SocketIO is not initialized, a warning is logged instead of failing silently.

5) Metrics label consistency
- HTTP status labels are always strings for Prometheus counters.

6) Logging handler stability
- Avoid duplicated log output on reload by resetting handlers on startup.

7) CORS configuration
- API now respects `CORS_ORIGINS` from config instead of default wildcard only.

## Files changed
- `src/app.py`
- `src/common/db.py`
- `src/users/api.py`
- `src/users/repository.py`
- `src/notifications/events.py`
- `src/observability/metrics.py`
- `src/observability/logging.py`
- `src/auth/jwt.py`
- `src/tournaments/api.py`

## Notes for running
- Ensure `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set to enable bootstrap admin creation.
- If you need to force reset the admin password, set `ADMIN_FORCE_RESET=1`.
- For frontend dev, update `CORS_ORIGINS` (comma-separated) as needed.
