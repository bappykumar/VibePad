@echo off
title VibePad Cleanup
color 0C

echo Removing VibePad auto-start...
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

if exist "%STARTUP_FOLDER%\VibePad.lnk" (
    del "%STARTUP_FOLDER%\VibePad.lnk"
    echo Success: VibePad removed from startup.
)

if exist "%STARTUP_FOLDER%\StickyNotes.lnk" (
    del "%STARTUP_FOLDER%\StickyNotes.lnk"
    echo Success: Legacy shortcut removed.
)

echo.
echo Done.
pause


