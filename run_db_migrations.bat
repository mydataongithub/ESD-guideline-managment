@echo off
REM Script to run database migrations for database enhancements task #5
echo Running database migrations for enhancing database schema...

cd "%~dp0"
python -m app.database.migrations

if %ERRORLEVEL% NEQ 0 (
    echo Migration failed! Please check the error log.
    exit /b %ERRORLEVEL%
) else (
    echo Database migrations completed successfully.
    echo.
    echo Database enhancements from task #5 have been implemented:
    echo - Extended database schema to store images associated with rules
    echo - Added support for storing explanatory texts
    echo - Implemented storage for technology-specific templates
    echo - Added rule categorization (ESD vs latchup)
    echo.
)
