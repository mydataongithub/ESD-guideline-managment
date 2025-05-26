@echo off
echo Starting ESD and Latch-up Guideline Generator...
echo.
echo Server will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

rem Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing uv package manager...
    pip install uv
)

rem Install required packages if they don't exist
uv pip install -r requirements.txt

rem Initialize database tables
python -m app.database.init_db

rem Start the server
python -m app.main
