# PrepAI-Prototype System Evaluation Report
## For AI Evaluation Experts

**Document Version:** 1.0  
**Date:** August 2025  
**System:** PrepAI-Prototype - AI-Powered Interview Preparation Platform  
**Target Audience:** AI Evaluation Researchers and Practitioners  

---

## Executive Summary

PrepAI-Prototype is an autonomous AI-powered interview preparation system that uses Google's Gemini 2.0 Flash model to conduct realistic mock interviews. The system features a two-loop architecture with autonomous interviewers, session tracking, and basic evaluation capabilities. This report provides comprehensive technical details to enable AI evaluation experts to assess the current system and recommend optimal evaluation strategies.

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   PostgreSQL    │
│   (HTML/JS)     │◄──►│   Backend        │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Redis Cache    │
                       │   (Sessions)     │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Gemini 2.0     │
                       │   AI API         │
                       └──────────────────┘
```

### 1.2 Core Components
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: FastAPI (Python 3.11+)
- **AI Engine**: Google Gemini 2.0 Flash (Experimental)
- **Session Management**: Redis-based session tracking
- **Data Persistence**: PostgreSQL with SQLAlchemy ORM
- **Deployment**: Render.com with auto-deployment

---

## 2. AI Agent Architecture

### 2.1 Autonomous Interviewer (`agents/autonomous_interviewer.py`)

#### Core Functionality
- **Single LLM Decision Making**: One unified call handles analysis, decision-making, and question generation
- **Temperature Control**: Configurable creativity levels (0.0-1.0) for different interview phases
- **Autonomous Progression**: Self-directed interview flow based on candidate performance

#### Key Methods
```python
def conduct_interview_turn(self, role, seniority, skill, interview_stage, 
                          conversation_history, session_context) -> Dict[str, Any]
def get_initial_question(self, role, seniority, skill, session_context) -> Dict[str, Any]
def _build_prompt(self, role, seniority, skill, interview_stage, 
                  conversation_history, session_context) -> str
```

#### Interview Stages
1. **Problem Understanding**: Initial problem comprehension
2. **Solution Design**: Approach and methodology
3. **Technical Depth**: Knowledge and reasoning
4. **Trade-offs & Constraints**: Real-world considerations
5. **Implementation**: Practical execution
6. **Adaptation**: Handling changes and challenges

#### Seniority Calibration
- **Junior**: Feature-level problems with clear boundaries
- **Senior**: Product-level problems requiring strategic thinking
- **Staff+**: Business-unit level problems with multiple stakeholders

### 2.2 Session Tracker (`agents/session_tracker.py`)

#### Session Management
- **Redis-based Storage**: 1-hour expiry, 20-turn conversation limit
- **Real-time State**: Live interview progression tracking
- **Context Preservation**: Role, seniority, skill, and progress tracking

#### Key Data Structures
```python
session_data = {
    "session_id": str,
    "role": str,
    "seniority": str,
    "skill": str,
    "start_time": float,
    "current_stage": str,
    "skill_progress": str,  # "not_started", "beginner", "intermediate", "advanced", "expert"
    "conversation_history": List[Dict],
    "interview_state": Dict
}
```

### 2.3 Evaluation Engine (`agents/evaluation.py`)

#### Current Implementation
- **Basic Scoring**: 1-5 scale for individual skills
- **Skill-based Assessment**: Evaluates specific skills against questions
- **Feedback Generation**: Constructive feedback for each skill
- **Overall Scoring**: Average of individual skill scores

#### Evaluation Prompt Structure
```python
prompt = f"""You are an expert FAANG interviewer. Your job is to evaluate the candidate's answer impartially.

Question Asked: {question}
Candidate's Answer: {answer}
Skills to Assess: {', '.join(skills_to_assess)}

Instructions:
1. Evaluate ONLY the skills listed above
2. Use a 1-5 scoring system
3. Provide specific, constructive feedback for each skill
4. Calculate an overall score (average of individual skill scores)
5. Return ONLY a valid JSON object with exact structure
"""
```

---

## 3. Data Models and Storage

### 3.1 Database Schema (`models.py`)

#### Core Tables
```python
class InterviewSession(Base):
    id: Integer (Primary Key)
    session_id: String (Unique)
    user_id: Integer
    role: String
    seniority: String
    skill: String
    created_at: DateTime
    started_at: DateTime
    completed_at: DateTime
    status: String
    final_stage: String
    final_skill_progress: String
    total_questions: Integer
    total_responses: Integer

class SessionState(Base):
    id: Integer (Primary Key)
    session_id: String (Unique)
    final_stage: String
    final_skill_progress: String
    final_conversation_history: Text (JSON)
    total_turns: Integer
    total_response_time_ms: Integer
    interview_completed_at: DateTime

class UserResponse(Base):
    id: Integer (Primary Key)
    session_id: String
    question_text: Text
    answer_text: Text
    response_length: Integer
    response_time_seconds: Integer
    created_at: DateTime
```

### 3.2 Redis Session Storage
- **Key Format**: `session:{session_id}`
- **Expiry**: 1 hour (3600 seconds)
- **Data Structure**: JSON-serialized session objects
- **Memory Management**: Automatic cleanup of expired sessions

---

## 4. AI Model Configuration

### 4.1 Gemini 2.0 Flash Configuration
```python
# Model: gemini-2.0-flash-exp (Experimental)
# Temperature Control: 0.0-1.0 range
# API Integration: Google Generative AI Python SDK
# Error Handling: Fallback responses for API failures
```

### 4.2 Temperature Strategy
- **Initial Questions**: 0.7 (Higher creativity for case study generation)
- **Follow-up Questions**: 0.6 (Balanced creativity and consistency)
- **Evaluation**: 0.3 (Consistent, focused scoring)

---

## 5. Current Evaluation Capabilities

### 5.1 Strengths
- **Real-time Assessment**: Live evaluation during interviews
- **Skill-specific Scoring**: Targeted evaluation of specific competencies
- **Structured Feedback**: Consistent feedback format across all evaluations
- **Performance Tracking**: Session-level progress monitoring

### 5.2 Limitations
- **Basic Scoring Scale**: Only 1-5 scale with limited granularity
- **Single Evaluation Method**: Relies solely on LLM-based assessment
- **No Validation**: No human expert validation or calibration
- **Limited Metrics**: Basic scores without advanced analytics
- **No Reliability Testing**: No consistency or reproducibility measures

### 5.3 Current Evaluation Flow
```
User Response → Gemini Evaluation → Score Calculation → Feedback Generation
     ↓              ↓                    ↓                ↓
Response Text → Skill Assessment → 1-5 Scoring → Constructive Feedback
```

---

## 6. Technical Infrastructure

### 6.1 API Endpoints
```python
# Health Check
GET /health

# Interview Management
POST /api/start-interview
POST /api/submit-answer
GET /api/interview-status/{session_id}
```

### 6.2 Performance Metrics
- **Response Latency**: Measured in milliseconds per API call
- **Session Duration**: Total interview time tracking
- **Turn Count**: Number of conversation exchanges
- **Error Rates**: API failure and fallback usage

### 6.3 Scalability Considerations
- **Redis Expiry**: Automatic session cleanup
- **Database Indexing**: Optimized queries on session_id
- **API Rate Limiting**: Not currently implemented
- **Connection Pooling**: Basic database connection management

---

## 7. Evaluation Data Available

### 7.1 Raw Data Sources
1. **Conversation History**: Complete interview transcripts
2. **Response Timing**: Per-response latency measurements
3. **Skill Progress**: Stage-by-stage progression tracking
4. **Interview States**: Dynamic state changes during sessions
5. **Performance Metrics**: Latency, turn count, duration

### 7.2 Data Quality Characteristics
- **Real-time Collection**: Live data during interviews
- **Structured Format**: JSON-based data storage
- **Temporal Tracking**: Timestamp-based progression
- **Context Preservation**: Role, seniority, and skill context

### 7.3 Data Limitations
- **Session Expiry**: 1-hour Redis TTL limits historical analysis
- **No Persistent Storage**: Real-time data only, no long-term retention
- **Limited Metadata**: Basic response information without rich context
- **No Cross-Session Analysis**: Individual session isolation

---

## 8. Current Testing Infrastructure

### 8.1 Test Coverage
- **Unit Tests**: Basic functionality testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Latency and response time measurement
- **Render Tests**: Production environment validation

### 8.2 Testing Tools
```bash
# Test Execution
./run_tests.sh                    # Full test suite
./run_tests.sh unit              # Unit tests only
./run_tests.sh integration       # Integration tests
./run_tests.sh performance       # Performance tests
./run_tests.sh render            # Production tests
```

---

---

## Appendix A: Technical Specifications

### A.1 System Requirements
- **Python**: 3.11+
- **Database**: PostgreSQL 12+
- **Cache**: Redis 6+
- **AI API**: Google Gemini 2.0 Flash
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0+

### A.2 API Specifications
- **Base URL**: https://prepai-api.onrender.com
- **Authentication**: None (public API)
- **Rate Limiting**: Not implemented
- **CORS**: Configured for multiple origins

### A.3 Data Formats
- **Request/Response**: JSON
- **Session Storage**: JSON in Redis
- **Database**: PostgreSQL with JSON columns
- **Logging**: Console-based with structured output

---

**Document Prepared By:** AI Assistant  
**Review Date:** December 2024  
**Next Review:** January 2025  

For questions or additional information, please refer to the project repository or contact the development team.
