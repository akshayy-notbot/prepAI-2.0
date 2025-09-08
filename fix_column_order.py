#!/usr/bin/env python3
"""
Fix script that uses the exact column order from the database
"""

import os
import sys
from sqlalchemy import text, inspect

# Add current directory to path
sys.path.append('.')

def get_database_column_order():
    """Get the exact column order from the database"""
    try:
        from models import get_engine
        
        engine = get_engine()
        inspector = inspect(engine)
        
        columns = inspector.get_columns('interview_sessions')
        column_names = [col['name'] for col in columns]
        
        print("📋 Database column order:")
        for i, name in enumerate(column_names):
            print(f"  {i+1}. {name}")
        
        return column_names
        
    except Exception as e:
        print(f"❌ Failed to get column order: {e}")
        return None

def fix_insert_with_correct_order():
    """Insert using the exact column order from the database"""
    try:
        from models import get_engine, get_session_local
        
        # Get the actual column order
        column_order = get_database_column_order()
        if not column_order:
            return False
        
        # Create a mapping of our data to the database columns
        session_data = {
            "session_id": f"test_correct_order_{int(__import__('time').time())}",
            "selected_skills": "Product Sense",
            "role": "Product Manager", 
            "seniority": "Mid",
            "skill": "Product Sense",
            "selected_archetype": "Improvement (\"1 to N\")",
            "generated_prompt": "Test interview prompt for correct order validation",
            "playbook_id": None,
            "interview_started_at": None,
            "interview_completed_at": None
        }
        
        # Build the SQL with the exact column order
        columns_str = ", ".join(column_order)
        placeholders = ", ".join([f":{col}" for col in column_order])
        
        sql = f"""
        INSERT INTO interview_sessions ({columns_str})
        VALUES ({placeholders})
        RETURNING id
        """
        
        print(f"🔍 SQL: {sql}")
        
        # Prepare parameters - only include columns that exist in our data
        params = {}
        for col in column_order:
            if col in session_data:
                params[col] = session_data[col]
            else:
                # For missing columns, use appropriate defaults
                if 'json' in col.lower() or col in ['conversation_history', 'collected_signals', 'final_evaluation', 'signal_map', 'evaluation_criteria']:
                    params[col] = None  # Let database handle JSON defaults
                elif col == 'created_at':
                    params[col] = __import__('datetime').datetime.utcnow()
                else:
                    params[col] = None
        
        print(f"🔍 Parameters: {params}")
        
        # Execute
        engine = get_engine()
        db = get_session_local()()
        
        result = db.execute(text(sql), params)
        db.commit()
        
        inserted_id = result.fetchone()[0]
        print(f"✅ Insert successful! ID: {inserted_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Insert failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = fix_insert_with_correct_order()
    if success:
        print("\n✅ Correct order insert successful!")
        sys.exit(0)
    else:
        print("\n❌ Correct order insert failed!")
        sys.exit(1)
