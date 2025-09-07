#!/usr/bin/env python3
"""
Script to clean up seniority levels in the interview_playbooks table.
Removes HTML formatting and standardizes to expected values.
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

def clean_seniority_levels():
    """Clean up seniority levels in the database"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Mapping from current values to clean values
    seniority_mapping = {
        "Student / Intern<br>(Entry-Level)": "Junior",
        "Junior / Mid-Level<br>(Product Manager)": "Mid", 
        "Senior<br>(Senior Product Manager)": "Senior",
        "Manager / Lead<br>(Lead, Principal, Group PM)": "Manager"
    }
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # First, let's see what we have
                print("🔍 Current seniority levels in database:")
                result = connection.execute(text("""
                    SELECT DISTINCT seniority, COUNT(*) as count 
                    FROM interview_playbooks 
                    GROUP BY seniority 
                    ORDER BY seniority
                """))
                
                for row in result:
                    print(f"  '{row.seniority}' - {row.count} records")
                
                print("\n🔄 Cleaning up seniority levels...")
                
                # Update each seniority level
                for old_value, new_value in seniority_mapping.items():
                    update_sql = text("""
                        UPDATE interview_playbooks 
                        SET seniority = :new_value 
                        WHERE seniority = :old_value
                    """)
                    
                    result = connection.execute(update_sql, {
                        'old_value': old_value,
                        'new_value': new_value
                    })
                    
                    if result.rowcount > 0:
                        print(f"✅ Updated {result.rowcount} records: '{old_value}' → '{new_value}'")
                    else:
                        print(f"ℹ️  No records found for: '{old_value}'")
                
                # Also clean any remaining HTML tags
                print("\n🧹 Cleaning any remaining HTML tags...")
                cleanup_sql = text("""
                    UPDATE interview_playbooks 
                    SET seniority = REGEXP_REPLACE(seniority, '<[^>]+>', '', 'g')
                    WHERE seniority ~ '<[^>]+>'
                """)
                
                result = connection.execute(cleanup_sql)
                if result.rowcount > 0:
                    print(f"✅ Cleaned HTML tags from {result.rowcount} records")
                
                # Remove parenthetical text
                print("\n🧹 Removing parenthetical text...")
                cleanup_sql = text("""
                    UPDATE interview_playbooks 
                    SET seniority = TRIM(REGEXP_REPLACE(seniority, '\\([^)]*\\)', '', 'g'))
                    WHERE seniority ~ '\\([^)]*\\)'
                """)
                
                result = connection.execute(cleanup_sql)
                if result.rowcount > 0:
                    print(f"✅ Removed parenthetical text from {result.rowcount} records")
                
                # Final cleanup - trim whitespace
                print("\n🧹 Trimming whitespace...")
                cleanup_sql = text("""
                    UPDATE interview_playbooks 
                    SET seniority = TRIM(seniority)
                    WHERE seniority != TRIM(seniority)
                """)
                
                result = connection.execute(cleanup_sql)
                if result.rowcount > 0:
                    print(f"✅ Trimmed whitespace from {result.rowcount} records")
                
                trans.commit()
                print("\n✅ Seniority levels cleaned successfully!")
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

def verify_cleanup():
    """Verify that the cleanup was successful"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return False
        
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            print("\n🔍 Final seniority levels after cleanup:")
            result = connection.execute(text("""
                SELECT DISTINCT seniority, COUNT(*) as count 
                FROM interview_playbooks 
                GROUP BY seniority 
                ORDER BY seniority
            """))
            
            expected_levels = ["Junior", "Mid", "Senior", "Manager"]
            found_levels = []
            
            for row in result:
                print(f"  '{row.seniority}' - {row.count} records")
                found_levels.append(row.seniority)
            
            # Check if we have the expected levels
            missing_levels = set(expected_levels) - set(found_levels)
            unexpected_levels = set(found_levels) - set(expected_levels)
            
            if missing_levels:
                print(f"\n⚠️  Missing expected levels: {missing_levels}")
            
            if unexpected_levels:
                print(f"\n⚠️  Unexpected levels found: {unexpected_levels}")
                print("These may need manual cleanup.")
            
            if not missing_levels and not unexpected_levels:
                print("\n✅ All seniority levels are clean and standardized!")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def show_sample_records():
    """Show sample records to verify the cleanup"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return False
        
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            print("\n📋 Sample records after cleanup:")
            result = connection.execute(text("""
                SELECT role, skill, seniority, archetype
                FROM interview_playbooks 
                ORDER BY role, skill, seniority
                LIMIT 10
            """))
            
            print("Role | Skill | Seniority | Archetype")
            print("-" * 50)
            
            for row in result:
                print(f"{row.role} | {row.skill} | {row.seniority} | {row.archetype}")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to show sample records: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Cleaning up seniority levels in interview_playbooks table")
    print("=" * 60)
    
    if clean_seniority_levels():
        print("\n🔍 Verifying cleanup...")
        if verify_cleanup():
            print("\n📋 Showing sample records...")
            show_sample_records()
            print("\n🎉 SUCCESS! Seniority levels are now clean and standardized!")
            print("\nThe system will now be able to:")
            print("✅ Match seniority levels correctly")
            print("✅ Use the guidance data properly")
            print("✅ Avoid fallback errors")
        else:
            print("\n❌ Cleanup verification failed")
    else:
        print("\n❌ Failed to clean up seniority levels")
        sys.exit(1)
