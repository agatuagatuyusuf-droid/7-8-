import os
import sys
import subprocess
import atexit
import time
from typing import Optional


def is_commercial_bundle() -> bool:
    """判断是否为 PyInstaller 商业包环境"""
    return getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS")


def _build_searched_paths() -> list:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = [
        os.path.join(os.path.dirname(sys.executable), "CoreService", "AutoDoor.CoreService.exe"),
        os.path.join(getattr(sys, "_MEIPASS", ""), "CoreService", "AutoDoor.CoreService.exe"),
        os.path.join(base, "CoreService", "AutoDoor.CoreService.exe"),
        os.path.join(base, "csharp", "AutoDoor.CoreService",
                     "src", "AutoDoor.CoreService", "bin", "Release",
                     "net8.0", "win-x64", "AutoDoor.CoreService.exe"),
        os.path.join(base, "csharp", "AutoDoor.CoreService",
                     "src", "AutoDoor.CoreService", "bin", "Debug",
                     "net8.0", "win-x64", "AutoDoor.CoreService.exe"),
    ]
    return paths


class CoreProcessManager:
    """管理 CoreService.exe 进程生命周期"""

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self.last_error: str = ""

    @staticmethod
    def find_core_service() -> tuple:
        """查找 CoreService.exe，返回 (exe_path, searched_paths)"""
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        searched = _build_searched_paths()

        candidates = [
            # Priority 1: PyInstaller bundle parent /CoreService
            (hasattr(sys, 'frozen'),
             os.path.join(os.path.dirname(sys.executable), "CoreService", "AutoDoor.CoreService.exe")),
            # Priority 2: PyInstaller _MEIPASS
            (hasattr(sys, '_MEIPASS'),
             os.path.join(getattr(sys, '_MEIPASS', ""), "CoreService", "AutoDoor.CoreService.exe")),
            # Priority 3: Project root / CoreService
            (True, os.path.join(base, "CoreService", "AutoDoor.CoreService.exe")),
            # Priority 4: C# publish directory
            (True, os.path.join(base, "csharp", "AutoDoor.CoreService",
                               "src", "AutoDoor.CoreService", "bin", "Release",
                               "net8.0", "win-x64", "publish",
                               "AutoDoor.CoreService.exe")),
            # Priority 5: C# build directory (Release)
            (True, os.path.join(base, "csharp", "AutoDoor.CoreService",
                               "src", "AutoDoor.CoreService", "bin", "Release",
                               "net8.0", "win-x64", "AutoDoor.CoreService.exe")),
            # Priority 6: C# build directory (Debug)
            (True, os.path.join(base, "csharp", "AutoDoor.CoreService",
                               "src", "AutoDoor.CoreService", "bin", "Debug",
                               "net8.0", "win-x64", "AutoDoor.CoreService.exe")),
            # Priority 7: Current working directory / CoreService
            (True, os.path.join(os.getcwd(), "CoreService", "AutoDoor.CoreService.exe")),
        ]

        for condition, path in candidates:
            if condition and os.path.exists(path):
                return path, searched

        return "", searched

    def start(self) -> bool:
        exe_path, searched = self.find_core_service()
        if not exe_path:
            lines = ["CoreService.exe not found.", "Searched paths:"]
            for i, p in enumerate(searched, 1):
                lines.append(f"{i}. {p}")
            if is_commercial_bundle():
                lines.append("")
                lines.append("商业包模式解决办法：")
                lines.append("确认 dist/autodoor-pro-*/CoreService/AutoDoor.CoreService.exe 存在")
            else:
                lines.append("")
                lines.append("源码开发模式解决办法：")
                lines.append("dotnet build csharp/AutoDoor.CoreService/AutoDoor.CoreService.sln -c Release")
                lines.append("或关闭 runtime.use_csharp_core")
            self.last_error = "\n".join(lines)
            return False

        try:
            self._process = subprocess.Popen(
                [exe_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            atexit.register(self.stop)
            return True
        except Exception as e:
            self.last_error = f"Failed to start CoreService: {e}"
            return False

    def stop(self):
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
        self._process = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def restart(self) -> bool:
        self.stop()
        time.sleep(1)
        return self.start()

    def get_last_error(self) -> str:
        return self.last_error
