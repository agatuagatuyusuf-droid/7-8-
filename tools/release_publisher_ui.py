import os
import subprocess
import sys
import threading
import json
from datetime import datetime
from tkinter import messagebox, Text, scrolledtext
import tkinter as tk

import customtkinter as ctk

from tools.release_publisher_config import load_config, save_config


TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TOOLS_DIR)


class LogHandler:
    def __init__(self, text_widget: Text):
        self.text_widget = text_widget

    def write(self, msg: str):
        self.text_widget.insert(tk.END, msg)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class ReleasePublisherUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoDoor Pro \u53d1\u5e03\u4e2d\u5fc3")
        self.geometry("900x700")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.config = load_config()

        self._build_ui()
        self._load_config_to_ui()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === Header ===
        header = ctk.CTkLabel(self, text="AutoDoor Pro \u53d1\u5e03\u4e2d\u5fc3",
                              font=("Microsoft YaHei", 20, "bold"))
        header.grid(row=0, column=0, pady=(12, 4), sticky="n")

        # === Main content: config + buttons + log ===
        main = ctk.CTkFrame(self)
        main.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="nsew")
        main.grid_columnconfigure(1, weight=1)

        row = 0

        # -- Version / Channel / Platform row --
        ctk.CTkLabel(main, text="\u7248\u672c", width=80, anchor="w").grid(row=row, column=0, padx=(6, 2), pady=3, sticky="w")
        self.version_var = ctk.StringVar(value="1.6.1")
        ctk.CTkEntry(main, textvariable=self.version_var, width=120).grid(row=row, column=1, padx=(0, 10), pady=3, sticky="w")

        ctk.CTkLabel(main, text="\u901a\u9053", width=50, anchor="w").grid(row=row, column=2, padx=(0, 2), pady=3, sticky="w")
        self.channel_var = ctk.StringVar(value="stable")
        channel_menu = ctk.CTkOptionMenu(main, variable=self.channel_var, values=["stable", "beta", "internal"], width=100)
        channel_menu.grid(row=row, column=3, padx=(0, 10), pady=3, sticky="w")

        ctk.CTkLabel(main, text="\u5e73\u53f0", width=50, anchor="w").grid(row=row, column=4, padx=(0, 2), pady=3, sticky="w")
        self.platform_var = ctk.StringVar(value="win-x64")
        ctk.CTkOptionMenu(main, variable=self.platform_var, values=["win-x64"], width=100).grid(row=row, column=5, padx=(0, 0), pady=3, sticky="w")
        row += 1

        # -- Mode / Mandatory / Min version --
        ctk.CTkLabel(main, text="\u6a21\u5f0f", width=80, anchor="w").grid(row=row, column=0, padx=(6, 2), pady=3, sticky="w")
        self.mode_var = ctk.StringVar(value="release")
        ctk.CTkOptionMenu(main, variable=self.mode_var, values=["release", "dev"], width=120).grid(row=row, column=1, padx=(0, 10), pady=3, sticky="w")

        self.mandatory_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(main, text="\u5f3a\u5236\u66f4\u65b0", variable=self.mandatory_var).grid(row=row, column=2, columnspan=2, padx=(0, 10), pady=3, sticky="w")

        ctk.CTkLabel(main, text="\u6700\u4f4e\u652f\u6301\u7248\u672c", width=90, anchor="w").grid(row=row, column=4, padx=(0, 2), pady=3, sticky="w")
        self.min_version_var = ctk.StringVar(value="1.6.0")
        ctk.CTkEntry(main, textvariable=self.min_version_var, width=100).grid(row=row, column=5, padx=(0, 0), pady=3, sticky="w")
        row += 1

        # -- Release Notes --
        ctk.CTkLabel(main, text="\u66f4\u65b0\u8bf4\u660e", anchor="w").grid(row=row, column=0, padx=(6, 2), pady=3, sticky="nw")
        self.notes_text = ctk.CTkTextbox(main, height=60, width=200)
        self.notes_text.grid(row=row, column=1, columnspan=5, padx=(0, 6), pady=3, sticky="ew")
        row += 1

        # -- Config paths --
        path_fields = [
            ("\u9879\u76ee\u8def\u5f84", "project_root", PROJECT_ROOT),
            ("dist \u76ee\u5f55", "dist_dir", os.path.join(PROJECT_ROOT, "dist")),
            ("release \u76ee\u5f55", "release_dir", os.path.join(PROJECT_ROOT, "release")),
            ("\u79c1\u94a5\u8def\u5f84", "private_key_path", ""),
            ("\u6df7\u6dc6\u5668\u8def\u5f84", "obfuscator_path", ""),
            ("\u670d\u52a1\u5668\u53d1\u5e03\u76ee\u5f55", "server_publish_dir", ""),
        ]
        self.path_vars = {}
        for label, key, default in path_fields:
            ctk.CTkLabel(main, text=label, width=100, anchor="w").grid(row=row, column=0, padx=(6, 2), pady=2, sticky="w")
            var = ctk.StringVar(value=self.config.get(key, default))
            self.path_vars[key] = var
            entry = ctk.CTkEntry(main, textvariable=var)
            entry.grid(row=row, column=1, columnspan=3, padx=(0, 4), pady=2, sticky="ew")
            btn = ctk.CTkButton(main, text="...", width=32, command=lambda k=key, v=var: self._browse_path(k, v))
            btn.grid(row=row, column=4, padx=(0, 2), pady=2, sticky="w")
            row += 1

        # -- Action buttons --
        btn_frame = ctk.CTkFrame(main)
        btn_frame.grid(row=row, column=0, columnspan=6, pady=(8, 4), sticky="ew")
        btn_frame.grid_columnconfigure(tuple(range(8)), weight=1)

        actions = [
            ("1.\u68c0\u67e5\u73af\u5883", self._step_check_env),
            ("2.\u6784\u5efa\u5546\u4e1a\u5305", self._step_build),
            ("3.\u52a0\u5bc6/\u6df7\u6dc6", self._step_protect),
            ("4.\u751f\u6210Manifest", self._step_manifest),
            ("5.\u7b7e\u540dManifest", self._step_sign),
            ("6.\u751f\u6210\u66f4\u65b0\u5305", self._step_update_pkg),
            ("7.\u68c0\u67e5\u53d1\u5e03\u5305", self._step_check_pkg),
            ("8.\u4e00\u952e\u53d1\u5e03", self._step_onekey),
        ]
        for i, (text, cmd) in enumerate(actions):
            ctk.CTkButton(btn_frame, text=text, command=cmd, width=90).grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        row += 1

        # === Live log ===
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(log_frame, state="normal", font=("Consolas", 11))
        self.log_text.grid(row=0, column=0, sticky="nsew")

        # Redirect stdout
        self.log_handler = LogHandler(self.log_text)
        self._orig_stdout = sys.stdout
        sys.stdout = self.log_handler

    def _browse_path(self, key: str, var: ctk.StringVar):
        path = tk.filedialog.askdirectory(title=f"\u9009\u62e9 {key}")
        if path:
            var.set(path)

    def _load_config_to_ui(self):
        self.channel_var.set(self.config.get("channel", "stable"))
        self.platform_var.set(self.config.get("platform", "win-x64"))
        self.mandatory_var.set(self.config.get("mandatory", False))
        self.min_version_var.set(self.config.get("min_supported_version", "1.6.0"))
        self.mode_var.set(self.config.get("mode", "release"))
        for key, var in self.path_vars.items():
            if key in self.config and self.config[key]:
                var.set(self.config[key])

    def _gather_args(self) -> list:
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--channel", self.channel_var.get(),
            "--platform", self.platform_var.get(),
            "--mode", self.mode_var.get(),
            "--mandatory", str(self.mandatory_var.get()).lower(),
            "--min-supported-version", self.min_version_var.get(),
        ]
        for key, var in self.path_vars.items():
            val = var.get().strip()
            if val:
                flag = "--" + key.replace("_", "-")
                args.extend([flag, val])
        notes = self.notes_text.get("1.0", tk.END).strip()
        if notes:
            notes_path = os.path.join(PROJECT_ROOT, "_ui_release_notes.json")
            with open(notes_path, "w", encoding="utf-8") as f:
                json.dump([notes], f, ensure_ascii=False)
            args.extend(["--notes-file", notes_path])
        return args

    def _run_in_thread(self, target_fn):
        t = threading.Thread(target=target_fn, daemon=True)
        t.start()

    def _log_pipeline(self, args: list):
        self.log_text.insert(tk.END, f"\n{'='*60}\n")
        self.log_text.insert(tk.END, f"[{datetime.now():%H:%M:%S}] \u6267\u884c\u547d\u4ee4:\n")
        self.log_text.insert(tk.END, " ".join(args) + "\n")
        self.log_text.insert(tk.END, f"{'='*60}\n")
        self.log_text.see(tk.END)

    def _run_pipeline(self):
        args = self._gather_args()
        self._log_pipeline(args)
        proc = subprocess.run(args, capture_output=True, text=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        self.log_text.insert(tk.END, out)
        self.log_text.insert(tk.END, f"\n>>> \u8fdb\u7a0b\u8fd4\u56de\u7801: {proc.returncode}\n")
        self.log_text.see(tk.END)
        if proc.returncode == 0:
            messagebox.showinfo("\u53d1\u5e03\u6210\u529f", "\u53d1\u5e03\u6d41\u6c34\u7ebf\u6267\u884c\u5b8c\u6210")
        else:
            messagebox.showerror("\u53d1\u5e03\u5931\u8d25", f"\u53d1\u5e03\u5931\u8d25\uff0c\u8fd4\u56de\u7801: {proc.returncode}\n\u8bf7\u67e5\u770b\u65e5\u5fd7\u8be6\u60c5")

    def _step_check_env(self):
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--private-key", self.path_vars["private_key_path"].get(),
            "--obfuscator-path", self.path_vars["obfuscator_path"].get(),
            "--mode", self.mode_var.get(),
        ]
        self._log_pipeline(args)
        def run():
            proc = subprocess.run(args, capture_output=True, text=True)
            self.log_text.insert(tk.END, (proc.stdout or "") + (proc.stderr or ""))
            self.log_text.see(tk.END)
        self._run_in_thread(run)

    def _step_build(self):
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--mode", self.mode_var.get(),
            "--project-root", self.path_vars["project_root"].get() or PROJECT_ROOT,
        ]
        self._log_pipeline(args)
        def run():
            proc = subprocess.run(args, capture_output=True, text=True)
            self.log_text.insert(tk.END, (proc.stdout or "") + (proc.stderr or ""))
            self.log_text.see(tk.END)
        self._run_in_thread(run)

    def _step_protect(self):
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--mode", self.mode_var.get(),
            "--obfuscator-path", self.path_vars["obfuscator_path"].get(),
            "--dist-dir", self.path_vars["dist_dir"].get(),
            "--release-dir", self.path_vars["release_dir"].get(),
        ]
        self._log_pipeline(args)
        def run():
            proc = subprocess.run(args, capture_output=True, text=True)
            self.log_text.insert(tk.END, (proc.stdout or "") + (proc.stderr or ""))
            self.log_text.see(tk.END)
        self._run_in_thread(run)

    def _step_manifest(self):
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--channel", self.channel_var.get(),
            "--platform", self.platform_var.get(),
            "--mandatory", str(self.mandatory_var.get()).lower(),
            "--min-supported-version", self.min_version_var.get(),
        ]
        self._log_pipeline(args)
        def run():
            proc = subprocess.run(args, capture_output=True, text=True)
            self.log_text.insert(tk.END, (proc.stdout or "") + (proc.stderr or ""))
            self.log_text.see(tk.END)
        self._run_in_thread(run)

    def _step_sign(self):
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--private-key", self.path_vars["private_key_path"].get(),
        ]
        self._log_pipeline(args)
        def run():
            proc = subprocess.run(args, capture_output=True, text=True)
            self.log_text.insert(tk.END, (proc.stdout or "") + (proc.stderr or ""))
            self.log_text.see(tk.END)
        self._run_in_thread(run)

    def _step_update_pkg(self):
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--platform", self.platform_var.get(),
            "--dist-dir", self.path_vars["dist_dir"].get(),
            "--release-dir", self.path_vars["release_dir"].get(),
        ]
        self._log_pipeline(args)
        def run():
            proc = subprocess.run(args, capture_output=True, text=True)
            self.log_text.insert(tk.END, (proc.stdout or "") + (proc.stderr or ""))
            self.log_text.see(tk.END)
        self._run_in_thread(run)

    def _step_check_pkg(self):
        args = [
            sys.executable, os.path.join(TOOLS_DIR, "release_pipeline.py"),
            "--version", self.version_var.get(),
            "--release-dir", self.path_vars["release_dir"].get(),
        ]
        self._log_pipeline(args)
        def run():
            proc = subprocess.run(args, capture_output=True, text=True)
            self.log_text.insert(tk.END, (proc.stdout or "") + (proc.stderr or ""))
            self.log_text.see(tk.END)
        self._run_in_thread(run)

    def _step_onekey(self):
        self._run_in_thread(self._run_pipeline)

    def _save_current_config(self):
        cfg = {
            "project_root": self.path_vars["project_root"].get(),
            "dist_dir": self.path_vars["dist_dir"].get(),
            "release_dir": self.path_vars["release_dir"].get(),
            "private_key_path": self.path_vars["private_key_path"].get(),
            "obfuscator_path": self.path_vars["obfuscator_path"].get(),
            "server_publish_dir": self.path_vars["server_publish_dir"].get(),
            "channel": self.channel_var.get(),
            "platform": self.platform_var.get(),
            "mandatory": self.mandatory_var.get(),
            "min_supported_version": self.min_version_var.get(),
            "mode": self.mode_var.get(),
        }
        save_config(cfg)

    def _on_close(self):
        self._save_current_config()
        sys.stdout = self._orig_stdout
        self.destroy()


def main():
    app = ReleasePublisherUI()
    app.mainloop()


if __name__ == "__main__":
    main()
