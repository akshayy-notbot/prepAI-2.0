#!/usr/bin/env python3
"""
Migration script to fix the database schema to match our model
"""

import os
import sys
from sqlalchemy import text, inspect

# Add current directory to path
sys.path.append('.')

def fix_database_schema():
    """Fix the database schema to match our model"""
    print("🔧 Fixing Database Schema...")
    
    try:
        from models import get_engine
        
        engine = get_engine()
        inspector = inspect(engine)
        
        # Check current schema
        print("\n📋 Current schema:")
        columns = inspector.get_columns('interview_sessions')
        for col in columns:
            print(f"  {col['name']}: {col['type']}")
        
        # Check if we need to add missing columns
        column_names = [col['name'] for col in columns]
        required_columns = [
            'selected_skills', 'role', 'seniority', 'skill', 'playbook_id',
            'selected_archetype', 'generated_prompt', 'signal_map', 
            'evaluation_criteria', 'conversation_history', 'collected_signals',
            'final_evaluation', 'interview_started_at', 'interview_completed_at'
        ]
        
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"\n🔄 Adding missing columns: {missing_columns}")
            
            with engine.connect() as connection:
                trans = connection.begin()
                try:
                    for column in missing_columns:
                        if column == 'selected_skills':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN selected_skills VARCHAR(255)"))
                        elif column == 'role':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN role VARCHAR(255)"))
                        elif column == 'seniority':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN seniority VARCHAR(255)"))
                        elif column == 'skill':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN skill VARCHAR(255)"))
                        elif column == 'playbook_id':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN playbook_id INTEGER"))
                        elif column == 'selected_archetype':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN selected_archetype VARCHAR(255)"))
                        elif column == 'generated_prompt':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN generated_prompt TEXT"))
                        elif column == 'signal_map':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN signal_map JSON"))
                        elif column == 'evaluation_criteria':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN evaluation_criteria JSON"))
                        elif column == 'conversation_history':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN conversation_history JSON"))
                        elif column == 'collected_signals':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN collected_signals JSON"))
                        elif column == 'final_evaluation':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN final_evaluation JSON"))
                        elif column == 'interview_started_at':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN interview_started_at TIMESTAMP"))
                        elif column == 'interview_completed_at':
                            connection.execute(text("ALTER TABLE interview_sessions ADD COLUMN interview_completed_at TIMESTAMP"))
                        
                        print(f"  ✅ Added column: {column}")
                    
                    trans.commit()
                    print("✅ All missing columns added successfully")
                    
                except Exception as e:
                    trans.rollback()
                    print(f"❌ Failed to add columns: {e}")
                    raise
        
        else:
            print("✅ All required columns already exist")
        
        # Check final schema
        print("\n📋 Final schema:")
        columns = inspector.get_columns('interview_sessions')
        for col in columns:
            print(f"  {col['name']}: {col['type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        print("\n✅ Database schema fix complete!")
        sys.exit(0)
    else:
        print("\n❌ Database schema fix failed!")
        sys.exit(1)
