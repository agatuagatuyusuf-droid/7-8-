#!/usr/bin/env python
"""
生成 manifest.json
"""
import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_files_recursive(root_dir: str, base_dir: str) -> list:
    files = []
    root_dir = os.path.normpath(root_dir)
    base_dir = os.path.normpath(base_dir)

    forbidden_names = {"manifest.json", "manifest.sig", "latest.json", "release_notes.json"}
    forbidden_ext = {".zip", ".tmp", ".log", ".pyc", ".pyo"}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]

        for fname in sorted(filenames):
            if fname in forbidden_names:
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext in forbidden_ext:
                continue
            if fname.endswith((".tmp", ".log", ".pyc", ".pyo")):
                continue
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, base_dir)
            files.append({
                "path": rel_path,
                "sha256": sha256_file(full_path)
            })
    return files


def main():
    parser = argparse.ArgumentParser(description="Generate manifest.json")
    parser.add_argument("--update-dir", required=True, help="更新包目录")
    parser.add_argument("--version", required=True, help="版本号")
    parser.add_argument("--channel", default="stable", help="更新通道")
    parser.add_argument("--platform", default="win-x64", help="平台")
    parser.add_argument("--mandatory", default="false", help="强制更新")
    parser.add_argument("--min-supported", default="1.6.0", help="最低支持版本")
    parser.add_argument("--notes-file", default="", help="更新说明文件")
    args = parser.parse_args()

    update_dir = os.path.normpath(args.update_dir)
    if not os.path.exists(update_dir):
        print(f"Error: update-dir not found: {update_dir}")
        exit(1)

    zip_files = [f for f in os.listdir(update_dir) if f.endswith(".zip")]
    if not zip_files:
        print("Error: no zip file found in update dir")
        exit(1)

    zip_file = zip_files[0]
    zip_path = os.path.join(update_dir, zip_file)
    zip_sha = sha256_file(zip_path)
    zip_size = os.path.getsize(zip_path)

    stage_dir = tempfile.mkdtemp(prefix="autodoor_manifest_")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(stage_dir)

        files = get_files_recursive(stage_dir, stage_dir)
    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)

    notes = []
    if args.notes_file and os.path.exists(args.notes_file):
        with open(args.notes_file, "r", encoding="utf-8") as f:
            try:
                notes = json.load(f)
            except Exception:
                pass

    manifest = {
        "app": "AutoDoor Pro",
        "version": args.version,
        "channel": args.channel,
        "platform": args.platform,
        "release_date": "",
        "mandatory": args.mandatory.lower() in ("true", "1", "yes"),
        "min_supported_version": args.min_supported,
        "package": {
            "file": zip_file,
            "size": zip_size,
            "sha256": zip_sha
        },
        "files": files,
        "notes": notes
    }

    manifest_path = os.path.join(update_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"manifest.json -> {manifest_path}")


if __name__ == "__main__":
    main()
