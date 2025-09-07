import os
import json
from typing import List, Dict, Any
from utils import get_gemini_client

def evaluate_answer(answer: str, question: str, skills_to_assess: List[str], conversation_history: List[Dict[str, str]] = None, role_context: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Evaluate a user's answer against specific skills using the Gemini API.
    
    Args:
        answer (str): The user's text answer
        question (str): The question they were asked
        skills_to_assess (List[str]): List of skills to evaluate (e.g., ["Problem Framing", "Tradeoff Analysis"])
        conversation_history (List[Dict[str, str]]): Previous Q&A pairs for context
        role_context (Dict[str, str]): Role and seniority information (e.g., {"role": "Software Engineer", "seniority": "Senior"})
    
    Returns:
        Dict[str, Any]: Structured scorecard in JSON format with scores, feedback, and ideal response
    """
    
    # Configure Gemini client
    try:
        model = get_gemini_client()
    except Exception as e:
        return {
            "error": f"Failed to configure Gemini API: {str(e)}",
            "scores": {},
            "overall_score": 0,
            "feedback": "Unable to evaluate due to API configuration error"
        }
    
    # Craft the evaluation prompt
    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\nConversation History (for context):\n"
        for i, qa in enumerate(conversation_history):
            conversation_context += f"Q{i+1}: {qa.get('question', '')}\nA{i+1}: {qa.get('answer', '')}\n"
    
    role_context_info = ""
    if role_context:
        role_context_info = f"\n\nRole Context:\n- Position: {role_context.get('role', 'Not specified')}\n- Seniority Level: {role_context.get('seniority', 'Not specified')}\n- Skills Focus: {', '.join(skills_to_assess)}"
    
    prompt = f"""You are an expert FAANG interviewer. Your job is to evaluate the candidate's answer impartially and provide an ideal response example.

Question Asked: {question}

Candidate's Answer: {answer}

Skills to Assess: {', '.join(skills_to_assess)}{role_context_info}{conversation_context}

Evaluation Guidance (use as reference, adapt to this specific response):
{_get_evaluation_guidance(role_context)}

Good vs Great Examples (use as reference for performance levels):
{_get_good_vs_great_examples(role_context)}

Instructions:
1. Evaluate ONLY the skills listed above. Do not assess skills not mentioned.
2. Consider the role and seniority level when evaluating - expectations differ for Junior vs Senior positions.
3. Use a 1-5 scoring system where:
   - 1 = Poor/Inadequate
   - 2 = Below Average
   - 3 = Average/Adequate
   - 4 = Above Average/Good
   - 5 = Excellent/Outstanding
4. Provide specific, constructive feedback for each skill
5. Calculate an overall score (average of individual skill scores)
6. Generate an ideal response example that demonstrates excellent performance for the specific role and seniority level
7. Use the evaluation guidance and good vs great examples above as reference, but make your own autonomous assessment based on the actual response
8. Return ONLY a valid JSON object with this exact structure:
{{
    "scores": {{
        "skill_name": {{
            "score": 1-5,
            "feedback": "specific feedback for this skill"
        }}
    }},
    "overall_score": "average_score",
    "overall_feedback": "summary of strengths and areas for improvement",
    "ideal_response": "A comprehensive, well-structured answer that demonstrates excellent performance for a {role_context.get('seniority', '')} {role_context.get('role', 'professional')} position. Include specific examples, frameworks, and best practices appropriate for this level."
}}

Be impartial, fair, and constructive in your evaluation. The ideal response should be educational and show what excellence looks like for the specific role and seniority level."""

    try:
        # Call the Gemini API
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response text
        # Remove markdown code fences if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse the JSON response
        evaluation_result = json.loads(response_text)
        
        # Validate the structure
        if not isinstance(evaluation_result, dict):
            raise ValueError("Response is not a valid JSON object")
        
        if "scores" not in evaluation_result or "overall_score" not in evaluation_result or "ideal_response" not in evaluation_result:
            raise ValueError("Response missing required fields")
        
        return evaluation_result
        
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse AI response as JSON: {str(e)}",
            "raw_response": response_text if 'response_text' in locals() else "No response received",
            "scores": {},
            "overall_score": 0,
            "feedback": "Unable to parse evaluation results"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error during evaluation: {str(e)}",
            "scores": {},
            "overall_score": 0,
            "feedback": "Evaluation failed due to unexpected error"
        }

def _get_evaluation_guidance(role_context: Dict[str, str]) -> str:
    """Get evaluation guidance patterns for the role/seniority combination"""
    if not role_context or not isinstance(role_context, dict):
        raise ValueError("Role context must be a non-empty dictionary")
    
    # Check if evaluation guidance is available in the role context
    if 'post_interview_evaluation' in role_context and role_context['post_interview_evaluation']:
        return role_context['post_interview_evaluation']
    
    # Check if it's available in interview plan
    interview_plan = role_context.get('interview_plan', {})
    if 'post_interview_evaluation' in interview_plan and interview_plan['post_interview_evaluation']:
        return interview_plan['post_interview_evaluation']
    
    raise ValueError("No evaluation guidance found in role context. The playbook must include 'post_interview_evaluation' data.")

def _get_good_vs_great_examples(role_context: Dict[str, str]) -> str:
    """Get good vs great examples for the role/seniority combination"""
    if not role_context or not isinstance(role_context, dict):
        raise ValueError("Role context must be a non-empty dictionary")
    
    # Check if good vs great examples are available in the role context
    if 'good_vs_great_examples' in role_context and role_context['good_vs_great_examples']:
        return str(role_context['good_vs_great_examples'])
    
    # Check if it's available in interview plan
    interview_plan = role_context.get('interview_plan', {})
    if 'good_vs_great_examples' in interview_plan and interview_plan['good_vs_great_examples']:
        return str(interview_plan['good_vs_great_examples'])
    
    raise ValueError("No good vs great examples found in role context. The playbook must include 'good_vs_great_examples' data.")
