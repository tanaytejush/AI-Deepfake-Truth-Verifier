#!/bin/bash

echo "========================================="
echo "Starting React Frontend"
echo "========================================="
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not installed!"
    echo "Installing dependencies..."
    npm install
else
    echo "✅ Dependencies found"
fi

echo ""
echo "========================================="
echo "🚀 Starting Development Server"
echo "========================================="
echo ""
echo "Frontend will be available at:"
echo "👉 http://localhost:3000"
echo ""
echo "Make sure backend is running on port 8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start development server
npm run dev
