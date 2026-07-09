#!/usr/bin/env python
import os
import subprocess
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND_SCRIPT = os.path.join(PROJECT_ROOT, "tools", "find_obfuscar.ps1")


def main() -> int:
    if not os.path.exists(FIND_SCRIPT):
        print("FAIL: tools/find_obfuscar.ps1 missing")
        return 1

    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                FIND_SCRIPT,
                "-ProjectRoot",
                PROJECT_ROOT,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as exc:
        print(f"FAIL: find_obfuscar.ps1 execution error: {exc}")
        return 1

    if result.returncode != 0:
        print("WARN: Obfuscar not found. Run tools/install_obfuscar.ps1 to install free Obfuscar.")
        return 0

    path = result.stdout.strip().splitlines()[-1].strip() if result.stdout.strip() else ""
    if not path or not os.path.exists(path):
        print(f"FAIL: Obfuscar path invalid: {path}")
        return 1

    print(f"PASS: Obfuscar found: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
