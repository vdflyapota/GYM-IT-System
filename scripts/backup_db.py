"""
Database Backup Script
Owner: Shattyk Kuziyeva
Purpose: Automated daily backups for fault tolerance
"""

import os
import shutil
from datetime import datetime

DB_FILE = "gym.db"
BACKUP_DIR = "backups"

def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"gym_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    shutil.copy2(DB_FILE, backup_path)

    print(f"Backup created successfully: {backup_path}")

if __name__ == "__main__":
    create_backup()
