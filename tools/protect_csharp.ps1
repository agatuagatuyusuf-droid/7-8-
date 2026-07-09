param(
  [string]$InputDir,
  [string]$OutputDir,
  [string]$ObfuscatorPath,
  [string]$Mode = "release",
  [bool]$AllowCopyFallback = $false
)

$ErrorActionPreference = "Stop"

Write-Host "protect_csharp.ps1"
Write-Host "  InputDir: $InputDir"
Write-Host "  OutputDir: $OutputDir"
Write-Host "  ObfuscatorPath: $ObfuscatorPath"
Write-Host "  Mode: $Mode"
Write-Host "  AllowCopyFallback: $AllowCopyFallback"

# Check input exists
$csExe = Join-Path $InputDir "AutoDoor.CoreService.exe"
if (-not (Test-Path $csExe)) {
    Write-Host "ERROR: CoreService exe not found: $csExe"
    if ($Mode -eq "release") { exit 1 }
    else { Write-Host "WARNING: dev mode, continuing without CoreService" }
}

# Create output dir
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if ($Mode -eq "release") {
    if (-not (Test-Path $ObfuscatorPath)) {
        Write-Host "ERROR: Obfuscator not found: $ObfuscatorPath"
        Write-Host "release mode cannot skip obfuscation"
        exit 1
    }

    # TODO: 在这里接入实际混淆器命令
    # Example with ConfuserEx:
    # & $ObfuscatorPath -i $InputDir -o $OutputDir

    if (-not $AllowCopyFallback) {
        Write-Host "ERROR: release mode requires real obfuscator command. Copy fallback disabled."
        exit 1
    }

    Write-Host "WARNING: AllowCopyFallback enabled, copying unprotected files"
    Copy-Item "$InputDir\*" $OutputDir -Recurse -Force
} else {
    Write-Host "WARNING: dev mode, skipping obfuscation"
    Copy-Item "$InputDir\*" $OutputDir -Recurse -Force
}

$outExe = Join-Path $OutputDir "AutoDoor.CoreService.exe"
if (Test-Path $outExe) {
    Write-Host "Protected CoreService: $outExe"
} else {
    Write-Host "WARNING: Output exe not found, some files may have been copied"
}

exit 0
