@echo off
title VibePad Cleaner
echo ============================================
echo      VIBEPAD CLEANER & RESETTER
echo ============================================
echo.
echo Stopping VibePad and Control Panel...
taskkill /f /im python.exe /t >nul 2>&1
taskkill /f /im pythonw.exe /t >nul 2>&1
taskkill /f /im VibePad.exe /t >nul 2>&1
taskkill /f /im VibePad_Control_Panel.exe /t >nul 2>&1
taskkill /f /im VibePad_Control_Panel.py /t >nul 2>&1

echo.
echo Deleting all saved notes...
if exist "%APPDATA%\VibePad\notes.json" (
    del /f /q "%APPDATA%\VibePad\notes.json"
    echo [SUCCESS] All notes removed from AppData.
) else (
    echo [INFO] No saved notes found to delete.
)

echo.
echo ============================================
echo Done! Application closed and data cleared.
echo ============================================
pause
