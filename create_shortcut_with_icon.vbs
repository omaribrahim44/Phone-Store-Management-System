' Create Desktop Shortcut with Custom Icon
' This creates a professional shortcut on the desktop

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get current directory
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Desktop path
desktopPath = WshShell.SpecialFolders("Desktop")

' Shortcut path
shortcutPath = desktopPath & "\Phone Management System.lnk"

' Create shortcut
Set shortcut = WshShell.CreateShortcut(shortcutPath)

' Set properties
shortcut.TargetPath = currentDir & "\START_APPLICATION.bat"
shortcut.WorkingDirectory = currentDir
shortcut.Description = "Phone Management System - Shop Management Application"
shortcut.WindowStyle = 1

' Try to set icon (if icon file exists)
iconPath = currentDir & "\app_icon.ico"
If fso.FileExists(iconPath) Then
    shortcut.IconLocation = iconPath & ",0"
End If

' Save shortcut
shortcut.Save

' Show success message
WScript.Echo "✅ Desktop shortcut created successfully!" & vbCrLf & vbCrLf & _
             "Shortcut name: Phone Management System" & vbCrLf & _
             "Location: Desktop" & vbCrLf & vbCrLf & _
             "Double-click the shortcut to start the application!"
