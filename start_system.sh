#!/bin/bash

echo "🏭 Starting Factory Supervision System..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Factory Supervision System..."
    kill $FASTAPI_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

echo "🚀 Starting FastAPI Backend (Port 8000)..."
cd backend
if [ -d "../tf-venv" ]; then
    echo "📦 Activating virtual environment..."
    source ../tf-venv/bin/activate
fi
python3 -m uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload &
FASTAPI_PID=$!
cd ..

# Wait for FastAPI to start
sleep 3

echo "🌐 Starting Frontend Server (Port 3000)..."
cd frontend
node dashboard_server.js &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 2

echo ""
echo "✅ Factory Supervision System Started Successfully!"
echo "📡 Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "💬 Chat System: Integrated with Azure OpenAI"
echo "📹 Computer Vision: FastAPI + YOLO Integration"
echo ""
echo "Press Ctrl+C to stop all services..."
echo "💬 Chat System: Integrated with Azure OpenAI"
echo "📹 Computer Vision: FastAPI + YOLO Integration"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for both processes
wait $FASTAPI_PID $FRONTEND_PID
