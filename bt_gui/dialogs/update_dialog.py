import customtkinter as ctk
import threading
from typing import Optional, Callable


class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, latest_version: str, current_version: str,
                 release_notes: list, mandatory: bool = False,
                 on_update: Optional[Callable] = None,
                 on_later: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None):
        super().__init__(parent)
        self.latest_version = latest_version
        self.current_version = current_version
        self.release_notes = release_notes
        self.mandatory = mandatory
        self._on_update = on_update
        self._on_later = on_later
        self._on_cancel = on_cancel

        self.title("发现新版本")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        w, h = 460, 380
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        if mandatory:
            self.protocol("WM_DELETE_WINDOW", lambda: None)

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="发现新版本",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, pady=(20, 5))

        ctk.CTkLabel(
            self, text=f"当前版本: {self.current_version}  \u2192  最新版本: {self.latest_version}",
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, pady=(0, 10))

        notes_text = "\n".join(f"\u2022 {note}" for note in self.release_notes) if self.release_notes else "暂无更新说明"

        textbox = ctk.CTkTextbox(self, height=140, width=400, wrap="word")
        textbox.grid(row=2, column=0, padx=30, pady=(0, 10))
        textbox.insert("0.0", notes_text)
        textbox.configure(state="disabled")

        if self.mandatory:
            ctk.CTkLabel(
                self, text="此版本为强制更新，更新后方可继续使用",
                font=ctk.CTkFont(size=12),
                text_color="#EF4444"
            ).grid(row=3, column=0, pady=(0, 10))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=(0, 20))

        ctk.CTkButton(
            btn_frame, text="立即更新", width=110, height=34,
            command=self._on_update_clicked
        ).pack(side="left", padx=8)

        if not self.mandatory:
            ctk.CTkButton(
                btn_frame, text="稍后再说", width=110, height=34,
                fg_color="gray", hover_color="#555555",
                command=self._on_later_clicked
            ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame, text="取消", width=110, height=34,
            fg_color="gray", hover_color="darkred",
            command=self._on_cancel_clicked
        ).pack(side="left", padx=8)

    def _on_update_clicked(self):
        if self._on_update:
            self._on_update()
        self.destroy()

    def _on_later_clicked(self):
        if self._on_later:
            self._on_later()
        self.destroy()

    def _on_cancel_clicked(self):
        if self._on_cancel:
            self._on_cancel()
        self.destroy()


class UpdateProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("正在更新")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.update_idletasks()
        w, h = 400, 160
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="正在下载更新",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, pady=(20, 10))

        self._status_label = ctk.CTkLabel(self, text="准备中...", font=ctk.CTkFont(size=12))
        self._status_label.grid(row=1, column=0, pady=(0, 5))

        self._progress_bar = ctk.CTkProgressBar(self, width=320)
        self._progress_bar.grid(row=2, column=0, padx=40, pady=(0, 10))
        self._progress_bar.set(0)

        self._percent_label = ctk.CTkLabel(self, text="0%", font=ctk.CTkFont(size=11))
        self._percent_label.grid(row=3, column=0)

    def set_progress(self, percent: float, status: str = ""):
        self._progress_bar.set(percent / 100.0)
        self._percent_label.configure(text=f"{int(percent)}%")
        if status:
            self._status_label.configure(text=status)
        self.update_idletasks()

    def set_status(self, status: str):
        self._status_label.configure(text=status)
        self.update_idletasks()