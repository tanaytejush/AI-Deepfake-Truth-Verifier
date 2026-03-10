#!/bin/bash

echo "======================================"
echo "AI Deepfake Truth Verifier"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found!"
    echo "Please run: ./setup.sh to install dependencies"
    exit 1
fi

# Run the application
echo ""
echo "🚀 Starting AI Deepfake Truth Verifier..."
echo ""
echo "The application will open in your browser at:"
echo "👉 http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
