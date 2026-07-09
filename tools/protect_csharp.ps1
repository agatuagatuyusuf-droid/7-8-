param(
    [string]$InputDir = "",
    [string]$OutputDir = "",
    [string]$ObfuscatorPath = "",
    [string]$Mode = "release",
    [bool]$AllowCopyFallback = $false
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

function Write-Step([string]$Message) {
    Write-Host "[protect_csharp] $Message"
}

function Copy-DirectoryClean([string]$Source, [string]$Destination) {
    if (Test-Path $Destination) {
        Remove-Item -Recurse -Force $Destination
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
}

function Resolve-Obfuscar([string]$ExplicitPath) {
    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        if (Test-Path $ExplicitPath) {
            return (Resolve-Path $ExplicitPath).Path
        }
        throw "ObfuscatorPath does not exist: $ExplicitPath"
    }

    $findScript = Join-Path $ScriptDir "find_obfuscar.ps1"
    if (Test-Path $findScript) {
        $result = & powershell -ExecutionPolicy Bypass -File $findScript -ProjectRoot $ProjectRoot
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($result)) {
            $candidate = ($result | Select-Object -Last 1).Trim()
            if (Test-Path $candidate) {
                return (Resolve-Path $candidate).Path
            }
        }
    }

    return ""
}

function Write-ObfuscarConfig([string]$ConfigPath, [string]$InputDirectory, [string]$OutputDirectory) {
    $inputFull = (Resolve-Path $InputDirectory).Path
    $outputFull = $OutputDirectory

    New-Item -ItemType Directory -Force -Path $outputFull | Out-Null

    $mainExe = Join-Path $inputFull "AutoDoor.CoreService.exe"
    $mainDll = Join-Path $inputFull "AutoDoor.CoreService.dll"

    $moduleFile = ""
    if (Test-Path $mainExe) {
        $moduleFile = $mainExe
    } elseif (Test-Path $mainDll) {
        $moduleFile = $mainDll
    } else {
        throw "AutoDoor.CoreService.exe/dll not found in input dir: $InputDirectory"
    }

    $xml = @"
<?xml version="1.0" encoding="utf-8"?>
<Obfuscator>
  <Var name="InPath" value="$inputFull" />
  <Var name="OutPath" value="$outputFull" />
  <Var name="KeepPublicApi" value="false" />
  <Var name="HidePrivateApi" value="true" />
  <Var name="RenameProperties" value="true" />
  <Var name="RenameEvents" value="true" />
  <Var name="RenameFields" value="true" />
  <Var name="UseUnicodeNames" value="true" />
  <Var name="HideStrings" value="true" />
  <Module file="$moduleFile">
    <SkipType name="AutoDoor.CoreService.Program" />
  </Module>
</Obfuscator>
"@

    Set-Content -Path $ConfigPath -Value $xml -Encoding UTF8
}

function Invoke-Obfuscar([string]$ObfuscarExe, [string]$ConfigPath) {
    Write-Step "Running Obfuscar: $ObfuscarExe"
    Write-Step "Config: $ConfigPath"

    & $ObfuscarExe $ConfigPath

    if ($LASTEXITCODE -ne 0) {
        throw "Obfuscar failed with exit code $LASTEXITCODE"
    }
}

function Verify-Output([string]$OutputDirectory) {
    $exe = Join-Path $OutputDirectory "AutoDoor.CoreService.exe"
    $dll = Join-Path $OutputDirectory "AutoDoor.CoreService.dll"

    if (-not (Test-Path $exe) -and -not (Test-Path $dll)) {
        throw "Obfuscated output missing AutoDoor.CoreService.exe/dll: $OutputDirectory"
    }

    $files = Get-ChildItem -Path $OutputDirectory -File -Recurse
    if (-not $files -or $files.Count -eq 0) {
        throw "Obfuscated output is empty: $OutputDirectory"
    }

    Write-Step "Output verified: $OutputDirectory"
}

if ([string]::IsNullOrWhiteSpace($InputDir)) {
    throw "InputDir is required"
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    throw "OutputDir is required"
}

if (-not (Test-Path $InputDir)) {
    throw "InputDir not found: $InputDir"
}

$Mode = $Mode.ToLowerInvariant()

Write-Step "Mode: $Mode"
Write-Step "InputDir: $InputDir"
Write-Step "OutputDir: $OutputDir"

$obfuscar = ""
try {
    $obfuscar = Resolve-Obfuscar $ObfuscatorPath
} catch {
    if ($Mode -eq "release") {
        throw
    }
    Write-Step "dev mode Obfuscar resolve failed: $_"
}

if ([string]::IsNullOrWhiteSpace($obfuscar)) {
    if ($Mode -eq "release") {
        throw "release mode requires real Obfuscar. Copy fallback disabled."
    }

    if ($AllowCopyFallback -or $Mode -eq "dev") {
        Write-Step "dev mode: Obfuscar not found, using copy fallback. This is NOT real obfuscation."
        Copy-DirectoryClean $InputDir $OutputDir
        Verify-Output $OutputDir
        exit 0
    }

    throw "Obfuscar not found and copy fallback not allowed"
}

$tempRoot = Join-Path $ProjectRoot "tools\.obfuscar-temp"
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

$stamp = Get-Date -Format "yyyyMMddHHmmss"
$configPath = Join-Path $tempRoot "AutoDoor.CoreService.$stamp.obfuscar.tmp.xml"

Write-ObfuscarConfig -ConfigPath $configPath -InputDirectory $InputDir -OutputDirectory $OutputDir
Invoke-Obfuscar -ObfuscarExe $obfuscar -ConfigPath $configPath
Verify-Output $OutputDir

Write-Step "REAL_OBFUSCAR_COMPLETED"
exit 0
