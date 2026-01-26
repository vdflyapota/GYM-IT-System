#!/bin/bash
# Microservices Database Backup Script
# Backs up all PostgreSQL databases and Redis data

set -e

# Configuration
BACKUP_DIR=${BACKUP_DIR:-"/backups"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${RETENTION_DAYS:-7}

# Database credentials
AUTH_DB_HOST=${AUTH_DB_HOST:-"auth-db"}
AUTH_DB_PORT=${AUTH_DB_PORT:-"5432"}
AUTH_DB_USER=${AUTH_DB_USER:-"authuser"}
AUTH_DB_NAME=${AUTH_DB_NAME:-"authdb"}
PGPASSWORD_AUTH=${AUTH_DB_PASSWORD:-"authpass"}

USER_DB_HOST=${USER_DB_HOST:-"user-db"}
USER_DB_PORT=${USER_DB_PORT:-"5432"}
USER_DB_USER=${USER_DB_USER:-"useruser"}
USER_DB_NAME=${USER_DB_NAME:-"userdb"}
PGPASSWORD_USER=${USER_DB_PASSWORD:-"userpass"}

TOURNAMENT_DB_HOST=${TOURNAMENT_DB_HOST:-"tournament-db"}
TOURNAMENT_DB_PORT=${TOURNAMENT_DB_PORT:-"5432"}
TOURNAMENT_DB_USER=${TOURNAMENT_DB_USER:-"tournamentuser"}
TOURNAMENT_DB_NAME=${TOURNAMENT_DB_NAME:-"tournamentdb"}
PGPASSWORD_TOURNAMENT=${TOURNAMENT_DB_PASSWORD:-"tournamentpass"}

REDIS_HOST=${REDIS_HOST:-"redis"}
REDIS_PORT=${REDIS_PORT:-"6379"}

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting database backups at $(date)"
echo "Backup directory: $BACKUP_DIR"

# Function to backup PostgreSQL database
backup_postgres() {
    local db_host=$1
    local db_port=$2
    local db_user=$3
    local db_name=$4
    local password=$5
    local backup_file="$BACKUP_DIR/${db_name}_${TIMESTAMP}.sql.gz"
    
    echo "Backing up $db_name..."
    
    PGPASSWORD="$password" pg_dump \
        -h "$db_host" \
        -p "$db_port" \
        -U "$db_user" \
        -d "$db_name" \
        --clean \
        --if-exists \
        | gzip > "$backup_file"
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully backed up $db_name to $backup_file"
        echo "  Size: $(du -h "$backup_file" | cut -f1)"
    else
        echo "✗ Failed to backup $db_name"
        return 1
    fi
}

# Function to backup Redis
backup_redis() {
    local backup_file="$BACKUP_DIR/redis_${TIMESTAMP}.rdb"
    
    echo "Backing up Redis..."
    
    # Trigger Redis BGSAVE
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" BGSAVE
    
    # Wait for save to complete
    sleep 2
    
    # Copy dump file if it exists
    if docker cp gymit-redis:/data/dump.rdb "$backup_file" 2>/dev/null; then
        gzip "$backup_file"
        echo "✓ Successfully backed up Redis to ${backup_file}.gz"
        echo "  Size: $(du -h "${backup_file}.gz" | cut -f1)"
    else
        echo "⚠ Redis backup may not be available (using in-memory only)"
    fi
}

# Backup all databases
echo ""
echo "=== Backing up PostgreSQL Databases ==="
backup_postgres "$AUTH_DB_HOST" "$AUTH_DB_PORT" "$AUTH_DB_USER" "$AUTH_DB_NAME" "$PGPASSWORD_AUTH"
backup_postgres "$USER_DB_HOST" "$USER_DB_PORT" "$USER_DB_USER" "$USER_DB_NAME" "$PGPASSWORD_USER"
backup_postgres "$TOURNAMENT_DB_HOST" "$TOURNAMENT_DB_PORT" "$TOURNAMENT_DB_USER" "$TOURNAMENT_DB_NAME" "$PGPASSWORD_TOURNAMENT"

echo ""
echo "=== Backing up Redis ==="
backup_redis

echo ""
echo "=== Cleaning up old backups ==="
# Remove backups older than retention period
find "$BACKUP_DIR" -name "*.gz" -type f -mtime +$RETENTION_DAYS -delete
echo "✓ Removed backups older than $RETENTION_DAYS days"

echo ""
echo "=== Backup Summary ==="
echo "Backup location: $BACKUP_DIR"
echo "Current backups:"
ls -lh "$BACKUP_DIR"/*_${TIMESTAMP}.* 2>/dev/null || echo "No backups created in this run"

echo ""
echo "Backup completed at $(date)"

# Optional: Upload to cloud storage
# Uncomment and configure for your cloud provider
# if [ -n "$BACKUP_BUCKET" ]; then
#     echo ""
#     echo "=== Uploading to cloud storage ==="
#     # AWS S3
#     # aws s3 sync "$BACKUP_DIR" "s3://$BACKUP_BUCKET/gym-it-backups/"
#     
#     # Google Cloud Storage
#     # gsutil -m rsync -r "$BACKUP_DIR" "gs://$BACKUP_BUCKET/gym-it-backups/"
#     
#     # Azure Blob Storage
#     # az storage blob upload-batch --destination "$BACKUP_BUCKET" --source "$BACKUP_DIR"
# fi
