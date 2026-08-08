@echo off
REM JARVIS Background Service Launcher
REM This script starts JARVIS in background mode

echo ========================================
echo Starting JARVIS Background Service
echo ========================================
echo.
echo Options:
echo 1. System Tray Mode (recommended)
echo 2. Console Mode with Wake Word
echo 3. Console Mode with Hotkey Only
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo Starting System Tray Mode...
    echo Right-click tray icon for options
    echo Press CTRL+ALT+J to activate
    python src\background\system_tray.py
) else if "%choice%"=="2" (
    echo Starting Console Mode with Wake Word...
    echo Say "Hi Jarvis" to activate
    python src\background\jarvis_daemon.py
) else if "%choice%"=="3" (
    echo Starting Console Mode (Hotkey Only)...
    echo Press CTRL+ALT+J to activate
    python src\background\jarvis_daemon.py --no-wake-word
) else (
    echo Invalid choice!
    pause
    exit /b 1
)
