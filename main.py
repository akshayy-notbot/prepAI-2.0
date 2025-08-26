import os
import json
import time
import random
from typing import List, Dict, Any
from datetime import datetime

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  dotenv not available, using system environment variables")

try:
    from fastapi import FastAPI, Depends, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from sqlalchemy.orm import Session
    print("✅ FastAPI components imported successfully")
except Exception as e:
    print(f"❌ Failed to import FastAPI components: {e}")
    raise

try:
    import redis
    print("✅ redis imported successfully")
except Exception as e:
    print(f"❌ Failed to import redis: {e}")
    raise

# Import our autonomous interviewer components
try:
    from agents.autonomous_interviewer import AutonomousInterviewer
    from agents.session_tracker import SessionTracker
    from agents.evaluation import evaluate_answer
    print("✅ Autonomous interviewer components imported successfully")
except Exception as e:
    print(f"❌ Failed to import autonomous interviewer components: {e}")
    raise

# --- FastAPI App Initialization ---
app = FastAPI(title="PrepAI Autonomous Interviewer API")

# --- CORS Middleware Configuration ---
origins = [
    "https://akshayy-notbot.github.io",
    "https://prepai-api.onrender.com",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class StartInterviewRequest(BaseModel):
    role: str
    seniority: str
    skills: List[str]

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "PrepAI Autonomous Interviewer Backend"
    }

# --- Interview Endpoints ---
@app.post("/api/start-interview")
async def start_interview(request: StartInterviewRequest):
    """
    Starts a new autonomous interview session.
    Creates a session and generates the first question.
    """
    try:
        print(f"🚀 Starting interview for {request.role} at {request.seniority} level")
        print(f"📚 Skills to practice: {', '.join(request.skills)}")
        
        # Generate unique session ID
        session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        print(f"✅ Generated session ID: {session_id}")
        
        # Initialize Session Tracker and Autonomous Interviewer
        try:
            session_tracker = SessionTracker()
            autonomous_interviewer = AutonomousInterviewer()
            
            # Create new session with simplified structure
            session_data = session_tracker.create_session(
                session_id=session_id,
                role=request.role,
                seniority=request.seniority,
                skill=request.skills[0] if request.skills else "General"  # Focus on first skill
            )
            
            print(f"✅ Session created successfully with autonomous interviewer")
            
        except Exception as session_error:
            print(f"❌ Failed to create session: {session_error}")
            return {"error": f"Failed to create interview session: {session_error}"}, 500
        
        # Generate the First Question
        print("🎭 Generating first interview question using Autonomous Interviewer...")
        
        try:
            # Get initial question from autonomous interviewer
            first_question_result = autonomous_interviewer.get_initial_question(
                role=request.role,
                seniority=request.seniority,
                skill=request.skills[0] if request.skills else "General",
                session_context=session_tracker.get_session_context(session_id)
            )
            
            if not first_question_result.get("response_text"):
                raise Exception("Autonomous Interviewer failed to generate opening statement")
            
            opening_statement = first_question_result["response_text"]
            print(f"✅ Opening statement generated: {opening_statement[:100]}...")
            
            # Update session with initial state
            session_tracker.update_interview_state(session_id, first_question_result["interview_state"])
            
        except Exception as interviewer_error:
            print(f"❌ Autonomous Interviewer failed: {interviewer_error}")
            return {"error": f"Failed to generate opening statement: {interviewer_error}"}, 500
        
        # Create and Save the History
        interview_history = [
            {
                "question": opening_statement,
                "answer": None,
                "timestamp": datetime.utcnow().isoformat(),
                "question_type": "opening"
            }
        ]
        
        # Save history to Redis
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is required")
            redis_client = redis.from_url(redis_url)
            
            history_json = json.dumps(interview_history)
            redis_client.set(f"history:{session_id}", history_json, ex=3600)  # Expire in 1 hour
            print(f"✅ Interview history saved to Redis")
            
        except Exception as redis_error:
            print(f"❌ Failed to save history to Redis: {redis_error}")
            return {"error": f"Failed to save interview history: {str(redis_error)}"}, 500
        
        # Return the Response
        response_data = {
            "session_id": session_id,
            "opening_statement": opening_statement,
            "status": "started",
            "role": request.role,
            "seniority": request.seniority,
            "skill": request.skills[0] if request.skills else "General",
            "estimated_duration_minutes": 45,  # Default duration
            "message": "Interview started successfully with autonomous interviewer"
        }
        
        print(f"🎯 Interview session {session_id} started successfully!")
        return response_data
        
    except Exception as e:
        print(f"❌ Unexpected error in start_interview: {e}")
        return {"error": f"Interview start failed: {str(e)}"}, 500

@app.post("/api/submit-answer")
async def submit_answer(request: SubmitAnswerRequest):
    """
    Receives an answer from the user and processes it using the autonomous interviewer.
    """
    if not request.session_id or not request.answer:
        raise HTTPException(status_code=400, detail="session_id and answer are required.")
    
    try:
        print(f"🎯 Processing answer for session {request.session_id}")
        
        # Get Redis connection
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is required")
        redis_client = redis.from_url(redis_url, decode_responses=False)
        
        # Fetch the Current State from Redis
        print("📥 Fetching current state from Redis...")
        
        # Get the conversation history
        history_json = redis_client.get(f"history:{request.session_id}")
        if not history_json:
            raise HTTPException(status_code=404, detail="Conversation history not found. Session may have expired.")
        
        conversation_history = json.loads(history_json.decode('utf-8') if isinstance(history_json, bytes) else history_json)
        print(f"✅ Retrieved conversation history with {len(conversation_history)} turns")
        
        # Update the Conversation History
        print("📝 Updating conversation history with user's answer...")
        
        if not conversation_history:
            raise HTTPException(status_code=400, detail="Conversation history is empty")
        
        # Update the last turn's answer
        last_turn = conversation_history[-1]
        last_turn["answer"] = request.answer
        print(f"✅ Updated last turn with user's answer: {request.answer[:50]}...")
        
        # Also add user's answer to session tracker
        try:
            session_tracker = SessionTracker()
            session_tracker.add_conversation_turn(request.session_id, "user", request.answer)
            print(f"✅ Added user's answer to session tracker")
        except Exception as e:
            print(f"⚠️  Warning: Failed to add user's answer to session tracker: {e}")
        
        # Use Autonomous Interviewer for Response Generation
        print("🎭 Using Autonomous Interviewer system for response generation...")
        
        try:
            autonomous_interviewer = AutonomousInterviewer()
            session_tracker = SessionTracker()
            
            # Get current session state
            session_data = session_tracker.get_session(request.session_id)
            if not session_data:
                raise Exception("Session not found or expired")
            
            # Create the conversation history for the AI with the user's answer included
            ai_conversation_history = []
            for turn in conversation_history:
                if turn.get("question"):
                    ai_conversation_history.append({
                        "role": "interviewer",
                        "content": turn["question"]
                    })
                if turn.get("answer"):  # Make sure we include user answers
                    ai_conversation_history.append({
                        "role": "user", 
                        "content": turn["answer"]
                    })
            
            print(f"🔍 AI Conversation History prepared: {len(ai_conversation_history)} turns")
            for i, turn in enumerate(ai_conversation_history):
                print(f"  Turn {i+1}: {turn['role']} - {turn['content'][:50]}...")
            
            print(f"🔍 Calling autonomous_interviewer.conduct_interview_turn with:")
            print(f"  - role: {session_data['role']}")
            print(f"  - seniority: {session_data['seniority']}")
            print(f"  - skill: {session_data['skill']}")
            print(f"  - interview_stage: {session_data['current_stage']}")
            print(f"  - conversation_history: {len(ai_conversation_history)} turns")
            print(f"  - session_context: {session_tracker.get_session_context(request.session_id)}")
            
            # Process the user response using autonomous interviewer
            interviewer_result = autonomous_interviewer.conduct_interview_turn(
                role=session_data["role"],
                seniority=session_data["seniority"],
                skill=session_data["skill"],
                interview_stage=session_data["current_stage"],
                conversation_history=ai_conversation_history,
                session_context=session_tracker.get_session_context(request.session_id)
            )
            
            if not interviewer_result.get("response_text"):
                raise Exception("Autonomous Interviewer failed to generate response")
            
            new_ai_question = interviewer_result["response_text"]
            current_stage = interviewer_result["interview_state"]["current_stage"]
            skill_progress = interviewer_result["interview_state"]["skill_progress"]
            next_focus = interviewer_result["interview_state"]["next_focus"]
            
            print(f"✅ Autonomous Interviewer generated response")
            print(f"🔍 FULL INTERVIEWER RESULT:")
            print(f"  - Chain of Thought: {interviewer_result.get('chain_of_thought', [])}")
            print(f"  - Response Text: {interviewer_result.get('response_text', 'No response text')}")
            print(f"  - Interview State: {interviewer_result.get('interview_state', {})}")
            print(f"📊 Current stage: {current_stage}")
            print(f"🎯 Skill progress: {skill_progress}")
            print(f"🎯 Next focus: {next_focus}")
            
            # Update session state
            session_tracker.update_interview_state(request.session_id, interviewer_result["interview_state"])
            
            # Add the new question to conversation history
            session_tracker.add_conversation_turn(request.session_id, "interviewer", new_ai_question)
            
            # Check if interview should end (based on skill progress or other criteria)
            if skill_progress in ["expert", "advanced"] and len(conversation_history) > 10:
                print("🎉 Interview completed by Autonomous Interviewer!")
                # Mark session as completed
                session_tracker.update_session(request.session_id, {"status": "completed"})
            
        except Exception as interviewer_error:
            print(f"❌ Autonomous Interviewer failed: {interviewer_error}")
            raise interviewer_error
        
        # Add the new question to the conversation history
        conversation_history.append({
            "question": new_ai_question,
            "answer": None,
            "timestamp": datetime.utcnow().isoformat(),
            "question_type": "follow_up"
        })
        
        # Save updated history to Redis
        try:
            history_json = json.dumps(conversation_history)
            redis_client.set(f"history:{request.session_id}", history_json, ex=3600)
            print(f"✅ Updated conversation history saved to Redis")
        except Exception as redis_error:
            print(f"⚠️  Warning: Failed to save updated history: {redis_error}")
        
        # Return the new question
        result = {
            "success": True,
            "message": "Answer processed successfully",
            "next_question": new_ai_question,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat(),
            "architecture": "autonomous_interviewer",
            "current_stage": current_stage if 'current_stage' in locals() else "unknown",
            "skill_progress": skill_progress if 'skill_progress' in locals() else "unknown"
        }
        
        print(f"🎉 Answer processing completed successfully for session {request.session_id}")
        return result
        
    except Exception as e:
        print(f"❌ Unexpected error in submit_answer: {e}")
        return {"error": f"Answer processing failed: {str(e)}"}, 500

@app.post("/api/interview/{session_id}/complete")
async def complete_interview(session_id: str):
    """
    Completes an interview session and provides comprehensive evaluation.
    """
    try:
        print(f"🏁 Completing interview session {session_id}")
        
        # Retrieve conversation history from Redis
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is required")
            redis_client = redis.from_url(redis_url)
            
            history_json = redis_client.get(f"history:{session_id}")
            if not history_json:
                return {"error": "Interview history not found. Session may have expired."}, 404
            
            conversation_history = json.loads(history_json.decode('utf-8'))
            
        except Exception as redis_error:
            print(f"❌ Failed to retrieve data from Redis: {redis_error}")
            return {"error": f"Failed to retrieve interview data: {str(redis_error)}"}, 500
        
        # Get session data
        try:
            session_tracker = SessionTracker()
            session_data = session_tracker.get_session(session_id)
            
            if not session_data:
                return {"error": "Session not found"}, 404
                
        except Exception as session_error:
            print(f"❌ Failed to get session data: {session_error}")
            return {"error": f"Failed to get session data: {str(session_error)}"}, 500
        
        # Extract Q&A pairs for evaluation
        qa_pairs = []
        for i, turn in enumerate(conversation_history):
            if turn.get("question") and turn.get("answer"):
                qa_pairs.append({
                    "question": turn["question"],
                    "answer": turn["answer"]
                })
        
        if not qa_pairs:
            return {"error": "No questions and answers found for evaluation"}, 400
        
        print(f"📊 Found {len(qa_pairs)} Q&A pairs for evaluation")
        
        # Evaluate each answer using the evaluation agent
        evaluations = []
        skills_to_assess = session_data.get("skills", ["Problem Solving", "Communication", "Technical Knowledge"])
        
        for qa in qa_pairs:
            print(f"🔍 Evaluating Q: {qa['question'][:50]}...")
            evaluation = evaluate_answer(qa["answer"], qa["question"], skills_to_assess)
            evaluations.append({
                "question": qa["question"],
                "answer": qa["answer"],
                "evaluation": evaluation
            })
        
        # Calculate overall scores
        all_scores = []
        for eval_data in evaluations:
            if "evaluation" in eval_data and "scores" in eval_data["evaluation"]:
                scores = eval_data["evaluation"]["scores"]
                for skill, score_data in scores.items():
                    if isinstance(score_data, dict) and "score" in score_data:
                        all_scores.append(score_data["score"])
        
        overall_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        
        # Generate comprehensive feedback
        overall_summary = f"Interview completed with {len(qa_pairs)} questions. Overall performance score: {overall_score}/5"
        
        # Prepare detailed feedback structure
        feedback_data = {
            "overall_score": overall_score,
            "overall_summary": overall_summary,
            "questions_evaluated": len(qa_pairs),
            "skills_assessed": skills_to_assess,
            "detailed_evaluations": evaluations,
            "session_id": session_id,
            "role": session_data.get("role"),
            "seniority": session_data.get("seniority"),
            "completed_at": datetime.now().isoformat()
        }
        
        # Mark session as completed
        session_tracker.update_session(session_id, {"status": "completed"})
        
        print(f"✅ Interview completion and evaluation finished for session {session_id}")
        return {"success": True, "data": feedback_data}
        
    except Exception as e:
        print(f"❌ Unexpected error in complete_interview: {e}")
        return {"error": f"Interview completion failed: {str(e)}"}, 500

@app.get("/api/interview/{session_id}/status")
async def get_interview_status(session_id: str):
    """
    Gets the current status of an interview session.
    """
    try:
        print(f"📊 Getting status for interview session {session_id}")
        
        # Retrieve data from Redis
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is required")
            redis_client = redis.from_url(redis_url)
            
            # Get the history
            history_json = redis_client.get(f"history:{session_id}")
            if not history_json:
                return {"error": "Interview history not found. Session may have expired."}, 404
            
            interview_history = json.loads(history_json.decode('utf-8'))
            
        except Exception as redis_error:
            print(f"❌ Failed to retrieve data from Redis: {redis_error}")
            return {"error": f"Failed to retrieve interview data: {str(redis_error)}"}, 500
        
        # Get session state from session tracker
        try:
            session_tracker = SessionTracker()
            session_data = session_tracker.get_session(session_id)
            
            if not session_data:
                return {"error": "Session not found"}, 404
                
        except Exception as session_error:
            print(f"❌ Failed to get session data: {session_error}")
            return {"error": f"Failed to get session data: {str(session_error)}"}, 500
        
        # Calculate progress
        questions_asked = len([qa for qa in interview_history if qa.get("question")])
        questions_answered = len([qa for qa in interview_history if qa.get("answer") is not None])
        
        # Prepare response
        status_data = {
            "session_id": session_id,
            "role": session_data.get("role"),
            "seniority": session_data.get("seniority"),
            "skill": session_data.get("skill"),
            "questions_asked": questions_asked,
            "questions_answered": questions_answered,
            "status": session_data.get("status", "in_progress"),
            "current_stage": session_data.get("current_stage"),
            "skill_progress": session_data.get("skill_progress"),
            "start_time": session_data.get("start_time")
        }
        
        print(f"✅ Interview status retrieved successfully for session {session_id}")
        return status_data
        
    except Exception as e:
        print(f"❌ Unexpected error in get_interview_status: {e}")
        return {"error": f"Failed to get interview status: {str(e)}"}, 500

# --- Startup Event Handler ---
@app.on_event("startup")
async def startup_event():
    """Run startup checks when the FastAPI app starts"""
    print("🚀 PrepAI Autonomous Interviewer Backend Starting Up...")
    print("✅ Service is ready to serve requests!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
