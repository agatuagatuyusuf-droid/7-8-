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

    ui = read("tools/release_publisher_ui.py")
    checks.append(("publisher has install Obfuscar button", "安装 Obfuscar" in ui))
    checks.append(("publisher has _install_obfuscar", "_install_obfuscar" in ui))
    checks.append(("publisher has _auto_detect_obfuscator", "_auto_detect_obfuscator" in ui))
    checks.append(("publisher references install script", "install_obfuscar.ps1" in ui))
    checks.append(("publisher references find script", "find_obfuscar.ps1" in ui))

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
