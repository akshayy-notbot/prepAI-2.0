#!/usr/bin/env python3
"""
Migration script to add core_philosophy column to interview_playbooks table.
This column will provide foundational guidance principles for each interview archetype.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def add_core_philosophy_column():
    """Add core_philosophy column to interview_playbooks table"""
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set your Render database URL in the .env file")
        return False
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Check if table exists
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'interview_playbooks' not in existing_tables:
            print("❌ interview_playbooks table does not exist")
            print("Please run create_interview_playbooks_table.py first")
            return False
        
        # Check if column already exists
        columns = inspector.get_columns('interview_playbooks')
        column_names = [col['name'] for col in columns]
        
        if 'core_philosophy' in column_names:
            print("✅ core_philosophy column already exists")
            return True
        
        # Add the column
        add_column_sql = """
        ALTER TABLE interview_playbooks 
        ADD COLUMN core_philosophy TEXT;
        """
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            try:
                # Add column
                connection.execute(text(add_column_sql))
                print("✅ Added core_philosophy column to interview_playbooks table")
                
                # Commit transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_column_addition():
    """Verify that the column was added correctly"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return False
        
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Get column information
        columns = inspector.get_columns('interview_playbooks')
        column_names = [col['name'] for col in columns]
        
        if 'core_philosophy' not in column_names:
            print("❌ core_philosophy column not found after migration")
            return False
        
        print("✅ Migration verification successful!")
        print(f"📋 All columns: {sorted(column_names)}")
        
        # Check current record count
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM interview_playbooks"))
            count = result.scalar()
            print(f"📊 Current records in table: {count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Adding core_philosophy column to interview_playbooks table...")
    print("=" * 70)
    
    # Add the column
    if add_core_philosophy_column():
        print("\n🔍 Verifying column addition...")
        if verify_column_addition():
            print("\n🎉 SUCCESS! core_philosophy column is ready!")
            print("\nThe column provides:")
            print("✅ Foundational interview guidance principles")
            print("✅ Philosophical approach for each archetype")
            print("✅ High-level direction for agent behavior")
            print("\nNext steps:")
            print("1. Update your CSV to include core_philosophy data")
            print("2. Import playbook data with the new column")
            print("3. Agents will use this as foundational guidance")
        else:
            print("\n❌ Migration verification failed")
    else:
        print("\n❌ Failed to add core_philosophy column")
        sys.exit(1)
