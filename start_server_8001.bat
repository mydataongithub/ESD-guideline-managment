@echo off
echo Starting ESD and Latch-up Guideline Generator on port 8001...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing uv package manager...
    pip install uv
)

REM Install dependencies
echo Installing dependencies...
uv pip install -r requirements.txt

REM Initialize Git repository if it doesn't exist
if not exist "guidelines_repo\.git" (
    echo Initializing Git repository...
    cd guidelines_repo
    git init
    git add README.md
    git commit -m "Initial commit: Setup guidelines repository"
    cd ..
    echo.
)

REM Start the FastAPI server on port 8001
echo Starting the web server on port 8001...
echo.
echo Web interface will be available at: http://localhost:8001
echo Press Ctrl+C to stop the server
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

pause
