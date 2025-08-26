#!/usr/bin/env python3
"""
Database migration script for PrepAI-Prototype.
Adds the complete_interview_data JSON field to session_states table.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_engine, Base

def migrate_database():
    """Run database migrations"""
    try:
        engine = get_engine()
        
        # Check if the complete_interview_data column exists
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('session_states')]
        
        if 'complete_interview_data' not in columns:
            print("🔄 Adding complete_interview_data column to session_states table...")
            
            with engine.connect() as connection:
                # Add the JSON column
                connection.execute(text("""
                    ALTER TABLE session_states 
                    ADD COLUMN complete_interview_data JSON
                """))
                connection.commit()
                print("✅ complete_interview_data column added successfully")
        else:
            print("✅ complete_interview_data column already exists")
        
        # Check if the average_score column exists
        if 'average_score' not in columns:
            print("🔄 Adding average_score column to session_states table...")
            
            with engine.connect() as connection:
                # Add the integer column
                connection.execute(text("""
                    ALTER TABLE session_states 
                    ADD COLUMN average_score INTEGER
                """))
                connection.commit()
                print("✅ average_score column added successfully")
        else:
            print("✅ average_score column already exists")
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

def create_tables_if_not_exist():
    """Create tables if they don't exist"""
    try:
        print("🔄 Creating database tables if they don't exist...")
        Base.metadata.create_all(bind=get_engine())
        print("✅ Database tables created/verified successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    
    # First create tables if they don't exist
    if create_tables_if_not_exist():
        # Then run migrations
        if migrate_database():
            print("🎉 All database operations completed successfully!")
        else:
            print("❌ Database migration failed!")
            sys.exit(1)
    else:
        print("❌ Failed to create database tables!")
        sys.exit(1)
