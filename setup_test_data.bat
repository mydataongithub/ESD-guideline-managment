@echo off
echo Setting up ESD Test Data and Images...
echo ======================================

REM Activate virtual environment
call venv\Scripts\activate

echo.
echo Step 1: Downloading ESD circuit images...
echo -----------------------------------------
python download_esd_images.py

echo.
echo Step 2: Populating database with test data...
echo ---------------------------------------------
python populate_test_data.py

echo.
echo ======================================
echo Setup completed!
echo.
echo You can now:
echo 1. Start the server with: start_server.bat
echo 2. Access the dashboard at: http://localhost:8000/dashboard
echo 3. View ESD images at: app\static\images\esd_circuits\index.html
echo.
pause
