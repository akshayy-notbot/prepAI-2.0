"""
Prompt Capture Decorator
Automatically captures prompt executions for AI agent methods
using a simple decorator pattern.
"""

import functools
import time
import json
from typing import Dict, Any, Optional, Callable
from .prompt_evaluator import prompt_evaluator

def capture_prompt_execution(component: str, 
                           method: str, 
                           prompt_type: str,
                           extract_prompt: Optional[Callable] = None,
                           extract_input_data: Optional[Callable] = None,
                           extract_output_data: Optional[Callable] = None,
                           extract_session_context: Optional[Callable] = None):
    """
    Decorator to automatically capture prompt executions for AI agent methods.
    
    Args:
        component: The component name (e.g., "autonomous_interviewer")
        method: The method name (e.g., "conduct_interview_turn")
        prompt_type: The type of prompt (e.g., "interview_question")
        extract_prompt: Function to extract prompt text from method args/kwargs
        extract_input_data: Function to extract input data from method args/kwargs
        extract_output_data: Function to extract output data from method return value
        extract_session_context: Function to extract session context from method args/kwargs
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            execution_id = None
            
            try:
                # Extract prompt text
                prompt_text = ""
                if extract_prompt:
                    prompt_text = extract_prompt(*args, **kwargs)
                
                # Extract input data
                input_data = {}
                if extract_input_data:
                    input_data = extract_input_data(*args, **kwargs)
                
                # Extract session context
                session_context = {}
                if extract_session_context:
                    session_context = extract_session_context(*args, **kwargs)
                
                # Execute the original function
                result = func(*args, **kwargs)
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract output data
                output_data = {}
                response_text = ""
                if extract_output_data:
                    output_data = extract_output_data(result)
                    response_text = str(result) if result else ""
                
                # Capture the execution
                execution_id = prompt_evaluator.capture_execution(
                    component=component,
                    method=method,
                    prompt_type=prompt_type,
                    input_data=input_data,
                    prompt_text=prompt_text,
                    output_data=output_data,
                    response_text=response_text,
                    latency_ms=latency_ms,
                    success=True,
                    session_id=session_context.get("session_id"),
                    user_id=session_context.get("user_id"),
                    role=session_context.get("role"),
                    seniority=session_context.get("seniority"),
                    skill=session_context.get("skill")
                )
                
                return result
                
            except Exception as e:
                # Calculate latency even for failed executions
                latency_ms = (time.time() - start_time) * 1000
                
                # Capture failed execution
                execution_id = prompt_evaluator.capture_execution(
                    component=component,
                    method=method,
                    prompt_type=prompt_type,
                    input_data=input_data if 'input_data' in locals() else {},
                    prompt_text=prompt_text if 'prompt_text' in locals() else "",
                    output_data={},
                    response_text="",
                    latency_ms=latency_ms,
                    success=False,
                    error_message=str(e),
                    session_id=session_context.get("session_id") if 'session_context' in locals() else None,
                    user_id=session_context.get("user_id") if 'session_context' in locals() else None,
                    role=session_context.get("role") if 'session_context' in locals() else None,
                    seniority=session_context.get("seniority") if 'session_context' in locals() else None,
                    skill=session_context.get("skill") if 'session_context' in locals() else None
                )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

# Common extractor functions for different AI agent patterns
def extract_prompt_from_kwargs(prompt_key: str = "prompt"):
    """Extract prompt text from kwargs"""
    def extractor(*args, **kwargs):
        return kwargs.get(prompt_key, "")
    return extractor

def extract_input_data_from_kwargs(*keys):
    """Extract specific keys from kwargs as input data"""
    def extractor(*args, **kwargs):
        return {key: kwargs.get(key) for key in keys if key in kwargs}
    return extractor

def extract_output_data_from_json_response():
    """Extract output data from JSON response"""
    def extractor(result):
        if isinstance(result, dict):
            return result
        elif isinstance(result, str):
            try:
                return json.loads(result)
            except:
                return {"raw_response": result}
        return {"raw_response": str(result)}
    return extractor

def extract_session_context_from_kwargs():
    """Extract session context from kwargs"""
    def extractor(*args, **kwargs):
        return {
            "session_id": kwargs.get("session_id"),
            "user_id": kwargs.get("user_id"),
            "role": kwargs.get("role"),
            "seniority": kwargs.get("seniority"),
            "skill": kwargs.get("skill")
        }
    return extractor

# Example usage patterns
"""
# For autonomous interviewer methods:
@capture_prompt_execution(
    component="autonomous_interviewer",
    method="conduct_interview_turn",
    prompt_type="interview_question",
    extract_input_data=extract_input_data_from_kwargs("role", "seniority", "skill", "interview_stage"),
    extract_output_data=extract_output_data_from_json_response(),
    extract_session_context=extract_session_context_from_kwargs()
)
def conduct_interview_turn(self, role, seniority, skill, interview_stage, ...):
    # Method implementation
    pass

# For evaluation methods:
@capture_prompt_execution(
    component="evaluation",
    method="evaluate_answer",
    prompt_type="evaluation",
    extract_input_data=extract_input_data_from_kwargs("answer", "question", "skills_to_assess"),
    extract_output_data=extract_output_data_from_json_response(),
    extract_session_context=extract_session_context_from_kwargs()
)
def evaluate_answer(self, answer, question, skills_to_assess, ...):
    # Method implementation
    pass
"""
