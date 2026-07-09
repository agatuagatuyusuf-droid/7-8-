#!/usr/bin/env python
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")

sys.path.insert(0, PROJECT_ROOT)
from bt_utils.release_signature import generate_key_pair


def run(cmd, cwd=PROJECT_ROOT, timeout=1800):
    print(">>>", " ".join(cmd))
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout, encoding="utf-8", errors="replace", env=env)


def write_text(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def make_fake_dist(root: str):
    dist = os.path.join(root, "dist")
    core = os.path.join(dist, "CoreService")
    os.makedirs(core, exist_ok=True)

    write_text(os.path.join(dist, "AutoDoorPro.exe"), "fake app placeholder")
    write_text(os.path.join(core, "AutoDoor.CoreService.dll"), "fake core dll placeholder")
    write_text(os.path.join(core, "AutoDoor.CoreService.exe"), "fake apphost placeholder")
    write_text(os.path.join(core, "AutoDoor.CoreService.runtimeconfig.json"), "{}")
    write_text(os.path.join(core, "AutoDoor.CoreService.deps.json"), "{}")
    write_text(os.path.join(core, "appsettings.json"), "{}")

    return dist


def find_obfuscar():
    script = os.path.join(TOOLS_DIR, "find_obfuscar.ps1")
    if not os.path.exists(script):
        return ""

    result = subprocess.run([
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        script,
        "-ProjectRoot",
        PROJECT_ROOT,
    ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)

    if result.returncode != 0:
        return ""

    out = result.stdout.strip()
    return out.splitlines()[-1].strip() if out else ""


def main() -> int:
    temp_root = tempfile.mkdtemp(prefix="autodoor_release_drill_")
    report_path = os.path.join(PROJECT_ROOT, "docs", "RELEASE_DRILL_REPORT.md")

    result = {
        "time": datetime.now().isoformat(),
        "temp_root": temp_root,
        "dev_drill": {},
        "release_drill": {},
        "obfuscar_path": "",
    }

    try:
        dist_dir = make_fake_dist(temp_root)
        release_dir = os.path.join(temp_root, "release")
        private_key = os.path.join(temp_root, "keys", "release_private.pem")
        public_key = os.path.join(temp_root, "keys", "release_public.pem")
        notes_file = os.path.join(temp_root, "notes.json")

        write_text(notes_file, json.dumps(["release drill"], ensure_ascii=False))

        ok = generate_key_pair(private_key, public_key)
        result["key_generation"] = {"success": ok}

        if not ok:
            raise RuntimeError("generate_key_pair failed")

        dev_cmd = [
            sys.executable,
            os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", "9.9.9-test",
            "--channel", "internal",
            "--platform", "win-x64",
            "--mode", "dev",
            "--mandatory", "false",
            "--min-supported-version", "1.6.0",
            "--skip-git-check",
            "--skip-build",
            "--notes-file", notes_file,
            "--private-key", private_key,
            "--dist-dir", dist_dir,
            "--release-dir", release_dir,
            "--base-update-url", "https://example.com/updates/internal/win-x64/9.9.9-test",
        ]

        dev_result = run(dev_cmd, timeout=1800)
        result["dev_drill"] = {
            "returncode": dev_result.returncode,
            "stdout_tail": dev_result.stdout[-4000:],
            "stderr_tail": dev_result.stderr[-4000:],
            "status": "PASS" if dev_result.returncode == 0 else "FAIL",
        }

        obfuscar = find_obfuscar()
        result["obfuscar_path"] = obfuscar

        if obfuscar:
            release_cmd = [
                sys.executable,
                os.path.join(TOOLS_DIR, "release_pipeline.py"),
                "--version", "9.9.9-release-drill",
                "--channel", "stable",
                "--platform", "win-x64",
                "--mode", "release",
                "--mandatory", "false",
                "--min-supported-version", "1.6.0",
                "--skip-git-check",
                "--skip-build",
                "--notes-file", notes_file,
                "--private-key", private_key,
                "--obfuscator-path", obfuscar,
                "--dist-dir", dist_dir,
                "--release-dir", release_dir,
                "--base-update-url", "https://example.com/updates/stable/win-x64/9.9.9-release-drill",
            ]
            release_result = run(release_cmd, timeout=1800)
            result["release_drill"] = {
                "returncode": release_result.returncode,
                "stdout_tail": release_result.stdout[-4000:],
                "stderr_tail": release_result.stderr[-4000:],
                "status": "PASS" if release_result.returncode == 0 else "FAIL",
            }
        else:
            result["release_drill"] = {
                "status": "BLOCKED",
                "reason": "Obfuscar not found. Run tools/install_obfuscar.ps1 first.",
            }

        report = [
            "# AutoDoor Pro Release Drill Report",
            "",
            f"- Time: {result['time']}",
            f"- Temp root: `{temp_root}`",
            f"- Obfuscar: `{obfuscar or 'NOT FOUND'}`",
            "",
            "## Dev Drill",
            "",
            f"- Status: {result['dev_drill'].get('status')}",
            f"- Return code: {result['dev_drill'].get('returncode')}",
            "",
            "```text",
            result["dev_drill"].get("stdout_tail", ""),
            "```",
            "",
            "## Release Drill",
            "",
            f"- Status: {result['release_drill'].get('status')}",
            f"- Return code: {result['release_drill'].get('returncode', '')}",
            f"- Reason: {result['release_drill'].get('reason', '')}",
            "",
            "```text",
            result["release_drill"].get("stdout_tail", ""),
            "```",
            "",
            "## Notes",
            "",
            "- 本报告不包含私钥内容。",
            "- 本报告不提交 dist/release/exe/zip。",
            "- release 模式没有 Obfuscar 时必须是 BLOCKED，不允许假写 PASS。",
        ]

        write_text(report_path, "\n".join(report))
        print(f"Report written: {report_path}")

        if result["dev_drill"].get("status") != "PASS":
            print("FAIL: dev drill failed")
            return 1

        if result["release_drill"].get("status") == "FAIL":
            print("FAIL: release drill failed")
            return 1

        print("check release drill completed")
        return 0

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())