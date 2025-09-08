import os
import json
import time
from typing import List, Dict, Any, Optional
from utils import get_gemini_client

class InterviewEvaluator:
    """
    Post-interview evaluator that reviews the complete interview transcript,
    signal evidence, and provides comprehensive evaluation against dimensions.
    """
    
    def __init__(self):
        self.llm = None  # Lazy initialization
        self._model = None
    
    def _get_model(self):
        """Lazy initialization of Gemini model"""
        if self._model is None:
            self._model = get_gemini_client()
        return self._model
    
    def evaluate_interview(self, 
                          role: str,
                          seniority: str,
                          skill: str,
                          conversation_history: List[Dict[str, Any]],
                          signal_evidence: Dict[str, Any],
                          interview_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive evaluation of the interview performance.
        
        Args:
            role: The role being interviewed for
            seniority: The seniority level
            skill: The primary skill being tested
            conversation_history: Complete interview transcript
            signal_evidence: Collected signals throughout the interview
            interview_plan: Original interview plan with evaluation dimensions
            
        Returns:
            Dict containing comprehensive evaluation results
        """
        
        start_time = time.time()
        
        try:
            # Extract comprehensive data from the interview plan
            top_dimensions = interview_plan.get("top_evaluation_dimensions", "")
            selected_archetype = interview_plan.get("selected_archetype", "")
            interview_objective = interview_plan.get("interview_objective", "")
            seniority_criteria = interview_plan.get("seniority_criteria", {})
            good_vs_great_examples = interview_plan.get("good_vs_great_examples", {})
            core_philosophy = interview_plan.get("core_philosophy", "")
            
            # Format conversation history for analysis
            formatted_history = self._format_conversation_history(conversation_history)
            
            # Create comprehensive evaluation prompt with playbook context
            prompt = self._build_evaluation_prompt(
                role, seniority, skill, top_dimensions, selected_archetype,
                interview_objective, formatted_history, signal_evidence,
                seniority_criteria, good_vs_great_examples, core_philosophy
            )
            
            # Get LLM evaluation
            model = self._get_model()
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            
            # Add metadata
            result["evaluation_metadata"] = {
                "role": role,
                "seniority": seniority,
                "skill": skill,
                "archetype": selected_archetype,
                "evaluation_timestamp": time.time(),
                "processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Evaluation failed: {str(e)}",
                "evaluation_metadata": {
                    "role": role,
                    "seniority": seniority,
                    "skill": skill,
                    "evaluation_timestamp": time.time(),
                    "processing_time_ms": 0
                }
            }
    
    def _build_evaluation_prompt(self, role: str, seniority: str, skill: str,
                                top_dimensions: str, selected_archetype: str,
                                interview_objective: str, conversation_history: str,
                                signal_evidence: Dict, seniority_criteria: Dict,
                                good_vs_great_examples: Dict, core_philosophy: str) -> str:
        """
        Build comprehensive evaluation prompt.
        """
        
        # Format signal evidence for analysis
        signal_summary = self._format_signal_evidence_for_evaluation(signal_evidence)
        
        prompt = f"""You are a senior expert Interview evaluator from a top-tier tech company (like Google or Meta) with an experience of more than 15 years in evaluating candidates.

**INTERVIEW CONTEXT:**
- Role: {role}
- Seniority: {seniority}
- Skill Being Tested: {skill}
- Selected Archetype: {selected_archetype}
- Interview Objective: {interview_objective}
- Top Evaluation Dimensions: {top_dimensions}

**CORE PHILOSOPHY (evaluation guidance - use as philosophical direction, not rigid criteria):**
{core_philosophy if core_philosophy else "Focus on understanding the candidate's thinking process and practical problem-solving approach."}

**COMPLETE INTERVIEW TRANSCRIPT:**
{conversation_history}

**SIGNAL EVIDENCE COLLECTED:**
{signal_summary}

**YOUR TASK:**
Conduct a comprehensive evaluation of this candidate's performance against the specified evaluation dimensions.

**EVALUATION REQUIREMENTS:**

1. **DIMENSION-BY-DIMENSION ASSESSMENT:**
   - Evaluate each evaluation dimension separately
   - Provide specific examples from the transcript
   - Rate performance on a 1-5 scale (1=Poor, 2=Below Average, 3=Average, 4=Above Average, 5=Excellent)
   - Include confidence level for each rating

2. **EVIDENCE-BASED SCORING:**
   - Use specific quotes and examples from the transcript
   - Reference the signal evidence collected
   - Provide concrete behavioral observations
   - Avoid generic statements

3. **SENIORITY ALIGNMENT:**
   - Assess if performance meets {seniority} level expectations
   - Identify areas of strength and growth
   - Consider career trajectory implications
   - Use the specific seniority criteria below for this role × skill × seniority

4. **GOOD VS GREAT ASSESSMENT:**
   - Evaluate if answers are "good" (competent, covers basics) or "great" (insightful, innovative, considers edge cases)
   - Use the specific good vs great examples below for this role × skill × seniority
   - Identify what would elevate "good" answers to "great" answers

5. **OVERALL ASSESSMENT:**
   - Provide a comprehensive summary
   - Recommend next steps (hire, no hire, consider for different role)
   - Identify key strengths and development areas

**SENIORITY CRITERIA FOR THIS ROLE × SKILL × SENIORITY:**
{json.dumps(seniority_criteria, indent=2)}

**GOOD VS GREAT EXAMPLES FOR THIS ROLE × SKILL × SENIORITY:**
{json.dumps(good_vs_great_examples, indent=2)}

**OUTPUT FORMAT:**
Return ONLY a JSON object with this exact structure:

{{
  "dimension_evaluations": {{
    "dimension_name": {{
      "rating": 1-5,
      "confidence": "High/Medium/Low",
      "strengths": ["specific strength 1", "specific strength 2"],
      "areas_for_improvement": ["specific area 1", "specific area 2"],
      "evidence": ["exact quote 1", "exact quote 2"],
      "assessment": "Detailed analysis of performance",
      "seniority_alignment": "How well this aligns with {seniority} expectations",
      "good_vs_great": "Good/Great/Approaching Great",
      "good_vs_great_analysis": "What would elevate this from good to great"
    }}
I 
  "overall_assessment": {{
    "overall_score": "Average of all dimension ratings",
    "performance_summary": "Comprehensive summary of candidate performance",
    "key_strengths": ["top 3 strengths"],
    "development_areas": ["top 3 areas for growth"],
    "executive_summary": "High-level executive summary of candidate performance and potential",
    "growth_trajectory": "Analysis of career growth trajectory and potential",
    "career_development": "Specific career development recommendations",
    "next_steps": "Specific recommendations for candidate development"
  }},
  "interview_quality": {{
    "archetype_effectiveness": "How well the {selected_archetype} archetype worked",
    "evidence_coverage": "How well we covered all evaluation dimensions",
    "interview_flow": "Assessment of interview progression and flow"
  }}
}}

**CONDUCT YOUR EVALUATION NOW:**"""
        
        return prompt
    
    def _format_conversation_history(self, conversation_history: List[Dict]) -> str:
        """
        Format conversation history for evaluation analysis.
        """
        if not conversation_history:
            return "No conversation history available."
        
        formatted = []
        for i, turn in enumerate(conversation_history):
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            timestamp = turn.get("timestamp", "")
            
            # Add timestamp if available
            time_str = f" [{timestamp}]" if timestamp else ""
            formatted.append(f"Turn {i+1} - {role.title()}{time_str}: {content}")
        
        return "\n".join(formatted)
    
    def _format_signal_evidence_for_evaluation(self, signal_evidence: Dict) -> str:
        """
        Format signal evidence for evaluation analysis.
        """
        if not signal_evidence:
            return "No signal evidence collected."
        
        formatted = []
        for dimension, evidence in signal_evidence.items():
            formatted.append(f"**{dimension}:**")
            
            if evidence.get("positive_signals"):
                formatted.append(f"  ✅ Positive Signals:")
                for signal in evidence["positive_signals"]:
                    formatted.append(f"    - {signal}")
            
            if evidence.get("areas_for_improvement"):
                formatted.append(f"  ⚠️ Areas for Improvement:")
                for area in evidence["areas_for_improvement"]:
                    formatted.append(f"    - {area}")
            
            if evidence.get("quotes"):
                formatted.append(f"  💬 Key Quotes:")
                for quote in evidence["quotes"]:
                    formatted.append(f'    - "{quote}"')
            
            if evidence.get("confidence"):
                formatted.append(f"  🎯 Confidence: {evidence['confidence']}")
            if evidence.get("seniority_alignment"):
                formatted.append(f"  🎯 Seniority: {evidence['seniority_alignment']}")
            if evidence.get("good_vs_great"):
                formatted.append(f"  🌟 Level: {evidence['good_vs_great']}")
            
            formatted.append("")
        
        return "\n".join(formatted)
    
    def generate_evaluation_summary(self, evaluation_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of evaluation results.
        """
        try:
            overall = evaluation_results.get("overall_assessment", {})
            dimensions = evaluation_results.get("dimension_evaluations", {})
            
            # Define newline character outside f-string to avoid syntax error
            newline = '\n'
            
            summary = f"""
# Interview Evaluation Summary

## Overall Assessment
**Score**: {overall.get('overall_score', 'N/A')}/5
**Executive Summary**: {overall.get('executive_summary', 'N/A')}
**Summary**: {overall.get('performance_summary', 'N/A')}

## Key Strengths
{newline.join([f"- {strength}" for strength in overall.get('key_strengths', [])])}

## Development Areas
{newline.join([f"- {area}" for area in overall.get('development_areas', [])])}

## Dimension-by-Dimension Breakdown
"""
            
            for dim_name, dim_eval in dimensions.items():
                summary += f"""
### {dim_name.replace('_', ' ').title()}
**Rating**: {dim_eval.get('rating', 'N/A')}/5
**Confidence**: {dim_eval.get('confidence', 'N/A')}
**Assessment**: {dim_eval.get('assessment', 'N/A')}
**Seniority Alignment**: {dim_eval.get('seniority_alignment', 'N/A')}
**Performance Level**: {dim_eval.get('good_vs_great', 'N/A')}

**Strengths:**
{newline.join([f"- {s}" for s in dim_eval.get('strengths', [])])}

**Areas for Improvement:**
{newline.join([f"- {a}" for a in dim_eval.get('areas_for_improvement', [])])}

**Evidence:**
{newline.join([f'- "{e}"' for e in dim_eval.get('evidence', [])])}

**Good vs Great Analysis**: {dim_eval.get('good_vs_great_analysis', 'N/A')}
"""
            
            return summary.strip()
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
