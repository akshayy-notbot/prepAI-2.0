# Prompt Evaluation System Guide

## Overview

The Prompt Evaluation System is a comprehensive tool for capturing, analyzing, and debugging all AI agent prompts in your PrepAI-Prototype. It provides detailed insights into prompt performance, success rates, latency, and error patterns to help optimize your AI interactions.

## 🚀 Quick Start

### 1. System Components

- **`PromptEvaluator`** (`agents/prompt_evaluator.py`): Core evaluation engine
- **`@capture_prompt_execution`** decorator: Easy integration with existing methods
- **CLI Tool** (`prompt_analysis_cli.py`): Command-line analysis
- **API Endpoints**: REST API for dashboard integration
- **SQLite Database**: Local storage of all prompt executions

### 2. Automatic Integration

The system automatically captures prompt executions when you use the decorator:

```python
from agents.prompt_capture_decorator import capture_prompt_execution, extract_input_data_from_kwargs, extract_output_data_from_json_response, extract_session_context_from_kwargs

@capture_prompt_execution(
    component="autonomous_interviewer",
    method="conduct_interview_turn",
    prompt_type="interview_question",
    extract_input_data=extract_input_data_from_kwargs("role", "seniority", "skill", "interview_stage"),
    extract_output_data=extract_output_data_from_json_response(),
    extract_session_context=extract_session_context_from_kwargs()
)
def conduct_interview_turn(self, role, seniority, skill, interview_stage, ...):
    # Your existing method implementation
    pass
```

### 3. Manual Integration

For methods that don't fit the decorator pattern:

```python
from agents.prompt_evaluator import prompt_evaluator

def your_method(self, *args, **kwargs):
    start_time = time.time()
    
    try:
        # Your existing logic
        result = your_ai_call()
        
        # Capture execution
        execution_id = prompt_evaluator.capture_execution(
            component="your_component",
            method="your_method",
            prompt_type="your_prompt_type",
            input_data={"arg1": args[0], "kwarg1": kwargs.get("key1")},
            prompt_text="Your actual prompt text",
            output_data=result,
            response_text=str(result),
            latency_ms=(time.time() - start_time) * 1000,
            success=True,
            session_id=kwargs.get("session_id"),
            role=kwargs.get("role"),
            seniority=kwargs.get("seniority"),
            skill=kwargs.get("skill")
        )
        
        return result
        
    except Exception as e:
        # Capture failed execution
        prompt_evaluator.capture_execution(
            component="your_component",
            method="your_method",
            prompt_type="your_prompt_type",
            input_data={"arg1": args[0] if args else None},
            prompt_text="",
            output_data={},
            response_text="",
            latency_ms=(time.time() - start_time) * 1000,
            success=False,
            error_message=str(e)
        )
        raise
```

## 📊 Analysis Tools

### 1. Command Line Interface

```bash
# Show overview of last 24 hours
python prompt_analysis_cli.py overview

# Analyze specific component
python prompt_analysis_cli.py component autonomous_interviewer --hours 168

# Show recent executions (errors only)
python prompt_analysis_cli.py executions --limit 20 --errors-only

# Analyze specific session
python prompt_analysis_cli.py session abc123

# Export data for analysis
python prompt_analysis_cli.py export --output data.json --hours 720

# List all components
python prompt_analysis_cli.py components
```

### 2. API Endpoints

```bash
# Get overview metrics
GET /api/prompt-evaluation/overview?hours=24

# Get component list
GET /api/prompt-evaluation/components

# Analyze specific component
GET /api/prompt-evaluation/component/autonomous_interviewer?hours=24

# Get recent executions
GET /api/prompt-evaluation/executions?limit=100&success_only=false

# Analyze session
GET /api/prompt-evaluation/session/{session_id}

# Export data
GET /api/prompt-evaluation/export?hours=24

# Test prompt capture
POST /api/prompt-evaluation/test

# Generate test data
POST /api/prompt-evaluation/generate-test-data
```

## 🔍 What Gets Captured

### Execution Data
- **Metadata**: Component, method, prompt type, timestamp
- **Input**: All input parameters and prompt text
- **Output**: AI response and structured data
- **Performance**: Latency, success/failure, error messages
- **Context**: Session ID, role, seniority, skill

### Analysis Metrics
- **Success Rates**: Overall and per-component
- **Latency Analysis**: Average, trends, outliers
- **Error Patterns**: Common failure modes
- **Component Performance**: Method-level breakdowns
- **Session Analysis**: Interview flow patterns

## 🛠️ Integration Examples

### 1. Autonomous Interviewer

```python
# In agents/autonomous_interviewer.py
from agents.prompt_capture_decorator import (
    capture_prompt_execution,
    extract_input_data_from_kwargs,
    extract_output_data_from_json_response,
    extract_session_context_from_kwargs
)

class AutonomousInterviewer:
    @capture_prompt_execution(
        component="autonomous_interviewer",
        method="get_initial_question",
        prompt_type="interview_question",
        extract_input_data=extract_input_data_from_kwargs("role", "seniority", "skill"),
        extract_output_data=extract_output_data_from_json_response(),
        extract_session_context=extract_session_context_from_kwargs()
    )
    def get_initial_question(self, role, seniority, skill, session_context=None):
        # Your existing implementation
        pass

    @capture_prompt_execution(
        component="autonomous_interviewer",
        method="conduct_interview_turn",
        prompt_type="interview_question",
        extract_input_data=extract_input_data_from_kwargs("role", "seniority", "skill", "interview_stage"),
        extract_output_data=extract_output_data_from_json_response(),
        extract_session_context=extract_session_context_from_kwargs()
    )
    def conduct_interview_turn(self, role, seniority, skill, interview_stage, ...):
        # Your existing implementation
        pass
```

### 2. Evaluation Engine

```python
# In agents/evaluation.py
from agents.prompt_capture_decorator import (
    capture_prompt_execution,
    extract_input_data_from_kwargs,
    extract_output_data_from_json_response
)

@capture_prompt_execution(
    component="evaluation",
    method="evaluate_answer",
    prompt_type="evaluation",
    extract_input_data=extract_input_data_from_kwargs("answer", "question", "skills_to_assess"),
    extract_output_data=extract_output_data_from_json_response()
)
def evaluate_answer(answer, question, skills_to_assess, ...):
    # Your existing implementation
    pass
```

### 3. Pre-Interview Planner

```python
# In agents/pre_interview_planner.py
from agents.prompt_capture_decorator import (
    capture_prompt_execution,
    extract_input_data_from_kwargs,
    extract_output_data_from_json_response
)

class PreInterviewPlanner:
    @capture_prompt_execution(
        component="pre_interview_planner",
        method="create_interview_plan",
        prompt_type="planning",
        extract_input_data=extract_input_data_from_kwargs("role", "skill", "seniority"),
        extract_output_data=extract_output_data_from_json_response()
    )
    def create_interview_plan(self, role, skill, seniority):
        # Your existing implementation
        pass
```

## 📈 Analysis Use Cases

### 1. Performance Optimization
```bash
# Find slow prompts
python prompt_analysis_cli.py executions --limit 100 | grep "500ms"

# Analyze component bottlenecks
python prompt_analysis_cli.py component autonomous_interviewer --hours 168
```

### 2. Error Debugging
```bash
# Find all errors
python prompt_analysis_cli.py executions --errors-only

# Analyze specific error patterns
python prompt_analysis_cli.py component evaluation --hours 24
```

### 3. Quality Assurance
```bash
# Monitor success rates
python prompt_analysis_cli.py overview --hours 1

# Track session quality
python prompt_analysis_cli.py session {session_id}
```

### 4. Cost Analysis
```bash
# Export data for external analysis
python prompt_analysis_cli.py export --output cost_analysis.json --hours 720

# Analyze token usage patterns
# (Token count is captured when available)
```

## 🔧 Configuration

### Database Location
The system uses SQLite by default. You can customize the database path:

```python
from agents.prompt_evaluator import PromptEvaluator

# Custom database location
evaluator = PromptEvaluator(db_path="/path/to/custom/prompts.db")
```

### Logging
The system provides console logging for all operations:

```
📊 Logged prompt execution: autonomous_interviewer.conduct_interview_turn
✅ Exported 150 executions to prompt_executions_export.json
❌ Failed to log prompt execution: database locked
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Locked**
   - Ensure only one process accesses the database
   - Check for concurrent access patterns

2. **Import Errors**
   - Verify the agents directory is in your Python path
   - Check that all dependencies are installed

3. **No Data Showing**
   - Verify prompts are being captured (check console logs)
   - Test with the test endpoint: `POST /api/prompt-evaluation/test`

4. **Performance Issues**
   - The system is designed to be lightweight
   - Database operations are asynchronous
   - Consider clearing old data periodically

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test prompt capture
from agents.prompt_evaluator import prompt_evaluator
execution_id = prompt_evaluator.capture_execution(...)
print(f"Execution captured: {execution_id}")
```

## 📋 Best Practices

### 1. Consistent Naming
- Use descriptive component and method names
- Standardize prompt types across your system
- Maintain consistent parameter naming

### 2. Comprehensive Capture
- Capture all relevant context (session, role, skill)
- Include both successful and failed executions
- Log detailed error messages for debugging

### 3. Regular Analysis
- Monitor success rates daily
- Analyze performance trends weekly
- Export data monthly for long-term analysis

### 4. Integration Strategy
- Start with critical AI components
- Gradually add to all AI interactions
- Use the decorator pattern for consistency

## 🔮 Future Enhancements

### Planned Features
- **Real-time Monitoring**: WebSocket updates for live dashboards
- **Advanced Analytics**: Machine learning for pattern detection
- **Cost Tracking**: Token usage and API cost analysis
- **A/B Testing**: Compare different prompt strategies
- **Alerting**: Notifications for performance degradation

### Custom Extensions
The system is designed to be extensible. You can:
- Add custom extractors for specific data patterns
- Implement custom analysis algorithms
- Integrate with external monitoring systems
- Add custom export formats

## 📞 Support

For issues or questions:
1. Check the console logs for error messages
2. Use the CLI tool to verify data capture
3. Test individual components with the test endpoints
4. Review the database schema and data integrity

The Prompt Evaluation System is designed to be robust and self-documenting. Most issues can be resolved by examining the captured data and using the built-in analysis tools.
