#!/usr/bin/env python3
"""
Script to import interview playbook data from CSV file to Render database.
Handles JSON columns and data validation.
"""

import os
import sys
import csv
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

def validate_csv_structure(csv_file_path):
    """Validate that CSV has the required columns"""
    required_columns = [
        'role', 'skill', 'seniority', 'archetype', 'interview_objective',
        'evaluation_dimensions', 'seniority_criteria', 'good_vs_great_examples',
        'pre_interview_strategy', 'during_interview_execution', 'post_interview_evaluation'
    ]
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            csv_columns = reader.fieldnames
            
            missing_columns = set(required_columns) - set(csv_columns)
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False
            
            print(f"✅ CSV structure valid. Found columns: {csv_columns}")
            return True
            
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return False

def parse_json_field(value):
    """Parse JSON field from CSV, handling both JSON strings and plain text"""
    if not value or value.strip() == '':
        return None
    
    # If it's already a JSON string, try to parse it
    if value.strip().startswith('{') or value.strip().startswith('['):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # If JSON parsing fails, return as string
            return value
    
    # If it's plain text, return as string
    return value

def import_csv_to_database(csv_file_path):
    """Import CSV data to interview_playbooks table"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Validate CSV structure first
    if not validate_csv_structure(csv_file_path):
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Clear existing data (optional - comment out if you want to keep existing data)
                connection.execute(text("DELETE FROM interview_playbooks"))
                print("🗑️  Cleared existing playbook data")
                
                # Read and insert CSV data
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    inserted_count = 0
                    
                    for row in reader:
                        # Parse JSON fields
                        evaluation_dimensions = parse_json_field(row.get('evaluation_dimensions'))
                        seniority_criteria = parse_json_field(row.get('seniority_criteria'))
                        good_vs_great_examples = parse_json_field(row.get('good_vs_great_examples'))
                        
                        # Insert record
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
                            'role': row.get('role', '').strip(),
                            'skill': row.get('skill', '').strip(),
                            'seniority': row.get('seniority', '').strip(),
                            'archetype': row.get('archetype', '').strip(),
                            'interview_objective': row.get('interview_objective', '').strip(),
                            'evaluation_dimensions': json.dumps(evaluation_dimensions) if evaluation_dimensions else None,
                            'seniority_criteria': json.dumps(seniority_criteria) if seniority_criteria else None,
                            'good_vs_great_examples': json.dumps(good_vs_great_examples) if good_vs_great_examples else None,
                            'pre_interview_strategy': row.get('pre_interview_strategy', '').strip(),
                            'during_interview_execution': row.get('during_interview_execution', '').strip(),
                            'post_interview_evaluation': row.get('post_interview_evaluation', '').strip(),
                            'created_at': datetime.utcnow()
                        })
                        
                        inserted_count += 1
                        print(f"✅ Inserted: {row.get('role')} - {row.get('skill')} - {row.get('seniority')}")
                
                trans.commit()
                print(f"\n🎉 Successfully imported {inserted_count} playbook(s)!")
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
    """Verify that the data was imported correctly"""
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
            
            # Show sample records
            result = connection.execute(text("""
                SELECT role, skill, seniority, archetype,
                       CASE 
                           WHEN pre_interview_strategy IS NOT NULL THEN 'Yes' 
                           ELSE 'No' 
                       END as has_strategy,
                       CASE 
                           WHEN during_interview_execution IS NOT NULL THEN 'Yes' 
                           ELSE 'No' 
                       END as has_execution,
                       CASE 
                           WHEN post_interview_evaluation IS NOT NULL THEN 'Yes' 
                           ELSE 'No' 
                       END as has_evaluation
                FROM interview_playbooks 
                ORDER BY role, skill, seniority
                LIMIT 10
            """))
            
            print("\n📋 Sample records:")
            print("Role | Skill | Seniority | Archetype | Strategy | Execution | Evaluation")
            print("-" * 80)
            
            for row in result:
                print(f"{row.role} | {row.skill} | {row.seniority} | {row.archetype} | {row.has_strategy} | {row.has_execution} | {row.has_evaluation}")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def create_sample_csv():
    """Create a sample CSV file with the correct structure"""
    sample_data = [
        {
            'role': 'Product Manager',
            'skill': 'Product Sense',
            'seniority': 'Mid-level',
            'archetype': 'broad_design',
            'interview_objective': 'Assess candidate ability to design products from scratch',
            'evaluation_dimensions': '{"problem_scoping": {"signals": ["asks clarifying questions"]}}',
            'seniority_criteria': '{"mid_level": {"problem_scoping": "Should ask basic questions"}}',
            'good_vs_great_examples': '{"problem_scoping": {"good": "Asks basic questions", "great": "Asks detailed clarifying questions"}}',
            'pre_interview_strategy': 'Step 1: Select archetype based on role and seniority...',
            'during_interview_execution': 'Guide conversation to collect signals...',
            'post_interview_evaluation': 'Review evidence and rate against rubric...'
        }
    ]
    
    csv_file = 'sample_playbooks.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=sample_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"✅ Created sample CSV file: {csv_file}")
    print("📝 Edit this file with your actual data, then run the import script")

if __name__ == "__main__":
    print("🚀 Import interview playbooks from CSV to Render database")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Usage: python import_playbooks_from_csv.py <csv_file_path>")
        print("\nOr create a sample CSV file:")
        create_sample_csv()
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        sys.exit(1)
    
    print(f"📁 Importing from: {csv_file_path}")
    
    if import_csv_to_database(csv_file_path):
        print("\n🔍 Verifying import...")
        if verify_import():
            print("\n🎉 SUCCESS! Your playbook data is now in the database!")
            print("\nThe AI agents can now use:")
            print("✅ Pre-interview strategy guidance")
            print("✅ During-interview execution guidance") 
            print("✅ Post-interview evaluation guidance")
            print("✅ Good vs Great examples")
            print("\nNo more fallback errors - real guidance is available!")
        else:
            print("\n❌ Import verification failed")
    else:
        print("\n❌ Failed to import CSV data")
        sys.exit(1)
