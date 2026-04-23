@echo off
title VibePad Setup
color 0A

echo Setting up VibePad auto-start...
echo.

:: Get current directory
set "APP_DIR=%~dp0"
set "EXE_FILE=%APP_DIR%VibePad.exe"
set "PYTHON_SCRIPT=%APP_DIR%VibePad.py"
set "VBS_SCRIPT=%APP_DIR%VibePad_Silent.vbs"

:: Shortcut path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\VibePad.lnk"

if exist "%EXE_FILE%" (
    echo VibePad EXE found. Creating direct shortcut...
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%EXE_FILE%'; $s.WorkingDirectory = '%APP_DIR%'; $s.Description = 'VibePad'; $s.Save()"
) else (
    echo VibePad EXE not found. Creating VBS launcher for Python script...
    :: Create VBS launcher
    echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
    echo WshShell.Run "pythonw ""%PYTHON_SCRIPT%""", 0, False >> "%VBS_SCRIPT%"
    
    :: Create shortcut via PowerShell
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_SCRIPT%\"'; $s.WorkingDirectory = '%APP_DIR%'; $s.Description = 'VibePad'; $s.Save()"
)

if exist "%SHORTCUT_PATH%" (
    echo Done! VibePad will now start with Windows.
) else (
    echo Error: Could not create shortcut.
)

echo.
pause


