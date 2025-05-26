@echo off
echo ESD & Latch-up Guideline Generator - System Test
echo ===============================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo Running system tests...
echo.
python test_system.py

echo.
echo Test completed. Check the output above for results.
echo.
pause
