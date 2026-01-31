\# Database Backup \& Restore



\## Backup Strategy

\- Automated daily backups using shell and Python scripts

\- Each microservice database is backed up independently



\## Restore Process

1\. Select the latest backup file

2\. Restore using PostgreSQL restore command

3\. Verify database integrity



\## Recovery Objective

\- Recovery Time Objective (RTO): < 5 minutes

\- Tested via manual restore simulation



This ensures fault tolerance and data safety in production.



