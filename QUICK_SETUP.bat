@echo off
REM Quick Setup Script for Shop PC
REM Run this after downloading from GitHub

echo.
echo ========================================
echo   Phone Management System Setup
echo ========================================
echo.
echo This will set up the application on this PC.
echo.
pause

echo.
echo Step 1/4: Installing dependencies...
echo ----------------------------------------
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Make sure Python is installed and added to PATH
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully
echo.

echo Step 2/4: Initializing database...
echo ----------------------------------------
python db_init.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo ✅ Database initialized successfully
echo.

echo Step 3/4: Creating desktop shortcut...
echo ----------------------------------------
call CREATE_DESKTOP_SHORTCUT.bat
echo ✅ Desktop shortcut created
echo.

echo Step 4/4: Testing application...
echo ----------------------------------------
python -c "import app; print('✅ Application ready')"
if errorlevel 1 (
    echo ERROR: Application test failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo   Setup Complete! 🎉
echo ========================================
echo.
echo You can now run the application from:
echo   • Desktop shortcut: "Phone Management System"
echo   • Or double-click: START_APPLICATION.bat
echo.
echo ========================================
echo   Default Login Credentials
echo ========================================
echo   Username: admin
echo   Password: admin123
echo.
echo ⚠️  IMPORTANT: Change this password immediately after first login!
echo.
echo ========================================
echo   Next Steps
echo ========================================
echo   1. Double-click the desktop shortcut
echo   2. Login with admin/admin123
echo   3. Go to Settings → Users → Change Password
echo   4. Configure shop details in Settings
echo   5. Add your products in Inventory
echo   6. Start making sales!
echo.
echo ========================================
echo   Need Help?
echo ========================================
echo   • Read: HOW_TO_RUN.md
echo   • Read: DEPLOYMENT_TO_SHOP_PC.md
echo   • Read: README.md
echo.
pause
