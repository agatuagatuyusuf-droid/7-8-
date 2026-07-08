@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Building AutoDoor.CoreService...
echo.

dotnet restore src\AutoDoor.CoreService\AutoDoor.CoreService.csproj
if errorlevel 1 exit /b 1

dotnet build src\AutoDoor.CoreService\AutoDoor.CoreService.csproj -c Release -r win-x64 --self-contained
if errorlevel 1 exit /b 1

echo.
echo Build completed.
echo Output: src\AutoDoor.CoreService\bin\Release\net8.0\win-x64\AutoDoor.CoreService.exe
pause
