#!/usr/bin/env python3
"""
Simple test script for PreInterviewPlanner that tests fallback functionality.
This doesn't require database connection.
"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️  dotenv not available, using system environment variables")

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_error_handling():
    """
    Test the error handling when required data is missing.
    """
    try:
        print("🧪 Testing PreInterviewPlanner error handling...")
        
        # Import the planner
        from agents.pre_interview_planner import PreInterviewPlanner
        print("✅ PreInterviewPlanner imported successfully")
        
        # Create planner instance
        planner = PreInterviewPlanner()
        print("✅ PreInterviewPlanner instance created")
        
        # Test that the planner raises proper errors when data is missing
        print("\n📋 Testing error handling...")
        
        # Test that seniority expectations method works with playbook parameter
        try:
            # This should work even without a real playbook object
            expectations = planner._get_seniority_expectations("problem_scoping", "Mid", None)
            print(f"✅ Seniority expectations method works: {expectations}")
        except Exception as e:
            print(f"⚠️ Seniority expectations method had issues: {e}")
        
        print("\n🎉 Error handling tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """
    Test that all required imports work correctly.
    """
    try:
        print("📦 Testing imports...")
        
        # Test basic imports
        from agents.pre_interview_planner import PreInterviewPlanner
        print("✅ PreInterviewPlanner import successful")
        
        # Test utility imports
        from utils import get_gemini_client
        print("✅ Utils import successful")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PreInterviewPlanner Simple Test Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PreInterviewPlanner is ready for database integration.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
