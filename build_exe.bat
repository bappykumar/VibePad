@echo off
title VibePad EXE Builder
color 0B

echo ============================================
echo      VIBEPAD EXE BUILDER (NO PYTHON MODE)
echo ============================================
echo.

:: Check for PyInstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller is not installed!
    echo.
    echo Please run: pip install pyinstaller
    echo Then try running this builder again.
    echo.
    pause
    exit /b
)

echo [1/2] Building VibePad.exe...
pyinstaller --noconsole --onefile --icon=NONE VibePad.py

echo.
echo [2/2] Building VibePad_Control_Panel.exe...
pyinstaller --noconsole --onefile --icon=NONE VibePad_Control_Panel.py

echo.
echo ============================================
echo      CLEANING UP TEMPORARY FILES...
echo ============================================
:: Move EXEs to main folder and cleanup
if exist "dist\VibePad.exe" (
    move /y "dist\VibePad.exe" ".\VibePad.exe"
)
if exist "dist\VibePad_Control_Panel.exe" (
    move /y "dist\VibePad_Control_Panel.exe" ".\VibePad_Control_Panel.exe"
)

:: Remove build artifacts
rd /s /q build
rd /s /q dist
del /f /q VibePad.spec
del /f /q VibePad_Control_Panel.spec

echo.
echo [SUCCESS] Your Python-free VibePad is ready!
echo You can now use VibePad.exe and VibePad_Control_Panel.exe.
echo.
pause
