#!/bin/bash

# Mojila Signal Setup Script
# This script sets up a virtual environment and installs all dependencies

echo "=========================================================="
echo "MOJILA SIGNAL - Setup Script"
echo "=========================================================="
echo "Setting up virtual environment and installing dependencies..."
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created successfully"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"

# Run installation test
echo "🧪 Running installation test..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo
    echo "=========================================================="
    echo "🎉 SETUP COMPLETED SUCCESSFULLY!"
    echo "=========================================================="
    echo "To use Mojila Signal:"
    echo
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo
    echo "2. Run the main application:"
    echo "   python main.py"
    echo
    echo "3. Or run examples:"
    echo "   python examples.py"
    echo
    echo "4. To deactivate the virtual environment when done:"
    echo "   deactivate"
    echo "=========================================================="
else
    echo
    echo "=========================================================="
    echo "❌ SETUP COMPLETED WITH ISSUES"
    echo "=========================================================="
    echo "Some tests failed, but the basic setup is complete."
    echo "You can still try running the application:"
    echo
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo
    echo "2. Run the main application:"
    echo "   python main.py"
    echo "=========================================================="
fi

echo
echo "Note: Always activate the virtual environment before using the application!"