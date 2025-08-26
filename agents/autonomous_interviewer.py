import os
import json
import time
from typing import List, Dict, Any, Optional
from utils import get_gemini_client

class AutonomousInterviewer:
    """
    Single autonomous LLM interviewer that handles the entire interview flow.
    Analyzes responses, decides next steps, and generates questions in one unified call.
    """
    
    def __init__(self):
        self.llm = None  # Lazy initialization
        self._model = None
    
    def _get_model(self):
        """Lazy initialization of Gemini model"""
        if self._model is None:
            self._model = get_gemini_client()
        return self._model
    
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
            
            print(f"🔍 Conducting interview turn with {len(conversation_history)} conversation turns")
            for i, turn in enumerate(conversation_history):
                print(f"  Turn {i+1}: {turn['role']} - {turn['content'][:100]}...")
            
            print(f"📝 FULL PROMPT SENT TO AUTONOMOUS INTERVIEWER:")
            print(f"================================================")
            print(prompt)
            print(f"================================================")
            
            # Get LLM response
            model = self._get_model()
            print(f"🤖 Calling Gemini API for interview turn...")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse the JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            print(f"🔍 Parsing interview response...")
            print(f"📨 RAW RESPONSE FROM GEMINI:")
            print(f"================================================")
            print(response_text)
            print(f"================================================")
            
            result = json.loads(response_text.strip())
            print(f"✅ Interview response parsed successfully")
            print(f"🔍 FULL PARSED RESPONSE:")
            print(f"  - Chain of Thought: {result.get('chain_of_thought', [])}")
            print(f"  - Response Text: {result.get('response_text', 'No response text')}")
            print(f"  - Interview State: {result.get('interview_state', {})}")
            
            # Add performance metrics
            result["latency_ms"] = round((time.time() - start_time) * 1000, 2)
            result["timestamp"] = time.time()
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR in conduct_interview_turn: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            print(f"❌ Full error details: {str(e)}")
            
            # Fallback response in case of API failure
            fallback_response = {
                "chain_of_thought": [
                    "Error occurred during interview turn",
                    f"Error details: {str(e)}",
                    "Using fallback response"
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
            
            print(f"🔄 Returning fallback response: {fallback_response}")
            return fallback_response
    
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
You are conducting a real interview. Your job is to:
1. Analyze the candidate's latest response and overall performance
2. Decide what to explore next based on their strengths and areas for improvement
3. Generate the next question or statement that will best assess their {skill}
4. Track your interview strategy and adapt based on their performance

**IMPORTANT: Handle Clarifying Questions Naturally**
- If the candidate asks a clarifying question (e.g., "What do you mean by X?", "Can you give an example?", "Can you give me background about..."), 
  answer it helpfully and then guide them back to answering the original question
- Be encouraging and patient when they need clarification
- Provide clear explanations or examples to help them understand


**EXAMPLES OF CLARIFYING QUESTIONS TO HANDLE:**
- "Can you give me background about the company and the product?"
- "What do you mean by 'conversion rates'?"
- "Can you give me an example?"
- "I don't understand the scenario, can you explain more?"

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
- Keep the interview flowing naturally and engaging

**CRITICAL: When the candidate asks for clarification about the scenario, company, or product:**
- Provide the requested background information or clarification
- Be specific and helpful with details
- Then guide them back to answering the original question
- Do NOT ignore their clarification request or give generic responses

**OUTPUT FORMAT:**
Your response MUST be a single, valid JSON object with this exact structure:

{{
  "chain_of_thought": [
    "Your first reasoning step - analyze their response",
    "Your second reasoning step - assess their performance", 
    "Your third reasoning step - decide next direction",
    "Your fourth reasoning step - plan your question"
  ],
  "response_text": "The exact words you will say to the candidate. This should be your next question or statement.",
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
Generate an engaging opening that will start the interview and assess the candidate's {skill}.

**CRITICAL REQUIREMENTS:**
- Start with a warm, professional greeting
- IMMEDIATELY present a specific, concrete problem or scenario related to {skill}
- Do NOT end with "Let me present you with a scenario..." - actually present the scenario
- Make it appropriate for {seniority} level
- Be encouraging and put the candidate at ease
- Give them something concrete to respond to

**EXAMPLES OF GOOD OPENINGS:**
- For A/B Testing: "Hello! I'm excited to interview you for the {seniority} {role} position. Today we'll focus on A/B Testing. Imagine you're working for an e-commerce company and want to test whether changing the checkout button color from blue to green increases conversion rates. How would you design this experiment?"
- For System Design: "Hello! I'm excited to interview you for the {seniority} {role} position. Today we'll focus on System Design. Design a URL shortening service like bit.ly that can handle 100 million URLs. How would you approach this?"

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
            model = self._get_model()
            print(f"🤖 Calling Gemini API for initial question...")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            print(f"✅ Gemini API response received: {len(response_text)} characters")
            
            # Parse the JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            print(f"🔍 Attempting to parse JSON response...")
            result = json.loads(response_text.strip())
            print(f"✅ JSON parsed successfully")
            result["timestamp"] = time.time()
            
            return result
            
        except Exception as e:
            print(f"❌ Error in get_initial_question: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            # Fallback opening with specific scenario
            if skill.lower() == "a/b testing":
                fallback_scenario = f"Hello! I'm excited to interview you for the {seniority} {role} position. Today we'll focus on A/B Testing. Imagine you're working for an e-commerce company and want to test whether changing the checkout button color from blue to green increases conversion rates. How would you design this experiment?"
            elif skill.lower() == "system design":
                fallback_scenario = f"Hello! I'm excited to interview you for the {seniority} {role} position. Today we'll focus on System Design. Design a URL shortening service like bit.ly that can handle 100 million URLs. How would you approach this?"
            else:
                fallback_scenario = f"Hello! I'm excited to interview you for the {seniority} {role} position. Today we'll focus on {skill}. Please describe a challenging project you've worked on related to {skill} and walk me through your approach."
            
            return {
                "chain_of_thought": [
                    "Using fallback opening due to API error",
                    "Providing specific scenario to get interview started"
                ],
                "response_text": fallback_scenario,
                "interview_state": {
                    "current_stage": "problem_understanding",
                    "skill_progress": "not_started",
                    "next_focus": "initial_problem_presentation"
                },
                "error": str(e),
                "timestamp": time.time()
            }
