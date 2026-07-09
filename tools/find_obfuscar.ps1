param(
    [string]$ProjectRoot = ""
)

$ErrorActionPreference = "SilentlyContinue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $ScriptDir
}

$candidates = @(
    (Join-Path $ProjectRoot "tools\.dotnet-tools"),
    (Join-Path $env:USERPROFILE ".dotnet\tools"),
    "D:\Tools\Obfuscator",
    "D:\Tools\ConfuserEx",
    "C:\Tools\Obfuscator",
    "C:\Tools\ConfuserEx",
    "C:\Program Files\Obfuscar",
    "C:\Program Files (x86)\Obfuscar"
)

$names = @(
    "obfuscar.exe",
    "obfuscar.console.exe",
    "Obfuscar.Console.exe",
    "Confuser.CLI.exe"
)

foreach ($dir in $candidates) {
    if ([string]::IsNullOrWhiteSpace($dir)) {
        continue
    }

    if (-not (Test-Path $dir)) {
        continue
    }

    foreach ($name in $names) {
        $direct = Join-Path $dir $name
        if (Test-Path $direct) {
            Write-Host $direct
            exit 0
        }
    }

    $found = Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -ieq "obfuscar.exe" -or
            $_.Name -ieq "obfuscar.console.exe" -or
            $_.Name -ieq "Obfuscar.Console.exe" -or
            $_.Name -ieq "Confuser.CLI.exe"
        } |
        Select-Object -First 1

    if ($found) {
        Write-Host $found.FullName
        exit 0
    }
}

exit 1
