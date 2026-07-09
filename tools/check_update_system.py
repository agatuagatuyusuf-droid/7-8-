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

    app_py = read("bt_gui/app.py")
    checks.append(("main update button uses v2 signed update", "_check_for_updates_v2" in app_py and "check_for_updates(manual=True)" not in app_py))
    checks.append(("app update callback uses UpdateService", "UpdateService" in app_py and "download_and_prepare" in app_py))
    checks.append(("app update does not open browser for update", "webbrowser.open(download_url)" not in app_py))

    manifest_py = read("tools/generate_manifest.py")
    checks.append(("manifest generated from extracted zip stage", "ZipFile" in manifest_py and "mkdtemp" in manifest_py))
    checks.append(("manifest excludes zip file", "forbidden_ext" in manifest_py and ".zip" in manifest_py))

    verifier_py = read("bt_utils/update_verifier.py")
    checks.append(("safe zip extraction exists", "safe_extract_zip" in verifier_py and "startswith" in verifier_py))

    agent_py = read("tools/update_agent.py")
    checks.append(("update agent verifies manifest after replace", "verify_files_by_manifest" in agent_py and "--manifest" in agent_py))

    launcher_py = read("bt_utils/update_agent_launcher.py")
    checks.append(("update agent launcher has no duplicate exe arg", "args = [agent_path]" in launcher_py or 'args = [sys.executable, agent_path]' in launcher_py))

    protect_ps1 = read("tools/protect_csharp.ps1")
    checks.append(("release mode cannot fake obfuscation", "AllowCopyFallback" in protect_ps1 and "Copy fallback disabled" in protect_ps1))

    obfuscar_check = read("tools/check_obfuscar_integration.py")
    checks.append(("pipeline protected dist check exists", "copy_full_dist_for_protection" in obfuscar_check and "pipeline does not package raw dist after protect" in obfuscar_check))
    checks.append(("protect copy before obfuscar check exists", "Preparing full CoreService output directory before Obfuscar" in obfuscar_check))
    checks.append(("publisher false log check exists", "Obfuscar 已自动识别" in obfuscar_check))

    pipeline_py = read("tools/release_pipeline.py")
    checks.append(("release latest url not empty", "base-update-url" in pipeline_py and "base_url" in pipeline_py))
    checks.append(("pipeline uses protected dist for update package", "protected_dist_dir" in pipeline_py and "generate_update_package(\n        protected_dist_dir" in pipeline_py))
    checks.append(("pipeline has full dist copy before protect", "copy_full_dist_for_protection" in pipeline_py))
    checks.append(("release pipeline verifies protected core in zip", "verify_update_zip_contains_protected_core" in pipeline_py and "VERIFY_UPDATE_ZIP_CONTAINS_PROTECTED_CORE_OK" in pipeline_py))
    checks.append(("release pipeline checks core dll zip hash", "zip_dll_hash" in pipeline_py and "protected_dll_hash" in pipeline_py))

    core_check = read("tools/check_core_runtime_slice.py")
    checks.append(("core runtime check verifies feature gate", "FEATURE_NOT_AUTHORIZED" in core_check and "CoreRuntimeFeature" in core_check))
    checks.append(("core runtime check blocks SendKeys fallback", "SendKeys.SendWait\" not in native" in core_check or "SendKeys.SendWait' not in native" in core_check))

    build_bat = read("build_release.bat")
    checks.append(("build_release requires base update url", "BASE_UPDATE_URL" in build_bat and "--base-update-url" in build_bat))

    version_checker = read("bt_utils/version_checker.py")
    checks.append(("auto check uses signed update v2", "start_auto_check" in version_checker and "check_for_updates_v2" in version_checker))
    checks.append(("auto check no old github default", "self.check_for_updates(manual=False)" not in version_checker))

    publisher_ui = read("tools/release_publisher_ui.py")
    checks.append(("publisher ui has base update url field", "base_update_url" in publisher_ui and "replace(\"_\", \"-\")" in publisher_ui))
    checks.append(("publisher has auto detect paths", "_auto_detect_paths" in publisher_ui))
    checks.append(("publisher has fill test config", "_fill_test_config" in publisher_ui))
    checks.append(("publisher has stop task", "_stop_current_task" in publisher_ui))
    checks.append(("publisher uses Popen", "subprocess.Popen" in publisher_ui))
    checks.append(("publisher supports private key file chooser", "askopenfilename" in publisher_ui and "*.pem" in publisher_ui))
    checks.append(("publisher supports obfuscator file chooser", "askopenfilename" in publisher_ui and "*.exe" in publisher_ui))
    checks.append(("publisher can generate test key", "generate_key_pair" in publisher_ui))
    checks.append(("publisher dev url avoids duplicate test suffix", "endswith(\"-test\")" in publisher_ui or "endswith('-test')" in publisher_ui))
    checks.append(("publisher filters unsupported pipeline args", "allowed_path_args" in publisher_ui and "server_publish_dir" in publisher_ui))
    checks.append(("publisher protect calls powershell ps1", "protect_csharp.ps1" in publisher_ui and "powershell" in publisher_ui))
    checks.append(("publisher has terminate helper", "_terminate_current_proc" in publisher_ui))
    checks.append(("publisher release notes uses temp dir", "tempfile.gettempdir()" in publisher_ui and "_get_release_notes_path" in publisher_ui))
    checks.append(("publisher cleans legacy root notes", "_cleanup_legacy_project_notes_file" in publisher_ui and "已清理历史临时 notes 文件" in publisher_ui))
    checks.append(("publisher logs temp release notes path", "release notes 临时文件" in publisher_ui))
    checks.append(("publisher gather args uses release notes helper", "notes_path = self._get_release_notes_path()" in publisher_ui))
    checks.append(("publisher gather args no direct project notes write", "notes_path = os.path.join(PROJECT_ROOT, \"_ui_release_notes.json\")" not in publisher_ui))
    checks.append(("publisher saves base update url", '"base_update_url"' in publisher_ui and "_save_current_config" in publisher_ui))
    checks.append(("publisher uses output queue for nonblocking timeout", "queue.Queue" in publisher_ui and "_reader_thread" in publisher_ui))
    checks.append(("publisher main timeout loop avoids blocking readline", "get_nowait" in publisher_ui and "output_queue" in publisher_ui))
    checks.append(("obfuscar integration check exists", file_exists("tools/check_obfuscar_integration.py")))
    checks.append(("core runtime slice check exists", file_exists("tools/check_core_runtime_slice.py")))
    checks.append(("install obfuscar script exists", file_exists("tools/install_obfuscar.ps1")))
    checks.append(("find obfuscar script exists", file_exists("tools/find_obfuscar.ps1")))

    checks.append(("release pipeline smoke check exists", file_exists("tools/check_release_pipeline_smoke.py")))
    smoke = read("tools/check_release_pipeline_smoke.py")
    checks.append(("release pipeline smoke checks good and bad zip", "expected protected CoreService zip verification to pass" in smoke and "expected corrupted CoreService zip verification to fail" in smoke))

    checks.append(("release drill check exists", file_exists("tools/check_release_drill.py")))
    checks.append(("release drill runner exists", file_exists("tools/run_release_drill.py")))
    drill_check = read("tools/check_release_drill.py")
    checks.append(("release drill check validates blocked release", "BLOCKED" in drill_check and "Obfuscar not found" in drill_check))

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
