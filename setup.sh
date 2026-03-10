#!/bin/bash

echo "======================================"
echo "AI Deepfake Truth Verifier - Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p uploads data/test_images data/predictions logs

# Create .gitkeep files
touch uploads/.gitkeep
touch data/test_images/.gitkeep
touch data/predictions/.gitkeep
touch logs/.gitkeep

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the app: streamlit run app.py"
echo ""
echo "Or test the detector directly: python src/detector.py"
echo ""
