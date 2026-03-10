#!/bin/bash

echo "========================================="
echo "AI Deepfake Truth Verifier"
echo "Starting Full Stack Application"
echo "========================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Warning: This script is optimized for macOS"
fi

echo "This will start both backend and frontend servers"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "========================================="
echo "Starting Backend..."
echo "========================================="

# Start backend in background
./start-backend.sh &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

echo ""
echo "========================================="
echo "Starting Frontend..."
echo "========================================="

# Start frontend in background
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "✅ Both servers are starting!"
echo "========================================="
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access the application at:"
echo "👉 http://localhost:3000"
echo ""
echo "API documentation at:"
echo "👉 http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
