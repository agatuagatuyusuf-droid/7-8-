import os
import sys
import subprocess
import atexit
import time
from typing import Optional


class CoreProcessManager:
    """管理 CoreService.exe 进程生命周期"""

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self.last_error: str = ""

    @staticmethod
    def _find_core_service() -> str:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Priority 1: PyInstaller dist directory
        if hasattr(sys, '_MEIPASS'):
            dist_core = os.path.join(sys._MEIPASS, "CoreService", "AutoDoor.CoreService.exe")
            if os.path.exists(dist_core):
                return dist_core

        # Priority 2: Project root / CoreService
        root_core = os.path.join(base, "CoreService", "AutoDoor.CoreService.exe")
        if os.path.exists(root_core):
            return root_core

        # Priority 3: C# publish directory
        publish_core = os.path.join(base, "csharp", "AutoDoor.CoreService",
                                     "src", "AutoDoor.CoreService", "bin", "Release",
                                     "net8.0", "win-x64", "publish",
                                     "AutoDoor.CoreService.exe")
        if os.path.exists(publish_core):
            return publish_core

        # Priority 4: C# build directory
        build_core = os.path.join(base, "csharp", "AutoDoor.CoreService",
                                   "src", "AutoDoor.CoreService", "bin", "Release",
                                   "net8.0", "win-x64", "AutoDoor.CoreService.exe")
        if os.path.exists(build_core):
            return build_core

        # Priority 5: Current working directory / CoreService
        cwd_core = os.path.join(os.getcwd(), "CoreService", "AutoDoor.CoreService.exe")
        if os.path.exists(cwd_core):
            return cwd_core

        return ""

    def start(self) -> bool:
        exe_path = self._find_core_service()
        if not exe_path:
            self.last_error = "CoreService.exe not found in any search path"
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
