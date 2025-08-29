#!/usr/bin/env python3
"""
Prompt Analysis CLI Tool
Command-line interface for analyzing prompt evaluation data
"""

import argparse
import json
import sys
from datetime import datetime
from agents.prompt_evaluator import prompt_evaluator

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print("-"*40)

def format_timestamp(timestamp):
    """Format timestamp for display"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def show_overview(hours=24):
    """Show overview of prompt evaluation metrics"""
    print_header("PROMPT EVALUATION OVERVIEW")
    print(f"Time Period: Last {hours} hours")
    
    try:
        analysis = prompt_evaluator.get_prompt_effectiveness_analysis(hours)
        
        if not analysis:
            print("❌ No data available for the specified time period")
            return
        
        # Overall stats
        overall = analysis.get("overall_stats", {})
        print_section("Overall Performance")
        print(f"Total Executions: {overall.get('total_executions', 0)}")
        print(f"Success Rate: {overall.get('success_rate', 0)}%")
        print(f"Average Latency: {overall.get('avg_latency_ms', 0)}ms")
        
        # Component breakdown
        components = analysis.get("component_breakdown", [])
        if components:
            print_section("Component Performance")
            for component in components:
                print(f"\n{component['component']}:")
                print(f"  Total: {component['total']}")
                print(f"  Success Rate: {component['success_rate']}%")
                print(f"  Avg Latency: {component['avg_latency_ms']}ms")
        
        # Prompt type analysis
        prompt_types = analysis.get("prompt_type_analysis", [])
        if prompt_types:
            print_section("Prompt Type Analysis")
            for prompt_type in prompt_types:
                print(f"\n{prompt_type['prompt_type']}:")
                print(f"  Total: {prompt_type['total']}")
                print(f"  Success Rate: {prompt_type['success_rate']}%")
                print(f"  Avg Latency: {prompt_type['avg_latency_ms']}ms")
                
    except Exception as e:
        print(f"❌ Error loading overview: {e}")

def show_component_analysis(component, hours=24):
    """Show detailed analysis for a specific component"""
    print_header(f"COMPONENT ANALYSIS: {component.upper()}")
    print(f"Time Period: Last {hours} hours")
    
    try:
        analysis = prompt_evaluator.analyze_component_performance(component, hours)
        
        if not analysis:
            print(f"❌ No data available for component '{component}'")
            return
        
        # Basic stats
        print_section("Performance Metrics")
        print(f"Total Executions: {analysis.get('total_executions', 0)}")
        print(f"Success Rate: {analysis.get('success_rate', 0)}%")
        print(f"Average Latency: {analysis.get('avg_latency_ms', 0)}ms")
        print(f"Failed Executions: {analysis.get('failed_executions', 0)}")
        
        # Method breakdown
        methods = analysis.get("method_breakdown", [])
        if methods:
            print_section("Method Breakdown")
            for method in methods:
                print(f"\n{method['method']}:")
                print(f"  Count: {method['count']}")
                print(f"  Avg Latency: {method['avg_latency_ms']}ms")
        
        # Recent errors
        errors = analysis.get("recent_errors", [])
        if errors:
            print_section("Recent Errors")
            for error in errors:
                print(f"\n{error['method']} at {error['timestamp']}:")
                print(f"  Error: {error['error']}")
        
    except Exception as e:
        print(f"❌ Error analyzing component: {e}")

def show_recent_executions(limit=50, show_errors_only=False):
    """Show recent prompt executions"""
    print_header("RECENT PROMPT EXECUTIONS")
    print(f"Limit: {limit} executions")
    if show_errors_only:
        print("Filter: Errors only")
    
    try:
        executions = prompt_evaluator.get_executions(
            limit=limit, 
            success_only=False if show_errors_only else None
        )
        
        if not executions:
            print("❌ No executions found")
            return
        
        # Filter errors if requested
        if show_errors_only:
            executions = [e for e in executions if not e.success]
        
        print_section(f"Showing {len(executions)} executions")
        
        for i, execution in enumerate(executions, 1):
            status = "✅" if execution.success else "❌"
            print(f"\n{i}. {status} {execution.component}.{execution.method}")
            print(f"   Time: {format_timestamp(execution.timestamp)}")
            print(f"   Type: {execution.prompt_type}")
            print(f"   Latency: {execution.latency_ms}ms")
            
            if execution.session_id:
                print(f"   Session: {execution.session_id}")
            
            if execution.role:
                print(f"   Context: {execution.seniority} {execution.role} - {execution.skill}")
            
            if not execution.success and execution.error_message:
                print(f"   Error: {execution.error_message}")
        
    except Exception as e:
        print(f"❌ Error loading executions: {e}")

def show_session_analysis(session_id):
    """Show analysis for a specific session"""
    print_header(f"SESSION ANALYSIS: {session_id}")
    
    try:
        analysis = prompt_evaluator.get_session_analysis(session_id)
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        # Session stats
        print_section("Session Overview")
        print(f"Total Prompts: {analysis.get('total_prompts', 0)}")
        print(f"Success Rate: {analysis.get('success_rate', 0)}%")
        print(f"Average Latency: {analysis.get('avg_latency_ms', 0)}ms")
        
        # Component breakdown
        components = analysis.get("component_breakdown", {})
        if components:
            print_section("Component Breakdown")
            for component, stats in components.items():
                print(f"\n{component}:")
                print(f"  Count: {stats['count']}")
                print(f"  Success Rate: {stats['success_rate']}%")
                print(f"  Avg Latency: {stats['avg_latency_ms']}ms")
        
        # Execution timeline
        timeline = analysis.get("execution_timeline", [])
        if timeline:
            print_section("Execution Timeline")
            for exec_item in timeline:
                status = "✅" if exec_item['success'] else "❌"
                print(f"{status} {exec_item['timestamp']} - {exec_item['component']}.{exec_item['method']} ({exec_item['latency_ms']}ms)")
        
    except Exception as e:
        print(f"❌ Error analyzing session: {e}")

def export_data(output_file, hours=24):
    """Export prompt evaluation data to JSON"""
    print_header("EXPORTING DATA")
    print(f"Output file: {output_file}")
    print(f"Time period: Last {hours} hours")
    
    try:
        success = prompt_evaluator.export_executions_to_json(output_file, hours)
        
        if success:
            print(f"✅ Data exported successfully to {output_file}")
        else:
            print("❌ Failed to export data")
            
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def list_components():
    """List all available components"""
    print_header("AVAILABLE COMPONENTS")
    
    try:
        executions = prompt_evaluator.get_executions(limit=1000)
        components = list(set(execution.component for execution in executions))
        
        if not components:
            print("❌ No components found")
            return
        
        for component in sorted(components):
            print(f"• {component}")
            
    except Exception as e:
        print(f"❌ Error listing components: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Prompt Analysis CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show overview of last 24 hours
  python prompt_analysis_cli.py overview
  
  # Show component analysis for last week
  python prompt_analysis_cli.py component autonomous_interviewer --hours 168
  
  # Show recent executions (errors only)
  python prompt_analysis_cli.py executions --limit 20 --errors-only
  
  # Analyze specific session
  python prompt_analysis_cli.py session abc123
  
  # Export data for last month
  python prompt_analysis_cli.py export --output data.json --hours 720
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Overview command
    overview_parser = subparsers.add_parser('overview', help='Show overview of prompt evaluation metrics')
    overview_parser.add_argument('--hours', type=int, default=24, help='Time period in hours (default: 24)')
    
    # Component analysis command
    component_parser = subparsers.add_parser('component', help='Analyze specific component performance')
    component_parser.add_argument('component', help='Component name to analyze')
    component_parser.add_argument('--hours', type=int, default=24, help='Time period in hours (default: 24)')
    
    # Executions command
    executions_parser = subparsers.add_parser('executions', help='Show recent prompt executions')
    executions_parser.add_argument('--limit', type=int, default=50, help='Maximum number of executions to show (default: 50)')
    executions_parser.add_argument('--errors-only', action='store_true', help='Show only failed executions')
    
    # Session analysis command
    session_parser = subparsers.add_parser('session', help='Analyze specific interview session')
    session_parser.add_argument('session_id', help='Session ID to analyze')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export prompt evaluation data to JSON')
    export_parser.add_argument('--output', default='prompt_evaluations.json', help='Output file name (default: prompt_evaluations.json)')
    export_parser.add_argument('--hours', type=int, default=24, help='Time period in hours (default: 24)')
    
    # List components command
    subparsers.add_parser('components', help='List all available components')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'overview':
            show_overview(args.hours)
        elif args.command == 'component':
            show_component_analysis(args.component, args.hours)
        elif args.command == 'executions':
            show_recent_executions(args.limit, args.errors_only)
        elif args.command == 'session':
            show_session_analysis(args.session_id)
        elif args.command == 'export':
            export_data(args.output, args.hours)
        elif args.command == 'components':
            list_components()
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
