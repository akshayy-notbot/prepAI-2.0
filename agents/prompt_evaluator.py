"""
Prompt Evaluator System
Captures, logs, and analyzes all prompt inputs and outputs from AI agents
for debugging, optimization, and quality assurance.
"""

import os
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

@dataclass
class PromptExecution:
    """Data structure for tracking prompt executions"""
    execution_id: str
    timestamp: float
    component: str  # e.g., "autonomous_interviewer", "evaluation", "pre_interview_planner"
    method: str     # e.g., "conduct_interview_turn", "evaluate_answer"
    prompt_type: str  # e.g., "interview_question", "evaluation", "planning"
    
    # Input data
    input_data: Dict[str, Any]
    prompt_text: str
    
    # Output data
    output_data: Dict[str, Any]
    response_text: str
    
    # Performance metrics
    latency_ms: float
    token_count: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    
    # Context
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    seniority: Optional[str] = None
    skill: Optional[str] = None

class PromptEvaluator:
    """
    Comprehensive prompt evaluation system that captures all AI interactions
    for analysis, debugging, and optimization.
    """
    
    def __init__(self, db_path: str = "prompt_evaluations.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for storing prompt executions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_executions (
                execution_id TEXT PRIMARY KEY,
                timestamp REAL,
                component TEXT,
                method TEXT,
                prompt_type TEXT,
                input_data TEXT,
                prompt_text TEXT,
                output_data TEXT,
                response_text TEXT,
                latency_ms REAL,
                token_count INTEGER,
                success BOOLEAN,
                error_message TEXT,
                session_id TEXT,
                user_id TEXT,
                role TEXT,
                seniority TEXT,
                skill TEXT
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_component ON prompt_executions(component)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON prompt_executions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON prompt_executions(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_success ON prompt_executions(success)')
        
        conn.commit()
        conn.close()
    
    def log_execution(self, execution: PromptExecution):
        """Log a prompt execution to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO prompt_executions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution.execution_id,
                execution.timestamp,
                execution.component,
                execution.method,
                execution.prompt_type,
                json.dumps(execution.input_data),
                execution.prompt_text,
                json.dumps(execution.output_data),
                execution.response_text,
                execution.latency_ms,
                execution.token_count,
                execution.success,
                execution.error_message,
                execution.session_id,
                execution.user_id,
                execution.role,
                execution.seniority,
                execution.skill
            ))
            
            conn.commit()
            conn.close()
            
            print(f"📊 Logged prompt execution: {execution.component}.{execution.method}")
            
        except Exception as e:
            print(f"❌ Failed to log prompt execution: {e}")
    
    def capture_execution(self, 
                         component: str,
                         method: str,
                         prompt_type: str,
                         input_data: Dict[str, Any],
                         prompt_text: str,
                         output_data: Dict[str, Any],
                         response_text: str,
                         latency_ms: float,
                         session_id: Optional[str] = None,
                         user_id: Optional[str] = None,
                         role: Optional[str] = None,
                         seniority: Optional[str] = None,
                         skill: Optional[str] = None,
                         token_count: Optional[int] = None,
                         success: bool = True,
                         error_message: Optional[str] = None) -> str:
        """
        Capture and log a prompt execution with all relevant metadata.
        Returns the execution ID for reference.
        """
        execution = PromptExecution(
            execution_id=str(uuid.uuid4()),
            timestamp=time.time(),
            component=component,
            method=method,
            prompt_type=prompt_type,
            input_data=input_data,
            prompt_text=prompt_text,
            output_data=output_data,
            response_text=response_text,
            latency_ms=latency_ms,
            token_count=token_count,
            success=success,
            error_message=error_message,
            session_id=session_id,
            user_id=user_id,
            role=role,
            seniority=seniority,
            skill=skill
        )
        
        self.log_execution(execution)
        return execution.execution_id
    
    def get_executions(self, 
                      component: Optional[str] = None,
                      method: Optional[str] = None,
                      session_id: Optional[str] = None,
                      success_only: bool = False,
                      limit: int = 100) -> List[PromptExecution]:
        """Retrieve prompt executions with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM prompt_executions WHERE 1=1"
            params = []
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            if method:
                query += " AND method = ?"
                params.append(method)
            
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            
            if success_only:
                query += " AND success = 1"
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            executions = []
            for row in rows:
                execution = PromptExecution(
                    execution_id=row[0],
                    timestamp=row[1],
                    component=row[2],
                    method=row[3],
                    prompt_type=row[4],
                    input_data=json.loads(row[5]) if row[5] else {},
                    prompt_text=row[6],
                    output_data=json.loads(row[7]) if row[7] else {},
                    response_text=row[8],
                    latency_ms=row[9],
                    token_count=row[10],
                    success=bool(row[11]),
                    error_message=row[12],
                    session_id=row[13],
                    user_id=row[14],
                    role=row[15],
                    seniority=row[16],
                    skill=row[17]
                )
                executions.append(execution)
            
            conn.close()
            return executions
            
        except Exception as e:
            print(f"❌ Failed to retrieve executions: {e}")
            return []
    
    def analyze_component_performance(self, component: str, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance metrics for a specific component"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_executions,
                    AVG(latency_ms) as avg_latency,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_executions,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_executions
                FROM prompt_executions 
                WHERE component = ? AND timestamp > ?
            ''', (component, cutoff_time))
            
            stats = cursor.fetchone()
            
            # Get method breakdown
            cursor.execute('''
                SELECT method, COUNT(*) as count, AVG(latency_ms) as avg_latency
                FROM prompt_executions 
                WHERE component = ? AND timestamp > ?
                GROUP BY method
            ''', (component, cutoff_time))
            
            method_stats = cursor.fetchall()
            
            # Get recent errors
            cursor.execute('''
                SELECT method, error_message, timestamp
                FROM prompt_executions 
                WHERE component = ? AND success = 0 AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (component, cutoff_time))
            
            recent_errors = cursor.fetchall()
            
            conn.close()
            
            return {
                "component": component,
                "time_period_hours": hours,
                "total_executions": stats[0],
                "avg_latency_ms": round(stats[1], 2) if stats[1] else 0,
                "success_rate": round((stats[2] / stats[0]) * 100, 2) if stats[0] > 0 else 0,
                "method_breakdown": [
                    {"method": m[0], "count": m[1], "avg_latency_ms": round(m[2], 2) if m[2] else 0}
                    for m in method_stats
                ],
                "recent_errors": [
                    {"method": e[0], "error": e[1], "timestamp": datetime.fromtimestamp(e[2]).isoformat()}
                    for e in recent_errors
                ]
            }
            
        except Exception as e:
            print(f"❌ Failed to analyze component performance: {e}")
            return {}
    
    def get_prompt_effectiveness_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze overall prompt effectiveness across all components"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall success rate
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    AVG(latency_ms) as avg_latency
                FROM prompt_executions 
                WHERE timestamp > ?
            ''', (cutoff_time,))
            
            overall_stats = cursor.fetchone()
            
            # Component breakdown
            cursor.execute('''
                SELECT 
                    component,
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    AVG(latency_ms) as avg_latency
                FROM prompt_executions 
                WHERE timestamp > ?
                GROUP BY component
            ''', (cutoff_time,))
            
            component_breakdown = cursor.fetchall()
            
            # Prompt type analysis
            cursor.execute('''
                SELECT 
                    prompt_type,
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    AVG(latency_ms) as avg_latency
                FROM prompt_executions 
                WHERE timestamp > ?
                GROUP BY prompt_type
            ''', (cutoff_time,))
            
            prompt_type_analysis = cursor.fetchall()
            
            conn.close()
            
            return {
                "time_period_hours": hours,
                "overall_stats": {
                    "total_executions": overall_stats[0],
                    "success_rate": round((overall_stats[1] / overall_stats[0]) * 100, 2) if overall_stats[0] > 0 else 0,
                    "avg_latency_ms": round(overall_stats[2], 2) if overall_stats[2] else 0
                },
                "component_breakdown": [
                    {
                        "component": c[0],
                        "total": c[1],
                        "success_rate": round((c[2] / c[1]) * 100, 2) if c[1] > 0 else 0,
                        "avg_latency_ms": round(c[3], 2) if c[3] else 0
                    }
                    for c in component_breakdown
                ],
                "prompt_type_analysis": [
                    {
                        "prompt_type": p[0],
                        "total": p[1],
                        "success_rate": round((p[2] / p[1]) * 100, 2) if p[1] > 0 else 0,
                        "avg_latency_ms": round(p[3], 2) if p[3] else 0
                    }
                    for p in prompt_type_analysis
                ]
            }
            
        except Exception as e:
            print(f"❌ Failed to get prompt effectiveness analysis: {e}")
            return {}
    
    def export_executions_to_json(self, 
                                 output_file: str = "prompt_executions_export.json",
                                 hours: int = 24) -> bool:
        """Export prompt executions to JSON file for external analysis"""
        try:
            executions = self.get_executions(limit=10000)  # Get all executions
            
            # Filter by time if specified
            if hours > 0:
                cutoff_time = time.time() - (hours * 3600)
                executions = [e for e in executions if e.timestamp > cutoff_time]
            
            # Convert to serializable format
            export_data = []
            for execution in executions:
                export_data.append({
                    **asdict(execution),
                    "timestamp_iso": datetime.fromtimestamp(execution.timestamp).isoformat()
                })
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Exported {len(export_data)} executions to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export executions: {e}")
            return False
    
    def get_session_analysis(self, session_id: str) -> Dict[str, Any]:
        """Analyze all prompt executions for a specific interview session"""
        try:
            executions = self.get_executions(session_id=session_id)
            
            if not executions:
                return {"error": "No executions found for session"}
            
            # Group by component
            component_breakdown = {}
            for execution in executions:
                if execution.component not in component_breakdown:
                    component_breakdown[execution.component] = []
                component_breakdown[execution.component].append(execution)
            
            # Calculate session metrics
            total_prompts = len(executions)
            successful_prompts = sum(1 for e in executions if e.success)
            avg_latency = sum(e.latency_ms for e in executions) / total_prompts if total_prompts > 0 else 0
            
            return {
                "session_id": session_id,
                "total_prompts": total_prompts,
                "success_rate": round((successful_prompts / total_prompts) * 100, 2),
                "avg_latency_ms": round(avg_latency, 2),
                "component_breakdown": {
                    component: {
                        "count": len(execs),
                        "success_rate": round((sum(1 for e in execs if e.success) / len(execs)) * 100, 2),
                        "avg_latency_ms": round(sum(e.latency_ms for e in execs) / len(execs), 2)
                    }
                    for component, execs in component_breakdown.items()
                },
                "execution_timeline": [
                    {
                        "timestamp": datetime.fromtimestamp(e.timestamp).isoformat(),
                        "component": e.component,
                        "method": e.method,
                        "success": e.success,
                        "latency_ms": e.latency_ms
                    }
                    for e in sorted(executions, key=lambda x: x.timestamp)
                ]
            }
            
        except Exception as e:
            print(f"❌ Failed to get session analysis: {e}")
            return {"error": str(e)}

# Global instance for easy access
prompt_evaluator = PromptEvaluator()
