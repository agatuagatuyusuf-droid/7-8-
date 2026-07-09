#!/usr/bin/env python
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path: str) -> str:
    full = os.path.join(PROJECT_ROOT, path)
    if not os.path.exists(full):
        return ""
    with open(full, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def exists(path: str) -> bool:
    return os.path.exists(os.path.join(PROJECT_ROOT, path))


def main() -> int:
    checks = []

    checks.append(("install_obfuscar exists", exists("tools/install_obfuscar.ps1")))
    checks.append(("find_obfuscar exists", exists("tools/find_obfuscar.ps1")))
    checks.append(("check_obfuscar_available exists", exists("tools/check_obfuscar_available.py")))

    protect = read("tools/protect_csharp.ps1")
    checks.append(("protect uses Obfuscar", "Obfuscar" in protect and "REAL_OBFUSCAR_COMPLETED" in protect))
    checks.append(("release requires real Obfuscar", "release mode requires real Obfuscar" in protect))
    checks.append(("dev fallback is explicit", "This is NOT real obfuscation" in protect))
    checks.append(("protect generates obfuscar config", "Write-ObfuscarConfig" in protect))
    checks.append(("protect invokes obfuscar", "Invoke-Obfuscar" in protect))
    checks.append(("protect verifies output", "Verify-Output" in protect))
    checks.append(("protect targets CoreService dll first", "Obfuscar module target" in protect and "AutoDoor.CoreService.dll not found. Refusing to obfuscate only apphost exe" in protect))
    checks.append(("protect verifies obfuscated dll hash changed", "Verify-ObfuscatedDllChanged" in protect and "OBFUSCATED_DLL_HASH_CHANGED" in protect))
    checks.append(("protect fails if dll hash unchanged", "Obfuscation verification failed: output AutoDoor.CoreService.dll hash equals input DLL hash" in protect))
    checks.append(("protect has sha256 helper", "Get-FileSha256" in protect and "Get-FileHash -Algorithm SHA256" in protect))
    checks.append(("protect does not prefer exe over dll", "if (Test-Path $mainExe) {\n        $moduleFile = $mainExe" not in protect))

    ui = read("tools/release_publisher_ui.py")
    checks.append(("publisher has install Obfuscar button", "安装 Obfuscar" in ui))
    checks.append(("publisher has _install_obfuscar", "_install_obfuscar" in ui))
    checks.append(("publisher has _auto_detect_obfuscator", "_auto_detect_obfuscator" in ui))
    checks.append(("publisher references install script", "install_obfuscar.ps1" in ui))
    checks.append(("publisher references find script", "find_obfuscar.ps1" in ui))

    pipeline = read("tools/release_pipeline.py")
    checks.append(("pipeline prepares protected dist", "copy_full_dist_for_protection" in pipeline and "protected_dist_dir" in pipeline))
    checks.append(("pipeline packages protected dist", "generate_update_package(" in pipeline and "protected_dist_dir" in pipeline))
    checks.append(("pipeline does not package raw dist after protect", "generate_update_package(\n        protected_dist_dir" in pipeline or "generate_update_package(protected_dist_dir" in pipeline))
    checks.append(("pipeline verifies zip protected core", "verify_update_zip_contains_protected_core" in pipeline and "VERIFY_UPDATE_ZIP_CONTAINS_PROTECTED_CORE_OK" in pipeline))
    checks.append(("pipeline compares zip dll hash with protected dll", "zip_dll_hash" in pipeline and "protected_dll_hash" in pipeline))
    checks.append(("pipeline checks CoreService zip entries", "CoreService/AutoDoor.CoreService.dll" in pipeline and "CoreService/appsettings.json" in pipeline))

    protect = read("tools/protect_csharp.ps1")
    checks.append(("protect copies full CoreService before obfuscation", "Preparing full CoreService output directory before Obfuscar" in protect and "Copy-DirectoryClean $InputDir $OutputDir" in protect))
    checks.append(("protect verifies runtimeconfig", "AutoDoor.CoreService.runtimeconfig.json" in protect))
    checks.append(("protect verifies deps json", "AutoDoor.CoreService.deps.json" in protect))
    checks.append(("protect verifies appsettings", "appsettings.json" in protect))

    ui = read("tools/release_publisher_ui.py")
    checks.append(("publisher avoids false obfuscator missing log", "Obfuscar 已自动识别" in ui and "elif obfus_already_found" in ui))

    gitignore = read(".gitignore")
    checks.append(("dotnet tools ignored", "tools/.dotnet-tools/" in gitignore))
    checks.append(("obfuscar temp ignored", "tools/.obfuscar-temp/" in gitignore))

    ok = True
    for name, result in checks:
        print(("PASS" if result else "FAIL") + ": " + name)
        if not result:
            ok = False

    if not ok:
        return 1

    print("check_obfuscar_integration OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
