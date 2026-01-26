#!/usr/bin/env bash
set -euo pipefail

# Requires: pg_dump, openssl (or age/gpg), AWS CLI (or similar), env vars set
# ENV: DATABASE_URL, BACKUP_BUCKET, BACKUP_ENC_RECIPIENT

STAMP=$(date -u +"%Y%m%d-%H%M%S")
TMPFILE="/tmp/gymit-db-${STAMP}.sql"
ARCHIVE="/tmp/gymit-db-${STAMP}.sql.gz"
ENCRYPTED="/tmp/gymit-db-${STAMP}.sql.gz.enc"

echo "[*] Dumping database..."
pg_dump "$DATABASE_URL" > "$TMPFILE"

echo "[*] Compressing..."
gzip -c "$TMPFILE" > "$ARCHIVE"

echo "[*] Encrypting..."
# Example with openssl AES-256-GCM using a derived key; prefer key management service in production.
openssl enc -aes-256-gcm -salt -pbkdf2 -in "$ARCHIVE" -out "$ENCRYPTED" -pass env:BACKUP_PASSPHRASE

echo "[*] Uploading to bucket..."
aws s3 cp "$ENCRYPTED" "s3://${BACKUP_BUCKET}/backups/${STAMP}.sql.gz.enc" --sse AES256

echo "[*] Cleanup"
rm -f "$TMPFILE" "$ARCHIVE" "$ENCRYPTED"

echo "[*] Done"
