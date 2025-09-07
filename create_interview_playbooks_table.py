#!/usr/bin/env python3
"""
Migration script to create the interview_playbooks table in Render database.
This table is essential for the new guidance-based AI system.
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

def create_interview_playbooks_table():
    """Create the interview_playbooks table with all required columns"""
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set your Render database URL in the .env file")
        return False
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Check if table already exists
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'interview_playbooks' in existing_tables:
            print("✅ interview_playbooks table already exists")
            return True
        
        # Create the table
        create_table_sql = """
        CREATE TABLE interview_playbooks (
            id SERIAL PRIMARY KEY,
            role VARCHAR(255) NOT NULL,
            skill VARCHAR(255) NOT NULL,
            seniority VARCHAR(255) NOT NULL,
            archetype VARCHAR(255),
            interview_objective TEXT,
            evaluation_dimensions JSONB,
            seniority_criteria JSONB,
            good_vs_great_examples JSONB,
            pre_interview_strategy TEXT,
            during_interview_execution TEXT,
            post_interview_evaluation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create indexes for better performance
        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_interview_playbooks_role ON interview_playbooks(role);",
            "CREATE INDEX IF NOT EXISTS idx_interview_playbooks_skill ON interview_playbooks(skill);",
            "CREATE INDEX IF NOT EXISTS idx_interview_playbooks_seniority ON interview_playbooks(seniority);",
            "CREATE INDEX IF NOT EXISTS idx_interview_playbooks_combo ON interview_playbooks(role, skill, seniority);"
        ]
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            try:
                # Create table
                connection.execute(text(create_table_sql))
                print("✅ Created interview_playbooks table")
                
                # Create indexes
                for index_sql in create_indexes_sql:
                    connection.execute(text(index_sql))
                print("✅ Created indexes for interview_playbooks table")
                
                # Commit transaction
                trans.commit()
                print("✅ interview_playbooks table created successfully!")
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

def verify_table_creation():
    """Verify that the table was created correctly"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return False
        
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Check if table exists
        if 'interview_playbooks' not in inspector.get_table_names():
            print("❌ interview_playbooks table not found after creation")
            return False
        
        # Get column information
        columns = inspector.get_columns('interview_playbooks')
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'id', 'role', 'skill', 'seniority', 'archetype', 
            'interview_objective', 'evaluation_dimensions', 
            'seniority_criteria', 'good_vs_great_examples',
            'pre_interview_strategy', 'during_interview_execution', 
            'post_interview_evaluation', 'created_at'
        ]
        
        missing_columns = set(expected_columns) - set(column_names)
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        print("✅ Table verification successful!")
        print(f"📋 Columns: {sorted(column_names)}")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating interview_playbooks table in Render database...")
    print("=" * 60)
    
    # Create the table
    if create_interview_playbooks_table():
        print("\n🔍 Verifying table creation...")
        if verify_table_creation():
            print("\n🎉 SUCCESS! interview_playbooks table is ready!")
            print("\nNext steps:")
            print("1. Populate the table with your playbook data")
            print("2. The AI agents will now be able to use the guidance columns")
            print("3. No more fallback errors - proper guidance will be available")
        else:
            print("\n❌ Table creation verification failed")
    else:
        print("\n❌ Failed to create interview_playbooks table")
        sys.exit(1)
