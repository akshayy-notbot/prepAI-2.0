import json
import time
from typing import List, Dict, Any, Optional
import redis
import os

class SessionTracker:
    """
    Simple session tracker for autonomous interviews.
    Manages conversation history, interview state, and skill progress.
    """
    
    def __init__(self):
        self._redis_client = None
    
    def _get_redis_client(self):
        """Lazy initialization of Redis client"""
        if self._redis_client is None:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is required")
            self._redis_client = redis.from_url(redis_url)
        return self._redis_client
    
    def create_session(self, session_id: str, role: str, seniority: str, skill: str) -> Dict[str, Any]:
        """
        Create a new interview session.
        """
        session_data = {
            "session_id": session_id,
            "role": role,
            "seniority": seniority,
            "skill": skill,
            "start_time": time.time(),
            "current_stage": "problem_understanding",
            "skill_progress": "not_started",
            "conversation_history": [],
            "interview_state": {
                "current_stage": "problem_understanding",
                "skill_progress": "not_started",
                "next_focus": "initial_problem_presentation"
            }
        }
        
        # Save to Redis
        redis_client = self._get_redis_client()
        redis_client.set(f"session:{session_id}", json.dumps(session_data), ex=3600)  # 1 hour expiry
        
        return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data from Redis.
        """
        redis_client = self._get_redis_client()
        session_json = redis_client.get(f"session:{session_id}")
        
        if session_json:
            return json.loads(session_json.decode('utf-8'))
        return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update session data with new information.
        """
        try:
            current_session = self.get_session(session_id)
            if not current_session:
                return False
            
            # Update the session data
            current_session.update(updates)
            current_session["last_updated"] = time.time()
            
            # Save back to Redis
            redis_client = self._get_redis_client()
            redis_client.set(f"session:{session_id}", json.dumps(current_session), ex=3600)
            
            return True
            
        except Exception as e:
            print(f"Error updating session {session_id}: {e}")
            return False
    
    def add_conversation_turn(self, session_id: str, role: str, content: str) -> bool:
        """
        Add a new conversation turn to the session.
        """
        try:
            current_session = self.get_session(session_id)
            if not current_session:
                return False
            
            # Add new turn
            new_turn = {
                "role": role,
                "content": content,
                "timestamp": time.time()
            }
            
            current_session["conversation_history"].append(new_turn)
            
            # Keep only last 20 turns to manage memory
            if len(current_session["conversation_history"]) > 20:
                current_session["conversation_history"] = current_session["conversation_history"][-20:]
            
            # Update session
            return self.update_session(session_id, current_session)
            
        except Exception as e:
            print(f"Error adding conversation turn to session {session_id}: {e}")
            return False
    
    def update_interview_state(self, session_id: str, new_state: Dict[str, Any]) -> bool:
        """
        Update the interview state (stage, progress, focus).
        """
        try:
            current_session = self.get_session(session_id)
            if not current_session:
                return False
            
            # Update interview state
            current_session["interview_state"] = new_state
            current_session["current_stage"] = new_state.get("current_stage", current_session["current_stage"])
            current_session["skill_progress"] = new_state.get("skill_progress", current_session["skill_progress"])
            
            return self.update_session(session_id, current_session)
            
        except Exception as e:
            print(f"Error updating interview state for session {session_id}: {e}")
            return False
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a session.
        """
        session = self.get_session(session_id)
        if session:
            return session.get("conversation_history", [])
        return []
    
    def get_current_stage(self, session_id: str) -> str:
        """
        Get the current interview stage.
        """
        session = self.get_session(session_id)
        if session:
            return session.get("current_stage", "problem_understanding")
        return "problem_understanding"
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get session context for the interviewer.
        """
        session = self.get_session(session_id)
        if session:
            return {
                "start_time": session.get("start_time"),
                "role": session.get("role"),
                "seniority": session.get("seniority"),
                "skill": session.get("skill"),
                "current_stage": session.get("current_stage"),
                "skill_progress": session.get("skill_progress"),
                "conversation_count": len(session.get("conversation_history", [])),
                "estimated_duration": 45  # Default 45 minutes
            }
        return {}
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from Redis.
        """
        try:
            redis_client = self._get_redis_client()
            redis_client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def is_session_active(self, session_id: str) -> bool:
        """
        Check if a session is still active.
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Check if session hasn't expired (1 hour)
        start_time = session.get("start_time", 0)
        return (time.time() - start_time) < 3600
