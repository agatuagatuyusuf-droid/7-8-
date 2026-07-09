@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/2] Check dist directory exists
if not exist "dist\autodoor-pro-*" (
    echo ERROR: dist directory not found. Run build_commercial.bat first.
    exit /b 1
)

echo [2/2] Build installer
if not exist "installer\AutoDoorPro.iss" (
    echo ERROR: installer/AutoDoorPro.iss not found
    exit /b 1
)

where iscc >nul 2>nul
if errorlevel 1 (
    echo Inno Setup not found, installer build skipped.
    echo Install Inno Setup from https://jrsoftware.org/isdl.php
    exit /b 0
)

iscc installer\AutoDoorPro.iss
if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed
    exit /b 1
)

echo Installer built successfully: dist\installers\AutoDoorPro-*-Setup.exe
pause
