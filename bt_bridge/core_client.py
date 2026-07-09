import json
import os
import socket
import threading
from typing import Any, Optional
from .ipc_protocol import make_request, parse_response


class CoreClient:
    """通过 TCP 与 C# CoreService 通信"""

    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 19527

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, timeout: float = 10.0):
        self._host = host or os.environ.get("AUTODOOR_CORE_HOST") or self._DEFAULT_HOST
        self._port = port or int(os.environ.get("AUTODOOR_CORE_PORT") or str(self._DEFAULT_PORT))
        self._timeout = timeout
        self._connected = False
        self._lock = threading.Lock()
        self._socket: Optional[socket.socket] = None
        self._file: Optional[Any] = None

    def connect(self) -> bool:
        try:
            self._socket = socket.create_connection((self._host, self._port), timeout=self._timeout)
            self._file = self._socket.makefile("rwb")
            self._connected = True
            return True
        except socket.timeout:
            self._connected = False
            return False
        except ConnectionRefusedError:
            self._connected = False
            return False
        except Exception:
            self._connected = False
            return False

    def disconnect(self):
        self._connected = False
        try:
            if self._file:
                self._file.close()
        except Exception:
            pass
        try:
            if self._socket:
                self._socket.close()
        except Exception:
            pass
        self._file = None
        self._socket = None

    def send_request(self, action: str, payload: Optional[dict] = None) -> dict:
        if not self._connected:
            if not self.connect():
                return {"success": False, "error_code": "NOT_CONNECTED",
                        "message": "Not connected to CoreService"}

        with self._lock:
            try:
                request = make_request(action, payload)
                if self._file:
                    self._file.write((request + "\n").encode("utf-8"))
                    self._file.flush()

                    line = self._file.readline()
                    if not line:
                        return {"success": False, "error_code": "IPC_DISCONNECTED",
                                "message": "CoreService disconnected"}
                    return parse_response(line.decode("utf-8"))
                return {"success": False, "error_code": "IPC_SEND_FAILED",
                        "message": "No file handle for IPC"}
            except socket.timeout:
                return {"success": False, "error_code": "IPC_TIMEOUT",
                        "message": "IPC request timed out"}
            except (BrokenPipeError, ConnectionResetError) as e:
                self._connected = False
                return {"success": False, "error_code": "IPC_DISCONNECTED",
                        "message": f"IPC connection lost: {e}"}
            except Exception as e:
                return {"success": False, "error_code": "IPC_ERROR",
                        "message": str(e)}

    def hello(self) -> bool:
        result = self.send_request("core.hello")
        return result.get("success", False)

    def auth_login(self, username: str, password: str):
        return self.send_request("auth.login", {
            "username": username,
            "password": password
        })

    def auth_logout(self, login_session: str):
        return self.send_request("auth.logout", {
            "login_session": login_session
        })

    def auth_status(self, login_session: str):
        return self.send_request("auth.status", {
            "login_session": login_session
        })

    def core_input_key_press(self, login_session: str, key: str):
        return self.send_request("core.input.key_press", {
            "login_session": login_session,
            "key": key
        })

    def core_input_text_input(self, login_session: str, text: str):
        return self.send_request("core.input.text_input", {
            "login_session": login_session,
            "text": text
        })

    def core_input_mouse_click(self, login_session: str, x: int, y: int, button: str = "left", count: int = 1):
        return self.send_request("core.input.mouse_click", {
            "login_session": login_session,
            "x": int(x),
            "y": int(y),
            "button": button,
            "count": int(count)
        })

    def shutdown(self):
        self.send_request("core.shutdown")
        self.disconnect()
