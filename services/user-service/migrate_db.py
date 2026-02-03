#!/usr/bin/env python3
"""
Database migration script to add missing columns and ensure all tables exist.
This should be run when the database schema needs to be updated.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from config import Config
from models import db, User, Notification, BlogPost, PasswordResetToken

def migrate_database():
    """Migrate database to add missing columns"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        # Create all tables if they don't exist
        print("Creating tables if they don't exist...")
        db.create_all()
        print("✓ All tables created/verified")
        
        # Check if we need to add is_active column to existing users table
        try:
            from sqlalchemy import text
            
            # Check if is_active column exists
            result = db.session.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='users' AND column_name='is_active'"
            ))
            
            if result.fetchone() is None:
                print("Adding is_active column to users table...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"
                ))
                db.session.commit()
                print("✓ Added is_active column")
            else:
                print("✓ is_active column already exists")
                
        except Exception as e:
            print(f"Note: Could not check/add is_active column: {e}")
            print("This might be expected if using SQLite or if column already exists")
        
        # Verify tables exist
        tables = ['users', 'notifications', 'blog_posts', 'password_reset_tokens']
        for table in tables:
            try:
                result = db.session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                print(f"✓ Table '{table}' exists and is accessible")
            except Exception as e:
                print(f"⚠ Warning: Could not access table '{table}': {e}")
        
        print("\n✅ Migration complete!")
        print("\nNext steps:")
        print("1. Restart the user-service")
        print("2. Check that the admin panel loads correctly")
        print("3. Verify notifications and blog features work")

if __name__ == '__main__':
    migrate_database()
