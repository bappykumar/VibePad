@echo off
if exist "VibePad.exe" (
    start "" "VibePad.exe"
) else (
    start pythonw VibePad.py
)
exit
