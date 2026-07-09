import os
import sys

DIST = sys.argv[1] if len(sys.argv) > 1 else "dist"
ALLOW_MISSING_DIST = "--allow-missing-dist" in sys.argv

if not os.path.isdir(DIST):
    if ALLOW_MISSING_DIST:
        print(f"SKIP: dist directory not found: {DIST}")
        sys.exit(0)
    print(f"FAIL: dist directory not found: {DIST}")
    sys.exit(1)

# Source extensions to detect leaks
FORBIDDEN_EXTENSIONS = (".py", ".pyw", ".cs", ".csproj", ".sln", ".env", ".pem", ".key")

# Our project source modules (not third-party)
PROJECT_MODULES = ("bt_core", "bt_gui", "bt_nodes", "bt_utils", "config", "bt_bridge", "main.py")

ALLOW_DIRS = ("examples", "user_scripts_template")

bad = []

for root, dirs, files in os.walk(DIST):
    normalized = root.replace("\\", "/")
    if any(f"/{allow}" in normalized or normalized.endswith(allow) for allow in ALLOW_DIRS):
        continue
    for f in files:
        if not f.lower().endswith(FORBIDDEN_EXTENSIONS):
            continue
        # .cs/.csproj/.sln/.env/.pem/.key are always forbidden
        if f.lower().endswith((".cs", ".csproj", ".sln", ".env", ".pem", ".key")):
            bad.append(os.path.join(root, f))
            continue
        rel_path = os.path.relpath(os.path.join(root, f), DIST).replace("\\", "/")
        if any(f"_internal/{mod}/" in rel_path or rel_path == f"_internal/{mod}"
               for mod in PROJECT_MODULES):
            bad.append(os.path.join(root, f))

if bad:
    print("发现项目源码/敏感文件泄露：")
    for p in bad:
        print(p)
    sys.exit(1)

print("OK: dist 中未发现项目源码或敏感文件")
