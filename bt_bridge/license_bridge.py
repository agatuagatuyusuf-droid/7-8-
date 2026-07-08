from typing import Optional
from .core_client import CoreClient


class LicenseBridge:
    """授权相关 API 桥接"""

    def __init__(self, client: CoreClient):
        self._client = client

    def status(self) -> dict:
        return self._client.send_request("license.status")

    def activate(self, code: str) -> dict:
        return self._client.send_request("license.activate", {"code": code})

    def refresh(self) -> dict:
        return self._client.send_request("license.refresh")

    def deactivate(self) -> dict:
        return self._client.send_request("license.deactivate")

    def machine_code(self) -> str:
        result = self._client.send_request("license.machine_code")
        if result.get("success"):
            data = result.get("data", {})
            return data.get("machine_code", "")
        return ""

    def feature_enabled(self, feature: str) -> bool:
        result = self._client.send_request("feature.check", {"feature": feature})
        if result.get("success"):
            data = result.get("data", {})
            return data.get("allowed", False)
        return False

    def feature_list(self) -> list:
        result = self._client.send_request("feature.list")
        if result.get("success"):
            data = result.get("data", {})
            return data.get("features", [])
        return []

    def is_activated(self) -> bool:
        result = self.status()
        if result.get("success"):
            data = result.get("data", {})
            return data.get("activated", False)
        return False

    def is_valid(self) -> bool:
        result = self.status()
        if result.get("success"):
            data = result.get("data", {})
            return data.get("valid", False)
        return False
