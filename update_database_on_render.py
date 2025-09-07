#!/usr/bin/env python3
"""
Script to update the database on Render to fix typos and ensure proper data structure.
This script should be run on the Render platform where the database is accessible.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Get database URL from environment"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        sys.exit(1)
    return database_url

def update_database():
    """Update the database to fix typos and data structure"""
    try:
        # Connect to database
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        print("🔧 Connecting to database...")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check current data
        print("📊 Checking current playbook data...")
        result = session.execute(text("SELECT role, skill, seniority FROM interview_playbooks LIMIT 5"))
        rows = result.fetchall()
        
        print("Current playbook entries:")
        for row in rows:
            print(f"  - {row[0]} | {row[1]} | {row[2]}")
        
        # Fix the typo: "Product Manger" -> "Product Manager"
        print("\n🔧 Fixing 'Product Manger' typo to 'Product Manager'...")
        update_result = session.execute(text("""
            UPDATE interview_playbooks 
            SET role = 'Product Manager' 
            WHERE role = 'Product Manger'
        """))
        
        print(f"✅ Updated {update_result.rowcount} rows")
        
        # Verify the fix
        print("\n📊 Verifying the fix...")
        result = session.execute(text("SELECT role, skill, seniority FROM interview_playbooks WHERE role = 'Product Manager' LIMIT 5"))
        rows = result.fetchall()
        
        print("Updated playbook entries:")
        for row in rows:
            print(f"  - {row[0]} | {row[1]} | {row[2]}")
        
        # Check data structure
        print("\n🔍 Checking data structure...")
        result = session.execute(text("""
            SELECT 
                role, 
                skill, 
                seniority,
                CASE WHEN evaluation_dimensions IS NOT NULL THEN 'Has evaluation_dimensions' ELSE 'Missing evaluation_dimensions' END as eval_status,
                CASE WHEN interview_objective IS NOT NULL THEN 'Has interview_objective' ELSE 'Missing interview_objective' END as obj_status
            FROM interview_playbooks 
            WHERE role = 'Product Manager'
            LIMIT 3
        """))
        rows = result.fetchall()
        
        print("Data structure check:")
        for row in rows:
            print(f"  - {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
        
        # Commit changes
        session.commit()
        print("\n✅ Database updates committed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        if 'session' in locals():
            session.rollback()
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Main function"""
    print("🚀 Starting database updates on Render...")
    
    success = update_database()
    
    if success:
        print("\n🎉 Database updates completed successfully!")
        print("The role 'Product Manger' has been corrected to 'Product Manager'")
    else:
        print("\n❌ Database updates failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
