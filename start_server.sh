#!/bin/bash
# MySQL MCP Server Startup Script

# Default values
TRANSPORT="stdio"
PORT=8000

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --transport)
            TRANSPORT="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--transport stdio|sse|streamable-http] [--port PORT]"
            echo ""
            echo "Options:"
            echo "  --transport    Transport mode (default: stdio)"
            echo "  --port         Port number for SSE/HTTP (default: 8000)"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Ensure we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found."
    echo "💡 Required: DB_HOST, DB_USER, DB_PASSWORD"
    echo "💡 Optional: DB_NAME (default database), DB_PORT (default: 3306), DEBUG_MODE (default: false)"
    echo ""
fi

echo "🚀 Starting MySQL MCP Server..."
echo "📊 Transport: $TRANSPORT"
echo "🔌 Port: $PORT"
echo "📁 Working directory: $SCRIPT_DIR"
echo ""
echo "💡 Press Ctrl+C to stop the server gracefully"
echo ""

# Activate virtual environment and start server
source venv/bin/activate
python mysql_server.py --transport "$TRANSPORT" --port "$PORT"
