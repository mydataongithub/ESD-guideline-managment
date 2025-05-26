#!/bin/bash

echo "Setting up UV Package Manager for ESD & Latchup Guidelines Generator"
echo "====================================================================="
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Checking Python version..."
python3 --version

# Install uv
echo
echo "Installing uv package manager..."
pip install --upgrade uv

# Verify uv installation
echo
echo "Verifying uv installation..."
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv installation failed"
    echo "Try installing with: pip install --user uv"
    exit 1
fi
uv --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo
echo "Activating virtual environment..."
source venv/bin/activate

# Install project dependencies with uv
echo
echo "Installing project dependencies with uv..."
uv pip install -r requirements.txt

echo
echo "====================================================================="
echo "UV setup complete!"
echo
echo "To start the server, run: ./start_server.sh"
echo
