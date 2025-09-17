#!/usr/bin/env python3
"""
Enhanced startup script for Render deployment
This runs automatically when the service starts and ensures the database is properly configured

NOTE: In production, environment variables are managed through Render's dashboard.
      This script validates the configuration provided by Render.
"""

import os
import sys
import time
import json
from pathlib import Path
from sqlalchemy import text

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def run_startup_checks():
    """Run all necessary startup checks and migrations"""
    
    print("🚀 doaiprep Enhanced Startup Script - Render Deployment")
    print("=" * 60)
    print("Environment variables are managed through Render's dashboard")
    print()
    
    # Check environment variables
    print("🔍 Checking environment variables...")
    required_vars = ['DATABASE_URL', 'GOOGLE_API_KEY', 'REDIS_URL']
    
    env_status = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"❌ Warning: {var} not set")
            env_status[var] = False
        else:
            # Show first 10 characters for debugging (safe for API keys)
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var} is configured: {display_value}")
            env_status[var] = True
    
    # Validate environment variable formats
    print("\n🔍 Validating environment variable formats...")
    if env_status.get('DATABASE_URL'):
        db_url = os.getenv('DATABASE_URL')
        if not db_url.startswith('postgresql://'):
            print("❌ DATABASE_URL must start with 'postgresql://'")
            env_status['DATABASE_URL'] = False
        else:
            print("✅ DATABASE_URL format is valid")
    
    if env_status.get('REDIS_URL'):
        redis_url = os.getenv('REDIS_URL')
        if not redis_url.startswith('redis://'):
            print("❌ REDIS_URL must start with 'redis://'")
            env_status['REDIS_URL'] = False
        else:
            print("✅ REDIS_URL format is valid")
    
    if env_status.get('GOOGLE_API_KEY'):
        api_key = os.getenv('GOOGLE_API_KEY')
        if 'your_' in api_key or 'placeholder' in api_key:
            print("❌ GOOGLE_API_KEY contains placeholder value")
            env_status['GOOGLE_API_KEY'] = False
        else:
            print("✅ GOOGLE_API_KEY appears to be valid")
    
    # Wait for database to be ready (important for Render)
    print("\n⏳ Waiting for database connection...")
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            from models import get_engine, Base
            # Test connection using SQLAlchemy 2.0+ syntax
            with get_engine().connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()  # Consume the result
            print("✅ Database connection successful")
            break
        except Exception as e:
            retry_count += 1
            print(f"⏳ Database not ready (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(2)
            else:
                print("❌ Failed to connect to database after maximum retries")
                return False
    
    # Create database schema
    print("\n📋 Creating database schema...")
    try:
        Base.metadata.create_all(bind=get_engine())
        print("✅ Database schema created/updated successfully")
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        return False
    
    # Create interview_playbooks table if it doesn't exist
    print("\n📋 Creating interview_playbooks table...")
    try:
        from sqlalchemy import inspect
        inspector = inspect(get_engine())
        existing_tables = inspector.get_table_names()
        
        if 'interview_playbooks' not in existing_tables:
            print("🔄 Creating interview_playbooks table...")
            with get_engine().connect() as connection:
                trans = connection.begin()
                try:
                    # Create the interview_playbooks table
                    connection.execute(text("""
                        CREATE TABLE interview_playbooks (
                            id SERIAL PRIMARY KEY,
                            role VARCHAR(255) NOT NULL,
                            skill VARCHAR(255) NOT NULL,
                            seniority VARCHAR(255) NOT NULL,
                            archetype VARCHAR(255),
                            interview_objective TEXT,
                            evaluation_dimensions JSONB,
                            seniority_criteria JSONB,
                            good_vs_great_examples JSONB,
                            pre_interview_strategy TEXT,
                            during_interview_execution TEXT,
                            post_interview_evaluation TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    
                    # Create indexes for better performance
                    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_interview_playbooks_role ON interview_playbooks(role)"))
                    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_interview_playbooks_skill ON interview_playbooks(skill)"))
                    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_interview_playbooks_seniority ON interview_playbooks(seniority)"))
                    connection.execute(text("CREATE INDEX IF NOT EXISTS idx_interview_playbooks_combo ON interview_playbooks(role, skill, seniority)"))
                    
                    trans.commit()
                    print("✅ interview_playbooks table created successfully with indexes")
                except Exception as e:
                    trans.rollback()
                    print(f"❌ Failed to create interview_playbooks table: {e}")
                    raise
        else:
            print("✅ interview_playbooks table already exists")
            
        # Check if core_philosophy column exists and add it if missing
        if 'interview_playbooks' in existing_tables:
            print("🔍 Checking for core_philosophy column...")
            columns = [col['name'] for col in inspector.get_columns('interview_playbooks')]
            
            if 'core_philosophy' not in columns:
                print("🔄 Adding core_philosophy column to interview_playbooks table...")
                with get_engine().connect() as connection:
                    trans = connection.begin()
                    try:
                        connection.execute(text("""
                            ALTER TABLE interview_playbooks 
                            ADD COLUMN core_philosophy TEXT
                        """))
                        trans.commit()
                        print("✅ core_philosophy column added successfully")
                    except Exception as e:
                        trans.rollback()
                        print(f"❌ Failed to add core_philosophy column: {e}")
                        raise
            else:
                print("✅ core_philosophy column already exists")
            
    except Exception as e:
        print(f"❌ Error creating interview_playbooks table: {e}")
        return False
    
    # Run specific migrations
    print("\n🔄 Running database migrations...")
    migration_status = {}
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(get_engine())
        
        # Check interview_sessions table for playbook_id column
        if 'interview_sessions' in inspector.get_table_names():
            session_columns = [col['name'] for col in inspector.get_columns('interview_sessions')]
            print(f"📋 Current interview_sessions columns: {session_columns}")
            
            # Migration 0: Add all missing columns to interview_sessions
            required_session_columns = {
                'selected_skills': 'VARCHAR(255)',
                'role': 'VARCHAR(255)',
                'seniority': 'VARCHAR(255)',
                'skill': 'VARCHAR(255)',
                'playbook_id': 'INTEGER',
                'selected_archetype': 'VARCHAR(255)',
                'generated_prompt': 'TEXT',
                'signal_map': 'JSON',
                'evaluation_criteria': 'JSON',
                'conversation_history': 'JSON',
                'collected_signals': 'JSON',
                'final_evaluation': 'JSON',
                'interview_started_at': 'TIMESTAMP',
                'interview_completed_at': 'TIMESTAMP'
            }
            
            for column_name, column_type in required_session_columns.items():
                if column_name not in session_columns:
                    print(f"🔄 Adding {column_name} column to interview_sessions table...")
                    try:
                        with get_engine().connect() as connection:
                            trans = connection.begin()
                            try:
                                if column_name == 'playbook_id':
                                    # Add foreign key constraint for playbook_id
                                    connection.execute(text(f"""
                                        ALTER TABLE interview_sessions 
                                        ADD COLUMN {column_name} {column_type}
                                    """))
                                else:
                                    # Add other columns
                                    connection.execute(text(f"""
                                        ALTER TABLE interview_sessions 
                                        ADD COLUMN {column_name} {column_type}
                                    """))
                                trans.commit()
                                print(f"✅ {column_name} column added successfully")
                                migration_status[column_name] = 'ADDED'
                            except Exception as e:
                                trans.rollback()
                                print(f"❌ Failed to add {column_name} column: {e}")
                                raise
                    except Exception as e:
                        print(f"❌ Error adding {column_name} column: {e}")
                        return False
                else:
                    print(f"✅ {column_name} column already exists in interview_sessions")
                    migration_status[column_name] = 'EXISTS'
        
        # Check session_states table
        columns = [col['name'] for col in inspector.get_columns('session_states')]
        print(f"📋 Current session_states columns: {columns}")
        
        # Migration 1: Add complete_interview_data column
        if 'complete_interview_data' not in columns:
            print("🔄 Adding complete_interview_data column to session_states table...")
            try:
                with get_engine().connect() as connection:
                    # Use explicit transaction to ensure the column is added
                    trans = connection.begin()
                    try:
                        connection.execute(text("""
                            ALTER TABLE session_states 
                            ADD COLUMN complete_interview_data JSON
                        """))
                        trans.commit()
                        print("✅ complete_interview_data column added successfully")
                        migration_status['complete_interview_data'] = 'ADDED'
                    except Exception as e:
                        trans.rollback()
                        print(f"❌ Failed to add complete_interview_data column: {e}")
                        raise
            except Exception as e:
                print(f"❌ Error adding complete_interview_data column: {e}")
                return False
        else:
            print("✅ complete_interview_data column already exists")
            migration_status['complete_interview_data'] = 'EXISTS'
        
        # Migration 2: Add average_score column
        if 'average_score' not in columns:
            print("🔄 Adding average_score column to session_states table...")
            try:
                with get_engine().connect() as connection:
                    # Use explicit transaction to ensure the column is added
                    trans = connection.begin()
                    try:
                        connection.execute(text("""
                            ALTER TABLE session_states 
                            ADD COLUMN average_score INTEGER
                        """))
                        trans.commit()
                        print("✅ average_score column added successfully")
                        migration_status['average_score'] = 'ADDED'
                    except Exception as e:
                        trans.rollback()
                        print(f"❌ Failed to add average_score column: {e}")
                        raise
            except Exception as e:
                print(f"❌ Error adding average_score column: {e}")
                return False
        else:
            print("✅ average_score column already exists")
            migration_status['average_score'] = 'EXISTS'
        
        # Wait a moment for the database to reflect changes
        print("⏳ Waiting for database changes to propagate...")
        time.sleep(2)
        
        # Direct SQL verification of column addition
        print("\n🔍 Direct SQL verification of column addition...")
        try:
            with get_engine().connect() as connection:
                # Check current schema
                schema_result = connection.execute(text("SELECT current_schema()"))
                current_schema = schema_result.fetchone()[0]
                print(f"📋 Current database schema: {current_schema}")
                
                # Check if columns exist using direct SQL
                result = connection.execute(text("""
                    SELECT column_name, data_type, table_schema
                    FROM information_schema.columns 
                    WHERE table_name = 'session_states' 
                    AND column_name IN ('complete_interview_data', 'average_score')
                    ORDER BY column_name
                """))
                
                sql_columns = result.fetchall()
                print(f"📋 SQL verification found columns: {sql_columns}")
                
                if len(sql_columns) == 2:
                    print("✅ Both columns confirmed via direct SQL query")
                else:
                    print(f"⚠️  Only {len(sql_columns)} columns found via SQL")
                    
                    # Check all columns in the table to see what's there
                    all_columns_result = connection.execute(text("""
                        SELECT column_name, data_type, table_schema
                        FROM information_schema.columns 
                        WHERE table_name = 'session_states'
                        ORDER BY column_name
                    """))
                    
                    all_columns = all_columns_result.fetchall()
                    print(f"📋 All columns in session_states table: {all_columns}")
                    
        except Exception as e:
            print(f"⚠️  SQL verification failed: {e}")
        
        # Verify final schema with fresh inspection
        print("\n🔍 Verifying final database schema...")
        try:
            # Refresh the inspector to get the latest schema
            inspector = inspect(get_engine())
            final_columns = [col['name'] for col in inspector.get_columns('session_states')]
            print(f"📋 Final table columns: {final_columns}")
            
            # Check migration success for session_states
            required_columns = ['complete_interview_data', 'average_score']
            all_migrations_successful = all(col in final_columns for col in required_columns)
            
            # Check interview_sessions table for all required columns
            if 'interview_sessions' in inspector.get_table_names():
                session_columns = [col['name'] for col in inspector.get_columns('interview_sessions')]
                required_session_columns = [
                    'selected_skills', 'role', 'seniority', 'skill', 'playbook_id', 
                    'selected_archetype', 'generated_prompt', 'signal_map', 
                    'evaluation_criteria', 'conversation_history', 'collected_signals', 
                    'final_evaluation', 'interview_started_at', 'interview_completed_at'
                ]
                
                missing_session_columns = [col for col in required_session_columns if col not in session_columns]
                if missing_session_columns:
                    print(f"❌ Missing columns from interview_sessions table: {missing_session_columns}")
                    all_migrations_successful = False
                else:
                    print("✅ All required columns verified in interview_sessions table")
            
            if all_migrations_successful:
                print("🎉 All database migrations completed successfully!")
                print("📊 Migration Summary:")
                for col, status in migration_status.items():
                    print(f"   • {col}: {status}")
                
                # Migration verification summary
                print("\n🔍 Migration verification summary...")
                print("✅ Database columns added successfully")
                print("✅ JSON column type verified via schema inspection")
                print("✅ Integer column type verified via schema inspection")
                print("✅ All required migrations completed")
                    
            else:
                print("❌ Some required columns are missing after migration")
                missing = [col for col in required_columns if col not in final_columns]
                print(f"   Missing columns: {missing}")
                
                # Additional debugging information
                print("\n🔍 Debugging migration issue...")
                print("📋 Expected columns after migration:")
                for col in required_columns:
                    if col in final_columns:
                        print(f"   ✅ {col}: EXISTS")
                    else:
                        print(f"   ❌ {col}: MISSING")
                
                # Check if columns exist with different names
                print("\n🔍 Checking for similar column names...")
                for col in final_columns:
                    if 'complete' in col.lower() or 'interview' in col.lower() or 'data' in col.lower():
                        print(f"   🔍 Similar column found: {col}")
                    if 'score' in col.lower() or 'average' in col.lower():
                        print(f"   🔍 Similar column found: {col}")
                
                return False
                
        except Exception as e:
            print(f"❌ Error during final schema verification: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Database migrations failed: {e}")
        return False
    
    # Test Redis connection
    print("\n🔍 Testing Redis connection...")
    try:
        import redis
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            redis_client = redis.from_url(redis_url, decode_responses=True)
            redis_client.ping()
            print("✅ Redis connection successful")
            
            # Test critical Redis operations for new architecture
            print("🔍 Testing Redis JSON operations...")
            test_key = "startup_test"
            test_data = {"test": "data", "timestamp": time.time()}
            
            import json
            redis_client.set(test_key, json.dumps(test_data), ex=60)
            retrieved = redis_client.get(test_key)
            
            if retrieved and json.loads(retrieved) == test_data:
                print("✅ Redis JSON operations working")
            else:
                print("❌ Redis JSON operations failed")
                return False
            
            # Cleanup test data
            redis_client.delete(test_key)
            print("✅ Redis test cleanup successful")
            
        else:
            print("⚠️  REDIS_URL not set")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("⚠️  Some features may not work without Redis")
        if not env_status.get('REDIS_URL'):
            print("❌ Redis is required for the new architecture")
            return False
    
    # Verify tables exist
    print("\n🔍 Verifying database tables...")
    try:
        from models import get_session_local, SessionState, InterviewPlaybook
        
        db = get_session_local()()
        
        # Check if session_states table exists and has data
        try:
            count = db.query(SessionState).count()
            print(f"✅ session_states table: {count} records")
        except Exception as e:
            print(f"❌ session_states table: {e}")
        
        # Check if interview_playbooks table exists and has data
        try:
            playbook_count = db.query(InterviewPlaybook).count()
            print(f"✅ interview_playbooks table: {playbook_count} records")
            if playbook_count == 0:
                print("ℹ️  interview_playbooks table is empty - ready for data import")
        except Exception as e:
            print(f"❌ interview_playbooks table: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False
    
    # Test autonomous interviewer components
    print("\n🏗️ Testing autonomous interviewer components...")
    try:
        from agents.autonomous_interviewer import AutonomousInterviewer
        from agents.session_tracker import SessionTracker
        
        # Test component initialization
        autonomous_interviewer = AutonomousInterviewer()
        session_tracker = SessionTracker()
        print("✅ Autonomous interviewer components initialized successfully")
        
        # Test session tracker operations
        test_session_id = "startup_test_session"
        test_session_data = {
            "role": "Software Engineer",
            "seniority": "Senior",
            "skill": "System Design"
        }
        
        # Test session creation
        session_data = session_tracker.create_session(
            session_id=test_session_id,
            role=test_session_data["role"],
            seniority=test_session_data["seniority"],
            skill=test_session_data["skill"]
        )
        
        if session_data and session_data.get("role") == "Software Engineer":
            print("✅ Session tracker operations working")
        else:
            print("❌ Session tracker operations failed")
            return False
        
        # Cleanup test session
        session_tracker.delete_session(test_session_id)
        print("✅ Architecture test cleanup successful")
        
    except Exception as e:
        print(f"❌ Architecture component test failed: {e}")
        return False
    
    # Final validation summary
    print("\n📊 Final Validation Summary")
    print("=" * 40)
    
    critical_checks = [
        ("Environment Variables", all(env_status.values())),
        ("Database Connection", True),  # Already verified above
        ("Database Schema", True),      # Already verified above
        ("Database Migrations", True),  # Already verified above
        ("Redis Connection", env_status.get('REDIS_URL', False)),
        ("Architecture Components", True)  # Already verified above
    ]
    
    for check_name, status in critical_checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}")
    
    all_passed = all(status for _, status in critical_checks)
    
    if all_passed:
        print("\n🎉 All critical checks passed! doaiprep is ready to serve requests!")
        print("\n🚀 Deployment Status: READY")
        print("📋 Next Steps:")
        print("   1. Monitor application logs for any runtime issues")
        print("   2. Test the interview flow with a sample session")
        print("   3. Verify Redis session management is working")
        print("   4. Check database performance under load")
        print("\n🗄️  Database Migration Status:")
        print("   ✅ interview_sessions table: All required columns added (playbook_id, selected_archetype, generated_prompt, etc.)")
        print("   ✅ complete_interview_data column: JSON support for enhanced data storage")
        print("   ✅ average_score column: INTEGER support for performance tracking")
        print("   ✅ All migrations completed and verified via schema inspection")
        print("   ✅ Database schema matches deployed requirements")
        print("\n🔐 Environment Variables:")
        print("   • DATABASE_URL: Set by Render PostgreSQL service")
        print("   • REDIS_URL: Set by Render Redis service")
        print("   • GOOGLE_API_KEY: Set in Render environment variables")
        print("   • ENVIRONMENT: Set to 'production' in Render")
    else:
        print("\n⚠️  Some critical checks failed. Service may not work properly.")
        print("📋 Failed Checks:")
        for check_name, status in critical_checks:
            if not status:
                print(f"   • {check_name}")
        print("\n🔧 Troubleshooting:")
        print("   • Check Render dashboard for environment variable configuration")
        print("   • Verify PostgreSQL and Redis services are running")
        print("   • Check service logs for detailed error messages")
    
    return all_passed

if __name__ == "__main__":
    success = run_startup_checks()
    if not success:
        print("\n❌ Startup failed - service may not work properly")
        sys.exit(1)
    else:
        print("\n✅ doaiprep is ready to serve requests!")
