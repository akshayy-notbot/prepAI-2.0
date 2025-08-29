#!/bin/bash

# PrepAI Test Runner Script
# This script provides easy access to run different types of tests

echo "🧪 PrepAI Two-Loop Architecture Test Runner"
echo "=============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Function to show usage
show_usage() {
    echo ""
    echo "Usage:"
    echo "  ./run_tests.sh                    # Run all tests"
    echo "  ./run_tests.sh unit               # Run unit tests only"
    echo "  ./run_tests.sh integration        # Run integration tests only"
    echo "  ./run_tests.sh performance        # Run performance tests only"
    echo "  ./run_tests.sh render             # Test against Render deployment"
    echo "  ./run_tests.sh help               # Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh unit               # Quick component testing"
    echo "  ./run_tests.sh performance        # Performance benchmarking"
    echo "  ./run_tests.sh render             # Production environment testing"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Make sure you have set the required environment variables:"
    echo "   - GOOGLE_API_KEY"
    echo "   - DATABASE_URL"
    echo "   - REDIS_URL"
    echo ""
fi

# Parse command line arguments
case "${1:-all}" in
    "unit")
        echo "🔬 Running Unit Tests..."
        python3 -m pytest tests/ -v -k "unit" --tb=short
        ;;
    "integration")
        echo "🔗 Running Integration Tests..."
        python3 -m pytest tests/ -v -k "integration" --tb=short
        ;;
    "performance")
        echo "⚡ Running Performance Tests..."
        python3 -m pytest tests/ -v -k "performance" --tb=short
        ;;
    "render")
        echo "☁️  Testing Render Integration..."
        python3 -m pytest tests/test_render_deployment.py -v --tb=short
        ;;
    "all")
        echo "🚀 Running All Tests..."
        python3 -m pytest tests/ -v --tb=short
        ;;
    "help"|"-h"|"--help")
        show_usage
        exit 0
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_usage
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests completed successfully!"
else
    echo ""
    echo "❌ Some tests failed. Check the output above for details."
fi
