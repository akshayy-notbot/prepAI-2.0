#!/usr/bin/env python3
"""
Script to populate the interview_playbooks table with sample data.
This includes the Product Sense example you provided earlier.
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def populate_playbooks():
    """Populate the interview_playbooks table with sample data"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Sample playbook data based on your Product Sense example
    sample_playbooks = [
        {
            "role": "Product Manager",
            "skill": "Product Sense",
            "seniority": "Mid-level",
            "archetype": "broad_design",
            "interview_objective": "Assess candidate's ability to design products from scratch, demonstrate user empathy, and think strategically about business impact",
            "evaluation_dimensions": {
                "problem_scoping": {
                    "signals": [
                        "Asks clarifying questions about business goals",
                        "Narrows scope appropriately",
                        "Identifies key constraints and assumptions"
                    ],
                    "probes": [
                        "What's the business goal here?",
                        "Who is the target user?",
                        "What are the key constraints?"
                    ]
                },
                "user_empathy": {
                    "signals": [
                        "Defines clear user persona",
                        "Identifies deep, non-obvious pain points",
                        "Considers user context and emotions"
                    ],
                    "probes": [
                        "Tell me about your target user",
                        "What are their biggest frustrations?",
                        "How does this fit into their daily life?"
                    ]
                },
                "creativity_vision": {
                    "signals": [
                        "Brainstorms range of solutions",
                        "Has compelling product vision",
                        "Thinks beyond obvious features"
                    ],
                    "probes": [
                        "What are some different approaches?",
                        "What's your vision for this product?",
                        "How is this different from existing solutions?"
                    ]
                },
                "business_acumen": {
                    "signals": [
                        "Connects product to business goals",
                        "Thinks about monetization",
                        "Considers competitive landscape"
                    ],
                    "probes": [
                        "How does this create business value?",
                        "How would you monetize this?",
                        "What's your competitive advantage?"
                    ]
                },
                "prioritization": {
                    "signals": [
                        "Ruthlessly prioritizes for MVP",
                        "Articulates reasoning behind priorities",
                        "Makes clear trade-off decisions"
                    ],
                    "probes": [
                        "What's your MVP?",
                        "Why these features first?",
                        "What would you cut and why?"
                    ]
                }
            },
            "seniority_criteria": {
                "mid_level": {
                    "problem_scoping": "Should ask basic clarifying questions and narrow scope",
                    "user_empathy": "Should identify clear user persona and main pain points",
                    "creativity_vision": "Should propose reasonable solutions with some innovation",
                    "business_acumen": "Should understand basic business value and monetization",
                    "prioritization": "Should prioritize features for MVP with clear reasoning"
                }
            },
            "good_vs_great_examples": {
                "problem_scoping": {
                    "good": "Asks 'What's the business goal?' and 'Who is the target user?'",
                    "great": "Asks 'What's the business goal? Is this a standalone app or part of a larger ecosystem?' and 'Are we focusing on solo travelers, families, or business tourists? What's their budget?'"
                },
                "user_empathy": {
                    "good": "Defines user as 'travelers' and identifies 'finding places to see' as main pain point",
                    "great": "Creates detailed persona 'Sarah, a 30-year-old solo traveler from Europe' and identifies non-obvious pain points like 'safety concerns, navigating local transport, dealing with language barriers, finding authentic food that won't make them sick'"
                },
                "creativity_vision": {
                    "good": "Proposes obvious solutions like 'maps and guides'",
                    "great": "Brainstorms both obvious (maps, guides) and innovative solutions (AR navigation, real-time translation help, 'safe-routes' feature) with compelling vision 'This isn't just a travel guide; it's a personal concierge that makes an intimidating city feel accessible and safe'"
                },
                "business_acumen": {
                    "good": "Mentions 'this could make money'",
                    "great": "Connects to company goals 'If we're Google, this could integrate with Google Maps and Flights to create a seamless travel ecosystem' and thinks about monetization 'We could offer premium guided tours or take a commission from partner restaurants'"
                },
                "prioritization": {
                    "good": "Lists 10 features and says 'we need all of them'",
                    "great": "Ruthlessly prioritizes 'For the first version, we absolutely must nail navigation, safety features, and a curated list of experiences. The social features can wait' and articulates the 'why' behind priorities"
                }
            },
            "pre_interview_strategy": """Step 1: Select the most relevant Archetype for the Role X Skill X Seniority. 
Eg. Broad Design ("0 to 1"): "Design X for Y." (e.g., "Design a new product for caregivers.") This is great for testing creativity and problem scoping from a blank slate. 
Improvement ("1 to N"): "How would you improve X?" (e.g., "How would you improve Google Maps?") This tests user empathy and prioritization within existing constraints. 
Strategic: "Should company X enter market Y?" (e.g., "Should Apple get into the home security business?") This is better for senior roles and heavily weighs business acumen. 
For a standard mid-level PM interview, I'll choose a Broad Design question. It gives the candidate the most room to run and demonstrate all the core competencies. But this differ based on Role X Skill X Seniority

Step 2: Start with choosing the best prompt to reveal the signals needed for the Role X Skill X Seniority based on Archetypes

Step 3: Map the prompt to the Evaluation Dimensions and list the specific signals she be listening for. This is their hidden checklist. 
Eg. Problem Scoping: Signal: Do they ask clarifying questions? "What's the business goal? Is this a standalone app or part of a larger ecosystem?" Signal: Do they narrow the scope? "Are we focusing on solo travelers, families, or business tourists? What's their budget?"
✅ User Empathy: Signal: Do they define a clear user persona? "Let's imagine Sarah, a 30-year-old solo traveler from Europe on a two-week trip." Signal: Do they identify deep, non-obvious pain points beyond just "finding places to see"? (e.g., safety concerns, navigating local transport, dealing with language barriers, finding authentic food that won't make them sick). 
✅ Creativity & Vision: Signal: Do they brainstorm a range of solutions? Both obvious (maps, guides) and innovative (AR navigation, real-time translation help, a 'safe-routes' feature). Signal: Do they have a compelling product vision? "This isn't just a travel guide; it's a 'personal concierge' that makes an intimidating city feel accessible and safe."
✅ Business Acumen: Signal: Do they connect the product to a company goal? "If we're Google, this could integrate with Google Maps and Flights to create a seamless travel ecosystem." Signal: Do they think about monetization? "We could offer premium guided tours or take a commission from partner restaurants."
✅ Prioritization & Trade-offs: Signal: Do they ruthlessly prioritize for an MVP? "For the first version, we absolutely must nail navigation, safety features, and a curated list of experiences. The social features can wait." Signal: Do they articulate the "why" behind their priorities?""",
            "during_interview_execution": """In-Interview Execution (45 minutes) My role is to be a collaborative guide, gently probing to ensure I get the signals I need. 
The Kick-off (5 mins) I introduce myself and the goal: "This is a collaborative product design session. There's no right answer. I'm most interested in how you think, so please think out loud. Let's design a new mobile application for first-time international tourists visiting Chennai."

The Guided Conversation (35 mins) I let the candidate drive, but I use my signal map to guide them if they get stuck or skim over a key area. 
If they jump straight to solutions... I'll gently pull them back to test Problem Scoping: "That's an interesting idea. Before we dive into features, can you tell me a bit more about the specific user you're building this for?"
If their user pain points are generic... I'll probe for deeper User Empathy: "A lot of apps show points of interest. What are some of the unique anxieties or problems a tourist faces specifically in Chennai that we could solve?"
If they list endless features... I'll force a test of Prioritization: "This is a great list of ten features. If we only had three months to launch, what are the absolute essential three we would build, and why?"
Once they have a core idea... I'll pivot to test Business Acumen: "This sounds like a great user-centric product. How might this product create value for our business?"
I'm taking notes directly against my signal map, collecting evidence (quotes, ideas, frameworks they use).

The Wrap-up (5 mins) I'll ask them to summarize their final product pitch. "So, in 30 seconds, what is the MVP of your product and why is it compelling?" This tests their ability to synthesize and communicate their vision.""",
            "post_interview_evaluation": """Post-Interview Evaluation (15 minutes) Immediately after the interview, I synthesize my notes. 
Review the Evidence: I go through my signal map and review the evidence I collected for each dimension. 
Rate Against the Rubric: I'll give a rating (e.g., "Exceeds Expectations," "Meets," "Below") for each dimension, with specific examples from the conversation to back it up. 
Example note: "User Empathy: Strong. Candidate created a detailed persona of a solo female traveler and focused on the non-obvious pain point of personal safety, proposing a 'safe-route' feature. This shows deep empathy."
Example note: "Prioritization: Met expectations. They correctly identified the MVP but I had to prompt them to force the trade-off decision." """
        }
    ]
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Clear existing data (optional - remove if you want to keep existing data)
                connection.execute(text("DELETE FROM interview_playbooks"))
                print("🗑️  Cleared existing playbook data")
                
                # Insert sample data
                for playbook in sample_playbooks:
                    insert_sql = text("""
                        INSERT INTO interview_playbooks (
                            role, skill, seniority, archetype, interview_objective,
                            evaluation_dimensions, seniority_criteria, good_vs_great_examples,
                            pre_interview_strategy, during_interview_execution, post_interview_evaluation,
                            created_at
                        ) VALUES (
                            :role, :skill, :seniority, :archetype, :interview_objective,
                            :evaluation_dimensions, :seniority_criteria, :good_vs_great_examples,
                            :pre_interview_strategy, :during_interview_execution, :post_interview_evaluation,
                            :created_at
                        )
                    """)
                    
                    connection.execute(insert_sql, {
                        'role': playbook['role'],
                        'skill': playbook['skill'],
                        'seniority': playbook['seniority'],
                        'archetype': playbook['archetype'],
                        'interview_objective': playbook['interview_objective'],
                        'evaluation_dimensions': json.dumps(playbook['evaluation_dimensions']),
                        'seniority_criteria': json.dumps(playbook['seniority_criteria']),
                        'good_vs_great_examples': json.dumps(playbook['good_vs_great_examples']),
                        'pre_interview_strategy': playbook['pre_interview_strategy'],
                        'during_interview_execution': playbook['during_interview_execution'],
                        'post_interview_evaluation': playbook['post_interview_evaluation'],
                        'created_at': datetime.utcnow()
                    })
                
                trans.commit()
                print(f"✅ Inserted {len(sample_playbooks)} playbook(s) successfully!")
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

def verify_data():
    """Verify that the data was inserted correctly"""
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
                       LENGTH(pre_interview_strategy) as strategy_length,
                       LENGTH(during_interview_execution) as execution_length,
                       LENGTH(post_interview_evaluation) as evaluation_length
                FROM interview_playbooks 
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row:
                print(f"📋 Sample record: {row.role} - {row.skill} - {row.seniority}")
                print(f"   Strategy length: {row.strategy_length} chars")
                print(f"   Execution length: {row.execution_length} chars") 
                print(f"   Evaluation length: {row.evaluation_length} chars")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Populating interview_playbooks table with sample data...")
    print("=" * 60)
    
    if populate_playbooks():
        print("\n🔍 Verifying data insertion...")
        if verify_data():
            print("\n🎉 SUCCESS! Sample playbook data is ready!")
            print("\nThe AI agents can now use:")
            print("✅ Pre-interview strategy guidance")
            print("✅ During-interview execution guidance") 
            print("✅ Post-interview evaluation guidance")
            print("✅ Good vs Great examples")
            print("\nNo more fallback errors - real guidance is available!")
        else:
            print("\n❌ Data verification failed")
    else:
        print("\n❌ Failed to populate playbook data")
        sys.exit(1)
