import os
import sys
import subprocess
import atexit
import signal
from typing import Optional


class CoreProcessManager:
    """管理 CoreService.exe 进程生命周期"""

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None

    @staticmethod
    def _find_core_service() -> str:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(base, "csharp", "AutoDoor.CoreService",
                         "src", "AutoDoor.CoreService", "bin", "Release",
                         "net8.0", "win-x64", "AutoDoor.CoreService.exe"),
            os.path.join(base, "AutoDoor.CoreService.exe"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return ""

    def start(self) -> bool:
        exe_path = self._find_core_service()
        if not exe_path:
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
        except Exception:
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
        return self.start()
