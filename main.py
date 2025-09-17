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
    from agents.pre_interview_planner import PreInterviewPlanner
    from agents.interview_evaluator import InterviewEvaluator
    from models import persist_complete_interview, persist_interview_session
    print("✅ Autonomous interviewer components imported successfully")
except Exception as e:
    print(f"❌ Failed to import autonomous interviewer components: {e}")
    raise

# --- FastAPI App Initialization ---
app = FastAPI(title="PrepAI Autonomous Interviewer API")

# --- CORS Middleware Configuration ---
origins = [
    "https://akshayy-notbot.github.io",    # Keep during transition
    "https://doaiprep.xyz",               # New custom domain
    "https://www.doaiprep.xyz",           # www version
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

class EvaluateInterviewRequest(BaseModel):
    role: str
    seniority: str
    skills: List[str]
    transcript: List[Dict[str, Any]]

# --- Root Endpoint ---
@app.get("/")
@app.head("/")
async def root():
    """Root endpoint for health checks and service discovery"""
    return {
        "message": "PrepAI Autonomous Interviewer API",
        "status": "running",
        "health_check": "/health",
        "docs": "/docs"
    }

# --- Evaluation Endpoint ---
@app.post("/api/evaluate-interview")
async def evaluate_interview(request: EvaluateInterviewRequest):
    """
    Evaluate an interview transcript and generate feedback.
    """
    try:
        print(f"🔍 Evaluating interview for {request.role} role ({request.seniority} level)")
        
        # Extract Q&A pairs from transcript
        qa_pairs = []
        for item in request.transcript:
            if item.get("question") and item.get("answer"):
                qa_pairs.append({
                    "question": item["question"],
                    "answer": item["answer"]
                })
        
        if not qa_pairs:
            raise HTTPException(status_code=400, detail="No valid question-answer pairs found in transcript")
        
        print(f"📊 Found {len(qa_pairs)} Q&A pairs for evaluation")
        
        # Evaluate each answer using the evaluation agent
        evaluations = []
        skills_to_assess = request.skills if request.skills else ["Problem Solving", "Communication", "Technical Knowledge"]
        
        for i, qa in enumerate(qa_pairs):
            print(f"🔍 Evaluating Q: {qa['question'][:50]}...")
            
            # Get conversation history up to this point for context
            conversation_history = qa_pairs[:i] if i > 0 else []
            
            # Create role context for better evaluation
            role_context = {
                "role": request.role,
                "seniority": request.seniority
            }
            
            evaluation = evaluate_answer(qa["answer"], qa["question"], skills_to_assess, conversation_history, role_context)
            evaluations.append({
                "question": qa["question"],
                "answer": qa["answer"],
                "evaluation": evaluation
            })
        
        # Calculate overall scores and extract feedback
        all_scores = []
        strengths = []
        improvements = []
        category_feedback = {}
        combined_scores = {}  # Aggregate scores across all questions
        
        for eval_data in evaluations:
            if "evaluation" in eval_data and "scores" in eval_data["evaluation"]:
                scores = eval_data["evaluation"]["scores"]
                
                # Aggregate scores across all questions for each skill
                for skill, score_data in scores.items():
                    if isinstance(score_data, dict) and "score" in score_data:
                        score = score_data["score"]
                        all_scores.append(score)
                        
                        # Initialize skill tracking if not exists
                        if skill not in combined_scores:
                            combined_scores[skill] = {
                                "scores": [],
                                "feedback": []
                            }
                        
                        # Collect all scores and feedback for this skill
                        combined_scores[skill]["scores"].append(score)
                        if "feedback" in score_data:
                            combined_scores[skill]["feedback"].append(score_data["feedback"])
                        
                        # Categorize feedback for strengths/improvements
                        feedback_text = score_data.get("feedback", "")
                        if score >= 4:
                            strengths.append(f"{skill}: {feedback_text}")
                        elif score <= 2:
                            improvements.append(f"{skill}: {feedback_text}")
                        
                        category_feedback[skill] = feedback_text
        
        # Calculate average scores for each skill
        skill_scores = {}
        for skill, data in combined_scores.items():
            if data["scores"]:
                avg_score = sum(data["scores"]) / len(data["scores"])
                # Get the most recent feedback for this skill
                latest_feedback = data["feedback"][-1] if data["feedback"] else f"Average performance in {skill}"
                
                skill_scores[skill] = {
                    "score": round(avg_score, 1),
                    "feedback": latest_feedback
                }
        
        # Calculate overall score on 0-5 scale (keep original scale)
        overall_score_5_scale = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        
        # Generate response matching feedback page expectations
        feedback_response = {
            "overall_score": overall_score_5_scale,  # Use 0-5 scale for frontend
            "overall_feedback": f"Your interview performance shows {'strong' if overall_score_5_scale >= 4.0 else 'good' if overall_score_5_scale >= 3.0 else 'developing'} skills in {request.role} for {request.seniority} level.",
            "scores": skill_scores,  # Individual skill scores for the UI
            "strengths": strengths[:3] if strengths else ["Good communication throughout the interview"],
            "improvements": improvements[:3] if improvements else ["Continue practicing to build confidence"],
            "category_feedback": category_feedback,
            "recommendations": [
                f"Focus on practicing {request.skills[0] if request.skills else 'core skills'} with real-world examples",
                "Review industry best practices and current trends",
                "Practice articulating your thought process clearly"
            ],
            "questions_evaluated": len(qa_pairs),
            "role": request.role,
            "seniority": request.seniority,
            "skills_assessed": skills_to_assess,
            "next_steps": [
                "Practice similar questions to build confidence",
                "Review your answers and identify areas for improvement",
                "Consider mock interviews with different scenarios"
            ],
            "detailed_evaluations": evaluations  # Include full evaluations with ideal responses
        }
        
        print(f"✅ Evaluation completed successfully with overall score: {overall_score_5_scale}/5")
        print(f"📊 Skill breakdown: {skill_scores}")
        return feedback_response
        
    except Exception as e:
        print(f"❌ Error in evaluate_interview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate interview: {str(e)}")

# --- Debug Endpoint ---
@app.post("/api/debug-request")
async def debug_request(request: dict):
    """Debug endpoint to see what the frontend is actually sending."""
    print("🔍 DEBUG: Received request")
    print(f"📦 Request type: {type(request)}")
    print(f"📦 Request keys: {list(request.keys()) if isinstance(request, dict) else 'Not a dict'}")
    print(f"📦 Request content: {json.dumps(request, indent=2)}")
    
    return {
        "success": True,
        "received_data": request,
        "message": "Debug endpoint - request received successfully"
    }

# --- Enhanced Interview Evaluation Endpoint ---
@app.post("/api/evaluate-interview-enhanced")
async def evaluate_interview_enhanced(request: EvaluateInterviewRequest):
    """
    Enhanced interview evaluation using the new InterviewEvaluator.
    Provides comprehensive dimension-by-dimension assessment with signal evidence.
    """
    try:
        # Validate required fields
        if not request.role or not request.seniority:
            raise HTTPException(status_code=422, detail="Role and seniority are required")
        
        if not request.transcript or len(request.transcript) == 0:
            raise HTTPException(status_code=422, detail="Transcript is required and cannot be empty")
        
        print(f"🔍 Enhanced evaluation for {request.role} role ({request.seniority} level)")
        print(f"📊 Skills: {request.skills}")
        print(f"📝 Transcript items: {len(request.transcript)}")
        
        # Debug: Check transcript structure
        if request.transcript:
            print(f"🔍 First transcript item keys: {list(request.transcript[0].keys())}")
            print(f"🔍 Sample transcript item: {str(request.transcript[0])[:200]}...")
        
        # Get the interview plan from the session context (if available)
        # For now, we'll create a basic plan structure
        # Get evaluation dimensions based on role and skill - no fallbacks
        if request.role == "Product Manager" and "Product Sense" in request.skills:
            evaluation_dimensions = [
                "Problem Scoping",
                "User Empathy", 
                "Business Acumen",
                "Prioritization & Trade-offs",
                "Creative Problem Solving"
            ]
        else:
            # No fallback - require proper configuration
            raise HTTPException(
                status_code=422, 
                detail=f"Evaluation dimensions not configured for role '{request.role}' with skills {request.skills}. Please configure proper evaluation criteria."
            )
        
        interview_plan = {
            "top_evaluation_dimensions": evaluation_dimensions,
            "selected_archetype": "comprehensive",
            "interview_objective": f"Assess {request.role} capabilities at {request.seniority} level",
            "seniority_criteria": {
                "junior": "Basic understanding and application",
                "mid": "Structured approach with some depth", 
                "senior": "Strategic thinking and comprehensive analysis",
                "staff+": "Innovative approaches and thought leadership"
            },
            "good_vs_great_examples": {
                "good": "Competent, covers basics, logical approach",
                "great": "Insightful, innovative, considers edge cases, shows deep understanding"
            }
        }
        
        # Convert transcript to conversation history format
        conversation_history = []
        for i, item in enumerate(request.transcript):
            try:
                if item.get("question"):
                    conversation_history.append({
                        "role": "interviewer",
                        "content": str(item["question"]),
                        "timestamp": item.get("timestamp", "")
                    })
                if item.get("answer") is not None and item.get("answer") != "":
                    conversation_history.append({
                        "role": "candidate",
                        "content": str(item["answer"]),
                        "timestamp": item.get("timestamp", "")
                    })
            except Exception as item_error:
                print(f"⚠️ Error processing transcript item {i}: {item_error}")
                print(f"📄 Problematic item: {item}")
                continue
        
        if not conversation_history:
            raise HTTPException(status_code=422, detail="No valid conversation data found in transcript")
        
        # Check if we have sufficient data for evaluation
        candidate_responses = [item for item in conversation_history if item["role"] == "candidate"]
        if len(candidate_responses) == 0:
            raise HTTPException(status_code=422, detail="No candidate responses found in transcript")
        
        print(f"📊 Found {len(candidate_responses)} candidate responses for evaluation")
        
        # Create signal evidence from the transcript
        signal_evidence = {}
        for skill in interview_plan["top_evaluation_dimensions"]:
            signal_evidence[skill] = {
                "positive_signals": [],
                "areas_for_improvement": [],
                "quotes": [],
                "confidence": "Medium"
            }
            
            # Simple signal extraction (in production, this would be more sophisticated)
            for item in request.transcript:
                if item.get("answer") and item["answer"] is not None and str(item["answer"]).strip():
                    answer = str(item["answer"]).lower()
                    if any(word in answer for word in ["think", "approach", "strategy"]):
                        signal_evidence[skill]["positive_signals"].append("Shows strategic thinking")
                    if any(word in answer for word in ["user", "customer", "need"]):
                        signal_evidence[skill]["positive_signals"].append("Demonstrates user empathy")
                    signal_evidence[skill]["quotes"].append(str(item["answer"])[:100] + "...")
        
        # Use the InterviewEvaluator for comprehensive evaluation
        try:
            evaluator = InterviewEvaluator()
            primary_skill = request.skills[0] if request.skills else "General"
            print(f"🎯 Evaluating primary skill: {primary_skill}")
            print(f"📊 Conversation history items: {len(conversation_history)}")
            print(f"🎯 Evaluation dimensions: {evaluation_dimensions}")
            
            evaluation_result = evaluator.evaluate_interview(
                role=request.role,
                seniority=request.seniority,
                skill=primary_skill,
                conversation_history=conversation_history,
                signal_evidence=signal_evidence,
                interview_plan=interview_plan
            )
            print(f"✅ Evaluation completed successfully")
            print(f"📊 Evaluation result keys: {list(evaluation_result.keys())}")
            if "overall_assessment" in evaluation_result:
                print(f"📊 Overall assessment keys: {list(evaluation_result['overall_assessment'].keys())}")
            
        except Exception as eval_error:
            print(f"❌ InterviewEvaluator failed: {eval_error}")
            print(f"📊 Debug - Conversation history: {conversation_history}")
            print(f"📊 Debug - Signal evidence keys: {list(signal_evidence.keys())}")
            raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(eval_error)}")
        
        if "error" in evaluation_result:
            raise Exception(evaluation_result["error"])
        
        # Generate human-readable summary
        summary = evaluator.generate_evaluation_summary(evaluation_result)
        
        # Return evaluation data at top level (frontend expects this structure)
        response = evaluation_result.copy()  # Start with the evaluation result
        response.update({
            "success": True,
            "summary": summary,
            "message": "Enhanced evaluation completed successfully"
        })
        
        return response
        
    except Exception as e:
        print(f"❌ Error in enhanced evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform enhanced evaluation: {str(e)}")

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
        
        # Step 1: Create interview plan using PreInterviewPlanner
        print("📋 Creating interview plan...")
        try:
            planner = PreInterviewPlanner()
            interview_plan = planner.create_interview_plan(
                role=request.role,
                skill=request.skills[0] if request.skills else "General",
                seniority=request.seniority
            )
            print(f"✅ Interview plan created with archetype: {interview_plan['selected_archetype']}")
            
        except Exception as planning_error:
            error_msg = str(planning_error)
            print(f"❌ Failed to create interview plan: {error_msg}")
            
            # Provide helpful error messages based on the error
            if "No interview playbook found" in error_msg:
                return {
                    "error": "Interview playbook not found",
                    "message": f"No interview playbook exists for {request.role} - {request.skills[0] if request.skills else 'General'} - {request.seniority}. Please ensure the playbook exists in the database.",
                    "status_code": 404
                }, 404
            elif "No evaluation dimensions found" in error_msg:
                return {
                    "error": "Incomplete playbook data",
                    "message": f"The interview playbook for {request.role} - {request.skills[0] if request.skills else 'General'} - {request.seniority} is missing evaluation dimensions. Please update the playbook.",
                    "status_code": 400
                }, 400
            elif "No interview objective found" in error_msg:
                return {
                    "error": "Incomplete playbook data",
                    "message": f"The interview playbook for {request.role} - {request.skills[0] if request.skills else 'General'} - {request.seniority} is missing interview objective. Please update the playbook.",
                    "status_code": 400
                }, 400
            else:
                return {
                    "error": "Interview planning failed",
                    "message": f"Failed to create interview plan: {error_msg}",
                    "status_code": 500
                }, 500
        
        # Step 2: Create interview session in database
        print("💾 Creating interview session...")
        try:
            session_data = {
                "session_id": session_id,
                "selected_skills": request.skills if request.skills else ["General"],  # Fixed: send as JSON array
                "role": request.role,
                "seniority": request.seniority,
                "skill": request.skills[0] if request.skills else "General",
                "selected_archetype": interview_plan["selected_archetype"],
                "generated_prompt": interview_plan["interview_prompt"],
                # Don't pass JSON fields - let SQLAlchemy use column defaults
                "playbook_id": None,
                "interview_started_at": None,
                "interview_completed_at": None
            }
            
            # Debug: Print session data to identify JSON parsing issue
            print(f"🔍 DEBUG - Session data keys and types:")
            for k, v in session_data.items():
                print(f"  {k}: {type(v)} = {repr(v)}")
            
            persist_interview_session(session_data)
            
            print(f"✅ Interview session created and persisted")
            
        except Exception as session_error:
            print(f"❌ Failed to create session: {session_error}")
            return {"error": f"Failed to create interview session: {session_error}"}, 500
        
        # Step 3: Initialize Session Tracker and Autonomous Interviewer
        try:
            session_tracker = SessionTracker()
            autonomous_interviewer = AutonomousInterviewer()
            
            # Create new session with simplified structure
            session_tracker.create_session(
                session_id=session_id,
                role=request.role,
                seniority=request.seniority,
                skill=request.skills[0] if request.skills else "General"
            )
            
            print(f"✅ Session tracker initialized successfully")
            
        except Exception as tracker_error:
            print(f"❌ Failed to initialize session tracker: {tracker_error}")
            # Continue anyway since we have the main session in database
        
        # Step 4: Generate the First Question using the interview plan
        print("🎭 Generating first interview question using interview plan...")
        
        try:
            # Get initial question from autonomous interviewer using the plan
            first_question_result = autonomous_interviewer.get_initial_question(
                role=request.role,
                seniority=request.seniority,
                skill=request.skills[0] if request.skills else "General",
                session_context={"interview_plan": interview_plan},
                interview_plan=interview_plan
            )
            
            if not first_question_result.get("response_text"):
                raise Exception("Autonomous Interviewer failed to generate opening statement")
            
            opening_statement = first_question_result["response_text"]
            print(f"✅ Opening statement generated: {opening_statement[:100]}...")
            
            # Update session with initial state
            if 'session_tracker' in locals():
                session_tracker.update_interview_state(session_id, first_question_result["interview_state"])
            
        except Exception as interviewer_error:
            print(f"❌ Autonomous Interviewer failed: {interviewer_error}")
            return {"error": f"Failed to generate opening statement: {interviewer_error}"}, 500
        
        # Create and Save the History with AI reasoning
        interview_history = [
            {
                "question": opening_statement,
                "answer": None,
                "timestamp": datetime.utcnow().isoformat(),
                "question_type": "opening",
                "ai_reasoning": first_question_result.get("chain_of_thought", []),
                "interview_state": first_question_result.get("interview_state", {}),
                "response_latency_ms": first_question_result.get("latency_ms", 0)
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
        
        # Return the Response with interview plan
        response_data = {
            "session_id": session_id,
            "opening_statement": opening_statement,
            "status": "started",
            "role": request.role,
            "seniority": request.seniority,
            "skill": request.skills[0] if request.skills else "General",
            "estimated_duration_minutes": 45,  # Default duration
            "message": "Interview started successfully with pre-interview planning",
            "interview_plan": {
                "archetype": interview_plan["selected_archetype"],
                "objective": interview_plan.get("evaluation_criteria", {}).get("seniority_adjustments", {}).get(request.seniority.lower(), "Standard evaluation"),
                "evaluation_dimensions": list(interview_plan.get("signal_map", {}).keys())
            }
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
            
            # Get the interview plan from the session context
            interview_plan = session_tracker.get_session_context(request.session_id).get("interview_plan", {})
            
            # Process the user response using enhanced autonomous interviewer with signal tracking
            interviewer_result = autonomous_interviewer.conduct_interview_turn(
                role=session_data["role"],
                seniority=session_data["seniority"],
                skill=session_data["skill"],
                interview_stage=session_data["current_stage"],
                conversation_history=ai_conversation_history,
                session_context=session_tracker.get_session_context(request.session_id),
                interview_plan=interview_plan
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
            
            # Enhanced completion check based on AI assessment
            completion_assessment = interviewer_result.get("completion_assessment", {})
            
            if (completion_assessment.get("should_complete") and 
                completion_assessment.get("completion_confidence") in ["High", "Medium"]):
                
                print("🎉 Interview completed by AI-driven assessment!")
                print(f"📊 Completion reason: {completion_assessment.get('reason', 'AI determined sufficient evidence collected')}")
                print(f"📈 Evidence summary: {completion_assessment.get('evidence_summary', 'N/A')}")
                print(f"🎯 Coverage percentage: {completion_assessment.get('coverage_percentage', 'N/A')}")
                
                # Mark session as completed with AI decision
                session_tracker.update_session(request.session_id, {
                    "status": "completed_by_ai",
                    "completion_reason": completion_assessment.get("reason"),
                    "final_coverage": completion_assessment.get("evidence_summary")
                })
                
                # Return completion response instead of continuing
                return {
                    "success": True,
                    "interview_completed": True,
                    "completion_reason": completion_assessment.get("reason"),
                    "evidence_summary": completion_assessment.get("evidence_summary"),
                    "coverage_percentage": completion_assessment.get("coverage_percentage"),
                    "next_question": new_ai_question,  # This should be the completion message
                    "session_id": request.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "architecture": "autonomous_interviewer_completion",
                    "ai_completion_assessment": completion_assessment
                }
            
            # Fallback: Check old completion criteria as backup
            elif skill_progress in ["expert", "advanced"] and len(conversation_history) > 15:
                print("🎉 Interview completed by fallback criteria (expert level + 15+ questions)")
                session_tracker.update_session(request.session_id, {"status": "completed_fallback"})
            
        except Exception as interviewer_error:
            print(f"❌ Autonomous Interviewer failed: {interviewer_error}")
            raise interviewer_error
        
        # Add the new question to conversation history with AI reasoning
        conversation_history.append({
            "question": new_ai_question,
            "answer": None,
            "timestamp": datetime.utcnow().isoformat(),
            "question_type": "follow_up",
            "ai_reasoning": interviewer_result.get("chain_of_thought", []),
            "interview_state": interviewer_result.get("interview_state", {}),
            "completion_assessment": interviewer_result.get("completion_assessment", {}),
            "response_latency_ms": interviewer_result.get("latency_ms", 0)
        })
        
        # Save updated history to Redis
        try:
            history_json = json.dumps(conversation_history)
            redis_client.set(f"history:{request.session_id}", history_json, ex=3600)
            print(f"✅ Updated conversation history saved to Redis")
        except Exception as redis_error:
            print(f"⚠️  Warning: Failed to save updated history: {redis_error}")
        
        # Return the new question with completion assessment
        result = {
            "success": True,
            "message": "Answer processed successfully",
            "next_question": new_ai_question,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat(),
            "architecture": "autonomous_interviewer",
            "current_stage": current_stage if 'current_stage' in locals() else "unknown",
            "skill_progress": skill_progress if 'skill_progress' in locals() else "unknown",
            "completion_assessment": interviewer_result.get("completion_assessment", {}),
            "interview_completed": False
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
        
        # Persist the complete interview data to the database
        try:
            # Prepare conversation history with complete data
            complete_conversation_history = []
            for turn in conversation_history:
                turn_data = {
                    "question": turn.get("question"),
                    "answer": turn.get("answer"),
                    "timestamp": turn.get("timestamp"),
                    "question_type": turn.get("question_type", "follow_up")
                }
                complete_conversation_history.append(turn_data)
            
            # Prepare final state data
            final_state = {
                "final_stage": session_data.get("current_stage", "unknown"),
                "final_skill_progress": session_data.get("skill_progress", "unknown"),
                "total_response_time_ms": 0,  # Could be calculated from timestamps
                "average_score": overall_score,
                "completion_time": datetime.now().isoformat(),
                "ai_reasoning": []  # Could be enhanced to capture AI reasoning
            }
            
            # Persist to database
            persist_complete_interview(
                session_id=session_id,
                session_data=session_data,
                conversation_history=complete_conversation_history,
                evaluations=evaluations,
                final_state=final_state
            )
            print(f"✅ Interview data persisted to database for session {session_id}")
        except Exception as db_error:
            print(f"❌ Failed to persist interview data to database: {db_error}")
            # Continue with returning feedback data even if persistence fails
        
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

# --- Prompt Evaluation Endpoints ---
from agents.prompt_evaluator import prompt_evaluator

@app.get("/api/prompt-evaluation/overview")
async def get_prompt_evaluation_overview(hours: int = 24):
    """Get overview of prompt evaluation metrics"""
    try:
        analysis = prompt_evaluator.get_prompt_effectiveness_analysis(hours)
        return analysis
    except Exception as e:
        print(f"❌ Error in get_prompt_evaluation_overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get overview: {str(e)}")

@app.get("/api/prompt-evaluation/components")
async def get_prompt_evaluation_components():
    """Get list of available components"""
    try:
        # Get unique components from database
        executions = prompt_evaluator.get_executions(limit=1000)
        components = list(set(execution.component for execution in executions))
        return components
    except Exception as e:
        print(f"❌ Error in get_prompt_evaluation_components: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get components: {str(e)}")

@app.get("/api/prompt-evaluation/component/{component}")
async def get_component_analysis(component: str, hours: int = 24):
    """Get detailed analysis for a specific component"""
    try:
        analysis = prompt_evaluator.analyze_component_performance(component, hours)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Component {component} not found")
        return analysis
    except Exception as e:
        print(f"❌ Error in get_component_analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze component: {str(e)}")

@app.get("/api/prompt-evaluation/executions")
async def get_prompt_executions(limit: int = 100, success_only: bool = None):
    """Get recent prompt executions"""
    try:
        executions = prompt_evaluator.get_executions(limit=limit, success_only=success_only)
        # Convert to serializable format
        serializable_executions = []
        for execution in executions:
            serializable_executions.append({
                "execution_id": execution.execution_id,
                "timestamp": execution.timestamp,
                "component": execution.component,
                "method": execution.method,
                "prompt_type": execution.prompt_type,
                "input_data": execution.input_data,
                "prompt_text": execution.prompt_text,
                "output_data": execution.output_data,
                "response_text": execution.response_text,
                "latency_ms": execution.latency_ms,
                "token_count": execution.token_count,
                "success": execution.success,
                "error_message": execution.error_message,
                "session_id": execution.session_id,
                "user_id": execution.user_id,
                "role": execution.role,
                "seniority": execution.seniority,
                "skill": execution.skill
            })
        return serializable_executions
    except Exception as e:
        print(f"❌ Error in get_prompt_executions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get executions: {str(e)}")

@app.get("/api/prompt-evaluation/session/{session_id}")
async def get_session_analysis(session_id: str):
    """Get analysis for a specific interview session"""
    try:
        analysis = prompt_evaluator.get_session_analysis(session_id)
        return analysis
    except Exception as e:
        print(f"❌ Error in get_session_analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze session: {str(e)}")

@app.get("/api/prompt-evaluation/export")
async def export_prompt_executions(hours: int = 24):
    """Export prompt executions to JSON"""
    try:
        success = prompt_evaluator.export_executions_to_json("prompt_executions_export.json", hours)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to export executions")
        
        # Return the file
        from fastapi.responses import FileResponse
        return FileResponse("prompt_executions_export.json", media_type="application/json")
        
    except Exception as e:
        print(f"❌ Error in export_prompt_executions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export: {str(e)}")

@app.post("/api/prompt-evaluation/clear")
async def clear_prompt_evaluation_database():
    """Clear all prompt evaluation data (for debugging)"""
    try:
        import sqlite3
        import os
        
        db_path = "prompt_evaluations.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            # Reinitialize the database
            prompt_evaluator._init_database()
        
        return {"message": "Database cleared successfully"}
        
    except Exception as e:
        print(f"❌ Error in clear_prompt_evaluation_database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")

@app.post("/api/prompt-evaluation/test")
async def test_prompt_capture():
    """Test prompt capture functionality"""
    try:
        execution_id = prompt_evaluator.capture_execution(
            component="test",
            method="test_method",
            prompt_type="test",
            input_data={"test": "data"},
            prompt_text="Test prompt",
            output_data={"test": "response"},
            response_text="Test response",
            latency_ms=100.0,
            success=True
        )
        return {"execution_id": execution_id, "message": "Test prompt captured successfully"}
        
    except Exception as e:
        print(f"❌ Error in test_prompt_capture: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test prompt capture: {str(e)}")

@app.post("/api/prompt-evaluation/generate-test-data")
async def generate_test_prompt_data():
    """Generate sample test data for demonstration"""
    try:
        import random
        import time
        
        # Generate some sample executions
        components = ["autonomous_interviewer", "evaluation", "pre_interview_planner"]
        methods = ["conduct_interview_turn", "evaluate_answer", "create_interview_plan"]
        prompt_types = ["interview_question", "evaluation", "planning"]
        roles = ["Product Manager", "Software Engineer", "Data Analyst"]
        seniorities = ["Junior", "Mid", "Senior", "Manager"]
        skills = ["System Design", "Problem Solving", "Communication"]
        
        count = 0
        for i in range(20):
            try:
                execution_id = prompt_evaluator.capture_execution(
                    component=random.choice(components),
                    method=random.choice(methods),
                    prompt_type=random.choice(prompt_types),
                    input_data={
                        "role": random.choice(roles),
                        "seniority": random.choice(seniorities),
                        "skill": random.choice(skills),
                        "test_data": True
                    },
                    prompt_text=f"Test prompt {i+1}",
                    output_data={"test": "response", "iteration": i+1},
                    response_text=f"Test response {i+1}",
                    latency_ms=random.uniform(50, 500),
                    success=random.random() > 0.1,  # 90% success rate
                    error_message="Test error" if random.random() <= 0.1 else None,
                    session_id=f"test_session_{random.randint(1, 5)}",
                    role=random.choice(roles),
                    seniority=random.choice(seniorities),
                    skill=random.choice(skills)
                )
                count += 1
                time.sleep(0.01)  # Small delay to ensure unique timestamps
                
            except Exception as e:
                print(f"Failed to generate test execution {i+1}: {e}")
                continue
        
        return {"count": count, "message": f"Generated {count} test prompt executions"}
        
    except Exception as e:
        print(f"❌ Error in generate_test_prompt_data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate test data: {str(e)}")

# --- Startup Event Handler ---
@app.on_event("startup")
async def startup_event():
    """Run startup checks when the FastAPI app starts"""
    print("🚀 PrepAI Autonomous Interviewer Backend Starting Up...")
    
    # Run comprehensive startup checks including database migration verification
    try:
        from startup import run_startup_checks
        success = run_startup_checks()
        if success:
            print("✅ All startup checks passed! Service is ready to serve requests!")
        else:
            print("⚠️  Some startup checks failed, but service will continue...")
    except Exception as e:
        print(f"⚠️  Startup checks failed with error: {e}")
        print("Service will continue, but some features may not work properly...")
    
    print("✅ Service is ready to serve requests!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
