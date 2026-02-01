# Database Backup & Restore

## Backup Strategy
- Automated daily backups for each microservice database using shell and Python scripts.
- Ensures independent recoverability of each service.

## Restore Process
1. Identify the latest backup file.
2. Restore using PostgreSQL restore commands.
3. Verify database integrity post-restore.

## Recovery Objective
- Recovery Time Objective (RTO): < 5 minutes
- Manual restore simulations have been conducted to verify this metric.




