@echo off
title VibePad Setup
color 0A

echo Setting up VibePad auto-start...
echo.

:: Get current directory
set "APP_DIR=%~dp0"
set "PYTHON_SCRIPT=%APP_DIR%VibePad.py"
set "VBS_SCRIPT=%APP_DIR%VibePad_Silent.vbs"

:: Create VBS launcher
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo WshShell.Run "pythonw ""%PYTHON_SCRIPT%""", 0, False >> "%VBS_SCRIPT%"

:: Shortcut path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\VibePad.lnk"

:: Create shortcut via PowerShell
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_SCRIPT%\"'; $s.WorkingDirectory = '%APP_DIR%'; $s.Description = 'VibePad'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo Done! VibePad will now start with Windows.
) else (
    echo Error: Could not create shortcut.
)

echo.
pause


