@echo off
REM Interactive Database Cleaning Utility

echo.
echo ========================================
echo   Database Cleaning Utility
echo ========================================
echo.
echo This tool helps you remove test/sample data
echo and prepare for real data entry.
echo.
echo Features:
echo   • Shows current database statistics
echo   • Creates automatic backup
echo   • Choose what to delete
echo   • Safe and reversible
echo.
pause

python clean_database.py

echo.
pause
