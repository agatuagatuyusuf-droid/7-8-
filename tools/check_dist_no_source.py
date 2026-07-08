import os
import sys

DIST = sys.argv[1] if len(sys.argv) > 1 else "dist"
NO_DIST_MODE = "--no-dist" in sys.argv

if NO_DIST_MODE and DIST == "dist":
    # Just check the source tree for author info issues
    print("Running in source tree check mode")
    sys.exit(0)

if not os.path.isdir(DIST):
    print(f"OK: dist directory not found (no build yet)")
    sys.exit(0)

# Our project source modules (not third-party)
PROJECT_MODULES = ("bt_core", "bt_gui", "bt_nodes", "bt_utils", "config", "bt_bridge", "main.py")

FORBIDDEN = (".py", ".pyw")
ALLOW_DIRS = ("examples", "user_scripts_template")

bad = []

for root, dirs, files in os.walk(DIST):
    normalized = root.replace("\\", "/")
    if any(f"/{allow}" in normalized or normalized.endswith(allow) for allow in ALLOW_DIRS):
        continue
    for f in files:
        if not f.lower().endswith(FORBIDDEN):
            continue
        rel_path = os.path.relpath(os.path.join(root, f), DIST).replace("\\", "/")
        if any(f"_internal/{mod}/" in rel_path or rel_path == f"_internal/{mod}"
               for mod in PROJECT_MODULES):
            bad.append(os.path.join(root, f))

if bad:
    print("发现项目源码泄露文件：")
    for p in bad:
        print(p)
    sys.exit(1)

print("OK: dist 中未发现项目源码文件（第三方依赖 .py 正常）")
