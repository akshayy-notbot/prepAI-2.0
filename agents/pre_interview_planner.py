import os
import json
import uuid
from typing import Dict, Any, List, Optional
from utils import get_gemini_client
from datetime import datetime

class PreInterviewPlanner:
    """
    Pre-interview planning agent that creates comprehensive interview plans.
    Selects archetypes, generates prompts, and creates signal maps for evaluation.
    """
    
    def __init__(self):
        self.llm = get_gemini_client()
    
    def create_interview_plan(self, role: str, skill: str, seniority: str) -> Dict[str, Any]:
        """
        Creates complete interview plan including:
        - Archetype selection
        - Interview prompt generation
        - Signal mapping
        - Evaluation criteria
        
        Args:
            role: The role being interviewed for (e.g., "Product Manager")
            skill: The primary skill being tested (e.g., "Product Design")
            seniority: The seniority level (e.g., "Junior", "Mid", "Senior")
            
        Returns:
            Dict containing complete interview plan
        """
        try:
            # Step 1: Get playbook data first
            playbook = self._get_playbook(role, skill, seniority)
            
            # Step 2: Prioritize top evaluation dimensions and select most relevant archetype
            top_dimensions, selected_archetype = self._prioritize_and_select_archetype(role, skill, seniority, playbook)
            
            # Step 3: Generate role-specific interview prompt/case study/question
            interview_prompt = self._generate_interview_prompt(
                role, skill, seniority, selected_archetype, playbook, top_dimensions
            )
            
            # Create comprehensive plan with all necessary data for enhanced evaluation
            interview_plan = {
                "plan_id": str(uuid.uuid4()),
                "top_evaluation_dimensions": top_dimensions,
                "selected_archetype": selected_archetype,
                "interview_prompt": interview_prompt,
                "role": role,
                "skill": skill,
                "seniority": seniority,
                "seniority_criteria": self._get_seniority_criteria_content(playbook.seniority_criteria),
                "good_vs_great_examples": self._get_good_vs_great_examples_content(playbook.good_vs_great_examples),
                "interview_objective": playbook.interview_objective,
                "core_philosophy": getattr(playbook, 'core_philosophy', None),
                "created_at": str(datetime.utcnow())
            }
            
            print(f"✅ Interview plan created for {seniority} {role} - {skill}")
            return interview_plan
            
        except Exception as e:
            print(f"❌ Failed to create interview plan: {e}")
            raise Exception(f"Failed to create interview plan for {role} - {skill} - {seniority}: {str(e)}")
    
    def _get_seniority_criteria_content(self, seniority_criteria):
        """Extract content from seniority_criteria, handling both old and new formats"""
        if isinstance(seniority_criteria, dict) and "content" in seniority_criteria:
            return seniority_criteria["content"]
        return seniority_criteria
    
    def _get_good_vs_great_examples_content(self, good_vs_great_examples):
        """Extract content from good_vs_great_examples, handling both old and new formats"""
        if isinstance(good_vs_great_examples, dict) and "content" in good_vs_great_examples:
            return good_vs_great_examples["content"]
        return good_vs_great_examples
    
    def _get_playbook(self, role: str, skill: str, seniority: str) -> Any:
        """
        Retrieves the interview playbook for the given role × skill × seniority combination.
        """
        try:
            from models import get_session_local, InterviewPlaybook
            
            session_local = get_session_local()
            db = session_local()
            
            # Find the playbook for this role × skill × seniority combination
            playbook = db.query(InterviewPlaybook).filter(
                InterviewPlaybook.role == role,
                InterviewPlaybook.skill == skill,
                InterviewPlaybook.seniority == seniority
            ).first()
            
            if not playbook:
                raise Exception(f"No interview playbook found for {role} - {skill} - {seniority}. Please ensure the playbook exists in the database.")
            
            # Store the strategy text directly for use in prompts
            if hasattr(playbook, 'pre_interview_strategy') and playbook.pre_interview_strategy:
                playbook.strategy_text = playbook.pre_interview_strategy
            
            return playbook
                
        except Exception as e:
            raise Exception(f"Failed to read playbook from database for {role} - {skill} - {seniority}: {str(e)}")
        finally:
            if db:
                db.close()
    
    def _prioritize_and_select_archetype(self, role: str, skill: str, seniority: str, playbook: Any) -> tuple[str, str]:
        """
        Uses LLM to:
        Step 1: Prioritize the top 3-4 evaluation dimensions for the given role × skill × seniority combination
        Step 2: Select the most relevant archetype based on those top dimensions
        
        Returns: (top_dimensions, selected_archetype)
        """
        if not playbook or not playbook.evaluation_dimensions:
            raise Exception(f"No evaluation dimensions found in playbook for {role} - {skill} - {seniority}")
        
        # Get all evaluation dimensions from the playbook
        # Handle both old string format and new JSON structure
        if isinstance(playbook.evaluation_dimensions, dict) and "content" in playbook.evaluation_dimensions:
            evaluation_dimensions = playbook.evaluation_dimensions["content"]
        else:
            evaluation_dimensions = playbook.evaluation_dimensions
        
        # Create prompt for LLM to make intelligent decisions
        prompt = f"""You are a senior expert Interview designer from a top-tier tech company (like Google or Meta) with an experience of more than 15 years in taking interviews.
You are an expert interviewer planning a {skill} interview for a {seniority} {role} position.

Available evaluation dimensions for this a {skill} interview for a {seniority} {role} position:
{evaluation_dimensions}. And Seniority expectations are as follows {self._get_seniority_criteria_content(playbook.seniority_criteria)}

Interview objective: {playbook.interview_objective}

Pre-Interview Strategy (use as reference, adapt to this specific context):
{getattr(playbook, 'strategy_text', 'No strategy guidance available')}

Your task is to:
1. PRIORITIZE: Select the top 3-4 evaluation dimension that should be the primary focus for this role × skill × seniority combination
2. SELECT ARCHETYPE: Choose the most relevant interview archetype from the available archetypes

Consider:
- Role requirements and responsibilities
- Skill complexity and depth needed
- Seniority level expectations
- Which archetype will best reveal signals for the top dimension
- Use the guidance examples above as reference, but make your own autonomous decision for THIS specific combination

FAANG-LEVEL RIGOR:**
- The prioritisation & selected Archetype must reflect the rigorous, first-principles thinking required in FAANG-level interviews
- You can take motivation for these dimensions & archetypes from platforms like tryexponent and LeetCode for the role × skill × seniority combination 

Return ONLY a JSON object with this exact structure:
{{
    "top_dimensions": "dimension_names",
    "selected_archetype": "archetype_name",
    "reasoning": "Brief explanation of your choices"
}}"""

        try:
            response = self.llm.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            
            top_dimensions = result["top_dimensions"]
            selected_archetype = result["selected_archetype"]
            
            print(f"🎯 LLM selected top dimensions: {top_dimensions}")
            print(f"🎭 LLM selected archetype: {selected_archetype}")
            print(f"💭 Reasoning: {result.get('reasoning', 'N/A')}")
            
            return top_dimensions, selected_archetype
            
        except Exception as e:
            raise Exception(f"LLM failed to prioritize dimension and select archetype for {role} - {skill} - {seniority}: {str(e)}")
    
    def _generate_interview_prompt(self, role: str, skill: str, seniority: str, archetype: str, playbook: Any, top_dimensions: str) -> str:
        """
        Generates role-specific interview prompt using the selected archetype.
        Uses the provided playbook data.
        """
        if not playbook or not playbook.interview_objective:
            raise Exception(f"No interview objective found in playbook for {role} - {skill} - {seniority}. Please ensure the playbook has an interview_objective field.")
        
        # Use the interview objective from the playbook
        prompt = f"""You are a senior expert Interview designer from a top-tier tech company (like Google or Meta) with an experience of more than 15 years in taking interviews.
You are an expert interviewer planning a {skill} interview for a {seniority} {role} position.

Interview Objective: {playbook.interview_objective}
Archetype: {archetype}

Top evaluation dimensions for this {skill} interview for a {seniority} {role} position we want to evaluate:
{top_dimensions}. And Seniority expectations are as follows: {self._get_seniority_criteria_content(playbook.seniority_criteria)}

Interview objective: {playbook.interview_objective}

FAANG-LEVEL RIGOR:**
- The interview and case study must reflect the rigorous, first-principles thinking required in FAANG-level interviews
- Emulate the strategic depth of case studies from platforms like tryexponent and LeetCode

Generate a specific and engaging opening question that will start the interview taking into account the following:
1. Uses the {archetype} archetype
2. Tests the {top_dimensions} for {skill} for a {seniority} {role} position
3. Is open-ended enough for a 45-minute discussion
4. Feels natural and conversational
5. Aligns with the objective: {playbook.interview_objective}


FAANG-LEVEL RIGOR:**
- The interview and case study must reflect the rigorous, first-principles thinking required in FAANG-level interviews
- Emulate the strategic depth of case studies from platforms like tryexponent and LeetCode


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
Return ONLY a JSON object with this exact structure:

{{
  "chain_of_thought": [
    "Your reasoning for choosing this opening approach",
    "Your reasoning for the specific problem/scenario",
    "Your reasoning for the difficulty level and seniority alignment",
    "Your reasoning for how this tests the evaluation dimensions"
  ],
  "interview_question": "Your complete opening statement and first question"
}}

**GENERATE YOUR OPENING NOW:**"""

        try:
            response = self.llm.generate_content(prompt)
            response_text = response.text.strip()
            
            # Debug: Print the raw response
            print(f"🔍 DEBUG - Raw LLM response:")
            print(f"Response length: {len(response_text)}")
            print(f"First 500 chars: {response_text[:500]}")
            print(f"Last 200 chars: {response_text[-200:]}")
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Debug: Print the cleaned response
            print(f"🔍 DEBUG - Cleaned response for JSON parsing:")
            print(f"Cleaned length: {len(response_text)}")
            print(f"Cleaned text: {response_text}")
            
            result = json.loads(response_text.strip())
            
            # Extract the interview question from the JSON response
            interview_question = result.get("interview_question", "")
            chain_of_thought = result.get("chain_of_thought", [])
            
            if not interview_question:
                raise Exception("LLM failed to generate interview question")
            
            print(f"🎭 Generated interview question with chain of thought: {len(chain_of_thought)} reasoning steps")
            return interview_question
            
        except Exception as e:
            raise Exception(f"LLM prompt generation failed for {role} - {skill} - {seniority}: {str(e)}")
    
    
