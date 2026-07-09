@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo AutoDoor Pro 发布中心
echo ========================================
echo.
echo 正在启动内部加密发布工具...
echo.

python tools\release_publisher_ui.py

if errorlevel 1 (
    echo.
    echo 启动失败，请确认 Python 环境和依赖是否安装。
    pause
    exit /b 1
)

exit /b 0
