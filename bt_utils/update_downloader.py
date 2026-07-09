import os
import shutil
import urllib.request
import urllib.error
from typing import Callable, Optional


class UpdateDownloader:
    def __init__(self, updates_dir: str):
        self._updates_dir = updates_dir
        os.makedirs(updates_dir, exist_ok=True)

    def download(self, url: str, filename: str,
                 progress_callback: Optional[Callable[[float, str], None]] = None) -> str:
        if not url.startswith("https://"):
            raise ValueError("只允许 HTTPS 下载")

        temp_path = os.path.join(self._updates_dir, filename + ".download")
        final_path = os.path.join(self._updates_dir, filename)

        if os.path.exists(final_path):
            os.remove(final_path)

        def report(count, block_size, total_size):
            if total_size > 0 and progress_callback:
                percent = min(count * block_size / total_size * 100, 100)
                progress_callback(percent, f"下载中 {int(percent)}%")

        try:
            urllib.request.urlretrieve(url, temp_path, reporthook=report)
            shutil.move(temp_path, final_path)
            if progress_callback:
                progress_callback(100, "下载完成")
            return final_path
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def download_text(self, url: str) -> str:
        if not url.startswith("https://"):
            raise ValueError("只允许 HTTPS 下载")
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode("utf-8")

    def download_bytes(self, url: str) -> bytes:
        if not url.startswith("https://"):
            raise ValueError("只允许 HTTPS 下载")
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read()
