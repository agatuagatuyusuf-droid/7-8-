param(
    [string]$ToolDir = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

if ([string]::IsNullOrWhiteSpace($ToolDir)) {
    $ToolDir = Join-Path $ProjectRoot "tools\.dotnet-tools"
}

Write-Host "AutoDoor Pro - Install Obfuscar"
Write-Host "ToolDir: $ToolDir"

$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
if (-not $dotnet) {
    Write-Host "ERROR: dotnet CLI not found"
    exit 1
}

New-Item -ItemType Directory -Force -Path $ToolDir | Out-Null

$existing = Get-ChildItem -Path $ToolDir -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -ieq "obfuscar.exe" -or
        $_.Name -ieq "obfuscar.console.exe" -or
        $_.Name -ieq "Obfuscar.Console.exe" -or
        $_.Name -ilike "*obfuscar*"
    } |
    Select-Object -First 1

if ($existing) {
    Write-Host "Obfuscar already exists: $($existing.FullName)"
    exit 0
}

Write-Host "Installing Obfuscar.GlobalTool..."
dotnet tool install Obfuscar.GlobalTool --tool-path "$ToolDir" --version 2.2.50

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: dotnet tool install failed"
    exit 1
}

$found = Get-ChildItem -Path $ToolDir -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -ieq "obfuscar.exe" -or
        $_.Name -ieq "obfuscar.console.exe" -or
        $_.Name -ieq "Obfuscar.Console.exe" -or
        $_.Name -ilike "*obfuscar*"
    } |
    Select-Object -First 1

if (-not $found) {
    Write-Host "ERROR: Obfuscar installed but executable not found"
    exit 1
}

Write-Host "Obfuscar installed: $($found.FullName)"
exit 0
