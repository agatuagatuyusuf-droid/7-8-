import json
import os
import re
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/check_commercial_package.py <dist_dir>")
        sys.exit(1)

    dist_base = sys.argv[1]
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if not os.path.isdir(dist_base):
        print(f"FAIL: dist directory not found: {dist_base}")
        sys.exit(1)

    # Read version
    build_config_path = os.path.join(project_root, "build_config.json")
    if not os.path.exists(build_config_path):
        print("FAIL: build_config.json not found")
        sys.exit(1)

    with open(build_config_path, "r", encoding="utf-8") as f:
        build_config = json.load(f)

    version = build_config.get("version", "0.0.0")
    dist_dir_name = f"autodoor-pro-{version}"
    dist_dir = os.path.join(dist_base, dist_dir_name)

    checks = []

    # 1. dist directory exists
    checks.append(("dist dir exists", os.path.isdir(dist_base)))

    # 2. Version subdir exists
    checks.append(("version dir exists", os.path.isdir(dist_dir)))

    # 3. Main exe exists
    exe_name = f"autodoor-pro-{version}.exe"
    main_exe = os.path.join(dist_dir, exe_name)
    checks.append(("main exe exists", os.path.isfile(main_exe)))

    # 4. CoreService exe exists
    cs_exe = os.path.join(dist_dir, "CoreService", "AutoDoor.CoreService.exe")
    checks.append(("CoreService exe exists", os.path.isfile(cs_exe)))

    # 5. appsettings.json exists
    cs_config = os.path.join(dist_dir, "CoreService", "appsettings.json")
    checks.append(("CoreService appsettings.json", os.path.isfile(cs_config)))

    # 6. NOTICE.txt exists
    notice = os.path.join(dist_dir, "NOTICE.txt")
    checks.append(("NOTICE.txt exists", os.path.isfile(notice)))

    # 7. THIRD_PARTY_LICENSES.txt exists
    licenses = os.path.join(dist_dir, "THIRD_PARTY_LICENSES.txt")
    checks.append(("THIRD_PARTY_LICENSES.txt exists", os.path.isfile(licenses)))

    # 8. No plain .py source files (allow third-party in _internal/)
    PROJECT_MODULES = ("bt_core", "bt_gui", "bt_nodes", "bt_utils", "config", "bt_bridge", "main.py")
    py_leak = []
    for root, dirs, files in os.walk(dist_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(root, f), dist_dir).replace("\\", "/")
            if any(f"_internal/{mod}/" in rel or rel == f"_internal/{mod}"
                   for mod in PROJECT_MODULES):
                py_leak.append(os.path.join(root, f))
    checks.append(("no plain .py source", len(py_leak) == 0))

    # 9. No old author keywords
    author_pattern = re.compile(r"wdhq4261761|298117299|QQ群|B站|bilibili|space\.bilibili\.com|my\.feishu\.cn")
    found_author = False
    for root, dirs, files in os.walk(dist_dir):
        for f in files:
            if f.endswith((".txt", ".md", ".json", ".bat", ".cfg")):
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                        if author_pattern.search(content):
                            found_author = True
                            break
                except Exception:
                    pass
        if found_author:
            break
    checks.append(("no old author info", not found_author))

    # 10. No contracts / authorization / private keys / .env
    forbidden = [".env", ".pem", ".key"]
    allowed_rel = {"_internal/certifi/cacert.pem"}
    found_forbidden = False
    for root, dirs, files in os.walk(dist_dir):
        for f in files:
            for ext in forbidden:
                if not f.endswith(ext):
                    continue
                rel = os.path.relpath(os.path.join(root, f), dist_dir).replace("\\", "/")
                if rel not in allowed_rel:
                    found_forbidden = True
                    break
        if found_forbidden:
            break
    checks.append(("no contracts/keys/env", not found_forbidden))

    # 11. No .git directory
    git_dir = os.path.join(dist_dir, ".git")
    checks.append(("no .git directory", not os.path.isdir(git_dir)))

    all_pass = True
    for name, result in checks:
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"  [{status}] {name}")

    if all_pass:
        print("check_commercial_package OK")
        sys.exit(0)
    else:
        print("check_commercial_package FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
