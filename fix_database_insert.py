#!/usr/bin/env python3
"""
Fix script to handle database insert with proper column mapping
"""

import os
import sys
from sqlalchemy import text

# Add current directory to path
sys.path.append('.')

def fix_persist_interview_session(session_data):
    """
    Fixed version of persist_interview_session that handles column order issues
    """
    try:
        from models import get_engine, get_session_local
        
        engine = get_engine()
        db = get_session_local()()
        
        # Use raw SQL to avoid column order issues
        sql = """
        INSERT INTO interview_sessions (
            session_id, selected_skills, role, seniority, skill, 
            playbook_id, selected_archetype, generated_prompt,
            interview_started_at, interview_completed_at
        ) VALUES (
            :session_id, :selected_skills, :role, :seniority, :skill,
            :playbook_id, :selected_archetype, :generated_prompt,
            :interview_started_at, :interview_completed_at
        ) RETURNING id
        """
        
        # Prepare parameters
        params = {
            'session_id': session_data['session_id'],
            'selected_skills': session_data['selected_skills'],
            'role': session_data['role'],
            'seniority': session_data['seniority'],
            'skill': session_data['skill'],
            'playbook_id': session_data.get('playbook_id'),
            'selected_archetype': session_data['selected_archetype'],
            'generated_prompt': session_data['generated_prompt'],
            'interview_started_at': session_data.get('interview_started_at'),
            'interview_completed_at': session_data.get('interview_completed_at')
        }
        
        print(f"🔍 DEBUG - SQL parameters:")
        for k, v in params.items():
            print(f"  {k}: {repr(v)} (type: {type(v)})")
        
        # Execute the insert
        result = db.execute(text(sql), params)
        db.commit()
        
        # Get the inserted ID
        inserted_id = result.fetchone()[0]
        print(f"✅ Interview session inserted with ID: {inserted_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to persist interview session: {e}")
        if db:
            db.rollback()
        return False
        
    finally:
        if db:
            db.close()

def test_fixed_persistence():
    """Test the fixed persistence function"""
    print("🧪 Testing Fixed Database Persistence...")
    
    try:
        # Test data
        session_data = {
            "session_id": f"test_fixed_{int(__import__('time').time())}",
            "selected_skills": "Product Sense",
            "role": "Product Manager",
            "seniority": "Mid",
            "skill": "Product Sense",
            "selected_archetype": "Improvement (\"1 to N\")",
            "generated_prompt": "Test interview prompt for fixed validation",
            "playbook_id": None,
            "interview_started_at": None,
            "interview_completed_at": None
        }
        
        print(f"Session ID: {session_data['session_id']}")
        
        # Test the fixed persistence
        success = fix_persist_interview_session(session_data)
        
        if success:
            print("✅ Fixed persistence successful!")
            
            # Verify the session was created
            from models import get_interview_session
            retrieved_session = get_interview_session(session_data['session_id'])
            if retrieved_session:
                print("✅ Session retrieved successfully!")
                print(f"Retrieved role: {retrieved_session.role}")
            else:
                print("❌ Failed to retrieve session")
                
        else:
            print("❌ Fixed persistence failed!")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_persistence()
    if success:
        print("\n✅ Fixed persistence test successful!")
        sys.exit(0)
    else:
        print("\n❌ Fixed persistence test failed!")
        sys.exit(1)
