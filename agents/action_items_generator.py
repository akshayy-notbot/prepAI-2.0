import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from utils import get_gemini_client

class SmartActionItemsGenerator:
    """
    Generates intelligent, evidence-based action items from evaluation data.
    Uses hybrid approach: LLM for complex interpretation + rule-based filtering/prioritization.
    """
    
    def __init__(self):
        self.llm = None  # Lazy initialization
        self._model = None
        
        # Priority weights for rule-based scoring
        self.priority_weights = {
            'rating': 0.3,      # 1-5 scale impact
            'confidence': 0.2,  # High/Medium/Low confidence
            'seniority': 0.3,   # Critical for target level
            'evidence': 0.2     # Strength of evidence
        }
    
    def _get_model(self):
        """Lazy initialization of Gemini model"""
        if self._model is None:
            self._model = get_gemini_client()
        return self._model
    
    def generate_action_items(self, evaluation_data: Dict[str, Any], 
                            interview_plan: Dict[str, Any], 
                            signal_evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main method to generate smart action items using hybrid approach.
        
        Args:
            evaluation_data: Complete evaluation result from InterviewEvaluator
            interview_plan: Original interview plan with seniority criteria
            signal_evidence: Signal evidence collected during interview
            
        Returns:
            List of structured action items with priorities and evidence
        """
        try:
            # Step 1: Rule-based filtering to identify critical dimensions
            critical_dimensions = self._identify_critical_dimensions(evaluation_data)
            
            if not critical_dimensions:
                return self._generate_default_action_items(evaluation_data, interview_plan)
            
            # Step 2: LLM generates smart action items for each critical dimension
            action_items = []
            for dimension_name, dimension_type in critical_dimensions:
                llm_actions = self._generate_llm_action_items(
                    dimension_name, 
                    evaluation_data.get('dimension_evaluations', {}).get(dimension_name, {}),
                    interview_plan, 
                    signal_evidence,
                    dimension_type
                )
                action_items.extend(llm_actions)
            
            # Step 3: Rule-based prioritization and deduplication
            prioritized_items = self._prioritize_and_deduplicate(action_items, evaluation_data, interview_plan)
            
            # Step 4: Limit to top 8 most important items
            return prioritized_items[:8]
            
        except Exception as e:
            print(f"❌ Error generating action items: {e}")
            return self._generate_fallback_action_items(evaluation_data, interview_plan)
    
    def _identify_critical_dimensions(self, evaluation_data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Rule-based filtering to identify dimensions needing action items.
        Returns list of (dimension_name, dimension_type) tuples.
        """
        critical = []
        dimensions = evaluation_data.get('dimension_evaluations', {})
        
        for dim_name, dim_data in dimensions.items():
            rating = dim_data.get('rating', 3)
            confidence = dim_data.get('confidence', 'Medium')
            
            # Rule-based criteria for critical dimensions
            if rating <= 2:  # Poor performance - critical gaps
                critical.append((dim_name, 'critical_gap'))
            elif rating == 3 and confidence in ['High', 'Medium']:  # Average performance - development opportunity
                critical.append((dim_name, 'development_opportunity'))
            elif rating >= 4 and confidence == 'High':  # Strong performance - leverage strength
                critical.append((dim_name, 'strength_leverage'))
        
        return critical
    
    def _generate_llm_action_items(self, dimension_name: str, dimension_data: Dict[str, Any], 
                                 interview_plan: Dict[str, Any], signal_evidence: Dict[str, Any],
                                 dimension_type: str) -> List[Dict[str, Any]]:
        """
        Use LLM to generate smart action items for a specific dimension.
        """
        try:
            # Format evidence for LLM
            evidence_text = self._format_evidence_for_llm(dimension_data, signal_evidence, dimension_name)
            
            # Get seniority and role context
            seniority = interview_plan.get('seniority', 'Unknown')
            role = interview_plan.get('role', 'Unknown')
            
            # Build LLM prompt
            prompt = self._build_action_items_prompt(
                dimension_name, dimension_data, interview_plan, 
                evidence_text, dimension_type, seniority, role
            )
            
            # Get LLM response
            model = self._get_model()
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            action_items = json.loads(response_text.strip())
            
            # Add metadata to each action item
            for item in action_items:
                item['dimension'] = dimension_name
                item['dimension_type'] = dimension_type
                item['priority_score'] = self._calculate_priority_score(item, dimension_data, interview_plan)
            
            return action_items
            
        except Exception as e:
            print(f"❌ Error generating LLM action items for {dimension_name}: {e}")
            return self._generate_rule_based_action_items(dimension_name, dimension_data, interview_plan, dimension_type)
    
    def _build_action_items_prompt(self, dimension_name: str, dimension_data: Dict[str, Any],
                                 interview_plan: Dict[str, Any], evidence_text: str,
                                 dimension_type: str, seniority: str, role: str) -> str:
        """Build comprehensive LLM prompt for action items generation."""
        
        seniority_criteria = interview_plan.get('seniority_criteria', {}).get(dimension_name, 'Not specified')
        good_vs_great = interview_plan.get('good_vs_great_examples', {}).get(dimension_name, 'Not specified')
        
        return f"""You are an expert career coach and technical mentor. Generate 2-3 specific, actionable development recommendations based on this interview performance data.

**DIMENSION**: {dimension_name}
**RATING**: {dimension_data.get('rating', 'N/A')}/5
**CONFIDENCE**: {dimension_data.get('confidence', 'N/A')}
**PERFORMANCE TYPE**: {dimension_type.replace('_', ' ').title()}
**SENIORITY LEVEL**: {seniority}
**ROLE**: {role}

**SPECIFIC EVIDENCE FROM INTERVIEW**:
{evidence_text}

**SENIORITY CRITERIA FOR THIS ROLE**:
{seniority_criteria}

**GOOD VS GREAT EXAMPLES**:
{good_vs_great}

**TASK**: Generate 2-3 specific, actionable recommendations that:
1. Address the specific gaps/opportunities identified in the evidence
2. Are appropriate for {seniority} level expectations
3. Include specific resources, frameworks, or practice areas
4. Reference the actual evidence from the interview
5. Provide clear, measurable outcomes

**OUTPUT FORMAT**: Return ONLY a JSON array with this structure:
[
    {{
        "title": "Specific, actionable title (max 60 chars)",
        "description": "Detailed description with specific steps and context",
        "priority": "Critical/High/Medium/Low",
        "category": "Technical Skills/Communication/Leadership/Problem Solving/Domain Knowledge",
        "evidence": ["exact quote 1", "exact quote 2"],
        "expectedOutcome": "What improvement this will achieve",
        "timeframe": "1-2 weeks/1 month/2-3 months",
        "resources": ["specific resource 1", "specific resource 2"],
        "seniorityContext": "Why this matters for {seniority} level",
        "goodVsGreat": "How this moves from good to great performance"
    }}
]

Focus on being specific, evidence-based, and actionable. Use the actual interview evidence to make recommendations."""
    
    def _format_evidence_for_llm(self, dimension_data: Dict[str, Any], 
                                signal_evidence: Dict[str, Any], dimension_name: str) -> str:
        """Format evidence from dimension data and signal evidence for LLM consumption."""
        evidence_parts = []
        
        # Add dimension-specific evidence
        if dimension_data.get('evidence'):
            evidence_parts.append("**Interview Evidence:**")
            for quote in dimension_data['evidence']:
                evidence_parts.append(f"- \"{quote}\"")
        
        # Add signal evidence for this dimension
        if signal_evidence.get(dimension_name):
            signal_data = signal_evidence[dimension_name]
            if signal_data.get('positive_signals'):
                evidence_parts.append("\n**Positive Signals:**")
                for signal in signal_data['positive_signals']:
                    evidence_parts.append(f"- {signal}")
            
            if signal_data.get('areas_for_improvement'):
                evidence_parts.append("\n**Areas for Improvement:**")
                for area in signal_data['areas_for_improvement']:
                    evidence_parts.append(f"- {area}")
            
            if signal_data.get('quotes'):
                evidence_parts.append("\n**Key Quotes:**")
                for quote in signal_data['quotes']:
                    evidence_parts.append(f"- \"{quote}\"")
        
        # Add assessment details
        if dimension_data.get('assessment'):
            evidence_parts.append(f"\n**Assessment:** {dimension_data['assessment']}")
        
        if dimension_data.get('seniority_alignment'):
            evidence_parts.append(f"\n**Seniority Alignment:** {dimension_data['seniority_alignment']}")
        
        return "\n".join(evidence_parts) if evidence_parts else "No specific evidence available."
    
    def _calculate_priority_score(self, action_item: Dict[str, Any], 
                                dimension_data: Dict[str, Any], 
                                interview_plan: Dict[str, Any]) -> int:
        """Calculate priority score using rule-based logic."""
        base_score = 0
        
        # Rating impact (1-5 scale)
        rating = dimension_data.get('rating', 3)
        if rating <= 2:
            base_score += 40  # Critical gaps
        elif rating == 3:
            base_score += 20  # Development opportunities
        else:
            base_score += 10  # Strengths
        
        # Confidence impact
        confidence = dimension_data.get('confidence', 'Medium')
        if confidence == 'High':
            base_score += 20
        elif confidence == 'Medium':
            base_score += 10
        
        # Priority from action item
        priority = action_item.get('priority', 'Medium')
        if priority == 'Critical':
            base_score += 30
        elif priority == 'High':
            base_score += 20
        elif priority == 'Medium':
            base_score += 10
        
        # Evidence strength
        evidence_count = len(action_item.get('evidence', []))
        base_score += min(evidence_count * 5, 20)  # Cap at 20 points
        
        return min(base_score, 100)  # Cap at 100
    
    def _prioritize_and_deduplicate(self, action_items: List[Dict[str, Any]], 
                                  evaluation_data: Dict[str, Any], 
                                  interview_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize and deduplicate action items."""
        # Sort by priority score (highest first)
        sorted_items = sorted(action_items, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # Simple deduplication based on title similarity
        unique_items = []
        seen_titles = set()
        
        for item in sorted_items:
            title = item.get('title', '').lower()
            if title not in seen_titles:
                unique_items.append(item)
                seen_titles.add(title)
        
        return unique_items
    
    def _generate_rule_based_action_items(self, dimension_name: str, dimension_data: Dict[str, Any],
                                        interview_plan: Dict[str, Any], dimension_type: str) -> List[Dict[str, Any]]:
        """Fallback rule-based action item generation when LLM fails."""
        rating = dimension_data.get('rating', 3)
        seniority = interview_plan.get('seniority', 'Unknown')
        
        if dimension_type == 'critical_gap':
            return [{
                'title': f'Improve {dimension_name.replace("_", " ").title()}',
                'description': f'Focus on developing core skills in {dimension_name.replace("_", " ").lower()} as this is a critical gap for {seniority} level.',
                'priority': 'Critical',
                'category': 'Technical Skills',
                'evidence': dimension_data.get('evidence', [])[:2],
                'expectedOutcome': f'Better performance in {dimension_name.replace("_", " ").lower()}',
                'timeframe': '2-3 months',
                'resources': ['Practice with similar problems', 'Study relevant frameworks'],
                'seniorityContext': f'Critical for {seniority} level expectations',
                'goodVsGreat': 'Move from basic understanding to advanced application',
                'dimension': dimension_name,
                'dimension_type': dimension_type,
                'priority_score': 80
            }]
        else:
            return []
    
    def _generate_default_action_items(self, evaluation_data: Dict[str, Any], 
                                     interview_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate default action items when no critical dimensions identified."""
        return [{
            'title': 'Continue Skill Development',
            'description': 'Continue practicing and developing your interview skills across all dimensions.',
            'priority': 'Medium',
            'category': 'General Development',
            'evidence': [],
            'expectedOutcome': 'Overall skill improvement',
            'timeframe': 'Ongoing',
            'resources': ['Regular practice sessions', 'Mock interviews'],
            'seniorityContext': 'General development for any level',
            'goodVsGreat': 'Consistent practice leads to mastery',
            'dimension': 'general',
            'dimension_type': 'general',
            'priority_score': 30
        }]
    
    def _generate_fallback_action_items(self, evaluation_data: Dict[str, Any], 
                                      interview_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback action items when system fails."""
        return [{
            'title': 'Review Interview Performance',
            'description': 'Review your interview performance and identify areas for improvement.',
            'priority': 'Medium',
            'category': 'General Development',
            'evidence': [],
            'expectedOutcome': 'Better understanding of performance',
            'timeframe': '1 week',
            'resources': ['Self-reflection', 'Practice sessions'],
            'seniorityContext': 'Important for continuous improvement',
            'goodVsGreat': 'Regular reflection leads to better performance',
            'dimension': 'general',
            'dimension_type': 'general',
            'priority_score': 20
        }]
