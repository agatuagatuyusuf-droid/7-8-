#!/usr/bin/env python
"""
AutoDoor Pro 一键发布流水线

Usage:
  python tools/release_pipeline.py --version 1.6.1 --mode release
  python tools/release_pipeline.py --version 1.6.1 --mode dev
"""
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from typing import List


TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TOOLS_DIR)


def log(msg: str):
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        print(line)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def run_step(name: str, fn, *args, **kwargs) -> bool:
    log(f"\u25b6 {name}...")
    try:
        result = fn(*args, **kwargs)
        if result:
            log(f"\u2713 {name} \u5b8c\u6210")
        else:
            log(f"\u2717 {name} \u5931\u8d25")
        return result
    except Exception as e:
        log(f"\u2717 {name} \u5f02\u5e38: {e}")
        return False


def check_git_clean() -> bool:
    result = subprocess.run(["git", "status", "--porcelain"],
                            capture_output=True, text=True, cwd=PROJECT_ROOT)
    if result.stdout.strip():
        log("Git \u5de5\u4f5c\u533a\u4e0d\u5e72\u51c0\uff0c\u8bf7\u5148\u63d0\u4ea4\u6216 stash")
        return False
    return True


def check_private_key(private_key_path: str) -> bool:
    if not private_key_path or not os.path.exists(private_key_path):
        log(f"\u79c1\u94a5\u4e0d\u5b58\u5728: {private_key_path}")
        return False
    return True


def check_obfuscator(obfuscator_path: str, mode: str) -> bool:
    if mode == "release":
        if not obfuscator_path or not os.path.exists(obfuscator_path):
            log(f"\u6df7\u6dc6\u5668\u672a\u914d\u7f6e: {obfuscator_path}")
            log("release \u6a21\u5f0f\u5fc5\u987b\u914d\u7f6e\u6df7\u6dc6\u5668")
            return False
    else:
        if not obfuscator_path or not os.path.exists(obfuscator_path):
            log("WARNING: \u6df7\u6dc6\u5668\u672a\u914d\u7f6e\uff0cdev \u6a21\u5f0f\u8df3\u8fc7\u6df7\u6dc6")
    return True


def build_commercial() -> bool:
    bat_path = os.path.join(PROJECT_ROOT, "build_commercial.bat")
    if not os.path.exists(bat_path):
        log(f"build_commercial.bat \u4e0d\u5b58\u5728: {bat_path}")
        return False
    result = subprocess.run([bat_path], cwd=PROJECT_ROOT, shell=True)
    return result.returncode == 0


def copy_full_dist_for_protection(source_dist_dir: str, protected_dist_dir: str) -> bool:
    if not os.path.exists(source_dist_dir):
        log(f"dist 目录不存在: {source_dist_dir}")
        return False

    if os.path.exists(protected_dist_dir):
        shutil.rmtree(protected_dist_dir)

    shutil.copytree(source_dist_dir, protected_dist_dir)
    log(f"protected dist prepared: {protected_dist_dir}")
    return True


def protect_csharp(input_dir: str, output_dir: str, obfuscator_path: str, mode: str) -> bool:
    ps1_path = os.path.join(TOOLS_DIR, "protect_csharp.ps1")
    if not os.path.exists(ps1_path):
        log(f"protect_csharp.ps1 \u4e0d\u5b58\u5728: {ps1_path}")
        return False

    cmd = [
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1_path,
        "-InputDir", input_dir,
        "-OutputDir", output_dir,
        "-ObfuscatorPath", obfuscator_path,
        "-Mode", mode,
    ]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode == 0


def generate_update_package(dist_dir: str, output_dir: str, version: str, platform: str) -> bool:
    script = os.path.join(TOOLS_DIR, "build_update_package.py")
    if not os.path.exists(script):
        log(f"build_update_package.py \u4e0d\u5b58\u5728")
        return False
    result = subprocess.run([
        sys.executable, script,
        "--dist-dir", dist_dir,
        "--output-dir", output_dir,
        "--version", version,
        "--platform", platform,
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0


def verify_update_zip_contains_protected_core(update_dir: str, version: str, platform: str, protected_dist_dir: str) -> bool:
    zip_name = f"AutoDoorPro-{version}-{platform}.zip"
    zip_path = os.path.join(update_dir, zip_name)

    if not os.path.exists(zip_path):
        log(f"update zip 不存在: {zip_path}")
        return False

    protected_core_dir = os.path.join(protected_dist_dir, "CoreService")
    protected_dll = os.path.join(protected_core_dir, "AutoDoor.CoreService.dll")
    protected_runtimeconfig = os.path.join(protected_core_dir, "AutoDoor.CoreService.runtimeconfig.json")
    protected_deps = os.path.join(protected_core_dir, "AutoDoor.CoreService.deps.json")
    protected_appsettings = os.path.join(protected_core_dir, "appsettings.json")

    required_files = [
        protected_dll,
        protected_runtimeconfig,
        protected_deps,
        protected_appsettings,
    ]

    for required in required_files:
        if not os.path.exists(required):
            log(f"protected CoreService 缺少文件: {required}")
            return False

    required_zip_entries = [
        "CoreService/AutoDoor.CoreService.dll",
        "CoreService/AutoDoor.CoreService.runtimeconfig.json",
        "CoreService/AutoDoor.CoreService.deps.json",
        "CoreService/appsettings.json",
    ]

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = set(zf.namelist())

            for entry in required_zip_entries:
                if entry not in names:
                    log(f"update zip 缺少 CoreService 文件: {entry}")
                    return False

            zip_dll_bytes = zf.read("CoreService/AutoDoor.CoreService.dll")
            zip_dll_hash = hashlib.sha256(zip_dll_bytes).hexdigest()
            protected_dll_hash = sha256_file(protected_dll)

            log(f"Zip CoreService DLL SHA256: {zip_dll_hash}")
            log(f"Protected CoreService DLL SHA256: {protected_dll_hash}")

            if zip_dll_hash != protected_dll_hash:
                log("update zip 内 CoreService DLL 与 protected_dist_dir 不一致")
                return False

    except Exception as exc:
        log(f"校验 update zip 失败: {exc}")
        return False

    log("VERIFY_UPDATE_ZIP_CONTAINS_PROTECTED_CORE_OK")
    return True


def generate_manifest(update_dir: str, version: str, channel: str, platform: str,
                      mandatory: bool, min_supported: str, notes: List[str]) -> bool:
    script = os.path.join(TOOLS_DIR, "generate_manifest.py")
    if not os.path.exists(script):
        log(f"generate_manifest.py \u4e0d\u5b58\u5728")
        return False

    notes_file = os.path.join(update_dir, "..", "release_notes.json")
    with open(notes_file, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False)

    result = subprocess.run([
        sys.executable, script,
        "--update-dir", update_dir,
        "--version", version,
        "--channel", channel,
        "--platform", platform,
        "--mandatory", str(mandatory).lower(),
        "--min-supported", min_supported,
        "--notes-file", notes_file,
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0


def sign_manifest(manifest_path: str, private_key_path: str) -> bool:
    script = os.path.join(TOOLS_DIR, "sign_manifest.py")
    if not os.path.exists(script):
        log(f"sign_manifest.py \u4e0d\u5b58\u5728")
        return False
    result = subprocess.run([
        sys.executable, script,
        "--manifest", manifest_path,
        "--private-key", private_key_path,
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0


def verify_manifest_sig(manifest_path: str, sig_path: str, public_key_path: str = "") -> bool:
    script = os.path.join(TOOLS_DIR, "verify_manifest.py")
    if not os.path.exists(script):
        log(f"verify_manifest.py \u4e0d\u5b58\u5728")
        return False
    cmd = [
        sys.executable, script,
        "--manifest", manifest_path,
        "--sig", sig_path,
    ]
    if public_key_path:
        cmd.extend(["--public-key", public_key_path])
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode == 0


def check_release_package(release_dir: str) -> bool:
    script = os.path.join(TOOLS_DIR, "check_release_package.py")
    if not os.path.exists(script):
        log(f"check_release_package.py \u4e0d\u5b58\u5728")
        return False
    result = subprocess.run([
        sys.executable, script,
        "--release-dir", release_dir,
    ], cwd=PROJECT_ROOT)
    return result.returncode == 0


def generate_latest_json(update_dir: str, version: str, channel: str, platform: str,
                         mandatory: bool, notes: List[str],
                         manifest_url: str, sig_url: str, package_url: str) -> bool:
    import hashlib
    zip_file = f"AutoDoorPro-{version}-{platform}.zip"
    zip_path = os.path.join(update_dir, zip_file)
    zip_sha = ""
    if os.path.exists(zip_path):
        h = hashlib.sha256()
        with open(zip_path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        zip_sha = h.hexdigest()

    latest = {
        "app": "AutoDoor Pro",
        "channel": channel,
        "platform": platform,
        "latest_version": version,
        "mandatory": mandatory,
        "manifest_url": manifest_url,
        "signature_url": sig_url,
        "package_url": package_url,
        "package_sha256": zip_sha,
        "notes": notes,
    }

    latest_path = os.path.join(update_dir, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(latest, f, indent=2, ensure_ascii=False)
    log(f"latest.json -> {latest_path}")
    return True


def _derive_public_key_path(private_key_path: str) -> str:
    base = os.path.dirname(private_key_path)
    name = os.path.basename(private_key_path)
    pub_name = name.replace("_private.", "_public.")
    return os.path.join(base, pub_name)


def main():
    parser = argparse.ArgumentParser(description="AutoDoor Pro Release Pipeline")
    parser.add_argument("--version", required=True, help="\u7248\u672c\u53f7")
    parser.add_argument("--channel", default="stable", help="\u901a\u9053")
    parser.add_argument("--platform", default="win-x64", help="\u5e73\u53f0")
    parser.add_argument("--mode", default="release", choices=["release", "dev"], help="\u6a21\u5f0f")
    parser.add_argument("--mandatory", default="false", help="\u5f3a\u5236\u66f4\u65b0")
    parser.add_argument("--min-supported-version", default="1.6.0", help="\u6700\u4f4e\u652f\u6301\u7248\u672c")
    parser.add_argument("--notes-file", default="", help="\u66f4\u65b0\u8bf4\u660e\u6587\u4ef6")
    parser.add_argument("--private-key", default="", help="\u79c1\u94a5\u8def\u5f84")
    parser.add_argument("--obfuscator-path", default="", help="\u6df7\u6dc6\u5668\u8def\u5f84")
    parser.add_argument("--dist-dir", default="", help="dist \u76ee\u5f55")
    parser.add_argument("--release-dir", default="", help="release \u8f93\u51fa\u76ee\u5f55")
    parser.add_argument("--project-root", default=PROJECT_ROOT, help="\u9879\u76ee\u6839\u76ee\u5f55")
    parser.add_argument("--base-update-url", default="", help="\u66f4\u65b0\u670d\u52a1\u5668\u57fa\u7840 URL")
    parser.add_argument("--skip-git-check", action="store_true", help="\u8df3\u8fc7 git \u5de5\u4f5c\u533a\u68c0\u67e5\uff08\u53d1\u5e03\u6f14\u7ec3\u7528\uff09")
    parser.add_argument("--skip-build", action="store_true", help="\u8df3\u8fc7\u6784\u5efa\u6b65\u9aa4\uff08\u53d1\u5e03\u6f14\u7ec3\u7528\uff09")
    args = parser.parse_args()

    args.mandatory = args.mandatory.lower() in ("true", "1", "yes")

    steps = []
    if not args.skip_git_check:
        steps.append(("\u68c0\u67e5 Git \u5de5\u4f5c\u533a", check_git_clean))
    steps.extend([
        ("\u68c0\u67e5\u79c1\u94a5", lambda: check_private_key(args.private_key)),
        ("\u68c0\u67e5\u6df7\u6dc6\u5668", lambda: check_obfuscator(args.obfuscator_path, args.mode)),
    ])

    version = args.version
    platform = args.platform
    channel = args.channel
    mode = args.mode

    dist_dir = args.dist_dir or os.path.join(PROJECT_ROOT, "dist")
    release_base = args.release_dir or os.path.join(PROJECT_ROOT, "release")
    release_dir = os.path.join(release_base, f"AutoDoorPro-{version}")
    update_dir = os.path.join(release_dir, "update")
    os.makedirs(update_dir, exist_ok=True)
    protected_dist_dir = os.path.join(release_dir, "dist")

    notes = []
    if args.notes_file and os.path.exists(args.notes_file):
        with open(args.notes_file, "r", encoding="utf-8") as f:
            notes = json.load(f)

    # Parse steps
    if not args.skip_build:
        steps.append(("\u6784\u5efa\u5546\u4e1a\u5305", build_commercial))

    steps.append(("\u51c6\u5907\u53d7\u4fdd\u62a4 dist", lambda: copy_full_dist_for_protection(
        dist_dir,
        protected_dist_dir
    )))

    steps.append(("\u52a0\u5bc6/\u6df7\u6dc6\u5904\u7406", lambda: protect_csharp(
        os.path.join(dist_dir, "CoreService"),
        os.path.join(protected_dist_dir, "CoreService"),
        args.obfuscator_path,
        mode
    )))

    steps.append(("\u751f\u6210\u66f4\u65b0\u5305", lambda: generate_update_package(
        protected_dist_dir,
        update_dir,
        version,
        platform
    )))
    steps.append(("\u6821\u9a8c\u66f4\u65b0\u5305 CoreService \u4ea7\u7269", lambda: verify_update_zip_contains_protected_core(
        update_dir,
        version,
        platform,
        protected_dist_dir
    )))
    steps.append(("\u751f\u6210 Manifest", lambda: generate_manifest(
        update_dir, version, channel, platform,
        args.mandatory, args.min_supported_version, notes
    )))
    steps.append(("\u7b7e\u540d Manifest", lambda: sign_manifest(
        os.path.join(update_dir, "manifest.json"), args.private_key
    )))

    manifest_path = os.path.join(update_dir, "manifest.json")
    sig_path = os.path.join(update_dir, "manifest.sig")
    public_key_path = _derive_public_key_path(args.private_key)

    steps.append(("\u6821\u9a8c Manifest \u7b7e\u540d", lambda: verify_manifest_sig(manifest_path, sig_path, public_key_path)))
    steps.append(("\u68c0\u67e5\u53d1\u5e03\u5305", lambda: check_release_package(release_dir)))
    base_url = args.base_update_url.rstrip("/")
    if not base_url and mode == "release":
        log("release \u6a21\u5f0f\u5fc5\u987b\u63d0\u4f9b --base-update-url")
        sys.exit(1)

    manifest_url = ""
    sig_url = ""
    package_url = ""
    if base_url:
        zip_file_name = f"AutoDoorPro-{version}-{platform}.zip"
        manifest_url = f"{base_url}/manifest.json"
        sig_url = f"{base_url}/manifest.sig"
        package_url = f"{base_url}/{zip_file_name}"

    steps.append(("\u751f\u6210 latest.json", lambda: generate_latest_json(
        update_dir, version, channel, platform,
        args.mandatory, notes, manifest_url, sig_url, package_url,
    )))

    for name, fn in steps:
        if not run_step(name, fn):
            log("\u53d1\u5e03\u5931\u8d25")
            sys.exit(1)

    log(f"\n\u53d1\u5e03\u6210\u529f: {release_dir}")
    print(f"\n{release_dir}")
    sys.exit(0)


if __name__ == "__main__":
    main()
