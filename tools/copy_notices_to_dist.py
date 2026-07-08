import json
import os
import shutil
import sys


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    build_config_path = os.path.join(project_root, "build_config.json")
    if not os.path.exists(build_config_path):
        print("ERROR: build_config.json not found")
        sys.exit(1)

    with open(build_config_path, "r", encoding="utf-8") as f:
        build_config = json.load(f)

    version = build_config.get("version", "0.0.0")
    dist_dir_name = f"autodoor-pro-{version}"
    dist_dir = os.path.join(project_root, "dist", dist_dir_name)

    if not os.path.exists(dist_dir):
        print(f"ERROR: dist directory not found: {dist_dir}")
        sys.exit(1)

    notices = ["NOTICE.txt", "THIRD_PARTY_LICENSES.txt"]
    for notice in notices:
        src = os.path.join(project_root, notice)
        dst = os.path.join(dist_dir, notice)
        if not os.path.exists(src):
            print(f"ERROR: {notice} not found in project root")
            sys.exit(1)
        shutil.copy2(src, dst)
        print(f"Copied {notice} to dist")


if __name__ == "__main__":
    main()
