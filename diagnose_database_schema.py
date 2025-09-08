#!/usr/bin/env python3
"""
Diagnostic script to check the actual database schema vs our model
"""

import os
import sys
from sqlalchemy import inspect, text

# Add current directory to path
sys.path.append('.')

def diagnose_database_schema():
    """Check the actual database schema"""
    print("🔍 Diagnosing Database Schema...")
    
    try:
        from models import get_engine
        
        engine = get_engine()
        inspector = inspect(engine)
        
        # Check if interview_sessions table exists
        tables = inspector.get_table_names()
        print(f"\n📋 Available tables: {tables}")
        
        if 'interview_sessions' not in tables:
            print("❌ interview_sessions table does not exist!")
            return False
        
        # Get the actual column information
        print(f"\n📋 interview_sessions table columns:")
        columns = inspector.get_columns('interview_sessions')
        
        for i, col in enumerate(columns):
            print(f"  {i+1}. {col['name']}: {col['type']} (nullable: {col['nullable']})")
        
        # Check the column order specifically
        print(f"\n📋 Column order in database:")
        column_names = [col['name'] for col in columns]
        for i, name in enumerate(column_names):
            print(f"  {i+1}. {name}")
        
        # Check if there are any JSON columns that might be causing issues
        print(f"\n📋 JSON columns in database:")
        json_columns = [col for col in columns if 'JSON' in str(col['type'])]
        for col in json_columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # Try to get a sample of existing data to see the structure
        print(f"\n📋 Sample data structure:")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM interview_sessions LIMIT 1"))
                row = result.fetchone()
                if row:
                    print("  Sample row found:")
                    for i, value in enumerate(row):
                        col_name = column_names[i] if i < len(column_names) else f"col_{i}"
                        print(f"    {col_name}: {repr(value)} (type: {type(value)})")
                else:
                    print("  No existing data found")
        except Exception as e:
            print(f"  Error getting sample data: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_database_schema()
    if success:
        print("\n✅ Database schema diagnosis complete!")
    else:
        print("\n❌ Database schema diagnosis failed!")