import json
import socket
import threading
import time
from typing import Any, Optional, Callable
from .ipc_protocol import make_request, parse_response


class CoreClient:
    """通过 Named Pipe 与 C# CoreService 通信"""

    PIPE_NAME = r"\\.\pipe\AutoDoorPro.CoreService"

    def __init__(self, timeout: float = 10.0):
        self._timeout = timeout
        self._connected = False
        self._lock = threading.Lock()

    def connect(self) -> bool:
        try:
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.settimeout(self._timeout)
            self._socket.connect(self.PIPE_NAME)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    def disconnect(self):
        self._connected = False
        try:
            self._socket.close()
        except Exception:
            pass

    def send_request(self, action: str, payload: Optional[dict] = None) -> dict:
        if not self._connected:
            return {"success": False, "error_code": "NOT_CONNECTED",
                    "message": "Not connected to CoreService"}

        with self._lock:
            try:
                request = make_request(action, payload)
                self._socket.sendall((request + "\n").encode("utf-8"))

                response_data = self._socket.recv(65536).decode("utf-8")
                return parse_response(response_data)
            except Exception as e:
                return {"success": False, "error_code": "IPC_ERROR",
                        "message": str(e)}

    def hello(self) -> bool:
        result = self.send_request("core.hello")
        return result.get("success", False)

    def shutdown(self):
        self.send_request("core.shutdown")
        self.disconnect()
