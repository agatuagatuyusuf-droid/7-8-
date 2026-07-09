@echo off
setlocal enabledelayedexpansion

REM AutoDoor Pro 一键发布

if "%1"=="" goto usage
if "%2"=="" goto usage
if "%3"=="" goto usage

set VERSION=%1
set PRIVATE_KEY=%2
set OBFUSCATOR=%3

python tools\release_pipeline.py ^
  --version %VERSION% ^
  --channel stable ^
  --platform win-x64 ^
  --mode release ^
  --private-key "%PRIVATE_KEY%" ^
  --obfuscator-path "%OBFUSCATOR%"

if errorlevel 1 (
    echo Release failed.
    exit /b 1
)

echo Release OK.
exit /b 0

:usage
echo Usage: build_release.bat ^<version^> ^<private_key_path^> ^<obfuscator_path^>
echo.
echo Example:
echo   build_release.bat 1.6.1 "%%APPDATA%%\AutoDoorProPublisher\keys\release_private.pem" "D:\Tools\Obfuscator\obfuscator.exe"
exit /b 1
