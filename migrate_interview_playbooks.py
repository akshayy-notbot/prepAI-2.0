#!/usr/bin/env python3
"""
Migration script to add interview playbook tables to existing database.
Run this after updating models.py to create the new tables.
"""

import os
import sys
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️  dotenv not available, using system environment variables")

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models import create_tables, get_engine, Base
    from sqlalchemy import inspect
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Failed to import models: {e}")
    sys.exit(1)

def migrate_interview_playbooks():
    """
    Create the new interview playbook tables.
    """
    try:
        print("🔄 Starting interview playbook migration...")
        
        # Create all tables (this will add the new ones)
        if create_tables():
            print("✅ Interview playbook tables created successfully")
            
            # Verify tables were created
            engine = get_engine()
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
            expected_tables = ["interview_playbooks", "interview_sessions"]
            for table in expected_tables:
                if table in table_names:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    
            return True
        else:
            print("❌ Failed to create interview playbook tables")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def seed_sample_playbooks():
    """
    Seed the database with sample interview playbooks for testing.
    """
    try:
        print("🌱 Seeding sample interview playbooks...")
        
        from models import get_session_local, InterviewPlaybook
        
        session_local = get_session_local()
        db = session_local()
        
        # Sample playbook for Product Manager - Product Design
        pm_product_design = InterviewPlaybook(
            role="Product Manager",
            skill="Product Design",
            seniority="Mid",
            archetype="broad_design",
            interview_objective="Test creativity, problem scoping, and user empathy",
            evaluation_dimensions={
                "problem_scoping": {
                    "description": "Ability to understand and frame problems",
                    "signals": ["clarifying_questions", "scope_narrowing", "constraint_identification"],
                    "probes": [
                        "What's the business goal?",
                        "Can you narrow the scope?",
                        "What constraints should we consider?"
                    ],
                    "integration_style": "conversational",
                    "context_triggers": [
                        "when_candidate_jumps_to_solutions",
                        "when_scope_is_too_broad",
                        "when_constraints_are_unclear"
                    ]
                },
                "user_empathy": {
                    "description": "Understanding user needs and pain points",
                    "signals": ["persona_definition", "pain_point_identification", "user_journey_mapping"],
                    "probes": [
                        "Who is your target user?",
                        "What are their biggest challenges?",
                        "How does this fit into their daily life?"
                    ],
                    "integration_style": "conversational",
                    "context_triggers": [
                        "when_candidate_jumps_to_solutions",
                        "when_user_pain_points_are_generic",
                        "when_persona_is_vague"
                    ]
                },
                "creativity_vision": {
                    "description": "Innovative thinking and product vision",
                    "signals": ["solution_variety", "innovative_approaches", "compelling_vision"],
                    "probes": [
                        "What other approaches could we consider?",
                        "How would you make this truly unique?",
                        "What's your vision for this product?"
                    ],
                    "integration_style": "conversational",
                    "context_triggers": [
                        "when_solutions_are_obvious",
                        "when_vision_is_unclear",
                        "when_creativity_is_needed"
                    ]
                },
                "prioritization_tradeoffs": {
                    "description": "Making decisions and trade-offs",
                    "signals": ["mvp_focus", "priority_justification", "trade_off_awareness"],
                    "probes": [
                        "What would you build first?",
                        "How do you prioritize these features?",
                        "What would you sacrifice and why?"
                    ],
                    "integration_style": "conversational",
                    "context_triggers": [
                        "when_feature_list_is_long",
                        "when_priorities_are_unclear",
                        "when_trade_offs_are_needed"
                    ]
                }
            },
            seniority_criteria={
                "junior": "Basic understanding and application",
                "mid": "Structured approach with some depth",
                "senior": "Strategic thinking and comprehensive analysis",
                "staff+": "Innovative approaches and thought leadership"
            },
            good_vs_great_examples={
                "problem_scoping": {
                    "good": "Asks basic clarifying questions",
                    "great": "Systematically breaks down problem into components"
                },
                "user_empathy": {
                    "good": "Identifies obvious user needs",
                    "great": "Discovers non-obvious pain points and user journeys"
                }
            }
        )
        
        # Sample playbook for Software Engineer - System Design
        swe_system_design = InterviewPlaybook(
            role="Software Engineer",
            skill="System Design",
            seniority="Senior",
            archetype="improvement",
            interview_objective="Test technical depth, scalability thinking, and trade-off analysis",
            evaluation_dimensions={
                "problem_scoping": {
                    "description": "Ability to understand and frame technical problems",
                    "signals": ["technical_requirements", "scale_understanding", "constraint_analysis"],
                    "probes": [
                        "What's the expected scale?",
                        "What are the performance requirements?",
                        "What are the technical constraints?"
                    ],
                    "integration_style": "conversational",
                    "context_triggers": [
                        "when_candidate_jumps_to_solutions",
                        "when_scale_is_unclear",
                        "when_constraints_are_missing"
                    ]
                },
                "technical_depth": {
                    "description": "Deep understanding of technical concepts",
                    "signals": ["concept_explanation", "implementation_details", "best_practices"],
                    "probes": [
                        "How would you implement this component?",
                        "What are the trade-offs of this approach?",
                        "How would you handle edge cases?"
                    ],
                    "integration_style": "conversational",
                    "context_triggers": [
                        "when_solution_is_superficial",
                        "when_implementation_details_are_missing",
                        "when_trade_offs_are_unclear"
                    ]
                },
                "scalability_thinking": {
                    "description": "Understanding of scalable system design",
                    "signals": ["scaling_strategies", "bottleneck_identification", "performance_optimization"],
                    "probes": [
                        "How would this system scale to 1M users?",
                        "What are the potential bottlenecks?",
                        "How would you optimize performance?"
                    ],
                    "integration_style": "conversational",
                    "context_triggers": [
                        "when_scale_is_not_considered",
                        "when_bottlenecks_are_ignored",
                        "when_performance_is_overlooked"
                    ]
                }
            },
            seniority_criteria={
                "junior": "Basic system understanding",
                "mid": "Component-level design",
                "senior": "System-level architecture",
                "staff+": "Cross-system architecture"
            },
            good_vs_great_examples={
                "technical_depth": {
                    "good": "Explains basic concepts",
                    "great": "Discusses implementation trade-offs and alternatives"
                },
                "scalability_thinking": {
                    "good": "Identifies obvious scaling issues",
                    "great": "Proposes sophisticated scaling strategies"
                }
            }
        )
        
        # Add playbooks to database
        db.add(pm_product_design)
        db.add(swe_system_design)
        db.commit()
        
        print("✅ Sample playbooks seeded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to seed sample playbooks: {e}")
        if db:
            db.rollback()
        return False
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    print("🚀 Interview Playbook Migration Script")
    print("=" * 50)
    
    # Run migration
    if migrate_interview_playbooks():
        print("\n✅ Migration completed successfully!")
        
        # Ask if user wants to seed sample data
        try:
            seed_choice = input("\n🌱 Would you like to seed sample playbooks? (y/n): ").lower().strip()
            if seed_choice in ['y', 'yes']:
                if seed_sample_playbooks():
                    print("✅ Sample data seeded successfully!")
                else:
                    print("❌ Failed to seed sample data")
            else:
                print("⏭️ Skipping sample data seeding")
        except KeyboardInterrupt:
            print("\n⏭️ Skipping sample data seeding")
        
        print("\n🎉 Migration script completed!")
        
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
