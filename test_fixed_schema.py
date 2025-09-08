#!/usr/bin/env python3
"""
Test script to verify the fixed schema works
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_fixed_schema():
    """Test the fixed schema with correct data types"""
    print("🧪 Testing Fixed Schema...")
    
    try:
        from models import persist_interview_session
        
        # Test data with correct types
        session_data = {
            "session_id": f"test_fixed_schema_{int(datetime.now().timestamp())}",
            "selected_skills": ["Product Sense"],  # ✅ JSON array (not string!)
            "role": "Product Manager",
            "seniority": "Mid", 
            "skill": "Product Sense",  # ✅ String (separate field)
            "selected_archetype": "Improvement (\"1 to N\")",
            "generated_prompt": "Test interview prompt for fixed schema validation",
            "playbook_id": None,
            "interview_started_at": None,
            "interview_completed_at": None
        }
        
        print(f"🔍 Test data:")
        for k, v in session_data.items():
            print(f"  {k}: {repr(v)} (type: {type(v)})")
        
        # Test persistence
        success = persist_interview_session(session_data)
        
        if success:
            print("✅ Fixed schema test successful!")
            
            # Verify the session was created
            from models import get_interview_session
            retrieved_session = get_interview_session(session_data['session_id'])
            if retrieved_session:
                print("✅ Session retrieved successfully!")
                print(f"  Role: {retrieved_session.role}")
                print(f"  Selected skills: {retrieved_session.selected_skills}")
                print(f"  Skill: {retrieved_session.skill}")
            else:
                print("❌ Failed to retrieve session")
                
        else:
            print("❌ Fixed schema test failed!")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_schema()
    if success:
        print("\n✅ Fixed schema test successful!")
        sys.exit(0)
    else:
        print("\n❌ Fixed schema test failed!")
        sys.exit(1)
