@echo off
setlocal enabledelayedexpansion

REM AutoDoor Pro 一键发布

if "%1%"=="" (
    echo Usage: build_release.bat ^<version^>
    echo Example: build_release.bat 1.6.1
    exit /b 1
)

set VERSION=%1%

python tools\release_pipeline.py --version %VERSION% --channel stable --platform win-x64 --mode release

if errorlevel 1 (
    echo Release failed.
    exit /b 1
)

echo Release OK.
exit /b 0
