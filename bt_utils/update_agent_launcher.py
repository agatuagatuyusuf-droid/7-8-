import os
import subprocess
import sys
from typing import Optional


def launch_update_agent(app_dir: str, package_dir: str,
                        main_exe: str = "AutoDoorPro.exe",
                        pid: int = 0) -> bool:
    agent_path = _find_agent()
    if not agent_path:
        return False

    args = [
        sys.executable if agent_path.endswith(".py") else agent_path,
        agent_path,
        "--app-dir", app_dir,
        "--package-dir", package_dir,
        "--main-exe", main_exe,
        "--pid", str(pid),
    ]
    try:
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW
        subprocess.Popen(args, creationflags=creationflags)
        return True
    except Exception:
        return False


def _find_agent() -> Optional[str]:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base, "tools", "update_agent.py"),
        os.path.join(getattr(sys, "_MEIPASS", ""), "update_agent", "update_agent.exe"),
        os.path.join(os.path.dirname(sys.executable), "update_agent.exe"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None
