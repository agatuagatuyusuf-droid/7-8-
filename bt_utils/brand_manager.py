import os
import json
from typing import Any, Optional

_BRAND_CACHE: Optional[dict] = None


def _get_brand_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config", "brand.json")


def load_brand() -> dict:
    global _BRAND_CACHE
    if _BRAND_CACHE is not None:
        return _BRAND_CACHE
    path = _get_brand_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            _BRAND_CACHE = json.load(f)
    except Exception:
        _BRAND_CACHE = {
            "product_name_en": "AutoDoor Pro",
            "product_name_cn": "AutoDoor 自动化系统",
            "company_name_en": "Sky Ocean",
            "company_name_cn": "Sky Ocean",
            "copyright_owner": "Sky Ocean",
            "support_url": "",
            "docs_url": "",
            "download_url": "",
            "license_server_url": "https://YOUR-DOMAIN.com",
            "repo_owner": "",
            "repo_name": "",
        }
    return _BRAND_CACHE


def get(key: str, default: Any = "") -> Any:
    return load_brand().get(key, default)


def product_name() -> str:
    return get("product_name_cn") or get("product_name_en", "AutoDoor Pro")


def product_name_en() -> str:
    return get("product_name_en", "AutoDoor Pro")


def company_name() -> str:
    return get("company_name_cn") or get("company_name_en", "Sky Ocean")


def copyright_owner() -> str:
    return get("copyright_owner", "Sky Ocean")


def license_server_url() -> str:
    return get("license_server_url", "https://YOUR-DOMAIN.com")


def support_url() -> str:
    return get("support_url", "")


def docs_url() -> str:
    return get("docs_url", "")


def download_url() -> str:
    return get("download_url", "")


def user_data_dir() -> str:
    return "AutoDoorPro"


def invalidate_cache():
    global _BRAND_CACHE
    _BRAND_CACHE = None
