#!/usr/bin/env python3
"""
Final corrected import script that stores JSON fields as proper JSON objects.
This ensures AI agents can access the data as expected: playbook.evaluation_dimensions, etc.
"""

import os
import re
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def parse_values_robust(values_content):
    """Robustly parse VALUES content handling quotes, commas, and nested structures"""
    values = []
    current_value = ''
    in_quotes = False
    quote_char = None
    paren_count = 0
    i = 0
    
    while i < len(values_content):
        char = values_content[i]
        
        if char in ["'", '"']:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                # Handle escaped quotes
                if i + 1 < len(values_content) and values_content[i + 1] == char:
                    current_value += char
                    i += 1
                else:
                    in_quotes = False
                    quote_char = None
            else:
                current_value += char
        elif char == '(' and not in_quotes:
            paren_count += 1
            current_value += char
        elif char == ')' and not in_quotes:
            paren_count -= 1
            current_value += char
        elif char == ',' and not in_quotes and paren_count == 0:
            values.append(current_value.strip())
            current_value = ''
        else:
            current_value += char
        
        i += 1
    
    if current_value.strip():
        values.append(current_value.strip())
    
    return values

def clean_value(value):
    """Clean and unescape SQL value"""
    value = value.strip()
    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
        # Handle escaped quotes
        value = value.replace("''", "'")
    return value

def create_json_structure(content, field_name, role, skill, seniority):
    """Create a proper JSON structure for the content"""
    return {
        "content": content,
        "metadata": {
            "field_name": field_name,
            "role": role,
            "skill": skill,
            "seniority": seniority,
            "content_type": "text",
            "note": "Original content preserved from CSV import"
        }
    }

def main():
    """Main import function"""
    print("🚀 Starting final corrected playbook import...")
    
    # Database connection
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        engine = create_engine(database_url)
        
        # Read and parse the SQL file
        with open('clean_playbooks_insert.sql', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all INSERT statements
        insert_pattern = r'INSERT INTO interview_playbooks\s*\([^)]+\)\s*VALUES\s*\((.*?)\);'
        matches = re.findall(insert_pattern, content, re.DOTALL)
        
        print(f"📊 Found {len(matches)} records to import")
        
        # Clear existing data
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM interview_playbooks"))
            connection.commit()
            print("🗑️ Cleared existing playbook data")
        
        # Process each record
        imported_count = 0
        
        for i, values_content in enumerate(matches):
            try:
                values = parse_values_robust(values_content)
                
                if len(values) >= 12:
                    # Extract all fields
                    role = clean_value(values[0])
                    seniority = clean_value(values[1])
                    skill = clean_value(values[2])
                    core_philosophy = clean_value(values[3])
                    evaluation_dimensions = clean_value(values[4])
                    seniority_criteria = clean_value(values[5])
                    archetype = clean_value(values[6])
                    interview_objective = clean_value(values[7])
                    good_vs_great_examples = clean_value(values[8])
                    pre_interview_strategy = clean_value(values[9])
                    during_interview_execution = clean_value(values[10])
                    post_interview_evaluation = clean_value(values[11])
                    
                    # Create proper JSON structures for JSON fields
                    evaluation_dimensions_json = create_json_structure(
                        evaluation_dimensions, "evaluation_dimensions", role, skill, seniority
                    )
                    seniority_criteria_json = create_json_structure(
                        seniority_criteria, "seniority_criteria", role, skill, seniority
                    )
                    good_vs_great_examples_json = create_json_structure(
                        good_vs_great_examples, "good_vs_great_examples", role, skill, seniority
                    )
                    
                    # Insert into database
                    with engine.connect() as connection:
                        insert_sql = text("""
                            INSERT INTO interview_playbooks 
                            (role, seniority, skill, core_philosophy, evaluation_dimensions, 
                             seniority_criteria, archetype, interview_objective, good_vs_great_examples,
                             pre_interview_strategy, during_interview_execution, post_interview_evaluation)
                            VALUES 
                            (:role, :seniority, :skill, :core_philosophy, :evaluation_dimensions,
                             :seniority_criteria, :archetype, :interview_objective, :good_vs_great_examples,
                             :pre_interview_strategy, :during_interview_execution, :post_interview_evaluation)
                        """)
                        
                        connection.execute(insert_sql, {
                            'role': role,
                            'seniority': seniority,
                            'skill': skill,
                            'core_philosophy': core_philosophy,
                            'evaluation_dimensions': json.dumps(evaluation_dimensions_json),
                            'seniority_criteria': json.dumps(seniority_criteria_json),
                            'archetype': archetype,
                            'interview_objective': interview_objective,
                            'good_vs_great_examples': json.dumps(good_vs_great_examples_json),
                            'pre_interview_strategy': pre_interview_strategy,
                            'during_interview_execution': during_interview_execution,
                            'post_interview_evaluation': post_interview_evaluation
                        })
                        connection.commit()
                        
                        imported_count += 1
                        print(f"✅ Imported: {role} - {skill} - {seniority}")
                
            except Exception as e:
                print(f"❌ Error importing record {i+1}: {e}")
                continue
        
        # Verify import
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM interview_playbooks"))
            total_count = result.scalar()
            
            # Get a sample record
            sample_result = connection.execute(text("""
                SELECT role, skill, seniority, archetype, 
                       evaluation_dimensions, seniority_criteria, good_vs_great_examples
                FROM interview_playbooks LIMIT 1
            """))
            sample = sample_result.fetchone()
            
            print(f"\n🔍 Verifying import...")
            print(f"📊 Total playbooks in database: {total_count}")
            
            if sample:
                print(f"✅ Sample record: {sample[0]} - {sample[1]} - {sample[2]} - {sample[3]}")
                print(f"✅ Has evaluation_dimensions: {'Yes' if sample[4] else 'No'}")
                print(f"✅ Has seniority_criteria: {'Yes' if sample[5] else 'No'}")
                print(f"✅ Has good_vs_great_examples: {'Yes' if sample[6] else 'No'}")
                
                # Show the actual content structure
                print(f"\n📋 Sample evaluation_dimensions structure:")
                if sample[4]:
                    try:
                        eval_data = json.loads(sample[4])
                        print(f"Type: {type(eval_data)}")
                        print(f"Content preview: {eval_data['content'][:200]}...")
                        print(f"Metadata: {eval_data['metadata']}")
                    except:
                        print(f"Raw content: {sample[4][:200]}...")
        
        print(f"\n🎉 Import completed successfully! {imported_count} records imported.")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    main()
