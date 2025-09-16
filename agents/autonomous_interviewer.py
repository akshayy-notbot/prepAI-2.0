import os
import json
import time
from typing import List, Dict, Any, Optional
from utils import get_gemini_client, get_gemini_client_with_temperature

class AutonomousInterviewer:
    """
    Enhanced autonomous LLM interviewer that integrates with PreInterviewPlanner
    and provides real-time signal tracking against evaluation dimensions.
    """
    
    def __init__(self):
        self.llm = None  # Lazy initialization
        self._model = None
        self._model_with_temp = None  # For temperature-controlled calls
        self.signal_tracker = SignalTracker()
    
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
                              session_context: Dict[str, Any],
                              interview_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct a single interview turn using autonomous LLM decision making
        with integrated signal tracking against evaluation dimensions.
        
        Args:
            role: The role being interviewed for (e.g., "Software Engineer")
            seniority: The seniority level (e.g., "Junior", "Senior", "Staff+")
            skill: The primary skill being tested (e.g., "System Design")
            interview_stage: Current stage of the interview
            conversation_history: List of conversation turns
            session_context: Additional session information
            interview_plan: Plan from PreInterviewPlanner containing evaluation dimensions and archetype
            
        Returns:
            Dict containing chain_of_thought, response_text, interview_state, and signal_evidence
        """
        
        # Get execution guidance directly from interview plan
        execution_guidance = interview_plan.get('during_interview_execution', 'No execution guidance available')
        
        start_time = time.time()
        
        try:
            # Extract data from the interview plan for signal tracking
            top_dimensions = interview_plan.get("top_evaluation_dimensions", "")
            selected_archetype = interview_plan.get("selected_archetype", "")
            seniority_criteria = interview_plan.get("seniority_criteria", {})
            
            # Track signals from the latest response with seniority context (good_vs_great only in final evaluation)
            signal_evidence = self._track_signals(
                conversation_history, 
                top_dimensions, 
                role, 
                skill, 
                seniority,
                seniority_criteria
            )
            
            # Craft the enhanced autonomous interviewer prompt
            prompt = self._build_enhanced_prompt(
                role, seniority, skill, interview_stage, 
                conversation_history, session_context, interview_plan,
                signal_evidence
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
            
            # Add signal tracking and performance metrics
            result["signal_evidence"] = signal_evidence
            result["latency_ms"] = round((time.time() - start_time) * 1000, 2)
            result["timestamp"] = time.time()
            
            return result
            
        except Exception as e:
            # Enhanced fallback response with signal tracking
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
                "signal_evidence": {},
                "latency_ms": 0,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _track_signals(self, conversation_history: List[Dict], 
                       top_dimensions: str, role: str, skill: str, seniority: str,
                       seniority_criteria: Dict) -> Dict[str, Any]:
        """
        Track signals from the latest response against evaluation dimensions.
        """
        if not conversation_history:
            return {}
        
        # Get the latest candidate response
        latest_response = None
        for turn in reversed(conversation_history):
            if turn.get("role") == "candidate":
                latest_response = turn.get("content", "")
                break
        
        if not latest_response:
            return {}
        
        # Use LLM to analyze signals against evaluation dimensions with playbook context
        prompt = f"""You are an expert interviewer analyzing a candidate's response for signals against evaluation dimensions.

**CONTEXT:**
- Role: {role}
- Skill: {skill}
- Seniority: {seniority}
- Top Evaluation Dimensions: {top_dimensions}

**CANDIDATE RESPONSE:**
{latest_response}

**YOUR TASK:**
Analyze this response and identify specific evidence (quotes, examples, behaviors) that indicate performance against each evaluation dimension.

**SIGNAL ANALYSIS:**
For each evaluation dimension, identify:
1. **Positive Signals**: Evidence of strong performance
2. **Areas for Improvement**: Evidence of gaps or weaknesses
3. **Specific Quotes**: Exact phrases that demonstrate the signal
4. **Confidence Level**: How confident you are in this assessment (High/Medium/Low)
5. **Seniority Alignment**: How well this aligns with {seniority} level expectations

**SENIORITY CRITERIA FOR THIS ROLE × SKILL × SENIORITY:**
{json.dumps(seniority_criteria, indent=2)}

**OUTPUT FORMAT:**
Return ONLY a JSON object with this structure:
{{
    "dimension_name": {{
        "positive_signals": ["specific evidence 1", "specific evidence 2"],
        "areas_for_improvement": ["gap 1", "gap 2"],
        "quotes": ["exact quote 1", "exact quote 2"],
        "confidence": "High/Medium/Low",
        "seniority_alignment": "How well this meets {seniority} expectations based on the specific criteria above",
        "overall_assessment": "Brief summary of performance"
    }}
}}

**ANALYZE NOW:**"""

        try:
            model = self._get_model()
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
            
        except Exception as e:
            print(f"Signal tracking failed: {e}")
            return {}
    
    def _build_enhanced_prompt(self, role: str, seniority: str, skill: str, 
                              interview_stage: str, conversation_history: List[Dict], 
                              session_context: Dict, interview_plan: Dict,
                              signal_evidence: Dict) -> str:
        """
        Build the enhanced prompt for the autonomous interviewer with signal tracking.
        """
        
        # Format conversation history for readability
        formatted_history = self._format_conversation_history(conversation_history)
        
        # Extract plan details
        top_dimensions = interview_plan.get("top_evaluation_dimensions", "")
        selected_archetype = interview_plan.get("selected_archetype", "")
        interview_objective = interview_plan.get("interview_objective", "")
        core_philosophy = interview_plan.get("core_philosophy", "")
        
        # Format signal evidence for context
        signal_summary = self._format_signal_evidence(signal_evidence)
        
        prompt = f"""

**YOUR TASK:**
You are a senior expert Interview designer and conductor from a top-tier tech company (like Google or Meta) with an experience of more than 15 years in taking interviews.
You have an expertise in the {seniority} {role} for {skill} domain and you are conducting a real interview.
You have full autonomy to conduct this interview however you think is best.

**INTERVIEW PLAN & CONTEXT:**
- Role: {role}
- Seniority: {seniority} 
- Skill Being Tested: {skill}
- Current Stage: {interview_stage}
- Top Evaluation Dimensions: {top_dimensions}
- Selected Archetype: {selected_archetype}
- Interview Objective: {interview_objective}
- Session Context: {json.dumps(session_context, indent=2)}

**CORE PHILOSOPHY (foundational guidance - use as philosophical direction, not rigid instruction):**
{core_philosophy if core_philosophy else "Focus on understanding the candidate's thinking process and practical problem-solving approach."}

**EXECUTION GUIDANCE (use as reference, adapt to current conversation):**
{interview_plan.get('during_interview_execution', 'No execution guidance available')}

**SIGNAL EVIDENCE COLLECTED SO FAR:**
{signal_summary}

**CONVERSATION HISTORY:**
{formatted_history}

**YOUR MISSION:**
You are a senior expert Interview Designer and conductor from a top-tier tech company (like Google or Meta) with an experience of more than 15 years in taking interviews.
You are conducting a real interview. Your job is to:
1. Analyze the candidate's latest response and overall performance
2. Review the signal evidence collected so far
3. Decide what to explore next based on their strengths and areas for improvement
4. Generate the next question or statement that will best assess the remaining evaluation dimensions
5. Track your interview strategy and adapt based on their performance
6. Ensure you're collecting evidence for ALL top evaluation dimensions

**INTERVIEW STAGES (Guide your progression):**
- **Problem Understanding**: Assess their ability to grasp the core problem
- **Solution Design**: Test their approach to solving the problem
- **Technical Depth**: Explore their technical knowledge and reasoning
- **Trade-offs & Constraints**: Evaluate their understanding of real-world considerations
- **Implementation**: Test their practical execution thinking
- **Adaptation**: Assess how they handle changes and challenges

**SIGNAL COLLECTION STRATEGY:**
- Focus on dimensions where you have LOW confidence or NO evidence
- Probe deeper into areas where they show potential but need more validation
- Challenge them on dimensions where they're performing well to confirm strength
- Balance coverage across all evaluation dimensions
- Use the {selected_archetype} archetype to guide your questioning style

**STRATEGIC INTERVIEW GUIDANCE:**
Let the candidate drive the conversation naturally, but use your signal map strategically to guide them when they get stuck or skim over key areas:

**Some examples of SIGNAL-BASED INTERVENTION STRATEGY:**

Note -- the below are just examples and you can use your judgement to guide the conversation.

- **If they jump straight to solutions**: Gently pull them back to test Problem Scoping
  - "That's an interesting idea! Before we dive into features, can you tell me a bit more about the specific user you're building this for?"
  - "I want to make sure I understand the problem space first. What specific pain points are you trying to solve?"
  
- **If they list endless features**: Force a test of Prioritization
  - "This is a great list of ten features! If we only had three months to launch, what are the absolute essential three we would build, and why?"
  - "How would you decide which features to build first? What's your prioritization framework?"
  
- **If they're struggling with complexity**: Provide gentle guidance and simpler questions
  - "Let's take a step back. Can you start with a simpler version of this problem?"
  - "What's the most basic version of this solution that would still be valuable?"
  
- **If they're excelling**: Challenge them with more complex scenarios and edge cases
  - "That's a great approach! Now let's add some complexity. What if we had to consider [edge case]?"
  - "How would your solution change if we had to scale this to [larger scope]?"

**KEY PRINCIPLES:**
- Always let the candidate lead first, but guide them as per the SIGNAL-BASED INTERVENTION STRATEGY when they're stuck or missing key areas
- Use your signal map to identify gaps in evaluation coverage
- Balance between letting them explore and ensuring comprehensive assessment
- Keep the conversation natural and engaging

**YOUR APPROACH:**
- Be friendly, professional, insightful, and encouraging
- Ask open-ended questions that probe for depth, not just surface answers
- Focus on understanding their "why" and "how", not just "what"
- Adapt your questions based on how well they're performing
- If they're struggling, provide gentle guidance and simpler questions
- If they're excelling, challenge them with more complex scenarios
- Always remember -- 
   - If the candidate asks clarification questions, provide a clear and concise answer and do not ask a question in that turn
   - If the candidate asks for some time to think, acknowledge their request and then wait for them to respond
- Keep the interview flowing naturally and engaging

**MAINTAIN FAANG-LEVEL RIGOR**: Ensure all follow-up questions maintain the same strategic depth and first-principles thinking
**SENIORITY CONSISTENCY**: Keep questions aligned with the {seniority} level scope established in the initial case study

**COMPLETION ASSESSMENT:**
Based on your signal evidence analysis, evaluate if this interview should continue or complete.

**CURRENT COVERAGE STATUS:**
{self._format_coverage_status(signal_evidence, top_dimensions)}

**COMPLETION CRITERIA FOR {seniority} {role} - {skill}:**
- HIGH confidence on at least 3 evaluation dimensions (4+ for Senior/Manager)
- MEDIUM+ confidence on all critical dimensions for this seniority level
- Sufficient evidence depth (specific examples, clear reasoning, frameworks)
- Minimum 6-8 substantial question exchanges (8-12 for Senior+)
- Current conversation length: {len(conversation_history)} exchanges

**COMPLETION DECISION FRAMEWORK:**
1. **Evidence Quality**: Review signal confidence levels across top dimensions
2. **Coverage Completeness**: Assess if all critical dimensions have adequate evidence
3. **Additional Value**: Consider if continuing would add significant new evidence
4. **Efficiency Balance**: Weigh thoroughness against interview length
5. **Seniority Standards**: Ensure depth meets {seniority} level expectations

**COVERAGE GAP ALERTS:**
- Identify any untested critical dimensions
- Flag dimensions with LOW confidence that need validation
- Consider interview length vs. remaining coverage needs
- Prioritize most critical gaps if efficiency limits approached

**OUTPUT FORMAT:**
Your response MUST be a single, valid JSON object with this exact structure:

{{
  "chain_of_thought": [
    "Your first reasoning step - analyze their response",
    "Your second reasoning step - assess signal evidence collected", 
    "Your third reasoning step - identify gaps in evaluation coverage",
    "Your fourth reasoning step - plan your next question strategy OR completion decision"
  ],
  "response_text": "The exact words you will say to the candidate. This should be your next question, clarification statement, or interview completion.",
  "interview_state": {{
    "current_stage": "The interview stage you're currently in or moving to",
    "skill_progress": "How well they're doing: 'beginner', 'intermediate', 'advanced', or 'expert'",
    "next_focus": "What specific aspect you plan to explore next",
    "evaluation_coverage": "Current coverage status: HIGH/MEDIUM/LOW confidence per dimension"
  }},
  "completion_assessment": {{
    "should_complete": true/false,
    "completion_confidence": "High/Medium/Low",
    "reason": "Specific reason for completion decision with evidence summary",
    "evidence_summary": "Coverage status across all dimensions with confidence levels",
    "remaining_gaps": ["List any critical gaps if not completing"],
    "coverage_percentage": "Estimated percentage of adequate coverage achieved"
  }}
}}

**EXECUTE YOUR INTERVIEW NOW:**"""
        
        return prompt
    
    def _format_signal_evidence(self, signal_evidence: Dict) -> str:
        """
        Format signal evidence for prompt readability.
        """
        if not signal_evidence:
            return "No signals collected yet."
        
        formatted = []
        for dimension, evidence in signal_evidence.items():
            formatted.append(f"**{dimension}:**")
            if evidence.get("positive_signals"):
                formatted.append(f"  ✅ Positive: {', '.join(evidence['positive_signals'])}")
            if evidence.get("areas_for_improvement"):
                formatted.append(f"  ⚠️ Areas: {', '.join(evidence['areas_for_improvement'])}")
            if evidence.get("confidence"):
                formatted.append(f"  🎯 Confidence: {evidence['confidence']}")
            if evidence.get("seniority_alignment"):
                formatted.append(f"  🎯 Seniority: {evidence['seniority_alignment']}")
            formatted.append("")
        
        return "\n".join(formatted)
    
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
    
    def _format_coverage_status(self, signal_evidence: Dict, top_dimensions: str) -> str:
        """
        Format current coverage status for completion assessment.
        """
        if not signal_evidence:
            return "No signal evidence collected yet. All dimensions need initial assessment."
        
        # Parse top dimensions (they come as a string like "Problem Scoping, User Empathy, Business Acumen")
        dimensions_list = [dim.strip() for dim in top_dimensions.split(',')]
        
        coverage_status = []
        high_confidence = []
        medium_confidence = []
        low_confidence = []
        untested = []
        
        for dimension in dimensions_list:
            # Check if this dimension has been tested
            dimension_found = False
            for evidence_key in signal_evidence.keys():
                # Flexible matching - check if dimension name is contained in evidence key
                if any(word in evidence_key.lower() for word in dimension.lower().split()):
                    dimension_found = True
                    confidence = signal_evidence[evidence_key].get("confidence", "Low")
                    
                    if confidence == "High":
                        high_confidence.append(dimension)
                    elif confidence == "Medium":
                        medium_confidence.append(dimension)
                    else:
                        low_confidence.append(dimension)
                    break
            
            if not dimension_found:
                untested.append(dimension)
        
        # Build coverage summary
        if high_confidence:
            coverage_status.append(f"HIGH CONFIDENCE: {', '.join(high_confidence)}")
        if medium_confidence:
            coverage_status.append(f"MEDIUM CONFIDENCE: {', '.join(medium_confidence)}")
        if low_confidence:
            coverage_status.append(f"LOW CONFIDENCE: {', '.join(low_confidence)}")
        if untested:
            coverage_status.append(f"UNTESTED: {', '.join(untested)}")
        
        if not coverage_status:
            return "No clear coverage mapping available. Focus on primary dimensions."
        
        # Add summary statistics
        total_dimensions = len(dimensions_list)
        tested_dimensions = total_dimensions - len(untested)
        adequate_dimensions = len(high_confidence) + len(medium_confidence)
        
        status_summary = f"\nCOVERAGE SUMMARY: {tested_dimensions}/{total_dimensions} dimensions tested, {adequate_dimensions}/{total_dimensions} with adequate evidence"
        
        return "\n".join(coverage_status) + status_summary
    
    def get_initial_question(self, role: str, seniority: str, skill: str, 
                           session_context: Dict[str, Any],
                           interview_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the initial interview question using the PreInterviewPlanner's generated prompt.
        """
        
        # Use the prompt from the interview plan instead of generating a new one
        if interview_plan and interview_plan.get("interview_prompt"):
            return {
                "chain_of_thought": [
                    "Using PreInterviewPlanner's generated prompt",
                    "Focusing on the selected archetype and evaluation dimensions",
                    "Ready to begin the interview"
                ],
                "response_text": interview_plan["interview_prompt"],
                "interview_state": {
                    "current_stage": "problem_understanding",
                    "skill_progress": "not_started",
                    "next_focus": "initial_problem_presentation"
                },
                "timestamp": time.time()
            }
        
        # If no plan provided, raise an error
        raise Exception(f"No interview plan provided for {seniority} {role} - {skill}. PreInterviewPlanner must generate a plan first.")



class SignalTracker:
    """
    Helper class for tracking signals against evaluation dimensions.
    """
    
    def __init__(self):
        self.collected_signals = {}
    
    def add_signal(self, dimension: str, signal_type: str, evidence: str, confidence: str):
        """
        Add a signal to the tracker.
        """
        if dimension not in self.collected_signals:
            self.collected_signals[dimension] = {
                "positive_signals": [],
                "areas_for_improvement": [],
                "quotes": [],
                "confidence": confidence
            }
        
        if signal_type == "positive":
            self.collected_signals[dimension]["positive_signals"].append(evidence)
        elif signal_type == "improvement":
            self.collected_signals[dimension]["areas_for_improvement"].append(evidence)
        
        self.collected_signals[dimension]["quotes"].append(evidence)
    
    def get_signals_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all collected signals.
        """
        return self.collected_signals.copy()
