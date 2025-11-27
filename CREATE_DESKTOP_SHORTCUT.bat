@echo off
REM Create Desktop Shortcut for Phone Management System
REM This creates a shortcut on the desktop with the app icon

echo.
echo ========================================
echo   Creating Desktop Shortcut
echo ========================================
echo.

REM Use PowerShell to create the shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $desktopPath = [Environment]::GetFolderPath('Desktop'); $currentDir = Get-Location; $shortcutPath = \"$desktopPath\Phone Management System.lnk\"; $shortcut = $WshShell.CreateShortcut($shortcutPath); $shortcut.TargetPath = \"$currentDir\START_APPLICATION.bat\"; $shortcut.WorkingDirectory = \"$currentDir\"; $shortcut.Description = 'Phone Management System'; $shortcut.IconLocation = \"$currentDir\app_icon.ico,0\"; $shortcut.Save()"

if errorlevel 1 (
    echo ❌ Failed to create shortcut
    pause
    exit /b 1
)

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
