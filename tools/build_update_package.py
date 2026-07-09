#!/usr/bin/env python
"""
构建更新包 (zip)
"""
import argparse
import os
import shutil
import zipfile


def main():
    parser = argparse.ArgumentParser(description="Build update package")
    parser.add_argument("--dist-dir", required=True, help="dist 目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--version", required=True, help="版本号")
    parser.add_argument("--platform", default="win-x64", help="平台")
    args = parser.parse_args()

    dist_dir = os.path.normpath(args.dist_dir)
    output_dir = os.path.normpath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    zip_name = f"AutoDoorPro-{args.version}-{args.platform}.zip"
    zip_path = os.path.join(output_dir, zip_name)

    if not os.path.exists(dist_dir):
        print(f"Error: dist dir not found: {dist_dir}")
        exit(1)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(dist_dir):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]
            for fname in filenames:
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, dist_dir)
                zf.write(full_path, rel_path)

    print(f"Update package: {zip_path} ({os.path.getsize(zip_path)} bytes)")


if __name__ == "__main__":
    main()
