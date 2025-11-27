Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
desktopPath = WshShell.SpecialFolders("Desktop")
shortcutPath = desktopPath & "\Phone Management System.lnk"

Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = currentDir & "\START_APPLICATION.bat"
shortcut.WorkingDirectory = currentDir
shortcut.Description = "Phone Management System"
shortcut.WindowStyle = 1

iconPath = currentDir & "\app_icon.ico"
If fso.FileExists(iconPath) Then
    shortcut.IconLocation = iconPath & ",0"
End If

shortcut.Save

WScript.Echo "Desktop shortcut created successfully!"
