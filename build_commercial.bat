@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/12] Clean old build
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo [2/12] Generate build info
python generate_build_info.py
if errorlevel 1 exit /b 1

echo [3/12] Python compile checks
python -m compileall main.py bt_core bt_gui bt_nodes bt_utils config bt_bridge
if errorlevel 1 exit /b 1

echo [4/12] Build CoreService
dotnet build csharp\AutoDoor.CoreService\AutoDoor.CoreService.sln -c Release
if errorlevel 1 exit /b 1

echo [5/12] Publish CoreService
dotnet publish csharp\AutoDoor.CoreService\src\AutoDoor.CoreService\AutoDoor.CoreService.csproj -c Release -r win-x64 --self-contained false
if errorlevel 1 exit /b 1

echo [6/12] Build OCRWorker
if not exist tools\ocr_worker.spec (
    echo ERROR: tools\ocr_worker.spec not found
    exit /b 1
)
pyinstaller tools\ocr_worker.spec --clean --distpath build\ocr_worker --workpath build\ocr_worker_build
if errorlevel 1 exit /b 1

if not exist build\ocr_worker\OCRWorker.exe (
    echo ERROR: OCRWorker.exe not found after PyInstaller build
    exit /b 1
)

echo [7/12] Build Python UI
pyinstaller autodoor_bt_commercial.spec --clean
if errorlevel 1 exit /b 1

echo [8/12] Copy CoreService and OCRWorker to dist
python tools\copy_core_service_to_dist.py
if errorlevel 1 exit /b 1

echo [9/12] Copy legal notices
python tools\copy_notices_to_dist.py
if errorlevel 1 exit /b 1

echo [10/12] Validate no source in dist
python tools\check_dist_no_source.py dist
if errorlevel 1 exit /b 1

echo [11/12] Validate commercial package
python tools\check_commercial_package.py dist
if errorlevel 1 exit /b 1

echo [12/12] Built app smoke test
python tools\check_built_app_smoke.py dist
if errorlevel 1 exit /b 1

echo Commercial build completed successfully.
exit /b 0
