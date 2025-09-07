#!/usr/bin/env python3
"""
Import script that PRESERVES all original content from the CSV/SQL file.
This script will extract the actual text content and import it as-is, only converting
the JSON fields to proper structure while keeping all original text intact.
"""

import os
import json
import re
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def parse_sql_file_preserve_content():
    """Parse the original SQL file and extract all playbook data PRESERVING original content"""
    
    playbooks = []
    
    try:
        with open('clean_playbooks_insert.sql', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all INSERT statements
        insert_pattern = r'INSERT INTO interview_playbooks\s*\([^)]+\)\s*VALUES\s*\((.*?)\);'
        matches = re.findall(insert_pattern, content, re.DOTALL)
        
        print(f"📊 Found {len(matches)} INSERT statements in SQL file")
        
        for i, values_content in enumerate(matches):
            try:
                # Parse the values using a more robust approach
                values = parse_values_robust(values_content)
                
                if len(values) >= 11:  # Ensure we have all required fields
                    playbook = {
                        'role': clean_value(values[0]),
                        'seniority': clean_value(values[1]), 
                        'skill': clean_value(values[2]),
                        'core_philosophy': clean_value(values[3]),
                        'evaluation_dimensions': clean_value(values[4]),  # Keep original text
                        'seniority_criteria': clean_value(values[5]),     # Keep original text
                        'archetype': clean_value(values[6]),
                        'interview_objective': clean_value(values[7]),
                        'good_vs_great_examples': clean_value(values[8]), # Keep original text
                        'pre_interview_strategy': clean_value(values[9]),
                        'during_interview_execution': clean_value(values[10]),
                        'post_interview_evaluation': clean_value(values[11]) if len(values) > 11 else ""
                    }
                    playbooks.append(playbook)
                    print(f"✅ Parsed record {i+1}: {playbook['role']} - {playbook['skill']} - {playbook['seniority']}")
                    
                    # Show sample of during_interview_execution for validation
                    if playbook['role'] == 'Product Manger' and playbook['seniority'] == 'Mid' and playbook['skill'] == 'Execution':
                        print(f"🔍 SAMPLE during_interview_execution (first 200 chars):")
                        print(f"   {playbook['during_interview_execution'][:200]}...")
                        
                else:
                    print(f"⚠️  Record {i+1} has insufficient fields ({len(values)}/11)")
                    
            except Exception as e:
                print(f"❌ Error parsing record {i+1}: {e}")
                continue
        
        print(f"📊 Successfully parsed {len(playbooks)} playbooks")
        return playbooks
        
    except Exception as e:
        print(f"❌ Error reading SQL file: {e}")
        return []

def parse_values_robust(values_content):
    """Robustly parse SQL VALUES content handling quotes and commas"""
    values = []
    current_value = ""
    in_quotes = False
    quote_char = None
    paren_count = 0
    i = 0
    
    while i < len(values_content):
        char = values_content[i]
        
        # Handle quote characters
        if char in ["'", '"']:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                # Check if it's an escaped quote
                if i + 1 < len(values_content) and values_content[i + 1] == char:
                    current_value += char
                    i += 1  # Skip the next quote
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
            current_value = ""
        else:
            current_value += char
        
        i += 1
    
    # Add the last value
    if current_value.strip():
        values.append(current_value.strip())
    
    return values

def clean_value(value):
    """Clean a SQL value by removing quotes and handling escaped quotes"""
    value = value.strip()
    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
        # Handle escaped quotes
        value = value.replace("''", "'")
    return value

def convert_text_to_structured_json(text_content, field_type, role, skill, seniority):
    """Convert plain text to structured JSON while preserving the original content"""
    
    if field_type == "evaluation_dimensions":
        # For now, wrap the original text in a structured format
        # This preserves all the original content while making it JSON-compatible
        return {
            "original_content": text_content,
            "structured_dimensions": {
                "note": "Original evaluation dimensions content preserved above",
                "content_type": "text",
                "role": role,
                "skill": skill,
                "seniority": seniority
            }
        }
    
    elif field_type == "seniority_criteria":
        # Preserve original content in structured format
        return {
            "original_content": text_content,
            "structured_criteria": {
                "note": "Original seniority criteria content preserved above",
                "content_type": "text",
                "role": role,
                "skill": skill,
                "seniority": seniority
            }
        }
    
    elif field_type == "good_vs_great_examples":
        # Preserve original content in structured format
        return {
            "original_content": text_content,
            "structured_examples": {
                "note": "Original good vs great examples content preserved above",
                "content_type": "text",
                "role": role,
                "skill": skill,
                "seniority": seniority
            }
        }
    
    return {}

def import_all_playbooks_preserve_content():
    """Import all playbook data preserving original content"""
    
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
                
                # Parse the original SQL file
                playbooks = parse_sql_file_preserve_content()
                
                if not playbooks:
                    print("❌ No playbooks found to import")
                    return False
                
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
                
                inserted_count = 0
                for playbook in playbooks:
                    # Convert only the JSON fields to structured format while preserving original content
                    playbook['evaluation_dimensions'] = json.dumps(
                        convert_text_to_structured_json(playbook['evaluation_dimensions'], "evaluation_dimensions", 
                                                       playbook['role'], playbook['skill'], playbook['seniority'])
                    )
                    playbook['seniority_criteria'] = json.dumps(
                        convert_text_to_structured_json(playbook['seniority_criteria'], "seniority_criteria", 
                                                       playbook['role'], playbook['skill'], playbook['seniority'])
                    )
                    playbook['good_vs_great_examples'] = json.dumps(
                        convert_text_to_structured_json(playbook['good_vs_great_examples'], "good_vs_great_examples", 
                                                       playbook['role'], playbook['skill'], playbook['seniority'])
                    )
                    
                    connection.execute(insert_sql, playbook)
                    inserted_count += 1
                    print(f"✅ Inserted: {playbook['role']} - {playbook['skill']} - {playbook['seniority']}")
                
                trans.commit()
                print(f"\n🎉 Successfully imported {inserted_count} playbook(s) with ORIGINAL CONTENT PRESERVED!")
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
    """Verify the import was successful and show sample content"""
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
            
            # Show sample of the Product Manager, Mid, Execution record
            result = connection.execute(text("""
                SELECT role, skill, seniority, during_interview_execution
                FROM interview_playbooks 
                WHERE role = 'Product Manger' AND seniority = 'Mid' AND skill = 'Execution'
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row:
                print(f"\n🔍 SAMPLE VERIFICATION - Product Manager, Mid, Execution:")
                print(f"   Role: {row.role}")
                print(f"   Skill: {row.skill}")
                print(f"   Seniority: {row.seniority}")
                print(f"   During Interview Execution (first 300 chars):")
                print(f"   {row.during_interview_execution[:300]}...")
            
            # Show all records
            result = connection.execute(text("""
                SELECT role, skill, seniority, archetype
                FROM interview_playbooks 
                ORDER BY role, skill, seniority
            """))
            
            print("\n📋 All playbooks:")
            for row in result:
                print(f"  • {row.role} - {row.skill} - {row.seniority} - {row.archetype}")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ORIGINAL CONTENT PRESERVATION Import Script")
    print("=" * 60)
    print("⚠️  This script preserves ALL original content from your CSV/SQL file")
    print("⚠️  Only converts JSON fields to proper structure while keeping original text")
    print("=" * 60)
    
    if import_all_playbooks_preserve_content():
        print("\n🔍 Verifying import...")
        if verify_import():
            print("\n🎉 SUCCESS! All original content preserved and imported!")
        else:
            print("\n❌ Import verification failed")
    else:
        print("\n❌ Failed to import playbooks")
