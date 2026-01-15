#!/bin/bash

echo "=================================="
echo "🚀 Starting Retail Void Analysis System"
echo "=================================="
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import flask, flask_cors, gspread, google.oauth2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -q flask flask-cors requests rapidfuzz gspread google-auth
fi

echo "✅ Dependencies ready"
echo ""

# Start backend server
echo "Starting backend API server..."
echo "Server will be available at: http://localhost:5000"
echo ""
echo "To open the dashboard:"
echo "  1. Open a new terminal"
echo "  2. Run: open interactive_dashboard.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

python api_server.py
