@echo off
REM Setup JARVIS to Auto-Start on Windows Boot
REM This script configures Windows Task Scheduler

echo ========================================
echo JARVIS Auto-Start Setup
echo ========================================
echo.
echo This will configure JARVIS to start automatically when Windows boots.
echo.
echo Choose installation method:
echo 1. Task Scheduler (Recommended - most reliable)
echo 2. Startup Folder (Quick - simple shortcut)
echo 3. Show manual instructions
echo 4. Cancel
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto task_scheduler
if "%choice%"=="2" goto startup_folder
if "%choice%"=="3" goto manual
if "%choice%"=="4" goto cancel

:task_scheduler
echo.
echo Installing JARVIS as Scheduled Task...
echo.

REM Import the task
schtasks /Create /XML "%~dp0config\task_scheduler_jarvis.xml" /TN "JARVIS_Assistant" /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ SUCCESS! JARVIS is now configured to start on boot.
    echo.
    echo To test: Open Task Scheduler and run "JARVIS_Assistant"
    echo To disable: Task Scheduler ^> Disable "JARVIS_Assistant"
    echo To remove: Task Scheduler ^> Delete "JARVIS_Assistant"
) else (
    echo.
    echo ✗ FAILED! You may need administrator rights.
    echo Try running this script as Administrator.
)
goto end

:startup_folder
echo.
echo Creating startup shortcut...
echo.

REM Get startup folder
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create shortcut using PowerShell
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP%\JARVIS.lnk'); $s.TargetPath = '%~dp0start_jarvis_background.bat'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'JARVIS Voice Assistant'; $s.Save()"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ SUCCESS! Shortcut created in Startup folder.
    echo.
    echo JARVIS will start when you log in to Windows.
    echo To disable: Delete the shortcut from Startup folder
    echo Location: %STARTUP%
) else (
    echo.
    echo ✗ FAILED! Could not create shortcut.
)
goto end

:manual
echo.
echo ========================================
echo MANUAL INSTALLATION INSTRUCTIONS
echo ========================================
echo.
echo METHOD 1: Task Scheduler (Recommended)
echo ----------------------------------------
echo 1. Open Task Scheduler (search in Start Menu)
echo 2. Click "Import Task" in the right panel
echo 3. Browse to: %~dp0config\task_scheduler_jarvis.xml
echo 4. Click "Import"
echo 5. Edit the task and verify paths
echo 6. Click OK
echo.
echo METHOD 2: Startup Folder (Simple)
echo ----------------------------------
echo 1. Press Win+R, type: shell:startup
echo 2. Create a shortcut to:
echo    %~dp0start_jarvis_background.bat
echo 3. Name it "JARVIS"
echo.
echo METHOD 3: NSSM Service (Advanced)
echo ----------------------------------
echo 1. Download NSSM from: https://nssm.cc/
echo 2. Extract to C:\nssm\
echo 3. Open Command Prompt as Admin
echo 4. Run:
echo    C:\nssm\win64\nssm.exe install JarvisService ^
echo      "C:\Python313\python.exe" ^
echo      "%~dp0src\background\system_tray.py"
echo 5. Run: nssm start JarvisService
echo.
goto end

:cancel
echo.
echo Installation cancelled.
goto end

:end
echo.
pause
