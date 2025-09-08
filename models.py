from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, text, inspect, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available

# Use the DATABASE_URL from the environment (Render will provide this)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # For testing purposes, use a dummy URL if DATABASE_URL is not set
    print("⚠️  DATABASE_URL not set, using dummy URL for testing")
    DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_db"

# Create the declarative base for SQLAlchemy models
Base = declarative_base()

# Simple initialization - create engine when needed
def get_engine():
    """Get database engine"""
    return create_engine(DATABASE_URL)

def get_session_local():
    """Get database session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

# --- Simplified Table Definitions - Only What We Actually Use ---

class SessionState(Base):
    """
    Main table for storing complete interview data.
    Updated to match the actual deployed database schema.
    """
    __tablename__ = "session_states"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    
    # Current deployed schema columns
    final_current_topic_id = Column(String, nullable=True)
    final_covered_topic_ids = Column(Text, nullable=True)  # JSON string of covered topics
    final_conversation_history = Column(Text, nullable=True)  # Complete conversation history as JSON string
    final_topic_progress = Column(Text, nullable=True)  # Topic progress as JSON string
    
    # Performance Tracking (existing)
    total_router_agent_calls = Column(Integer, default=0)
    total_generator_agent_calls = Column(Integer, default=0)
    total_response_time_ms = Column(Integer, default=0)
    
    # Enhanced: Complete Interview Data as JSON (to be added by migration)
    complete_interview_data = Column(JSON, nullable=True)  # All turns, evaluations, AI reasoning, metadata
    
    # Enhanced: Average Score (to be added by migration)
    average_score = Column(Integer, nullable=True)  # Average evaluation score
    
    # Timestamps
    interview_completed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SessionState(session_id={self.session_id}, final_stage={self.final_stage})>"

class InterviewPlaybook(Base):
    """
    Stores interview playbooks for different Role × Skill × Seniority combinations.
    Contains evaluation dimensions, signals, and archetype information.
    """
    __tablename__ = "interview_playbooks"
    
    id = Column(Integer, primary_key=True)
    role = Column(String, index=True)
    skill = Column(String, index=True)
    seniority = Column(String, index=True)
    archetype = Column(String)  # "broad_design", "improvement", "strategic"
    interview_objective = Column(Text)
    evaluation_dimensions = Column(JSON)  # Each dimension with signals and probes
    seniority_criteria = Column(JSON)  # How evaluation differs by level
    good_vs_great_examples = Column(JSON)  # Examples of different performance levels
    core_philosophy = Column(Text, nullable=True)  # Foundational guidance principles
    pre_interview_strategy = Column(Text, nullable=True)  # Strategy guidance for planning
    during_interview_execution = Column(Text, nullable=True)  # Execution guidance for interviewer
    post_interview_evaluation = Column(Text, nullable=True)  # Evaluation guidance for assessment
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<InterviewPlaybook(role={self.role}, skill={self.skill}, seniority={self.seniority})>"

class InterviewSession(Base):
    """
    Tracks individual interview sessions with their plans, execution, and evaluation.
    """
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, index=True)
    
    # Interview metadata
    selected_skills = Column(String, nullable=False)
    role = Column(String, nullable=False)
    seniority = Column(String, nullable=False)
    skill = Column(String, nullable=False)
    
    # Pre-interview planning data
    playbook_id = Column(Integer, ForeignKey("interview_playbooks.id"), nullable=True)
    selected_archetype = Column(String)
    generated_prompt = Column(Text)
    signal_map = Column(JSON)
    evaluation_criteria = Column(JSON)
    
    # Interview execution data
    conversation_history = Column(JSON, default=list)
    collected_signals = Column(JSON, default=dict)
    
    # Post-interview data
    final_evaluation = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    interview_started_at = Column(DateTime, nullable=True)
    interview_completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<InterviewSession(session_id={self.session_id}, archetype={self.selected_archetype})>"

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

def persist_complete_interview(session_id: str, session_data: dict, conversation_history: list, 
                             evaluations: list, final_state: dict) -> bool:
    """
    Persist complete interview data to PostgreSQL in a single operation.
    
    Args:
        session_id: The session identifier
        session_data: Basic session information (role, seniority, skill)
        conversation_history: Complete list of conversation turns
        evaluations: List of evaluation results for each turn
        final_state: Final interview state and metrics
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from sqlalchemy.orm import Session
        
        # Prepare the complete interview data as JSON
        complete_data = {
            "session_metadata": {
                "session_id": session_id,
                "role": session_data.get("role"),
                "seniority": session_data.get("seniority"),
                "skill": session_data.get("skill"),
                "start_time": session_data.get("start_time"),
                "completion_time": final_state.get("completion_time")
            },
            "conversation_turns": conversation_history,
            "evaluations": evaluations,
            "interview_metrics": {
                "total_turns": len(conversation_history),
                "total_response_time_ms": final_state.get("total_response_time_ms", 0),
                "average_score": final_state.get("average_score", 0),
                "final_stage": final_state.get("final_stage"),
                "final_skill_progress": final_state.get("final_skill_progress")
            },
            "ai_reasoning": final_state.get("ai_reasoning", []),
            "persisted_at": datetime.utcnow().isoformat()
        }
        
        # Create database session
        engine = get_engine()
        db_session = Session(engine)
        
        try:
            # Check if session state already exists
            existing_state = db_session.query(SessionState).filter(
                SessionState.session_id == session_id
            ).first()
            
            if existing_state:
                # Update existing record
                existing_state.final_stage = final_state.get("final_stage", "unknown")
                existing_state.final_skill_progress = final_state.get("final_skill_progress", "unknown")
                existing_state.final_conversation_history = str(conversation_history)
                existing_state.complete_interview_data = complete_data
                existing_state.total_turns = len(conversation_history)
                existing_state.total_response_time_ms = final_state.get("total_response_time_ms", 0)
                existing_state.average_score = final_state.get("average_score", 0)
                existing_state.interview_completed_at = datetime.utcnow()
            else:
                # Create new record
                new_state = SessionState(
                    session_id=session_id,
                    final_stage=final_state.get("final_stage", "unknown"),
                    final_skill_progress=final_state.get("final_skill_progress", "unknown"),
                    final_conversation_history=str(conversation_history),
                    complete_interview_data=complete_data,
                    total_turns=len(conversation_history),
                    total_response_time_ms=final_state.get("total_response_time_ms", 0),
                    average_score=final_state.get("average_score", 0)
                )
                db_session.add(new_state)
            
            # Commit the changes
            db_session.commit()
            print(f"✅ Complete interview data persisted for session {session_id}")
            return True
            
        except Exception as e:
            db_session.rollback()
            print(f"❌ Database error during interview persistence: {e}")
            return False
        finally:
            db_session.close()
            
    except Exception as e:
        print(f"❌ Failed to persist interview data: {e}")
        return False

def persist_interview_session(session_data: dict) -> bool:
    """
    Persist interview session data to PostgreSQL.
    
    Args:
        session_data: Dictionary containing session information
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        session_local = get_session_local()
        db = session_local()
        
        # Create new interview session
        interview_session = InterviewSession(**session_data)
        db.add(interview_session)
        db.commit()
        db.refresh(interview_session)
        
        print(f"✅ Interview session {session_data['session_id']} persisted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to persist interview session: {e}")
        if db:
            db.rollback()
        return False
        
    finally:
        if db:
            db.close()

def get_interview_session(session_id: str) -> Optional[InterviewSession]:
    """
    Retrieve interview session by session ID.
    
    Args:
        session_id: The session identifier
        
    Returns:
        InterviewSession object or None if not found
    """
    try:
        session_local = get_session_local()
        db = session_local()
        
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()
        
        return session
        
    except Exception as e:
        print(f"❌ Failed to retrieve interview session: {e}")
        return None
        
    finally:
        if db:
            db.close()

def update_interview_session(session_id: str, updates: dict) -> bool:
    """
    Update interview session with new data.
    
    Args:
        session_id: The session identifier
        updates: Dictionary of fields to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        session_local = get_session_local()
        db = session_local()
        
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()
        
        if not session:
            print(f"❌ Interview session {session_id} not found")
            return False
        
        # Update fields
        for field, value in updates.items():
            if hasattr(session, field):
                setattr(session, field, value)
        
        db.commit()
        print(f"✅ Interview session {session_id} updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update interview session: {e}")
        if db:
            db.rollback()
        return False
        
    finally:
        if db:
            db.close()

def get_table_names():
    """Get list of all table names"""
    try:
        engine = get_engine()
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        print(f"❌ Failed to get table names: {e}")
        return []

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
