#!/usr/bin/env python
"""
检查更新系统完整性
"""
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    full = os.path.join(PROJECT_ROOT, path)
    if os.path.exists(full):
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def file_exists(path):
    return os.path.exists(os.path.join(PROJECT_ROOT, path))


def main():
    checks = []

    required = [
        ("bt_gui/dialogs/update_dialog.py", "update dialog exists"),
        ("bt_utils/update_service.py", "update service exists"),
        ("bt_utils/update_downloader.py", "update downloader exists"),
        ("bt_utils/update_verifier.py", "update verifier exists"),
        ("bt_utils/update_paths.py", "update paths exists"),
        ("bt_utils/update_agent_launcher.py", "update agent launcher exists"),
        ("bt_utils/release_signature.py", "release signature exists"),
        ("tools/update_agent.py", "update agent exists"),
        ("tools/release_publisher_ui.py", "publisher UI exists"),
        ("tools/release_pipeline.py", "release pipeline exists"),
        ("tools/generate_manifest.py", "generate manifest exists"),
        ("tools/sign_manifest.py", "sign manifest exists"),
        ("tools/verify_manifest.py", "verify manifest exists"),
        ("tools/build_update_package.py", "build update package exists"),
        ("tools/protect_csharp.ps1", "protect csharp exists"),
        ("tools/check_release_package.py", "check release package exists"),
        ("build_release.bat", "build release bat exists"),
    ]

    for path, name in required:
        checks.append((name, file_exists(path)))

    tools_dir = os.path.join(PROJECT_ROOT, "tools")
    private_key_in_tools = os.path.exists(os.path.join(tools_dir, "release_private.pem"))
    checks.append(("private key not in repo", not private_key_in_tools))

    svc = read("bt_utils/update_service.py")
    checks.append(("manifest signature verification exists", "verify_manifest_signature" in svc))

    dl = read("bt_utils/update_downloader.py")
    checks.append(("https only download check exists", "https://" in dl and "ValueError" in dl))

    pub_path = os.path.join(PROJECT_ROOT, "dist", "release_publisher_ui.py")
    checks.append(("publisher ui not copied to dist", not os.path.exists(pub_path)))

    ok = True
    for name, result in checks:
        print(("PASS" if result else "FAIL") + ": " + name)
        if not result:
            ok = False

    if not ok:
        sys.exit(1)
    print("check_update_system OK")


if __name__ == "__main__":
    main()
