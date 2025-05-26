#!/bin/bash

echo "Starting ESD & Latch-up Guideline Generator..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    pip install uv
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Initialize Git repository if it doesn't exist
if [ ! -d "guidelines_repo/.git" ]; then
    echo "Initializing Git repository..."
    cd guidelines_repo
    git init
    git add README.md
    git commit -m "Initial commit: Setup guidelines repository"
    cd ..
    echo
fi

# Start the FastAPI server
echo "Starting the web server..."
echo
echo "Web interface will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
