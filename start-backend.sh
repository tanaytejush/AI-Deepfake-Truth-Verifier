#!/bin/bash

echo "========================================="
echo "Starting Backend API Server"
echo "========================================="
echo ""

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv

    echo "Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
fi

# Create necessary directories
mkdir -p uploads models/cache logs

echo ""
echo "========================================="
echo "🚀 Starting FastAPI Server"
echo "========================================="
echo ""
echo "API will be available at:"
echo "👉 http://localhost:8000"
echo ""
echo "API Documentation:"
echo "👉 http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
