#!/usr/bin/env python3
"""
Test script to validate interview startup flow on Render production environment
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_interview_startup():
    """Test the complete interview startup flow"""
    print("🧪 Testing Interview Startup Flow on Render...")
    
    try:
        # Test 1: Import modules
        print("\n--- Test 1: Module Imports ---")
        from models import InterviewSession, persist_interview_session
        from agents.pre_interview_planner import PreInterviewPlanner
        print("✅ All modules imported successfully")
        
        # Test 2: Database connection
        print("\n--- Test 2: Database Connection ---")
        from models import test_database_connection
        if test_database_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test 3: Create test session data
        print("\n--- Test 3: Session Data Creation ---")
        session_data = {
            "session_id": f"test_session_{int(datetime.now().timestamp())}",
            "selected_skills": "Product Sense",
            "role": "Product Manager",
            "seniority": "Mid",
            "skill": "Product Sense",
            "selected_archetype": "Improvement (\"1 to N\")",
            "generated_prompt": "Test interview prompt for validation",
            "playbook_id": None,
            "interview_started_at": None,
            "interview_completed_at": None
        }
        print("✅ Session data created")
        print(f"Session ID: {session_data['session_id']}")
        
        # Test 4: Create InterviewSession object
        print("\n--- Test 4: InterviewSession Object Creation ---")
        session = InterviewSession(**session_data)
        print("✅ InterviewSession object created successfully")
        print(f"Role: {session.role}")
        print(f"Conversation history: {session.conversation_history} (type: {type(session.conversation_history)})")
        print(f"Collected signals: {session.collected_signals} (type: {type(session.collected_signals)})")
        
        # Test 5: Test database persistence
        print("\n--- Test 5: Database Persistence ---")
        success = persist_interview_session(session_data)
        if success:
            print("✅ Interview session persisted successfully to database")
        else:
            print("❌ Failed to persist interview session")
            return False
        
        # Test 6: Verify session was created
        print("\n--- Test 6: Session Verification ---")
        from models import get_interview_session
        retrieved_session = get_interview_session(session_data['session_id'])
        if retrieved_session:
            print("✅ Session retrieved from database successfully")
            print(f"Retrieved role: {retrieved_session.role}")
            print(f"Retrieved conversation_history: {retrieved_session.conversation_history}")
            print(f"Retrieved collected_signals: {retrieved_session.collected_signals}")
        else:
            print("❌ Failed to retrieve session from database")
            return False
        
        print("\n🎉 ALL TESTS PASSED! Interview startup flow is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_interview_startup()
    if success:
        print("\n✅ Interview startup validation successful!")
        sys.exit(0)
    else:
        print("\n❌ Interview startup validation failed!")
        sys.exit(1)
