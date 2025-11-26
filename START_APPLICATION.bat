@echo off
REM Phone Management System Launcher
REM This script starts the Phone Management System application

echo.
echo ========================================
echo   Phone Management System
echo ========================================
echo.
echo Starting application...
echo.

REM Run the application
python app.py

REM If there's an error, pause so user can see it
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERROR: Application failed to start
    echo ========================================
    echo.
    echo Please check:
    echo 1. Python is installed
    echo 2. All dependencies are installed
    echo 3. Database is initialized
    echo.
    pause
)
