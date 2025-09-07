#!/usr/bin/env python3
"""
Script to convert the user's CSV to the correct format for our system.
Handles column name mapping and data cleaning.
"""

import csv
import re
import json
import os

def clean_html_tags(text):
    """Remove HTML tags from text"""
    if not text:
        return text
    # Remove <br> tags and replace with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def clean_seniority_level(seniority):
    """Clean and standardize seniority levels"""
    if not seniority:
        return seniority
    
    # Remove HTML tags and parenthetical text
    seniority = clean_html_tags(seniority)
    seniority = re.sub(r'\([^)]*\)', '', seniority).strip()
    
    # Map to our 4-level system
    seniority_mapping = {
        'junior': 'Junior',
        'mid': 'Mid', 
        'senior': 'Senior',
        'manager': 'Manager',
        'lead': 'Manager',
        'principal': 'Manager'
    }
    
    seniority_lower = seniority.lower()
    for key, value in seniority_mapping.items():
        if key in seniority_lower:
            return value
    
    return seniority

def parse_json_field(text):
    """Parse text that should be JSON, handling both JSON and plain text"""
    if not text:
        return None
    
    # Clean HTML tags first
    text = clean_html_tags(text)
    
    # If it looks like JSON, try to parse it
    if text.strip().startswith('{') or text.strip().startswith('['):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    
    # Return as string
    return text

def convert_csv():
    """Convert the user's CSV to system format"""
    
    input_file = '/Users/akyadav/Downloads/PrepAI Interview Playbook - Sheet1.csv'
    output_file = 'converted_playbooks.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Define column mapping
            column_mapping = {
                'Role': 'role',
                'Seniority Level': 'seniority', 
                'Skills ': 'skill',
                'Archetypes Types': 'archetype',
                'Objective of the interview': 'interview_objective',
                'Evaluation Dimensions': 'evaluation_dimensions',
                'seniority_criteria': 'seniority_criteria',
                'Good vs Great examples': 'good_vs_great_examples',
                'Pre-interview Strategy': 'pre_interview_strategy',
                'During the interview ': 'during_interview_execution',
                'Post Interview Evaluation': 'post_interview_evaluation'
            }
            
            # Prepare output data
            output_data = []
            
            for row_num, row in enumerate(reader, 1):
                print(f"🔄 Processing row {row_num}...")
                
                # Create new row with mapped columns
                new_row = {}
                
                for old_col, new_col in column_mapping.items():
                    value = row.get(old_col, '').strip()
                    
                    if new_col == 'seniority':
                        value = clean_seniority_level(value)
                    elif new_col in ['evaluation_dimensions', 'seniority_criteria', 'good_vs_great_examples']:
                        value = parse_json_field(value)
                    else:
                        value = clean_html_tags(value)
                    
                    new_row[new_col] = value
                
                # Add missing columns with default values
                if 'archetype' not in new_row or not new_row['archetype']:
                    new_row['archetype'] = 'broad_design'  # Default archetype
                
                output_data.append(new_row)
            
            # Write converted CSV
            if output_data:
                fieldnames = [
                    'role', 'skill', 'seniority', 'archetype', 'interview_objective',
                    'evaluation_dimensions', 'seniority_criteria', 'good_vs_great_examples',
                    'pre_interview_strategy', 'during_interview_execution', 'post_interview_evaluation'
                ]
                
                with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for row in output_data:
                        # Convert JSON fields to strings for CSV
                        csv_row = {}
                        for key, value in row.items():
                            if isinstance(value, (dict, list)):
                                csv_row[key] = json.dumps(value)
                            else:
                                csv_row[key] = value
                        writer.writerow(csv_row)
                
                print(f"✅ Converted {len(output_data)} rows to {output_file}")
                return True
            else:
                print("❌ No data to convert")
                return False
                
    except Exception as e:
        print(f"❌ Error converting CSV: {e}")
        return False

def validate_converted_csv():
    """Validate the converted CSV"""
    output_file = 'converted_playbooks.csv'
    
    if not os.path.exists(output_file):
        print(f"❌ Converted file not found: {output_file}")
        return False
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            print(f"\n📋 Converted CSV Headers:")
            for i, header in enumerate(headers, 1):
                print(f"  {i}. \"{header}\"")
            
            # Check required columns
            required_columns = [
                'role', 'skill', 'seniority', 'archetype', 'interview_objective',
                'evaluation_dimensions', 'seniority_criteria', 'good_vs_great_examples',
                'pre_interview_strategy', 'during_interview_execution', 'post_interview_evaluation'
            ]
            
            missing_columns = set(required_columns) - set(headers)
            if missing_columns:
                print(f"\n❌ Missing columns: {missing_columns}")
                return False
            
            print(f"\n✅ All required columns present!")
            
            # Check sample data
            print(f"\n📋 Sample converted data:")
            for i, row in enumerate(reader):
                if i >= 2:
                    break
                print(f"\nRow {i+1}:")
                print(f"  Role: {row.get('role', 'N/A')}")
                print(f"  Skill: {row.get('skill', 'N/A')}")
                print(f"  Seniority: {row.get('seniority', 'N/A')}")
                print(f"  Archetype: {row.get('archetype', 'N/A')}")
                print(f"  Has Strategy: {'Yes' if row.get('pre_interview_strategy') else 'No'}")
                print(f"  Has Execution: {'Yes' if row.get('during_interview_execution') else 'No'}")
                print(f"  Has Evaluation: {'Yes' if row.get('post_interview_evaluation') else 'No'}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error validating converted CSV: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Converting CSV to system format...")
    print("=" * 50)
    
    if convert_csv():
        print("\n🔍 Validating converted CSV...")
        if validate_converted_csv():
            print("\n🎉 SUCCESS! CSV converted and validated!")
            print("\nNext steps:")
            print("1. Review the converted file: converted_playbooks.csv")
            print("2. Run: python import_playbooks_from_csv.py converted_playbooks.csv")
            print("3. Your playbook data will be imported to the database!")
        else:
            print("\n❌ CSV validation failed")
    else:
        print("\n❌ CSV conversion failed")
