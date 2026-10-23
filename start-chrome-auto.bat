@echo off
setlocal

set "HUNTER_PROFILE=%USERPROFILE%\.chrome-hunter"

:: 1. Check if Chrome debugging port 9222 is already active
netstat -ano | findstr /R /C:":9222 .*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Chrome Hunter is already running and listening on port 9222.
    goto :open_url
)

:: 2. Locate Chrome executable
set "CHROME_BIN="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
)

if "%CHROME_BIN%"=="" (
    echo [ERROR] Chrome executable was not found in standard paths.
    pause
    exit /b 1
)

echo Starting Chrome with dedicated Hunter Profile on port 9222...
start "" "%CHROME_BIN%" --remote-debugging-port=9222 --user-data-dir="%HUNTER_PROFILE%" --remote-allow-origins=* "https://www.instagram.com"
echo Done!
exit /b 0

:open_url
echo Bringing Instagram to focus...
start "" "https://www.instagram.com"
exit /b 0