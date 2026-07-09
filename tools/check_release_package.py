#!/usr/bin/env python
"""
检查发布包安全
"""
import argparse
import os
import sys


def find_files(root_dir: str, extensions: set) -> list:
    found = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in extensions:
                found.append(os.path.relpath(os.path.join(dirpath, fname), root_dir))
    return found


def main():
    parser = argparse.ArgumentParser(description="Check release package")
    parser.add_argument("--release-dir", required=True, help="发布目录")
    args = parser.parse_args()

    release_dir = os.path.normpath(args.release_dir)
    if not os.path.exists(release_dir):
        print(f"Error: release dir not found: {release_dir}")
        exit(1)

    ok = True

    source_exts = {".py", ".cs", ".sln", ".csproj"}
    leaked = find_files(release_dir, source_exts)
    if leaked:
        print("FAIL: Source code files found in release:")
        for f in leaked:
            print(f"  {f}")
        ok = False

    key_exts = {".pem", ".key", ".pfx", ".p12"}
    leaked_keys = find_files(release_dir, key_exts)
    if leaked_keys:
        print("FAIL: Key files found in release:")
        for f in leaked_keys:
            print(f"  {f}")
        ok = False

    leaked_env = find_files(release_dir, {".env"})
    if leaked_env:
        print("FAIL: .env files found in release")
        ok = False

    if ok:
        print("PASS: Release package check OK")
    else:
        exit(1)


if __name__ == "__main__":
    main()
