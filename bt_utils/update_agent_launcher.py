import os
import subprocess
import sys
from typing import Optional


def launch_update_agent(app_dir: str, package_dir: str,
                        main_exe: str = "AutoDoorPro.exe",
                        pid: int = 0,
                        manifest: str = "") -> bool:
    agent_path = _find_agent()
    if not agent_path:
        return False

    if agent_path.endswith(".py"):
        args = [sys.executable, agent_path]
    else:
        args = [agent_path]

    args.extend([
        "--app-dir", app_dir,
        "--package-dir", package_dir,
        "--main-exe", main_exe,
        "--pid", str(pid),
    ])
    if manifest:
        args.extend(["--manifest", manifest])

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
