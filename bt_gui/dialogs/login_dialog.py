import hashlib
import customtkinter as ctk

USERNAME = "admin"
PASSWORD_HASH = hashlib.sha256(b"admin123").hexdigest()


class LoginDialog(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.logged_in = False
        self.login_session = ""

        self.title("AutoDoor Pro - 登录")
        self.resizable(False, False)

        self.update_idletasks()
        w, h = 380, 260
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.transient(self.master)
        self.grab_set()

        self._build_ui()

        self.bind("<Return>", lambda e: self._do_login())

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="AutoDoor Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=(30, 5))

        ctk.CTkLabel(
            self, text="请输入账号密码登录",
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, pady=(0, 20))

        ctk.CTkLabel(self, text="账号：", anchor="w").grid(row=2, column=0, padx=60, sticky="w")
        self._username_entry = ctk.CTkEntry(self, width=280, height=32)
        self._username_entry.grid(row=3, column=0, padx=60, pady=(0, 10))

        ctk.CTkLabel(self, text="密码：", anchor="w").grid(row=4, column=0, padx=60, sticky="w")
        self._password_entry = ctk.CTkEntry(self, width=280, height=32, show="*")
        self._password_entry.grid(row=5, column=0, padx=60, pady=(0, 16))

        self._error_label = ctk.CTkLabel(
            self, text="", text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self._error_label.grid(row=6, column=0, pady=(0, 5))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=7, column=0, pady=(0, 20))

        ctk.CTkButton(
            btn_frame, text="登录", width=100, height=32,
            command=self._do_login
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="退出", width=100, height=32,
            fg_color="gray", hover_color="darkred",
            command=self._on_exit
        ).pack(side="left", padx=10)

        self._username_entry.focus_set()

    def _try_core_login(self, username: str, password: str):
        try:
            from bt_bridge.core_process import CoreProcessManager
            from bt_bridge.core_client import CoreClient

            manager = CoreProcessManager()
            if not manager.start() and not manager.is_running():
                return {
                    "success": False,
                    "message": manager.get_last_error() or "CoreService 无法启动"
                }

            client = CoreClient()
            if not client.connect():
                return {
                    "success": False,
                    "error_code": "NOT_CONNECTED",
                    "message": "无法连接 CoreService"
                }

            try:
                result = client.auth_login(username, password)
                return result
            finally:
                try:
                    client.disconnect()
                except Exception:
                    pass

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    def _do_login(self):
        from bt_bridge.core_process import is_commercial_bundle

        username = self._username_entry.get().strip()
        password = self._password_entry.get()

        if not username or not password:
            self._error_label.configure(text="请输入账号和密码")
            return

        if is_commercial_bundle():
            result = self._try_core_login(username, password)
            if result.get("success"):
                data = result.get("data", {})
                token = data.get("login_session", "")
                if token:
                    self.login_session = token
                    self.logged_in = True
                    self.grab_release()
                    self.destroy()
                    return

            self._error_label.configure(text=result.get("message", "登录失败"))
            self._password_entry.delete(0, "end")
            self._password_entry.focus_set()
            return

        result = self._try_core_login(username, password)
        if result.get("success"):
            data = result.get("data", {})
            token = data.get("login_session", "")
            if token:
                self.login_session = token
                self.logged_in = True
                self.grab_release()
                self.destroy()
                return

        if username == USERNAME and hashlib.sha256(password.encode("utf-8")).hexdigest() == PASSWORD_HASH:
            self.login_session = "DEV-LOCAL-LOGIN"
            self.logged_in = True
            self.grab_release()
            self.destroy()
            return

        self._error_label.configure(text="账号或密码错误")
        self._password_entry.delete(0, "end")
        self._password_entry.focus_set()

    def _on_exit(self):
        self.grab_release()
        self.destroy()
