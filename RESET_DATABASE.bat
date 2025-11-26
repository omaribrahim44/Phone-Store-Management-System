@echo off
REM Reset Database - Remove all test data and start fresh

echo.
echo ========================================
echo   Database Reset Utility
echo ========================================
echo.
echo This will DELETE ALL DATA and create a fresh database.
echo.
echo ⚠️  WARNING: This action CANNOT be undone!
echo.
echo What will be deleted:
echo   • All products/inventory
echo   • All sales records
echo   • All customers
echo   • All repair orders
echo   • All users (except admin)
echo   • All audit logs
echo.
echo The admin user will be recreated with:
echo   Username: admin
echo   Password: admin123
echo.
set /p confirm="Are you sure you want to continue? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo.
    echo Operation cancelled.
    echo.
    pause
    exit /b 0
)

echo.
echo Creating backup before reset...
python -c "import shutil; import datetime; shutil.copy('shop.db', f'backups/before_reset_{datetime.datetime.now().strftime(\"%%Y%%m%%d_%%H%%M%%S\")}.db'); print('✅ Backup created')"

echo.
echo Resetting database...
python db_init.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Database reset failed
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Database Reset Complete! ✅
echo ========================================
echo.
echo Your database is now clean and ready for data entry.
echo.
echo Default login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo ⚠️  IMPORTANT: Change the admin password after login!
echo.
echo Next steps:
echo   1. Start the application
echo   2. Login with admin/admin123
echo   3. Change admin password
echo   4. Configure shop details in Settings
echo   5. Start adding your real data
echo.
pause
