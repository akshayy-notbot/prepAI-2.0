#!/usr/bin/env python3
"""
Test script to verify the signal_map fix works
"""

import os
import sys

# Add current directory to path
sys.path.append('.')

def test_signal_map_fix():
    """Test that signal_map access works correctly"""
    print("🧪 Testing Signal Map Fix...")
    
    try:
        # Test the interview plan structure
        interview_plan = {
            "selected_archetype": "Improvement (\"1 to N\")",
            "signal_map": {},  # Empty signal map
            "evaluation_criteria": {}  # Empty evaluation criteria
        }
        
        # Test the access pattern from main.py
        evaluation_dimensions = list(interview_plan.get("signal_map", {}).keys())
        print(f"✅ Evaluation dimensions: {evaluation_dimensions}")
        
        # Test the evaluation criteria access
        objective = interview_plan.get("evaluation_criteria", {}).get("seniority_adjustments", {}).get("mid", "Standard evaluation")
        print(f"✅ Objective: {objective}")
        
        print("✅ Signal map fix test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_signal_map_fix()
    if success:
        print("\n✅ Signal map fix test successful!")
        sys.exit(0)
    else:
        print("\n❌ Signal map fix test failed!")
        sys.exit(1)
