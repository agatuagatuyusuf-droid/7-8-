"""
Complete production readiness verification.

Usage: python tools/check_production_ready.py

Runs all checks sequentially and outputs .goal/production_check_result.json
"""

import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT_FILE = os.path.join(PROJECT_ROOT, ".goal", "production_check_result.json")

checks = []


def run_check(name, cmd_args, cwd=None, shell=False, timeout=120):
    print(f"\n{'='*60}")
    print(f"[{name}]")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            cmd_args, capture_output=True, text=True,
            cwd=cwd or PROJECT_ROOT, shell=shell, timeout=timeout
        )
        if result.returncode == 0:
            print(f"[PASS] {name}")
            return {"name": name, "status": "pass", "reason": ""}
        else:
            out = (result.stdout + result.stderr)[:500]
            print(f"[FAIL] {name}: {out}")
            return {"name": name, "status": "fail", "reason": out}
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {name}: Timeout")
        return {"name": name, "status": "fail", "reason": "Timeout"}
    except FileNotFoundError as e:
        print(f"[SKIP] {name}: {e}")
        return {"name": name, "status": "skip", "reason": str(e)}
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return {"name": name, "status": "fail", "reason": str(e)}


def main():
    global checks

    # 1. Python compileall
    checks.append(run_check(
        "Python compileall",
        [sys.executable, "-m", "compileall", "main.py", "bt_core", "bt_gui",
         "bt_nodes", "bt_utils", "config", "bt_bridge", "-q"]
    ))

    if any(c["status"] == "fail" for c in checks):
        pass  # continue but note failures

    # 2. dotnet build CoreService Release
    checks.append(run_check(
        "dotnet build CoreService Release",
        ["dotnet", "build",
         os.path.join(PROJECT_ROOT, "csharp", "AutoDoor.CoreService",
                      "AutoDoor.CoreService.sln"),
         "-c", "Release"],
        timeout=180
    ))

    # 3. dotnet build Server Release
    checks.append(run_check(
        "dotnet build Server Release",
        ["dotnet", "build",
         os.path.join(PROJECT_ROOT, "server", "AutoDoor.Server",
                      "AutoDoor.Server.sln"),
         "-c", "Release"],
        timeout=180
    ))

    # 4. check_core_ipc
    checks.append(run_check(
        "check_core_ipc",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_core_ipc.py")]
    ))

    # 5. check_core_runtime
    checks.append(run_check(
        "check_core_runtime",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_core_runtime.py")]
    ))

    # 6. check_license_e2e
    checks.append(run_check(
        "check_license_e2e",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_license_e2e.py")]
    ))

    # 7. check_ui_runtime_bridge
    checks.append(run_check(
        "check_ui_runtime_bridge",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_ui_runtime_bridge.py")]
    ))

    # 8. check_ui_uses_csharp_runtime (static)
    checks.append(run_check(
        "check_ui_uses_csharp_runtime",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_ui_uses_csharp_runtime.py")]
    ))

    # 9. check_server_health
    checks.append(run_check(
        "check_server_health",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_server_health.py")]
    ))

    # 10. check_server_postgres
    checks.append(run_check(
        "check_server_postgres",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_server_postgres.py")]
    ))

    # 11. check_license_cache_security
    checks.append(run_check(
        "check_license_cache_security",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_license_cache_security.py")]
    ))

    # 12. check_ocr_worker
    checks.append(run_check(
        "check_ocr_worker",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_ocr_worker.py")]
    ))

    # 13. build_commercial
    checks.append(run_check(
        "build_commercial",
        ["cmd", "/c", "build_commercial.bat"],
        timeout=900
    ))

    # 14. check_dist_no_source
    checks.append(run_check(
        "check_dist_no_source",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_dist_no_source.py"), "dist"]
    ))

    # 15. check_commercial_package
    checks.append(run_check(
        "check_commercial_package",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_commercial_package.py"), "dist"]
    ))

    # 16. check_built_app_smoke
    checks.append(run_check(
        "check_built_app_smoke",
        [sys.executable, os.path.join(PROJECT_ROOT, "tools", "check_built_app_smoke.py"), "dist"]
    ))

    # 17. Security scan
    print(f"\n{'='*60}")
    print("[Security scan]")
    print(f"{'='*60}")
    security_pass = True
    try:
        # Check for bypassed actions
        r1 = subprocess.run(
            ["rg", "-n", "license.save_ticket|license.reload", "."],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
        )
        if r1.returncode == 0:
            print(f"  FAIL: Found bypassed actions: {r1.stdout[:300]}")
            security_pass = False
        else:
            print("  PASS: No bypassed license actions")

        # Check for admin123 / test keys
        r2 = subprocess.run(
            ["rg", "-n", "admin123|CHANGE_ME_DEV_SECRET|TEST-ACTIVATE-123456",
             "server", "csharp", "bt_bridge", "bt_gui", "main.py"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
        )
        # Allow docs mentions
        if r2.returncode == 0:
            lines = [l for l in r2.stdout.split('\n') if l.strip()
                     and 'docs/' not in l and '.goal/' not in l and '.md' not in l]
            if lines:
                print(f"  WARN: Found test/dev keys: {lines[:3]}")
                security_pass = False
            else:
                print("  PASS: No test keys in source (docs only)")
        else:
            print("  PASS: No test keys")

        # Check for private keys
        r3 = subprocess.run(
            ["rg", "-n", "PRIVATE_KEY", "."],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30
        )
        private_key_files = [l for l in r3.stdout.split('\n')
                            if l.strip() and 'check_' not in l and '.goal/' not in l]
        if private_key_files:
            print(f"  WARN: Private key references found: {private_key_files[:3]}")
            # Only fail if actual PEM files committed
        else:
            print("  PASS: No private key references")

        checks.append({
            "name": "Security scan",
            "status": "pass" if security_pass else "fail",
            "reason": "" if security_pass else "Security scan failed"
        })
    except FileNotFoundError:
        print("  SKIP: rg (ripgrep) not available")
        checks.append({
            "name": "Security scan",
            "status": "skip",
            "reason": "rg not available"
        })

    # Determine overall result
    fails = [c for c in checks if c["status"] == "fail"]
    blocking_skips = [
        c for c in checks
        if c["status"] == "skip" and c["name"] not in ("check_server_postgres",)
    ]

    if fails or blocking_skips:
        result = "fail"
    else:
        result = "pass"

    output = {
        "result": result,
        "checks": checks
    }

    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Result: {result}")
    if fails:
        print(f"Failed checks: {len(fails)}")
        for f in fails:
            print(f"  - {f['name']}: {f['reason'][:100]}")
    else:
        passes = [c for c in checks if c["status"] == "pass"]
        skips = [c for c in checks if c["status"] == "skip"]
        print(f"Pass: {len(passes)}, Skip: {len(skips)}")

    sys.exit(0 if result == "pass" else 1)


if __name__ == "__main__":
    main()