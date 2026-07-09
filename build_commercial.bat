@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/11] Clean old build
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo [2/11] Generate build info
python generate_build_info.py
if errorlevel 1 exit /b 1

echo [3/11] Python compile checks
python -m compileall main.py bt_core bt_gui bt_nodes bt_utils config bt_bridge
if errorlevel 1 exit /b 1

echo [4/11] Build CoreService
dotnet build csharp/AutoDoor.CoreService/AutoDoor.CoreService.sln -c Release
if errorlevel 1 exit /b 1

echo [5/11] Publish CoreService
dotnet publish csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/AutoDoor.CoreService.csproj -c Release -r win-x64 --self-contained false
if errorlevel 1 exit /b 1

echo [6/11] Build OCRWorker
pyinstaller tools/ocr_worker.spec --clean --distpath build\ocr_worker --workpath build\ocr_worker_build
if errorlevel 1 exit /b 1

echo [7/11] Build Python UI
pyinstaller autodoor_bt_commercial.spec --clean
if errorlevel 1 exit /b 1

echo [8/11] Copy CoreService to dist
python tools/copy_core_service_to_dist.py
if errorlevel 1 exit /b 1

echo [8b/11] Copy OCRWorker to dist
xcopy /E /I /Y build\ocr_worker\OCRWorker .\dist\autodoor-pro-*\OCRWorker\
if errorlevel 1 exit /b 1

echo [9/11] Copy legal notices
python tools/copy_notices_to_dist.py
if errorlevel 1 exit /b 1

echo [10/11] Validate package
python tools/check_dist_no_source.py dist
if errorlevel 1 exit /b 1
python tools/check_commercial_package.py dist
if errorlevel 1 exit /b 1

echo [11/11] Built app smoke test
python tools/check_built_app_smoke.py dist
if errorlevel 1 exit /b 1

echo Commercial build completed.
pause
