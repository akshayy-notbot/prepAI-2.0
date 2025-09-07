#!/usr/bin/env python3
"""
Script to check current seniority levels in the interview_playbooks table.
Shows what needs to be cleaned up.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def check_seniority_levels():
    """Check current seniority levels in the database"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            print("🔍 Current seniority levels in interview_playbooks table:")
            print("=" * 60)
            
            # Get all distinct seniority levels with counts
            result = connection.execute(text("""
                SELECT DISTINCT seniority, COUNT(*) as count 
                FROM interview_playbooks 
                GROUP BY seniority 
                ORDER BY seniority
            """))
            
            total_records = 0
            for row in result:
                print(f"📋 '{row.seniority}' - {row.count} records")
                total_records += row.count
            
            print(f"\n📊 Total records: {total_records}")
            
            # Check for HTML tags
            print("\n🔍 Checking for HTML formatting...")
            html_result = connection.execute(text("""
                SELECT DISTINCT seniority 
                FROM interview_playbooks 
                WHERE seniority ~ '<[^>]+>'
            """))
            
            html_levels = [row.seniority for row in html_result]
            if html_levels:
                print("❌ Found HTML tags in these seniority levels:")
                for level in html_levels:
                    print(f"  - '{level}'")
            else:
                print("✅ No HTML tags found")
            
            # Check for parenthetical text
            print("\n🔍 Checking for parenthetical text...")
            paren_result = connection.execute(text("""
                SELECT DISTINCT seniority 
                FROM interview_playbooks 
                WHERE seniority ~ '\\([^)]*\\)'
            """))
            
            paren_levels = [row.seniority for row in paren_result]
            if paren_levels:
                print("❌ Found parenthetical text in these seniority levels:")
                for level in paren_levels:
                    print(f"  - '{level}'")
            else:
                print("✅ No parenthetical text found")
            
            # Show expected vs actual
            print("\n🎯 Expected seniority levels:")
            expected_levels = ["Junior", "Mid", "Senior", "Manager"]
            for level in expected_levels:
                print(f"  - '{level}'")
            
            # Check which expected levels are missing
            actual_result = connection.execute(text("""
                SELECT DISTINCT seniority 
                FROM interview_playbooks
            """))
            
            actual_levels = [row.seniority for row in actual_result]
            missing_levels = set(expected_levels) - set(actual_levels)
            unexpected_levels = set(actual_levels) - set(expected_levels)
            
            if missing_levels:
                print(f"\n⚠️  Missing expected levels: {missing_levels}")
            
            if unexpected_levels:
                print(f"\n⚠️  Unexpected levels found: {unexpected_levels}")
            
            # Show sample records
            print("\n📋 Sample records:")
            sample_result = connection.execute(text("""
                SELECT role, skill, seniority, archetype
                FROM interview_playbooks 
                ORDER BY role, skill, seniority
                LIMIT 5
            """))
            
            print("Role | Skill | Seniority | Archetype")
            print("-" * 60)
            
            for row in sample_result:
                print(f"{row.role} | {row.skill} | {row.seniority} | {row.archetype}")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking seniority levels in interview_playbooks table")
    print("=" * 60)
    
    if check_seniority_levels():
        print("\n✅ Check completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python clean_seniority_levels.py' to clean up the data")
        print("2. Verify the cleanup was successful")
        print("3. Your system will then work with clean, standardized seniority levels")
    else:
        print("\n❌ Failed to check seniority levels")
        sys.exit(1)
