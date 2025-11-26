@echo off
REM Create Desktop Shortcut for Phone Management System

echo Creating desktop shortcut...

set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=Phone Management System.lnk
set TARGET=%SCRIPT_DIR%START_APPLICATION.bat
set DESKTOP=%USERPROFILE%\Desktop

REM Create VBS script to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\%SHORTCUT_NAME%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%TARGET%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Phone Management System - Shop Management Application" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

REM Execute VBS script
cscript CreateShortcut.vbs

REM Clean up
del CreateShortcut.vbs

echo.
echo ========================================
echo   Desktop Shortcut Created!
echo ========================================
echo.
echo You can now find "Phone Management System"
echo shortcut on your desktop.
echo.
echo Double-click it to start the application!
echo.
pause
