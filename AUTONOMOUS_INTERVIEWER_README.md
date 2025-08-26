# Autonomous Interviewer System

## 🎯 Overview

The Autonomous Interviewer is a simplified, intelligent interview system that replaces the complex topic graph approach with a single LLM that makes real-time decisions about interview flow. It provides a more natural, adaptive interview experience while maintaining assessment quality.

## 🏗️ Architecture

### **Single LLM Approach**
Instead of multiple specialized agents, we use **one powerful LLM** that:
- Analyzes candidate responses in real-time
- Decides what to explore next based on performance
- Generates contextually appropriate questions
- Manages the entire interview flow autonomously

### **Key Components**

1. **`AutonomousInterviewer`** (`agents/autonomous_interviewer.py`)
   - Main interviewer class that handles all interview logic
   - Generates initial questions and follow-up questions
   - Makes autonomous decisions about interview direction

2. **`SessionTracker`** (`agents/session_tracker.py`)
   - Simple session state management
   - Tracks conversation history and interview progress
   - Manages skill assessment progress

## 🚀 How It Works

### **1. Interview Start**
```python
# Create new session
session_tracker = SessionTracker()
session_data = session_tracker.create_session(
    session_id="unique_id",
    role="Software Engineer",
    seniority="Senior",
    skill="System Design"
)

# Get initial question
autonomous_interviewer = AutonomousInterviewer()
initial_question = autonomous_interviewer.get_initial_question(
    role="Software Engineer",
    seniority="Senior", 
    skill="System Design",
    session_context=session_tracker.get_session_context(session_id)
)
```

### **2. Interview Turn**
```python
# Process user response and get next question
next_question = autonomous_interviewer.conduct_interview_turn(
    role="Software Engineer",
    seniority="Senior",
    skill="System Design",
    interview_stage="problem_understanding",
    conversation_history=conversation_history,
    session_context=session_context
)

# Update session state
session_tracker.update_interview_state(session_id, next_question["interview_state"])
```

### **3. Output Structure**
```python
{
  "chain_of_thought": [
    "Analyze candidate's response depth",
    "Assess current skill coverage",
    "Decide next interview direction",
    "Plan adaptive challenge"
  ],
  "response_text": "The next interview question or statement",
  "interview_state": {
    "current_stage": "technical_design",
    "skill_progress": "intermediate",
    "next_focus": "architectural trade-offs"
  }
}
```

## 🔧 Configuration

### **Environment Variables**
```bash
GOOGLE_API_KEY=your_gemini_api_key
REDIS_URL=your_redis_url
```

### **Interview Stages**
The system uses predefined interview stages to guide progression:
- **Problem Understanding**: Assess problem comprehension
- **Solution Design**: Test solution approach
- **Technical Depth**: Explore technical knowledge
- **Trade-offs & Constraints**: Evaluate real-world thinking
- **Implementation**: Test practical execution
- **Adaptation**: Assess handling of changes

## 📊 Benefits

### **Simplicity**
- **One agent** instead of multiple specialized agents
- **No complex topic graphs** to manage
- **Simpler state management** with Redis
- **Easier debugging** and maintenance

### **Intelligence**
- **Real-time adaptation** based on candidate performance
- **Natural conversation flow** without rigid scripts
- **Context-aware questions** that build on previous responses
- **Performance-based difficulty adjustment**

### **Flexibility**
- **Dynamic topic selection** based on candidate strengths/weaknesses
- **Adaptive challenge levels** for different skill levels
- **Natural interview progression** that feels human
- **Easy to extend** with new interview types

## 🧪 Testing

### **Run Tests**
```bash
python test_autonomous_interviewer.py
```

### **Test Coverage**
- Session creation and management
- Initial question generation
- Interview turn processing
- State management and updates
- Prompt generation

## 🔄 Migration from Old System

### **What Changed**
- **Removed**: Complex topic graph system
- **Removed**: Multiple specialized agents
- **Removed**: Rigid interview progression
- **Added**: Single autonomous interviewer
- **Added**: Simple session tracking
- **Added**: Dynamic interview flow

### **API Compatibility**
The new system maintains API compatibility with the frontend:
- Same endpoint structure
- Similar response format
- Backward-compatible session management

## 🎯 Future Enhancements

### **Phase 2: Enhanced Intelligence**
- **Multi-skill assessment** support
- **Advanced performance analytics**
- **Interview quality scoring**
- **Custom interview styles**

### **Phase 3: Advanced Features**
- **Real-time feedback** generation
- **Interview coaching** suggestions
- **Performance benchmarking** against standards
- **Integration** with learning management systems

## 🐛 Troubleshooting

### **Common Issues**

1. **API Key Errors**
   - Ensure `GOOGLE_API_KEY` is set correctly
   - Check API key permissions and quotas

2. **Redis Connection Issues**
   - Verify `REDIS_URL` is correct
   - Check Redis server availability

3. **Prompt Generation Errors**
   - Check conversation history format
   - Verify session context structure

### **Debug Mode**
Enable debug logging by setting environment variable:
```bash
DEBUG=true python your_script.py
```

## 📚 Examples

### **Basic Usage**
```python
from agents.autonomous_interviewer import AutonomousInterviewer
from agents.session_tracker import SessionTracker

# Initialize
interviewer = AutonomousInterviewer()
tracker = SessionTracker()

# Start interview
session_id = tracker.create_session("role", "seniority", "skill")
initial_q = interviewer.get_initial_question(...)

# Conduct interview
next_q = interviewer.conduct_interview_turn(...)
```

### **Advanced Usage**
```python
# Custom interview configuration
custom_context = {
    "company": "TechCorp",
    "team_size": 50,
    "tech_stack": ["Python", "AWS", "React"]
}

# Conduct interview with custom context
result = interviewer.conduct_interview_turn(
    role="Backend Engineer",
    seniority="Senior",
    skill="System Architecture",
    interview_stage="current_stage",
    conversation_history=history,
    session_context=custom_context
)
```

## 🤝 Contributing

### **Code Style**
- Follow PEP 8 guidelines
- Use type hints for all functions
- Add comprehensive docstrings
- Include unit tests for new features

### **Testing**
- Run tests before submitting changes
- Add tests for new functionality
- Ensure backward compatibility
- Test with different interview scenarios

---

**Note**: This system is designed to be simple, intelligent, and maintainable. It follows the KISS principle while providing sophisticated interview capabilities.
