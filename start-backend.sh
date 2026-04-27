#!/bin/bash

echo "========================================="
echo "Starting Backend API Server"
echo "========================================="
echo ""

cd backend

VENV_DIR=".venv"
MARKER_FILE="$VENV_DIR/.deps_installed"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating local virtual environment at backend/$VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if [ ! -f "$MARKER_FILE" ] || [ "requirements.txt" -nt "$MARKER_FILE" ]; then
    echo "Installing backend dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    touch "$MARKER_FILE"
else
    echo "✅ Backend dependencies already installed"
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
echo "👉 http://localhost:8001"
echo ""
echo "API Documentation:"
echo "👉 http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
