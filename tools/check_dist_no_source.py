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

PROJECT_MODULES = (
    "bt_core",
    "bt_gui",
    "bt_nodes",
    "bt_utils",
    "config",
    "bt_bridge",
    "main.py",
)

ALLOW_DIRS = (
    "examples",
    "user_scripts_template",
)

ALLOWED_SENSITIVE_REL_PATHS = {
    "_internal/certifi/cacert.pem",
}

FORBIDDEN_EXTENSIONS = (
    ".py",
    ".pyw",
    ".cs",
    ".csproj",
    ".sln",
    ".env",
    ".pem",
    ".key",
)

FORBIDDEN_NAME_PARTS = (
    "private_key",
    "server_private",
    "license_private",
    "合同",
    "授权书",
)

bad = []

for root, dirs, files in os.walk(DIST):
    normalized_root = root.replace("\\", "/")

    if any(
        f"/{allow}" in normalized_root or normalized_root.endswith(allow)
        for allow in ALLOW_DIRS
    ):
        continue

    for filename in files:
        lower_name = filename.lower()
        full_path = os.path.join(root, filename)
        rel_path = os.path.relpath(full_path, DIST).replace("\\", "/")
        rel_lower = rel_path.lower()

        if rel_path in ALLOWED_SENSITIVE_REL_PATHS or rel_lower.endswith("/certifi/cacert.pem"):
            continue

        if any(part in lower_name for part in FORBIDDEN_NAME_PARTS):
            bad.append(full_path)
            continue

        if not lower_name.endswith(FORBIDDEN_EXTENSIONS):
            continue

        if lower_name.endswith((".cs", ".csproj", ".sln", ".env", ".pem", ".key")):
            bad.append(full_path)
            continue

        if lower_name.endswith((".py", ".pyw")):
            if any(
                f"_internal/{mod}/" in rel_path or rel_path == f"_internal/{mod}"
                for mod in PROJECT_MODULES
            ):
                bad.append(full_path)

if bad:
    print("发现项目源码或敏感文件泄露：")
    for path in bad:
        print(path)
    sys.exit(1)

print("OK: dist 中未发现项目源码或敏感文件")
sys.exit(0)
