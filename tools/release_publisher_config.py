import json
import os


CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AutoDoorProPublisher")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config() -> dict:
    default = {
        "project_root": "",
        "dist_dir": "",
        "release_dir": "",
        "private_key_path": "",
        "obfuscator_path": "",
        "server_publish_dir": "",
        "channel": "stable",
        "platform": "win-x64",
        "mandatory": False,
        "min_supported_version": "1.6.0",
        "mode": "release",
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**default, **json.load(f)}
        except Exception:
            pass
    return default


def save_config(config: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
