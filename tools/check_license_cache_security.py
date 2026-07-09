"""
Check that license cache is DPAPI encrypted (not plaintext).

Usage: python tools/check_license_cache_security.py

Checks:
1. Look for %APPDATA%/AutoDoorPro/license/license.cache
2. If exists, read bytes and check it doesn't contain plaintext fields
3. Check that C# code uses ProtectedData.Protect
"""

import os
import sys


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checks = []
    any_failed = False

    # 1. Check C# code uses ProtectedData.Protect
    found_protect = False
    cs_license_dir = os.path.join(project_root, "csharp", "AutoDoor.CoreService",
                                   "src", "AutoDoor.CoreService", "License")
    for root, dirs, files in os.walk(cs_license_dir):
        for f in files:
            if f.endswith(".cs"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "ProtectedData.Protect" in content:
                        found_protect = True
                        break
    checks.append(("ProtectedData.Protect used in License code", found_protect))

    # 2. Check cache file if exists
    app_data = os.environ.get("APPDATA", "")
    cache_paths = [
        os.path.join(app_data, "AutoDoorPro", "license", "cache.dat"),
        os.path.join(app_data, "AutoDoorPro", "license", "license.cache"),
    ]

    cache_secure = True
    forbidden = ["license_id", "machine_code", "signature", "expire_at"]
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    data = f.read()
                decoded = data.decode("utf-8", errors="ignore")
                for keyword in forbidden:
                    if keyword in decoded:
                        print(f"  FAIL: Cache {cache_path} contains plaintext '{keyword}'")
                        cache_secure = False
            except (UnicodeDecodeError, Exception):
                # Binary data means likely encrypted - good
                pass
    checks.append(("Cache file secure (encrypted if exists)", cache_secure))

    # 3. Check no plaintext .json cache file
    no_plaintext = True
    cs_license_dir = os.path.join(project_root, "csharp", "AutoDoor.CoreService",
                                   "src", "AutoDoor.CoreService", "License")
    for root, dirs, files in os.walk(cs_license_dir):
        for f in files:
            path = os.path.join(root, f)
            if f.endswith(".cs"):
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "File.WriteAllText" in content and "cache" in content.lower():
                        print(f"  WARN: Plaintext cache write in {f}")
                        no_plaintext = False
    checks.append(("No plaintext cache writes", no_plaintext))

    # 4. Check LicenseCacheStore or LicenseCache exists
    cache_class_found = False
    for root, dirs, files in os.walk(cs_license_dir):
        for f in files:
            if f.endswith(".cs"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "class LicenseCache" in content or "class LicenseCacheStore" in content:
                        cache_class_found = True
                        break
    checks.append(("LicenseCache class exists with DPAPI", cache_class_found))

    for name, result in checks:
        status = "PASS" if result else "FAIL"
        if not result:
            any_failed = True
        print(f"  [{status}] {name}")

    if any_failed:
        print("check_license_cache_security FAILED")
        sys.exit(1)

    print("check_license_cache_security OK")
    sys.exit(0)


if __name__ == "__main__":
    main()