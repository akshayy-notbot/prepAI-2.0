#!/usr/bin/env python3
"""
Safe import script for interview playbooks using Python instead of direct SQL.
This avoids encoding issues by using Python's database connection.
"""

import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def import_playbook_safely():
    """Import playbook data using Python to avoid encoding issues"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Clear existing data (optional)
                connection.execute(text("DELETE FROM interview_playbooks"))
                print("🗑️  Cleared existing playbook data")
                
                # Define the playbook data as Python dictionaries (no encoding issues)
                playbook_data = {
                    'role': 'Product Manager',
                    'seniority': 'Junior',
                    'skill': 'Product Sense',
                    'core_philosophy': 'First and foremost, understand that there is no single correct answer to a Product Sense question. The prompt be it Design a new product for remote workers or How would you improve Spotify is a vessel. What we are truly interested in is your thought process. We want to see how you navigate ambiguity, structure a complex problem, and apply your product intuition. The interview is a simulation of a real-life product discussion. Can you take a vague idea, explore its potential, and articulate a compelling product vision? That is the essence of what we are testing.',
                    
                    'evaluation_dimensions': {
                        "problem_scoping": {
                            "description": "Ability to take an ambiguous prompt and methodically break it down",
                            "signals": ["clarifying_questions", "scope_narrowing", "constraint_identification", "framework_laying"],
                            "probes": [
                                "What are the goals and constraints?",
                                "Who is the target user?",
                                "Can you lay out a clear framework for your answer?"
                            ],
                            "integration_style": "conversational",
                            "context_triggers": [
                                "when_candidate_jumps_to_solutions",
                                "when_scope_is_too_broad",
                                "when_constraints_are_unclear"
                            ]
                        },
                        "user_empathy": {
                            "description": "Genuine user-first thinking and customer centricity",
                            "signals": ["user_segmentation", "pain_point_identification", "user_journey_storytelling", "beyond_surface_assumptions"],
                            "probes": [
                                "Who are the specific user segments?",
                                "What are their pain points?",
                                "Can you tell a compelling story about their needs?"
                            ],
                            "integration_style": "conversational",
                            "context_triggers": [
                                "when_candidate_jumps_to_solutions",
                                "when_user_assumptions_are_generic",
                                "when_empathy_is_surface_level"
                            ]
                        },
                        "creativity_vision": {
                            "description": "Innovative thinking and product vision",
                            "signals": ["solution_variety", "innovative_approaches", "long_term_vision", "spark_of_innovation"],
                            "probes": [
                                "What other approaches could we consider?",
                                "How would you make this truly unique?",
                                "What is your long-term vision for this product?"
                            ],
                            "integration_style": "conversational",
                            "context_triggers": [
                                "when_solutions_are_obvious",
                                "when_vision_is_unclear",
                                "when_creativity_is_needed"
                            ]
                        },
                        "business_acumen": {
                            "description": "Understanding that great products need business viability",
                            "signals": ["business_goal_connection", "strategic_alignment", "market_understanding", "revenue_model_awareness"],
                            "probes": [
                                "How does this connect to business goals?",
                                "What is the market opportunity?",
                                "How would this generate value?"
                            ],
                            "integration_style": "conversational",
                            "context_triggers": [
                                "when_product_ideas_lack_business_context",
                                "when_strategic_thinking_is_needed",
                                "when_market_considerations_are_missing"
                            ]
                        }
                    },
                    
                    'seniority_criteria': {
                        "junior": {
                            "description": "Focus on raw potential and basic competencies",
                            "problem_scoping": "Should ask basic clarifying questions and show structured thinking",
                            "user_empathy": "Strong user empathy and creativity expected",
                            "creativity_vision": "Ability to brainstorm interesting solutions",
                            "business_acumen": "Less developed business acumen is acceptable"
                        },
                        "mid": {
                            "description": "More well-rounded performance expected",
                            "problem_scoping": "Should connect product ideas to business goals",
                            "user_empathy": "Solid grasp of prioritization and metrics",
                            "creativity_vision": "Evidence of owning a feature from start to finish",
                            "business_acumen": "Connect product ideas to business goals"
                        },
                        "senior": {
                            "description": "Strategic thinking becomes paramount",
                            "problem_scoping": "Zoom out and consider broader market implications",
                            "user_empathy": "Cross-functional leadership and complex stakeholder management",
                            "creativity_vision": "Long-term strategic vision and roadmap thinking",
                            "business_acumen": "Deep business acumen and strategic alignment"
                        }
                    },
                    
                    'archetype': 'broad_design',
                    'interview_objective': 'Assess candidate ability to design products from scratch and demonstrate core Product Sense competencies',
                    
                    'good_vs_great_examples': {
                        "problem_scoping": {
                            "good": "Starts by identifying the user and buyer, lists common pain points, brainstorms basic features",
                            "great": "Frames the problem more broadly, segments users further, tells compelling user journey stories"
                        },
                        "user_empathy": {
                            "good": "Identifies obvious user needs and basic pain points",
                            "great": "Discovers non-obvious pain points and creates detailed user personas with specific needs"
                        },
                        "creativity_vision": {
                            "good": "Brainstorms a few practical features and defines basic success metrics",
                            "great": "Creates innovative solutions with gamification elements and long-term vision for product evolution"
                        },
                        "business_acumen": {
                            "good": "Defines success as basic user satisfaction metrics",
                            "great": "Connects to broader business goals, considers market opportunity, and articulates strategic value"
                        }
                    },
                    
                    'pre_interview_strategy': 'Pre-Interview Strategy: Step 1: Select the most relevant Archetype for the Role X Skill X Seniority. For a standard mid-level PM interview, choose a Broad Design question. It gives the candidate the most room to run and demonstrate all the core competencies. Step 2: Start with choosing the best prompt to reveal the signals needed for the Role X Skill X Seniority based on Archetypes. Step 3: Map the prompt to evaluation dimensions and prepare follow-up questions.',
                    
                    'during_interview_execution': 'During-Interview Execution: Guide the conversation to collect signals for each evaluation dimension. Ask follow-up questions based on the candidate responses. Look for evidence of structured thinking, user empathy, creativity, and business acumen. Take notes on specific examples and quotes that demonstrate competency levels.',
                    
                    'post_interview_evaluation': 'Post-Interview Evaluation: Review the evidence collected against each evaluation dimension. Rate the candidate on a 1-5 scale for each competency. Consider the seniority level expectations when making final assessments. Provide specific feedback with examples from the interview.'
                }
                
                # Insert using parameterized query (avoids encoding issues)
                insert_sql = text("""
                    INSERT INTO interview_playbooks (
                        role, seniority, skill, core_philosophy, evaluation_dimensions,
                        seniority_criteria, archetype, interview_objective, good_vs_great_examples,
                        pre_interview_strategy, during_interview_execution, post_interview_evaluation,
                        created_at
                    ) VALUES (
                        :role, :seniority, :skill, :core_philosophy, :evaluation_dimensions,
                        :seniority_criteria, :archetype, :interview_objective, :good_vs_great_examples,
                        :pre_interview_strategy, :during_interview_execution, :post_interview_evaluation,
                        CURRENT_TIMESTAMP
                    )
                """)
                
                # Convert Python dicts to JSON strings for database
                playbook_data['evaluation_dimensions'] = json.dumps(playbook_data['evaluation_dimensions'])
                playbook_data['seniority_criteria'] = json.dumps(playbook_data['seniority_criteria'])
                playbook_data['good_vs_great_examples'] = json.dumps(playbook_data['good_vs_great_examples'])
                
                connection.execute(insert_sql, playbook_data)
                
                trans.commit()
                print("✅ Playbook imported successfully using Python!")
                return True
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_import():
    """Verify the import was successful"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return False
        
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # Count records
            result = connection.execute(text("SELECT COUNT(*) FROM interview_playbooks"))
            count = result.scalar()
            print(f"📊 Total playbooks in database: {count}")
            
            # Show sample record
            result = connection.execute(text("""
                SELECT role, skill, seniority, archetype,
                       CASE 
                           WHEN evaluation_dimensions IS NOT NULL THEN 'Yes' 
                           ELSE 'No' 
                       END as has_evaluation_dimensions
                FROM interview_playbooks 
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Sample record: {row.role} - {row.skill} - {row.seniority} - {row.archetype}")
                print(f"✅ Has evaluation_dimensions: {row.has_evaluation_dimensions}")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Safe Playbook Import Script (Python-based)")
    print("=" * 50)
    
    if import_playbook_safely():
        print("\n🔍 Verifying import...")
        if verify_import():
            print("\n🎉 SUCCESS! Playbook imported without encoding issues!")
        else:
            print("\n❌ Import verification failed")
    else:
        print("\n❌ Failed to import playbook")
