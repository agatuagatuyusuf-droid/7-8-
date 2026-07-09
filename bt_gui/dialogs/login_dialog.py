import hashlib
import customtkinter as ctk

USERNAME = "admin"
PASSWORD_HASH = hashlib.sha256(b"admin123").hexdigest()
MAX_ATTEMPTS = 3


def check_login(username: str, password: str) -> bool:
    if username != USERNAME:
        return False
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pw_hash == PASSWORD_HASH


class LoginDialog(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.logged_in = False
        self._attempts = 0

        self.title("AutoDoor Pro - 登录")
        self.resizable(False, False)

        self.update_idletasks()
        w, h = 380, 280
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

        title = ctk.CTkLabel(
            self, text="AutoDoor Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, pady=(30, 5))

        subtitle = ctk.CTkLabel(
            self, text="请输入账号密码登录",
            font=ctk.CTkFont(size=13)
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))

        ctk.CTkLabel(self, text="账号：", anchor="w").grid(row=2, column=0, padx=60, sticky="w")
        self._username_entry = ctk.CTkEntry(self, width=280, height=32)
        self._username_entry.grid(row=3, column=0, padx=60, pady=(0, 10))
        self._username_entry.insert(0, "")

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

    def _do_login(self):
        username = self._username_entry.get().strip()
        password = self._password_entry.get()

        if self._attempts >= MAX_ATTEMPTS:
            self._error_label.configure(text="错误次数过多，程序退出")
            self.after(1000, self._on_exit)
            return

        if check_login(username, password):
            self.logged_in = True
            self.grab_release()
            self.destroy()
        else:
            self._attempts += 1
            remaining = MAX_ATTEMPTS - self._attempts
            self._error_label.configure(
                text=f"账号或密码错误，剩余尝试次数：{remaining}"
            )
            self._password_entry.delete(0, "end")
            self._password_entry.focus_set()
            if remaining <= 0:
                self.after(1500, self._on_exit)

    def _on_exit(self):
        self.grab_release()
        self.destroy()