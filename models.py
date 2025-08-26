from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Use the DATABASE_URL from the environment (Render will provide this)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required. Please set it in Render dashboard.")

# Create the declarative base for SQLAlchemy models
Base = declarative_base()

# Simple initialization - create engine when needed
def get_engine():
    """Get database engine"""
    return create_engine(DATABASE_URL)

def get_session_local():
    """Get database session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

# --- Simplified Table Definitions for Autonomous Interviewer ---

class InterviewSession(Base):
    """
    Stores basic interview session information.
    Note: Real-time state is managed in Redis by SessionTracker.
    """
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)  # Frontend-generated session ID
    user_id = Column(Integer, index=True, default=1)  # For now, using dummy user ID
    
    # Interview Configuration
    role = Column(String, nullable=False)
    seniority = Column(String, nullable=False)
    skill = Column(String, nullable=False)  # Single skill focus
    
    # Session Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String, default='ready')  # ready, in_progress, completed
    
    # Final State (from Redis when interview ended)
    final_stage = Column(String)  # Final interview stage
    final_skill_progress = Column(String)  # Final skill assessment
    
    # Performance Metrics
    total_questions = Column(Integer, default=0)
    total_responses = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<InterviewSession(id={self.id}, role={self.role}, status={self.status})>"

class SessionState(Base):
    """
    Final session state for completed interviews (persisted after completion).
    Real-time state during interviews lives in Redis only.
    """
    __tablename__ = "session_states"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    
    # Final State (from Redis when interview ended)
    final_stage = Column(String, nullable=False)
    final_skill_progress = Column(String, nullable=False)
    
    # Final Conversation State
    final_conversation_history = Column(Text)  # Complete conversation history as JSON string
    
    # Performance Tracking
    total_turns = Column(Integer, default=0)
    total_response_time_ms = Column(Integer, default=0)
    
    # Timestamps
    interview_completed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SessionState(session_id={self.session_id}, final_stage={self.final_stage})>"

class UserResponse(Base):
    """
    Stores individual user responses for analysis and audit purposes
    """
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    
    # Response Metadata
    response_length = Column(Integer)  # Character count
    response_time_seconds = Column(Integer)  # Time taken to respond
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserResponse(id={self.id}, session_id={self.session_id})>"

# --- Database Utility Functions ---

def create_tables():
    """Create all database tables"""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False

def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        engine = get_engine()
        Base.metadata.drop_all(bind=engine)
        print("✅ Database tables dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to drop database tables: {e}")
        return False

def get_table_names():
    """Get list of all table names"""
    try:
        engine = get_engine()
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        print(f"❌ Failed to get table names: {e}")
        return []

# --- Legacy Compatibility Functions ---

def get_engine_legacy():
    """Legacy function - use get_engine() instead"""
    return get_engine()

def get_session_local_legacy():
    """Legacy function - use get_session_local() instead"""
    return get_session_local()

# --- Database Connection Test ---

def test_database_connection():
    """Test database connectivity"""
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing database models...")
    
    # Test table creation
    if create_tables():
        print("✅ Table creation test passed")
    else:
        print("❌ Table creation test failed")
    
    # Test database connection
    if test_database_connection():
        print("✅ Database connection test passed")
    else:
        print("❌ Database connection test failed")
    
    print("🎉 Database model tests completed!")
