import os
import json
from typing import List, Dict, Any
from utils import get_gemini_client

def evaluate_answer(answer: str, question: str, skills_to_assess: List[str]) -> Dict[str, Any]:
    """
    Evaluate a user's answer against specific skills using the Gemini API.
    
    Args:
        answer (str): The user's text answer
        question (str): The question they were asked
        skills_to_assess (List[str]): List of skills to evaluate (e.g., ["Problem Framing", "Tradeoff Analysis"])
    
    Returns:
        Dict[str, Any]: Structured scorecard in JSON format with scores and feedback
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
    prompt = f"""You are an expert FAANG interviewer. Your job is to evaluate the candidate's answer impartially.

Question Asked: {question}

Candidate's Answer: {answer}

Skills to Assess: {', '.join(skills_to_assess)}

Instructions:
1. Evaluate ONLY the skills listed above. Do not assess skills not mentioned.
2. Use a 1-5 scoring system where:
   - 1 = Poor/Inadequate
   - 2 = Below Average
   - 3 = Average/Adequate
   - 4 = Above Average/Good
   - 5 = Excellent/Outstanding
3. Provide specific, constructive feedback for each skill
4. Calculate an overall score (average of individual skill scores)
5. Return ONLY a valid JSON object with this exact structure:
{{
    "scores": {{
        "skill_name": {{
            "score": 1-5,
            "feedback": "specific feedback for this skill"
        }}
    }},
    "overall_score": "average_score",
    "overall_feedback": "summary of strengths and areas for improvement"
}}

Be impartial, fair, and constructive in your evaluation."""

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
        
        if "scores" not in evaluation_result or "overall_score" not in evaluation_result:
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
