#!/usr/bin/env python3
"""
Test script for the Autonomous Interviewer system.
This script tests the basic functionality without requiring the full web server.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_autonomous_interviewer():
    """Test the autonomous interviewer functionality."""
    
    print("🧪 Testing Autonomous Interviewer System")
    print("=" * 50)
    
    try:
        # Import our new classes
        from agents.autonomous_interviewer import AutonomousInterviewer
        from agents.session_tracker import SessionTracker
        
        print("✅ Successfully imported Autonomous Interviewer and Session Tracker")
        
        # Test 1: Session Tracker
        print("\n📋 Test 1: Session Tracker")
        print("-" * 30)
        
        session_tracker = SessionTracker()
        test_session_id = f"test_session_{int(datetime.now().timestamp())}"
        
        # Create a test session
        session_data = session_tracker.create_session(
            session_id=test_session_id,
            role="Software Engineer",
            seniority="Senior",
            skill="System Design"
        )
        
        print(f"✅ Created test session: {test_session_id}")
        print(f"   Role: {session_data['role']}")
        print(f"   Seniority: {session_data['seniority']}")
        print(f"   Skill: {session_data['skill']}")
        
        # Test 2: Get Initial Question
        print("\n🎯 Test 2: Get Initial Question")
        print("-" * 30)
        
        autonomous_interviewer = AutonomousInterviewer()
        
        initial_question = autonomous_interviewer.get_initial_question(
            role="Software Engineer",
            seniority="Senior",
            skill="System Design",
            session_context=session_tracker.get_session_context(test_session_id)
        )
        
        print(f"✅ Generated initial question")
        print(f"   Response: {initial_question['response_text'][:100]}...")
        print(f"   Stage: {initial_question['interview_state']['current_stage']}")
        print(f"   Progress: {initial_question['interview_state']['skill_progress']}")
        
        # Test 3: Conduct Interview Turn
        print("\n🔄 Test 3: Conduct Interview Turn")
        print("-" * 30)
        
        # Simulate a user response
        user_response = "I would start by understanding the requirements and constraints. For a ride-sharing app, I'd need to consider scalability, real-time updates, and user experience."
        
        # Add user response to session
        session_tracker.add_conversation_turn(test_session_id, "user", user_response)
        
        # Get next question from interviewer
        next_question = autonomous_interviewer.conduct_interview_turn(
            role="Software Engineer",
            seniority="Senior",
            skill="System Design",
            interview_stage="problem_understanding",
            conversation_history=session_tracker.get_conversation_history(test_session_id),
            session_context=session_tracker.get_session_context(test_session_id)
        )
        
        print(f"✅ Generated follow-up question")
        print(f"   Response: {next_question['response_text'][:100]}...")
        print(f"   Stage: {next_question['interview_state']['current_stage']}")
        print(f"   Progress: {next_question['interview_state']['skill_progress']}")
        print(f"   Next Focus: {next_question['interview_state']['next_focus']}")
        
        # Test 4: Session State Management
        print("\n💾 Test 4: Session State Management")
        print("-" * 30)
        
        # Update interview state
        session_tracker.update_interview_state(test_session_id, next_question["interview_state"])
        
        # Retrieve updated session
        updated_session = session_tracker.get_session(test_session_id)
        print(f"✅ Updated session state")
        print(f"   Current Stage: {updated_session['current_stage']}")
        print(f"   Skill Progress: {updated_session['skill_progress']}")
        print(f"   Conversation Turns: {len(updated_session['conversation_history'])}")
        
        # Test 5: Cleanup
        print("\n🧹 Test 5: Cleanup")
        print("-" * 30)
        
        session_tracker.delete_session(test_session_id)
        print(f"✅ Deleted test session: {test_session_id}")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_generation():
    """Test the prompt generation functionality."""
    
    print("\n📝 Test: Prompt Generation")
    print("-" * 30)
    
    try:
        from agents.autonomous_interviewer import AutonomousInterviewer
        
        interviewer = AutonomousInterviewer()
        
        # Test prompt building
        prompt = interviewer._build_prompt(
            role="Software Engineer",
            seniority="Senior",
            skill="System Design",
            interview_stage="problem_understanding",
            conversation_history=[
                {"role": "interviewer", "content": "Tell me about a challenging system design problem you've solved."},
                {"role": "user", "content": "I designed a scalable notification system for a social media app."}
            ],
            session_context={"start_time": 1234567890, "estimated_duration": 45}
        )
        
        print(f"✅ Generated prompt successfully")
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Contains role: {'Software Engineer' in prompt}")
        print(f"   Contains skill: {'System Design' in prompt}")
        print(f"   Contains stages: {'problem_understanding' in prompt}")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt generation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Autonomous Interviewer Tests")
    print("=" * 50)
    
    # Set up environment variables for testing
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY not set. Some tests may fail.")
    
    if not os.environ.get('REDIS_URL'):
        print("⚠️  Warning: REDIS_URL not set. Session tracking tests may fail.")
    
    # Run tests
    test1_passed = test_autonomous_interviewer()
    test2_passed = test_prompt_generation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Autonomous Interviewer Tests: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Prompt Generation Tests: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The autonomous interviewer is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)
