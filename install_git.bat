@echo off
echo Git Installation Helper
echo ======================
echo.
echo The ESD Guidelines system works better with Git for version control,
echo but it's completely optional.
echo.
echo Benefits of installing Git:
echo - Track changes to generated guidelines
echo - View document history  
echo - Compare different versions
echo - Automatic backup of all changes
echo.
echo The system works WITHOUT Git, but you'll miss these features.
echo.
choice /C YN /M "Do you want to install Git now (opens browser)"
if errorlevel 2 goto :skip
if errorlevel 1 goto :install

:install
echo Opening Git download page...
start https://git-scm.com/download/win
echo.
echo After installation:
echo 1. Restart your computer
echo 2. Run test_system.bat again
echo 3. Git features will be automatically enabled
goto :end

:skip
echo Git installation skipped.
echo The system will work without version control features.
echo You can install Git later if needed.

:end
echo.
pause
