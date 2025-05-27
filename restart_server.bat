@echo off
echo Killing any existing Python processes...
taskkill /F /IM python.exe 2>nul
echo.
echo Starting server...
cd /d "C:\Users\weidner\Desktop\workflow3"
python -m uvicorn app.main:app --reload --port 8000
pause