@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo AutoDoor Pro - Commercial Build
echo ========================================
echo.

echo [1/6] Clean old build
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo [2/6] Generate build info
python generate_build_info.py
if errorlevel 1 exit /b 1

echo [3/6] Run unit smoke checks
python -m compileall main.py bt_core bt_gui bt_nodes bt_utils config
if errorlevel 1 exit /b 1

echo [4/6] Build commercial package
pyinstaller autodoor_bt_commercial.spec --clean
if errorlevel 1 exit /b 1

echo [5/6] Check source leakage
python tools/check_dist_no_source.py dist
if errorlevel 1 exit /b 1

echo [6/6] Done
pause
