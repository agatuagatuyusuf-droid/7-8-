import threading
import customtkinter as ctk
from bt_bridge.license_session import LicenseSession


class ActivationDialog(ctk.CTkToplevel):
    """License activation dialog shown before main application."""

    def __init__(self, session: LicenseSession):
        super().__init__()
        self.session = session
        self.activated = False
        self._activating = False

        self.title("AutoDoor 自动化系统 - 授权激活")
        self.resizable(False, False)

        # Center on screen
        self.update_idletasks()
        w, h = 480, 400
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.transient(self.master)
        self.grab_set()

        self._build_ui()

        # Load machine code
        self._load_machine_code()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self, text="AutoDoor 自动化系统",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, pady=(30, 5))

        subtitle = ctk.CTkLabel(
            self, text="请输入激活码完成授权",
            font=ctk.CTkFont(size=14)
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))

        # Machine code row
        machine_frame = ctk.CTkFrame(self)
        machine_frame.grid(row=2, column=0, padx=40, pady=(0, 5), sticky="ew")
        machine_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(machine_frame, text="机器码：", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=(10, 5), pady=10, sticky="w"
        )

        self.machine_code_var = ctk.StringVar(value="获取中...")
        machine_code_entry = ctk.CTkEntry(
            machine_frame, textvariable=self.machine_code_var,
            state="readonly", width=240
        )
        machine_code_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        copy_btn = ctk.CTkButton(
            machine_frame, text="复制", width=60,
            command=self._copy_machine_code
        )
        copy_btn.grid(row=0, column=2, padx=(5, 10), pady=10)

        # Activation code input
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=3, column=0, padx=40, pady=5, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="激活码：", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=(10, 5), pady=10, sticky="w"
        )

        self.code_var = ctk.StringVar()
        self.code_entry = ctk.CTkEntry(
            input_frame, textvariable=self.code_var,
            placeholder_text="请输入激活码", width=240
        )
        self.code_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.code_entry.bind("<Return>", lambda e: self._on_activate())

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=(15, 10))

        self.activate_btn = ctk.CTkButton(
            btn_frame, text="激活", width=100,
            command=self._on_activate
        )
        self.activate_btn.grid(row=0, column=0, padx=10)

        self.exit_btn = ctk.CTkButton(
            btn_frame, text="退出", width=100,
            command=self._on_exit, fg_color="gray"
        )
        self.exit_btn.grid(row=0, column=1, padx=10)

        # Status
        self.status_var = ctk.StringVar(value="未激活")
        self.status_label = ctk.CTkLabel(
            self, textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=5, column=0, pady=(10, 20))

    def _load_machine_code(self):
        def _do():
            code = self.session.machine_code()
            self.after(0, lambda: self.machine_code_var.set(code or "获取失败"))
        threading.Thread(target=_do, daemon=True).start()

    def _copy_machine_code(self):
        self.clipboard_clear()
        self.clipboard_append(self.machine_code_var.get())
        self.status_var.set("机器码已复制")
        self.after(2000, lambda: self.status_var.set("未激活"))

    def _on_activate(self):
        code = self.code_var.get().strip()
        if not code:
            self.status_var.set("请输入激活码")
            return

        self._activating = True
        self.activate_btn.configure(state="disabled")
        self.code_entry.configure(state="disabled")
        self.status_var.set("激活中...")
        self.status_label.configure(text_color="orange")

        def _do():
            result = self.session.activate(code)
            self.after(0, lambda: self._on_activate_result(result))

        threading.Thread(target=_do, daemon=True).start()

    def _on_activate_result(self, result: dict):
        self._activating = False
        if result.get("success"):
            self.activated = True
            self.status_var.set("激活成功")
            self.status_label.configure(text_color="green")
            self.after(300, self.destroy)
        else:
            error_code = result.get("error_code", "UNKNOWN")
            message = result.get("message", "激活失败")
            self.status_var.set(f"激活失败 [{error_code}]: {message}")
            self.status_label.configure(text_color="red")
            self.activate_btn.configure(state="normal")
            self.code_entry.configure(state="normal")

    def _on_exit(self):
        self.activated = False
        self.destroy()
