@echo off
echo Setting up UV Package Manager for ESD & Latchup Guidelines Generator
echo =====================================================================
echo.

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Checking Python version...
python --version

REM Install uv
echo.
echo Installing uv package manager...
pip install --upgrade uv

REM Verify uv installation
echo.
echo Verifying uv installation...
uv --version
if %errorlevel% neq 0 (
    echo ERROR: uv installation failed
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install project dependencies with uv
echo.
echo Installing project dependencies with uv...
uv pip install -r requirements.txt

echo.
echo =====================================================================
echo UV setup complete!
echo.
echo To start the server, run: start_server.bat
echo.
pause
