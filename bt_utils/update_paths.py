import os


def get_appdata_dir() -> str:
    return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AutoDoorPro")


def get_updates_dir() -> str:
    d = os.path.join(get_appdata_dir(), "updates", "downloads")
    os.makedirs(d, exist_ok=True)
    return d


def get_prepared_dir() -> str:
    d = os.path.join(get_appdata_dir(), "updates", "prepared")
    os.makedirs(d, exist_ok=True)
    return d


def get_backup_dir() -> str:
    d = os.path.join(get_appdata_dir(), "backups")
    os.makedirs(d, exist_ok=True)
    return d


def get_update_log_path() -> str:
    d = os.path.join(get_appdata_dir(), "logs")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "update.log")


def get_security_log_path() -> str:
    d = os.path.join(get_appdata_dir(), "logs")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "security.log")


def get_public_key_path() -> str:
    import sys
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, "..", "resources", "security", "release_public.pem"),
        os.path.join(getattr(sys, "_MEIPASS", ""), "resources", "security", "release_public.pem"),
        os.path.join(os.path.dirname(sys.executable), "resources", "security", "release_public.pem"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # Fallback - return the dev path
    return os.path.normpath(os.path.join(base, "..", "resources", "security", "release_public.pem"))
