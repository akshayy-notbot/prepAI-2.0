import os
import json
import time
from typing import List, Dict, Any, Optional
from utils import get_gemini_client, get_gemini_client_with_temperature

class AutonomousInterviewer:
    """
    Single autonomous LLM interviewer that handles the entire interview flow.
    Analyzes responses, decides next steps, and generates questions in one unified call.
    """
    
    def __init__(self):
        self.llm = None  # Lazy initialization
        self._model = None
        self._model_with_temp = None  # For temperature-controlled calls
    
    def _get_model(self):
        """Lazy initialization of Gemini model"""
        if self._model is None:
            self._model = get_gemini_client()
        return self._model
    
    def _get_model_with_temperature(self, temperature: float = 0.7):
        """Lazy initialization of Gemini model with temperature control"""
        if self._model_with_temp is None:
            self._model_with_temp, _ = get_gemini_client_with_temperature(temperature)
        return self._model_with_temp
    
    def conduct_interview_turn(self, 
                              role: str,
                              seniority: str, 
                              skill: str,
                              interview_stage: str,
                              conversation_history: List[Dict[str, Any]],
                              session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct a single interview turn using autonomous LLM decision making.
        
        Args:
            role: The role being interviewed for (e.g., "Software Engineer")
            seniority: The seniority level (e.g., "Junior", "Senior", "Staff+")
            skill: The primary skill being tested (e.g., "System Design")
            interview_stage: Current stage of the interview
            conversation_history: List of conversation turns
            session_context: Additional session information
            
        Returns:
            Dict containing chain_of_thought, response_text, and interview_state
        """
        
        start_time = time.time()
        
        try:
            # Craft the autonomous interviewer prompt
            prompt = self._build_prompt(
                role, seniority, skill, interview_stage, 
                conversation_history, session_context
            )
            
            # Get LLM response with temperature control for better variety
            model = self._get_model_with_temperature(temperature=0.6)  # Balanced temperature for follow-up questions
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse the JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            
            # Add performance metrics
            result["latency_ms"] = round((time.time() - start_time) * 1000, 2)
            result["timestamp"] = time.time()
            
            return result
            
        except Exception as e:
            # Fallback response in case of API failure
            return {
                "chain_of_thought": [
                    "Error occurred during interview turn",
                    "Falling back to default follow-up question"
                ],
                "response_text": "I see. Can you tell me more about your approach to this problem?",
                "interview_state": {
                    "current_stage": interview_stage,
                    "skill_progress": "unknown",
                    "next_focus": "continue_current_topic"
                },
                "latency_ms": 0,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _build_prompt(self, role: str, seniority: str, skill: str, 
                      interview_stage: str, conversation_history: List[Dict], 
                      session_context: Dict) -> str:
        """
        Build the comprehensive prompt for the autonomous interviewer.
        """
        
        # Format conversation history for readability
        formatted_history = self._format_conversation_history(conversation_history)
        
        prompt = f"""You are an expert {seniority} {role} interviewer testing {skill}. You have full autonomy to conduct this interview however you think is best.

**INTERVIEW CONTEXT:**
- Role: {role}
- Seniority: {seniority} 
- Skill Being Tested: {skill}
- Current Stage: {interview_stage}
- Session Context: {json.dumps(session_context, indent=2)}

**CONVERSATION HISTORY:**
{formatted_history}

**YOUR MISSION:**
You are a senior expert Interview Designer and conductor from a top-tier tech company (like Google or Meta) with an experience of more than 15 years in taking interviews.
You are conducting a real interview. Your job is to:
1. Analyze the candidate's latest response and overall performance
2. Decide what to explore next based on their strengths and areas for improvement
3. Generate the next question or statement that will best assess their {skill}
4. Track your interview strategy and adapt based on their performance

**INTERVIEW STAGES (Guide your progression):**
- **Problem Understanding**: Assess their ability to grasp the core problem
- **Solution Design**: Test their approach to solving the problem
- **Technical Depth**: Explore their technical knowledge and reasoning
- **Trade-offs & Constraints**: Evaluate their understanding of real-world considerations
- **Implementation**: Test their practical execution thinking
- **Adaptation**: Assess how they handle changes and challenges

**YOUR APPROACH:**
- Be professional, insightful, and encouraging
- Ask open-ended questions that probe for depth, not just surface answers
- Focus on understanding their "why" and "how", not just "what"
- Adapt your questions based on how well they're performing
- If they're struggling, provide gentle guidance and simpler questions
- If they're excelling, challenge them with more complex scenarios
- If the candidate asks clarification questions, provide a clear and concise answer. Do not ask a question in that turn
- If the candidate asks for some time to think, acknowledge their request and then wait for them to respond
- Keep the interview flowing naturally and engaging


- **MAINTAIN FAANG-LEVEL RIGOR**: Ensure all follow-up questions maintain the same strategic depth and first-principles thinking
- **SENIORITY CONSISTENCY**: Keep questions aligned with the {seniority} level scope established in the initial case study

**OUTPUT FORMAT:**
Your response MUST be a single, valid JSON object with this exact structure:

{{
  "chain_of_thought": [
    "Your first reasoning step - analyze their response",
    "Your second reasoning step - assess their performance", 
    "Your third reasoning step - decide next direction",
    "Your fourth reasoning step - plan your question"
  ],
  "response_text": "The exact words you will say to the candidate. This should be your next question or a clarification statement.",
  "interview_state": {{
    "current_stage": "The interview stage you're currently in or moving to",
    "skill_progress": "How well they're doing: 'beginner', 'intermediate', 'advanced', or 'expert'",
    "next_focus": "What specific aspect you plan to explore next"
  }}
}}

**EXECUTE YOUR INTERVIEW NOW:**"""
        
        return prompt
    
    def _format_conversation_history(self, conversation_history: List[Dict]) -> str:
        """
        Format conversation history for better prompt readability.
        """
        if not conversation_history:
            return "No previous conversation."
        
        formatted = []
        for i, turn in enumerate(conversation_history):
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            formatted.append(f"Turn {i+1} - {role.title()}: {content}")
        
        return "\n".join(formatted)
    
    def get_initial_question(self, role: str, seniority: str, skill: str, 
                           session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the initial interview question to start the session.
        """
        
        prompt = f"""You are an expert {seniority} {role} interviewer starting an interview to test {skill}.

**INTERVIEW CONTEXT:**
- Role: {role}
- Seniority: {seniority} 
- Skill Being Tested: {skill}
- Session Context: {json.dumps(session_context, indent=2)}

**YOUR TASK:**
You are a senior expert Interview designer and conductor from a top-tier tech company (like Google or Meta) with an experience of more than 15 years in taking interviews.
Generate an engaging opening question that will start the interview and assess the candidate's {skill}.

**CRITICAL REQUIREMENTS:**

**1. SENIORITY CALIBRATION - The case study scope MUST reflect the specified {seniority}:**
- **Junior**: A well-defined feature-level problem with clear boundaries and specific requirements
- **Senior**: A more ambiguous product-level or multi-feature problem requiring strategic thinking
- **Staff+**: A broad, strategic business-unit or ecosystem-level problem with multiple stakeholders

**2. SKILL FOCUS:**
- The central theme of the case study should assess the {skill} selected by the user
- Focus deeply on this specific skill area, not general knowledge

**3. FAANG-LEVEL RIGOR:**
- The interview and case study must reflect the rigorous, first-principles thinking required in FAANG-level interviews
- Emulate the strategic depth of case studies from platforms like tryexponent and LeetCode
- Present complex, real-world scenarios that test analytical and strategic thinking

**ADDITIONAL REQUIREMENTS:**
- Start with a warm, professional greeting
- Present a clear, engaging problem or scenario related to {skill}
- **CRITICAL**: Generate a unique, creative case study - avoid generic or repetitive scenarios
- Make it appropriate for {seniority} level
- Set clear expectations for the interview
- Be encouraging and put the candidate at ease

**CRITICAL OUTPUT REQUIREMENTS:**
- Write the complete opening statement as if you're speaking directly to the candidate
- Do NOT use placeholders like [candidate name], [company name], or [position]
- Do NOT use template language or brackets
- Write the actual words you would say, not a template
- Use "question" terminology, NOT "prompt"
- Speak naturally as an interviewer would in a real conversation

**OUTPUT FORMAT:**
{{
  "chain_of_thought": [
    "Your reasoning for choosing this opening approach",
    "Your reasoning for the specific problem/scenario",
    "Your reasoning for the difficulty level"
  ],
  "response_text": "Your complete opening statement and first question",
  "interview_state": {{
    "current_stage": "problem_understanding",
    "skill_progress": "not_started",
    "next_focus": "initial_problem_presentation"
  }}
}}

**GENERATE YOUR OPENING NOW:**"""
        
        try:
            model = self._get_model_with_temperature(temperature=0.7) # Use higher temperature for more creative case study generation
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse the JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            result["timestamp"] = time.time()
            
            return result
            
        except Exception as e:
            # Fallback opening
            return {
                "chain_of_thought": [
                    "Using fallback opening due to API error",
                    "Focusing on standard problem presentation"
                ],
                "response_text": f"Hello! I'm excited to interview you for the {seniority} {role} position. Today we'll be focusing on {skill}. Let me present you with a scenario to get started...",
                "interview_state": {
                    "current_stage": "problem_understanding",
                    "skill_progress": "not_started",
                    "next_focus": "initial_problem_presentation"
                },
                "error": str(e),
                "timestamp": time.time()
            }
