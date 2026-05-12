@echo off
echo ============================================================
echo   VibePad v3.0.0 - Professional Build Script
echo ============================================================
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt pyinstaller
echo.
echo Building VibePad_v3.0.0.exe with v3.0.0 metadata...
pyinstaller --noconsole --onefile --name VibePad_v3.0.0 --version-file=version_info.txt --icon=NONE VibePad.py
echo.
echo Cleaning up build artifacts...
if exist VibePad_v3.0.0.exe del VibePad_v3.0.0.exe
move dist\VibePad_v3.0.0.exe .\
rd /s /q build
rd /s /q dist
del VibePad_v3.0.0.spec
echo.
echo ============================================================
echo   Build Complete! VibePad_v3.0.0.exe is now in the root.
echo ============================================================
pause
