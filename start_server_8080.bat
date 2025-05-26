@echo off
echo Starting ESD and Latch-up Guideline Generator...
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
uv pip install fastapi uvicorn jinja2 markdown2

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

REM Start the FastAPI server on port 8080 (Windows-friendly)
echo Starting the web server...
echo.
echo Web interface will be available at: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload

pause
