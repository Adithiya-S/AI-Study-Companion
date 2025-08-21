#!/bin/bash
echo "========================================"
echo "Study Focus App - Python 3.8-3.12 Compatible"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.8-3.12 from your package manager or python.org"
    exit 1
fi

# Check Python version compatibility
python3 -c "import sys; exit(0 if (3,8) <= sys.version_info <= (3,12) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Incompatible Python version detected"
    echo "This app requires Python 3.8-3.12"
    echo "Python 3.13+ is not yet supported due to MediaPipe limitations"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to install dependencies"
    echo "Try running: sudo pip3 install -r requirements.txt"
    exit 1
fi

# Launch the application
echo
echo "🚀 Starting Study Focus App..."
echo
python3 main.py

# Check exit code
if [ $? -ne 0 ]; then
    echo
    echo "❌ Application exited with error"
    read -p "Press Enter to continue..."
fi
