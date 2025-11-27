@echo off
REM Phone Management System - One-Click Installer and Launcher
REM This script installs, sets up, and runs the application

echo.
echo ========================================
echo   Phone Management System
echo   One-Click Installer
echo ========================================
echo.

REM Check if already installed by looking for shop.db
if exist "shop.db" (
    echo ✅ Application already installed!
    echo.
    echo Starting application...
    echo.
    python app.py
    if errorlevel 1 (
        echo.
        echo ❌ Error starting application
        echo Please check that Python is installed correctly
        pause
    )
    exit /b 0
)

REM First-time installation
echo 📦 First-time installation detected
echo.
echo This will:
echo   1. Install required Python packages
echo   2. Initialize the database
echo   3. Create a desktop shortcut
echo   4. Start the application
echo.
pause

echo.
echo ========================================
echo   Step 1/4: Installing Dependencies
echo ========================================
echo.
echo Installing Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ Failed to install dependencies
    echo.
    echo Please check:
    echo   • Python is installed
    echo   • Python is added to PATH
    echo   • You have internet connection
    echo.
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully
echo.

echo ========================================
echo   Step 2/4: Initializing Database
echo ========================================
echo.
python db_init.py
if errorlevel 1 (
    echo.
    echo ❌ Failed to initialize database
    pause
    exit /b 1
)
echo ✅ Database initialized successfully
echo.

echo ========================================
echo   Step 3/4: Creating Desktop Shortcut
echo ========================================
echo.
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $desktopPath = [Environment]::GetFolderPath('Desktop'); $currentDir = Get-Location; $shortcutPath = \"$desktopPath\Phone Management System.lnk\"; $shortcut = $WshShell.CreateShortcut($shortcutPath); $shortcut.TargetPath = \"$currentDir\INSTALL_AND_RUN.bat\"; $shortcut.WorkingDirectory = \"$currentDir\"; $shortcut.Description = 'Phone Management System'; $shortcut.IconLocation = \"$currentDir\app_icon.ico,0\"; $shortcut.Save()"
if errorlevel 1 (
    echo ⚠️  Could not create desktop shortcut
    echo You can still run the application from this folder
) else (
    echo ✅ Desktop shortcut created successfully
)
echo.

echo ========================================
echo   Step 4/4: Starting Application
echo ========================================
echo.
echo Installation complete! Starting application...
echo.
echo ========================================
echo   Default Login Credentials
echo ========================================
echo   Username: admin
echo   Password: admin123
echo.
echo ⚠️  IMPORTANT: Change this password immediately after first login!
echo     (Settings → Users → Change Password)
echo.
echo ========================================
echo.
echo From now on, you can:
echo   • Double-click the desktop shortcut
echo   • Or run this file again
echo.
pause

echo.
echo Starting application...
echo.
python app.py

if errorlevel 1 (
    echo.
    echo ❌ Error starting application
    pause
)
