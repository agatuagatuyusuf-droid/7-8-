import time
import socket
from typing import Optional
from .core_process import CoreProcessManager
from .core_client import CoreClient
from .license_bridge import LicenseBridge


class LicenseSession:
    """Manage license lifecycle: CoreService startup, connection, activation check."""

    def __init__(self):
        self.process_manager = CoreProcessManager()
        self.client = CoreClient()
        self.bridge = LicenseBridge(self.client)
        self.last_error = ""
        self._core_started = False

    def start_core(self) -> bool:
        if self.process_manager.is_running():
            self._core_started = True
            return True
        ok = self.process_manager.start()
        if not ok:
            self.last_error = self.process_manager.get_last_error()
            return False
        self._core_started = True
        return True

    def connect(self) -> bool:
        if self.client._connected:
            return True
        ok = self.client.connect()
        if not ok:
            self.last_error = "授权服务连接失败，请重新安装或联系技术支持。"
        return ok

    def ensure_ready(self) -> bool:
        if not self.start_core():
            return False
        # Wait for port to be ready
        timeout = 15
        start = time.time()
        while time.time() - start < timeout:
            if self.connect():
                return True
            time.sleep(0.5)

        if not self._core_started:
            self.last_error = "授权服务启动失败，请重新安装或联系技术支持。"
        else:
            self.last_error = "授权服务连接失败，请重新安装或联系技术支持。"
        return False

    def status(self) -> dict:
        try:
            return self.bridge.status()
        except Exception as e:
            self.last_error = str(e)
            return {"success": False, "error_code": "STATUS_ERROR", "message": str(e)}

    def machine_code(self) -> str:
        try:
            return self.bridge.machine_code()
        except Exception as e:
            self.last_error = str(e)
            return ""

    def activate(self, code: str) -> dict:
        try:
            result = self.bridge.activate(code)
            if result.get("success"):
                status = self.status()
                if status.get("success"):
                    data = status.get("data", {})
                    if data.get("valid"):
                        return result
                    self.last_error = "激活令牌验证失败。"
                    return {"success": False, "error_code": "VALIDATION_FAILED",
                            "message": self.last_error}
            return result
        except Exception as e:
            self.last_error = str(e)
            return {"success": False, "error_code": "ACTIVATE_ERROR", "message": str(e)}

    def refresh(self) -> dict:
        try:
            return self.bridge.refresh()
        except Exception as e:
            self.last_error = str(e)
            return {"success": False, "error_code": "REFRESH_ERROR", "message": str(e)}

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

    def get_license_state(self):
        from bt_bridge.license_state import LicenseState
        try:
            result = self.status()
            if not result.get("success"):
                return LicenseState(
                    activated=False,
                    valid=False,
                    error=result.get("message") or result.get("error") or "授权状态获取失败"
                )
            payload = result.get("data")
            if not isinstance(payload, dict):
                payload = result
            return LicenseState(
                activated=bool(payload.get("activated")),
                valid=bool(payload.get("valid")),
                edition=str(payload.get("edition") or ""),
                expire_at=str(payload.get("expire_at") or ""),
                machine_code=str(payload.get("machine_code") or ""),
                features=list(payload.get("features") or []),
                error=str(payload.get("error") or "")
            )
        except Exception as e:
            return LicenseState(valid=False, error=str(e))

    def shutdown(self):
        try:
            self.client.shutdown()
        except Exception:
            pass
        self.process_manager.stop()
