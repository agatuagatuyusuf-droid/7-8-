import json
import os
import threading
from typing import Callable, Optional

from .update_paths import get_updates_dir, get_prepared_dir, get_public_key_path
from .update_downloader import UpdateDownloader
from .update_verifier import (
    verify_package_sha256,
    verify_manifest_signature,
    extract_and_verify,
    sha256_file,
)


class UpdateService:
    def __init__(self):
        self._downloader = UpdateDownloader(get_updates_dir())

    def check_latest(self, latest_url: str) -> Optional[dict]:
        try:
            text = self._downloader.download_text(latest_url)
            return json.loads(text)
        except Exception:
            return None

    def download_and_prepare(self, latest_info: dict,
                             progress_callback: Optional[Callable[[float, str], None]] = None) -> Optional[dict]:
        try:
            manifest_url = latest_info.get("manifest_url", "")
            sig_url = latest_info.get("signature_url", "")
            package_url = latest_info.get("package_url", "")
            version = latest_info.get("latest_version", "")

            if not manifest_url or not sig_url or not package_url:
                raise ValueError("更新信息不完整")

            if progress_callback:
                progress_callback(0, "下载 manifest.json")

            manifest_json = self._downloader.download_text(manifest_url)
            manifest_path = os.path.join(get_updates_dir(), "manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(manifest_json)
            manifest = json.loads(manifest_json)

            if progress_callback:
                progress_callback(15, "下载 manifest.sig")

            sig_data = self._downloader.download_bytes(sig_url)
            sig_path = os.path.join(get_updates_dir(), "manifest.sig")
            with open(sig_path, "wb") as f:
                f.write(sig_data)

            if progress_callback:
                progress_callback(30, "校验签名")

            public_key = get_public_key_path()
            if not verify_manifest_signature(manifest_path, sig_path, public_key):
                raise ValueError("manifest 签名校验失败")

            if progress_callback:
                progress_callback(40, "签名校验通过，下载更新包")

            package_file = manifest.get("package", {}).get("file", f"update-{version}.zip")
            zip_path = self._downloader.download(
                package_url, package_file, progress_callback
            )

            if progress_callback:
                progress_callback(85, "校验更新包 hash")

            expected_sha = manifest.get("package", {}).get("sha256", "")
            if expected_sha and not verify_package_sha256(zip_path, expected_sha):
                raise ValueError("更新包 hash 校验失败")

            if progress_callback:
                progress_callback(90, "解压并校验文件")

            extract_dir = os.path.join(get_prepared_dir(), version)
            if os.path.exists(extract_dir):
                import shutil
                shutil.rmtree(extract_dir)

            errors = extract_and_verify(zip_path, extract_dir, manifest)
            if errors:
                raise ValueError(f"文件校验失败: {'; '.join(errors)}")

            if progress_callback:
                progress_callback(100, "更新准备就绪")

            return {
                "version": version,
                "prepared_dir": extract_dir,
                "main_exe": self._find_main_exe(extract_dir),
            }

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"更新失败: {str(e)}")
            raise

    def _find_main_exe(self, extract_dir: str) -> str:
        for name in os.listdir(extract_dir):
            if name.lower().endswith(".exe") and "autodoor" in name.lower():
                return name
        for root, dirs, files in os.walk(extract_dir):
            for f in files:
                if f.lower().endswith(".exe") and "autodoor" in f.lower():
                    return os.path.relpath(os.path.join(root, f), extract_dir)
        return "AutoDoorPro.exe"

    def launch_update_agent(self, prepared: dict, app_dir: str, main_exe: str, pid: int) -> bool:
        import subprocess
        import sys

        agent_path = self._find_update_agent()
        if not agent_path:
            return False

        args = [
            agent_path,
            "--app-dir", app_dir,
            "--package-dir", prepared.get("prepared_dir", ""),
            "--main-exe", main_exe,
            "--pid", str(pid),
        ]
        try:
            subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception:
            return False

    def _find_update_agent(self) -> str:
        import sys as _sys
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base, "..", "tools", "update_agent.py"),
            os.path.join(getattr(_sys, "_MEIPASS", ""), "update_agent", "update_agent.exe"),
            os.path.join(os.path.dirname(_sys.executable), "update_agent.exe"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return ""
