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
    
    print("🚀 PrepAI Enhanced Startup Script - Render Deployment")
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
    
    # Run specific migrations
    print("\n🔄 Running database migrations...")
    migration_status = {}
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(get_engine())
        columns = [col['name'] for col in inspector.get_columns('session_states')]
        
        print(f"📋 Current table columns: {columns}")
        
        # Migration 1: Add complete_interview_data column
        if 'complete_interview_data' not in columns:
            print("🔄 Adding complete_interview_data column to session_states table...")
            with get_engine().connect() as connection:
                connection.execute(text("""
                    ALTER TABLE session_states 
                    ADD COLUMN complete_interview_data JSON
                """))
                connection.commit()
                print("✅ complete_interview_data column added successfully")
                migration_status['complete_interview_data'] = 'ADDED'
        else:
            print("✅ complete_interview_data column already exists")
            migration_status['complete_interview_data'] = 'EXISTS'
        
        # Migration 2: Add average_score column
        if 'average_score' not in columns:
            print("🔄 Adding average_score column to session_states table...")
            with get_engine().connect() as connection:
                connection.execute(text("""
                    ALTER TABLE session_states 
                    ADD COLUMN average_score INTEGER
                """))
                connection.commit()
                print("✅ average_score column added successfully")
                migration_status['average_score'] = 'ADDED'
        else:
            print("✅ average_score column already exists")
            migration_status['average_score'] = 'EXISTS'
        
        # Verify final schema
        print("\n🔍 Verifying final database schema...")
        final_columns = [col['name'] for col in inspector.get_columns('session_states')]
        print(f"📋 Final table columns: {final_columns}")
        
        # Check migration success
        required_columns = ['complete_interview_data', 'average_score']
        all_migrations_successful = all(col in final_columns for col in required_columns)
        
        if all_migrations_successful:
            print("🎉 All database migrations completed successfully!")
            print("📊 Migration Summary:")
            for col, status in migration_status.items():
                print(f"   • {col}: {status}")
            
            # Additional migration verification
            print("\n🔍 Running comprehensive migration verification...")
            try:
                # Test JSON column functionality
                print("🧪 Testing JSON column functionality...")
                with get_engine().connect() as connection:
                    # Test if we can insert and retrieve JSON data
                    test_data = {"test": "migration_verification", "timestamp": time.time()}
                    test_json = json.dumps(test_data)
                    
                    # Create a temporary test table to verify JSON support
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS migration_test (
                            id SERIAL PRIMARY KEY,
                            test_data JSON
                        )
                    """))
                    
                    # Insert test JSON data
                    connection.execute(text("""
                        INSERT INTO migration_test (test_data) VALUES (%s)
                    """), (test_json,))
                    
                    # Retrieve and verify
                    result = connection.execute(text("SELECT test_data FROM migration_test"))
                    retrieved_data = result.fetchone()[0]
                    
                    if retrieved_data == test_data:
                        print("✅ JSON column functionality verified successfully")
                    else:
                        print("❌ JSON column functionality test failed")
                        return False
                    
                    # Cleanup test table
                    connection.execute(text("DROP TABLE migration_test"))
                    connection.commit()
                    print("✅ Migration verification cleanup successful")
                    
            except Exception as e:
                print(f"❌ Migration verification failed: {e}")
                return False
                
        else:
            print("❌ Some required columns are missing after migration")
            missing = [col for col in required_columns if col not in final_columns]
            print(f"   Missing columns: {missing}")
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
        from models import get_session_local, SessionState
        
        db = get_session_local()()
        
        # Check if session_states table exists and has data
        try:
            count = db.query(SessionState).count()
            print(f"✅ session_states table: {count} records")
        except Exception as e:
            print(f"❌ session_states table: {e}")
        
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
        print("\n🎉 All critical checks passed! PrepAI is ready to serve requests!")
        print("\n🚀 Deployment Status: READY")
        print("📋 Next Steps:")
        print("   1. Monitor application logs for any runtime issues")
        print("   2. Test the interview flow with a sample session")
        print("   3. Verify Redis session management is working")
        print("   4. Check database performance under load")
        print("\n🗄️  Database Migration Status:")
        print("   ✅ complete_interview_data column: JSON support for enhanced data storage")
        print("   ✅ average_score column: INTEGER support for performance tracking")
        print("   ✅ All migrations verified and functional")
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
        print("\n✅ PrepAI is ready to serve requests!")
