@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/9] Clean old build
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo [2/9] Generate build info
python generate_build_info.py
if errorlevel 1 exit /b 1

echo [3/9] Python compile checks
python -m compileall main.py bt_core bt_gui bt_nodes bt_utils config bt_bridge
if errorlevel 1 exit /b 1

echo [4/9] Build CoreService
dotnet build csharp/AutoDoor.CoreService/AutoDoor.CoreService.sln -c Release
if errorlevel 1 exit /b 1

echo [5/9] Publish CoreService
dotnet publish csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/AutoDoor.CoreService.csproj -c Release -r win-x64 --self-contained false
if errorlevel 1 exit /b 1

echo [6/9] Build Python UI
pyinstaller autodoor_bt_commercial.spec --clean
if errorlevel 1 exit /b 1

echo [7/9] Copy CoreService to dist
python tools/copy_core_service_to_dist.py
if errorlevel 1 exit /b 1

echo [8/9] Copy legal notices
python tools/copy_notices_to_dist.py
if errorlevel 1 exit /b 1

echo [9/9] Validate package
python tools/check_dist_no_source.py dist
if errorlevel 1 exit /b 1
python tools/check_commercial_package.py dist
if errorlevel 1 exit /b 1

echo Commercial build completed.
pause
