# AGENTS.md

A comprehensive guide for AI coding agents working on the PrepAI-Prototype project.

## Project Overview

PrepAI-Prototype is an AI-powered interview preparation platform that uses Google's Gemini AI to conduct realistic mock interviews. The system features a two-loop architecture with autonomous interviewers, session tracking, and real-time evaluation.

**Key Components:**
- **Autonomous Interviewer**: AI agent that conducts interviews and adapts questions
- **Session Tracker**: Manages interview sessions and conversation history
- **Evaluation Engine**: Assesses responses and provides feedback
- **FastAPI Backend**: REST API with PostgreSQL database
- **Celery Task Queue**: Background job processing with Redis

## Development Environment Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Redis server
- Google Gemini API key

### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd PrepAI-Prototype

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp env.example .env
# Edit .env with your actual values

# Database setup
python migrate_database.py
python seed.py

# Start services
uvicorn main:app --reload  # Backend API
celery -A celery_app worker --loglevel=info  # Task queue
```

## Code Style & Standards

### Python Code
- **Follow KISS principle**: Keep It Simple, Stupid
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings for all public functions and classes

### AI Agent Development
- Keep agent logic modular and testable
- Use dependency injection for external services
- Implement proper error handling and logging
- Follow the existing pattern in `agents/` directory

### Database Models
- Use SQLAlchemy 2.0+ syntax
- Define clear relationships between models
- Include proper indexes for performance
- Use Pydantic for data validation

## Testing Strategy

### Test Structure
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Performance Tests**: Benchmark critical operations
- **Render Tests**: Test against production deployment

### Running Tests
```bash
# Run all tests
./run_tests.sh

# Run specific test types
./run_tests.sh unit          # Quick component testing
./run_tests.sh integration   # Component interaction testing
./run_tests.sh performance   # Performance benchmarking
./run_tests.sh render        # Production environment testing

# Direct pytest usage
python -m pytest tests/ -v
python -m pytest tests/ -k "unit" --tb=short
```

### Testing Guidelines
- **Always run tests before committing**: `./run_tests.sh`
- **Write tests for new features**: Even if not explicitly requested
- **Test AI agent responses**: Ensure consistent behavior
- **Mock external services**: Google API, database connections
- **Test error conditions**: Invalid inputs, network failures

## AI Agent Development

### Autonomous Interviewer
- **Location**: `agents/autonomous_interviewer.py`
- **Purpose**: Conducts interviews and adapts questions based on responses
- **Key Methods**:
  - `get_initial_question()`: Start interview with context
  - `conduct_interview_turn()`: Process responses and generate follow-ups
  - `evaluate_response()`: Assess answer quality

### Session Tracker
- **Location**: `agents/session_tracker.py`
- **Purpose**: Manages interview sessions and conversation history
- **Key Methods**:
  - `create_session()`: Initialize new interview session
  - `add_conversation_turn()`: Record user/agent interactions
  - `get_session_context()`: Retrieve session information

### Evaluation Engine
- **Location**: `agents/evaluation.py`
- **Purpose**: Assesses interview responses and provides feedback
- **Key Methods**:
  - `evaluate_response()`: Score answer quality
  - `generate_feedback()`: Provide constructive feedback

## Database Operations

### Models
- **Location**: `models.py`
- **Key Entities**: Interview sessions, responses, evaluations
- **Relationships**: Sessions → Responses → Evaluations

### Database Commands
```bash
# Create database tables
python migrate_database.py

# Seed with initial data
python seed.py

# Reset database (development)
python recreate_database.py
```

## API Development

### FastAPI Endpoints
- **Health Check**: `GET /health`
- **Start Interview**: `POST /api/start-interview`
- **Submit Answer**: `POST /api/submit-answer`
- **Interview Status**: `GET /api/interview-status/{session_id}`

### API Guidelines
- Use Pydantic models for request/response validation
- Implement proper error handling with HTTP status codes
- Add comprehensive logging for debugging
- Use async/await for database operations
- Implement rate limiting for production

## Frontend Integration

### JavaScript Files
- **Main App**: `app.js` - Core interview logic
- **Configuration**: `config.js` - API endpoints and settings
- **HTML**: `index.html` - Main interface

### Frontend Guidelines
- Keep vanilla JavaScript (no frameworks)
- Use modern ES6+ syntax
- Implement responsive design
- Handle API errors gracefully
- Provide user feedback for all actions

## Deployment & Configuration

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/db
GOOGLE_API_KEY=your_gemini_api_key
PYTHON_VERSION=3.11.9

# Optional
ENVIRONMENT=development
REDIS_URL=redis://localhost:6379
```

### Render Deployment
- **Configuration**: `render.yaml` defines deployment settings
- **Auto-deploy**: Connected to GitHub repository
- **Environment**: Production-ready with PostgreSQL and Redis

## Common Development Tasks

### Adding New Interview Types
1. Update `agents/autonomous_interviewer.py` with new role logic
2. Add role-specific prompts and evaluation criteria
3. Update frontend to include new options
4. Add tests for new functionality

### Modifying AI Behavior
1. Edit prompts in the relevant agent file
2. Test with various input scenarios
3. Ensure consistent response patterns
4. Update tests to reflect new behavior

### Database Schema Changes
1. Modify models in `models.py`
2. Create migration script
3. Update seed data if needed
4. Test with existing data

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure virtual environment is activated
- **Database Connection**: Check PostgreSQL service and connection string
- **Redis Issues**: Verify Redis server is running
- **API Key Problems**: Validate Google Gemini API key and quotas

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

## Performance Considerations

### Optimization Guidelines
- Use database indexes for frequently queried fields
- Implement caching for AI responses where appropriate
- Monitor API response times
- Use connection pooling for database connections
- Implement rate limiting for external API calls

### Monitoring
- Check `/health` endpoint for service status
- Monitor database query performance
- Track AI API response times
- Watch for memory leaks in long-running processes

## Security Best Practices

### Data Protection
- Validate all user inputs
- Sanitize data before database storage
- Use parameterized queries
- Implement proper authentication (when added)
- Secure API key storage

### API Security
- Implement CORS properly
- Add rate limiting
- Validate request payloads
- Log security-relevant events
- Use HTTPS in production

## Contributing Guidelines

### Code Changes
1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Follow coding standards**: KISS principle, type hints, docstrings
3. **Write tests**: Cover new functionality and edge cases
4. **Run test suite**: Ensure all tests pass
5. **Update documentation**: Keep AGENTS.md current

### Commit Messages
- Use descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic
- Test before committing

## AI Agent Specific Instructions

### When Working with AI Components
- **Test AI responses**: Ensure consistent behavior across runs
- **Validate prompts**: Check for bias, clarity, and effectiveness
- **Monitor API usage**: Track Google Gemini API calls and costs
- **Handle failures gracefully**: Implement fallbacks for API errors
- **Optimize prompts**: Reduce token usage while maintaining quality

### AI Testing Strategy
- **Unit tests**: Mock AI API calls for fast testing
- **Integration tests**: Test with real AI responses
- **Performance tests**: Measure response generation time
- **Quality tests**: Validate response relevance and coherence

---

**Remember**: This project follows the KISS principle. When in doubt, choose the simpler, more maintainable solution over complex abstractions. Always prioritize code clarity and testability.
