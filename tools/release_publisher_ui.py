import os
import subprocess
import sys
import threading
import json
import queue
import shutil
import signal
import time
from datetime import datetime
from tkinter import messagebox, Text, filedialog
import tkinter as tk
import glob as glob_mod

import customtkinter as ctk

from tools.release_publisher_config import load_config, save_config
from bt_utils.release_signature import generate_key_pair


TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TOOLS_DIR)


TASK_TIMEOUTS = {
    "check_env": 120,
    "build": 1800,
    "protect": 600,
    "manifest": 120,
    "sign": 120,
    "update_pkg": 300,
    "check_pkg": 120,
    "onekey": 2400,
}


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
        self.title("AutoDoor Pro 发布中心")
        self.geometry("900x750")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.config = load_config()
        self._current_proc = None
        self._task_cancelled = False

        self._build_ui()
        self._load_config_to_ui()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(self, text="AutoDoor Pro 发布中心",
                              font=("Microsoft YaHei", 20, "bold"))
        header.grid(row=0, column=0, pady=(12, 4), sticky="n")

        main = ctk.CTkFrame(self)
        main.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="nsew")
        main.grid_columnconfigure(1, weight=1)

        row = 0

        ctk.CTkLabel(main, text="版本", width=80, anchor="w").grid(row=row, column=0, padx=(6, 2), pady=3, sticky="w")
        self.version_var = ctk.StringVar(value="1.6.1")
        ctk.CTkEntry(main, textvariable=self.version_var, width=120).grid(row=row, column=1, padx=(0, 10), pady=3, sticky="w")

        ctk.CTkLabel(main, text="通道", width=50, anchor="w").grid(row=row, column=2, padx=(0, 2), pady=3, sticky="w")
        self.channel_var = ctk.StringVar(value="stable")
        channel_menu = ctk.CTkOptionMenu(main, variable=self.channel_var, values=["stable", "beta", "internal"], width=100)
        channel_menu.grid(row=row, column=3, padx=(0, 10), pady=3, sticky="w")

        ctk.CTkLabel(main, text="平台", width=50, anchor="w").grid(row=row, column=4, padx=(0, 2), pady=3, sticky="w")
        self.platform_var = ctk.StringVar(value="win-x64")
        ctk.CTkOptionMenu(main, variable=self.platform_var, values=["win-x64"], width=100).grid(row=row, column=5, padx=(0, 0), pady=3, sticky="w")
        row += 1

        ctk.CTkLabel(main, text="模式", width=80, anchor="w").grid(row=row, column=0, padx=(6, 2), pady=3, sticky="w")
        self.mode_var = ctk.StringVar(value="release")
        ctk.CTkOptionMenu(main, variable=self.mode_var, values=["release", "dev"], width=120).grid(row=row, column=1, padx=(0, 10), pady=3, sticky="w")

        self.mandatory_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(main, text="强制更新", variable=self.mandatory_var).grid(row=row, column=2, columnspan=2, padx=(0, 10), pady=3, sticky="w")

        ctk.CTkLabel(main, text="最低支持版本", width=90, anchor="w").grid(row=row, column=4, padx=(0, 2), pady=3, sticky="w")
        self.min_version_var = ctk.StringVar(value="1.6.0")
        ctk.CTkEntry(main, textvariable=self.min_version_var, width=100).grid(row=row, column=5, padx=(0, 0), pady=3, sticky="w")
        row += 1

        ctk.CTkLabel(main, text="更新说明", anchor="w").grid(row=row, column=0, padx=(6, 2), pady=3, sticky="nw")
        self.notes_text = ctk.CTkTextbox(main, height=60, width=200)
        self.notes_text.grid(row=row, column=1, columnspan=5, padx=(0, 6), pady=3, sticky="ew")
        row += 1

        path_fields = [
            ("项目路径", "project_root", PROJECT_ROOT),
            ("dist 目录", "dist_dir", os.path.join(PROJECT_ROOT, "dist")),
            ("release 目录", "release_dir", os.path.join(PROJECT_ROOT, "release")),
            ("私钥路径", "private_key_path", ""),
            ("混淆器路径", "obfuscator_path", ""),
            ("服务器发布目录", "server_publish_dir", ""),
            ("更新服务器 URL", "base_update_url", ""),
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

        btn_frame = ctk.CTkFrame(main)
        btn_frame.grid(row=row, column=0, columnspan=6, pady=(8, 4), sticky="ew")
        btn_frame.grid_columnconfigure(tuple(range(8)), weight=1)

        row += 1

        extra_btn_frame = ctk.CTkFrame(main)
        extra_btn_frame.grid(row=row, column=0, columnspan=6, pady=(0, 4), sticky="ew")
        extra_btn_frame.grid_columnconfigure(tuple(range(6)), weight=1)

        extra_actions = [
            ("自动搜索路径", self._auto_detect_paths),
            ("填充测试配置", self._fill_test_config),
            ("生成测试私钥", self._generate_test_key),
            ("安装 Obfuscar", self._install_obfuscar),
            ("停止任务", self._stop_current_task),
        ]
        for i, (text, cmd) in enumerate(extra_actions):
            ctk.CTkButton(extra_btn_frame, text=text, command=cmd, width=100).grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        row += 1

        actions = [
            ("1.检查环境", self._step_check_env),
            ("2.构建商业包", self._step_build),
            ("3.加密/混淆", self._step_protect),
            ("4.生成Manifest", self._step_manifest),
            ("5.签名Manifest", self._step_sign),
            ("6.生成更新包", self._step_update_pkg),
            ("7.检查发布包", self._step_check_pkg),
            ("8.一键发布", self._step_onekey),
        ]

        action_frame = ctk.CTkFrame(main)
        action_frame.grid(row=row, column=0, columnspan=6, pady=(0, 4), sticky="ew")
        action_frame.grid_columnconfigure(tuple(range(8)), weight=1)

        for i, (text, cmd) in enumerate(actions):
            ctk.CTkButton(action_frame, text=text, command=cmd, width=90).grid(row=0, column=i, padx=2, pady=2, sticky="ew")

        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(log_frame, state="normal", font=("Consolas", 11))
        self.log_text.grid(row=0, column=0, sticky="nsew")

        self.log_handler = LogHandler(self.log_text)
        self._orig_stdout = sys.stdout
        sys.stdout = self.log_handler

    def _browse_path(self, key: str, var: ctk.StringVar):
        if key == "private_key_path":
            path = filedialog.askopenfilename(
                title="选择 release_private.pem",
                filetypes=[("PEM Key", "*.pem"), ("All Files", "*.*")]
            )
            if path:
                var.set(path)
        elif key == "obfuscator_path":
            path = filedialog.askopenfilename(
                title="选择混淆器 exe",
                filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
            )
            if path:
                var.set(path)
        elif key == "base_update_url":
            var.set("https://example.com/updates/internal/win-x64/1.6.1-test")
        else:
            path = filedialog.askdirectory(title=f"选择 {key}")
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

    def _auto_detect_paths(self):
        self._log("开始自动搜索路径...")

        self.path_vars["project_root"].set(PROJECT_ROOT)

        dist_candidates = [
            os.path.join(PROJECT_ROOT, "dist", "AutoDoorPro"),
            os.path.join(PROJECT_ROOT, "dist"),
        ]
        release_dists = glob_mod.glob(os.path.join(PROJECT_ROOT, "release", "*", "dist"))
        dist_candidates.extend(sorted(release_dists))

        found_dist = None
        for d in dist_candidates:
            if os.path.isdir(d):
                found_dist = d
                break
        if found_dist:
            self.path_vars["dist_dir"].set(found_dist)
            self._log(f"dist 目录: {found_dist}")
        else:
            default_dist = os.path.join(PROJECT_ROOT, "dist")
            self.path_vars["dist_dir"].set(default_dist)
            self._log(f"未找到 dist 目录，默认: {default_dist}")

        release_dir = os.path.join(PROJECT_ROOT, "release")
        self.path_vars["release_dir"].set(release_dir)
        self._log(f"release 目录: {release_dir}")

        key_candidates = [
            os.path.join(os.environ.get("APPDATA", ""), "AutoDoorProPublisher", "keys", "release_private.pem"),
            os.path.join(os.environ.get("USERPROFILE", ""), ".autodoor", "keys", "release_private.pem"),
            os.path.join(PROJECT_ROOT, "keys", "release_private.pem"),
        ]
        found_key = None
        for k in key_candidates:
            if os.path.isfile(k):
                found_key = k
                break
        if found_key:
            self.path_vars["private_key_path"].set(found_key)
            self._log(f"私钥路径: {found_key}")
        else:
            self._log("未找到 release_private.pem，请生成或选择私钥。")
            self._log("推荐位置: %APPDATA%\\AutoDoorProPublisher\\keys\\release_private.pem")

        pub_path = os.path.join(PROJECT_ROOT, "resources", "security", "release_public.pem")
        if os.path.isfile(pub_path):
            self._log(f"公钥已存在: {pub_path}")
        else:
            self._log("警告: 未找到 resources/security/release_public.pem")

        if self._auto_detect_obfuscator():
            obfus_already_found = True
        else:
            obfus_already_found = False

        obfus_candidates = [
            os.path.join(PROJECT_ROOT, "tools", ".dotnet-tools", "obfuscar.exe"),
            os.path.join(os.environ.get("USERPROFILE", ""), ".dotnet", "tools", "obfuscar.exe"),
            os.path.join("D:\\Tools\\Obfuscator\\obfuscator.exe"),
            os.path.join("D:\\Tools\\ConfuserEx\\Confuser.CLI.exe"),
            os.path.join("D:\\Tools\\ConfuserEx\\ConfuserEx.exe"),
            os.path.join("C:\\Tools\\Obfuscator\\obfuscator.exe"),
            os.path.join("C:\\Tools\\ConfuserEx\\Confuser.CLI.exe"),
            os.path.join("C:\\Program Files\\ConfuserEx\\Confuser.CLI.exe"),
        ]
        found_obfus = None
        for o in obfus_candidates:
            if os.path.isfile(o):
                found_obfus = o
                break
        if found_obfus and not obfus_already_found:
            self.path_vars["obfuscator_path"].set(found_obfus)
            self._log(f"混淆器路径: {found_obfus}")
        else:
            self._log("未找到混淆器。dev 模式可以跳过混淆；release 模式必须配置真实混淆器。")

        self._auto_fill_update_url()
        self._log("自动搜索路径完成。")

    def _auto_fill_update_url(self):
        version = self.version_var.get().strip()
        channel = self.channel_var.get().strip()
        platform = self.platform_var.get().strip()
        mode = self.mode_var.get().strip()
        if mode == "dev":
            dev_version = version if version.endswith("-test") else f"{version}-test"
            url = f"https://example.com/updates/internal/{platform}/{dev_version}"
        else:
            url = f"https://your-domain.com/updates/{channel}/{platform}/{version}"
        self.path_vars["base_update_url"].set(url)

    def _fill_test_config(self):
        self.version_var.set("1.6.1-test")
        self.channel_var.set("internal")
        self.platform_var.set("win-x64")
        self.mode_var.set("dev")
        self.mandatory_var.set(False)
        self.min_version_var.set("1.6.0")
        self.path_vars["base_update_url"].set("https://example.com/updates/internal/win-x64/1.6.1-test")
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", "发布演练测试版本，不作为正式销售版本")
        self._auto_detect_paths()
        self._log("测试配置已填充。")

    def _install_obfuscar(self):
        script = os.path.join(TOOLS_DIR, "install_obfuscar.ps1")
        if not os.path.exists(script):
            self._log("未找到 tools/install_obfuscar.ps1")
            return

        args = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", script,
        ]

        def run():
            self._run_pipeline_with_timeout(args, 600)
            self._auto_detect_obfuscator()

        self._run_in_thread(run)

    def _auto_detect_obfuscator(self):
        find_script = os.path.join(TOOLS_DIR, "find_obfuscar.ps1")
        if os.path.exists(find_script):
            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-ExecutionPolicy", "Bypass",
                        "-File", find_script,
                        "-ProjectRoot", PROJECT_ROOT,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip().splitlines()[-1].strip()
                    if os.path.exists(path):
                        self.path_vars["obfuscator_path"].set(path)
                        self._log(f"Obfuscar 路径: {path}")
                        return True
            except Exception as e:
                self._log(f"自动查找 Obfuscar 失败: {e}")

        return False

    def _generate_test_key(self):
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        keys_dir = os.path.join(appdata, "AutoDoorProPublisher", "keys")
        private_key_path = os.path.join(keys_dir, "release_private.pem")
        public_key_path = os.path.join(PROJECT_ROOT, "resources", "security", "release_public.pem")

        if os.path.isfile(private_key_path):
            self._log(f"私钥已存在: {private_key_path}")
            self.path_vars["private_key_path"].set(private_key_path)
            return

        self._log("正在生成测试密钥对...")
        try:
            ok = generate_key_pair(private_key_path, public_key_path)
            if ok:
                self.path_vars["private_key_path"].set(private_key_path)
                self._log(f"私钥已生成到: {private_key_path}")
                self._log("私钥已生成到 APPDATA，不要提交 git")
            else:
                self._log("密钥生成失败，请检查依赖（cryptography 库）")
        except Exception as e:
            self._log(f"密钥生成失败: {e}")

    def _terminate_current_proc(self):
        if self._current_proc and self._current_proc.poll() is None:
            try:
                self._current_proc.terminate()
                time.sleep(1)
                if self._current_proc.poll() is None:
                    self._current_proc.kill()
            except Exception:
                pass

    def _stop_current_task(self):
        if self._current_proc and self._current_proc.poll() is None:
            self._log("正在停止当前任务...")
            self._task_cancelled = True
            self._terminate_current_proc()
            self._log("任务已停止。")
        else:
            self._log("当前无运行中的任务。")

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
        allowed_path_args = {
            "project_root",
            "dist_dir",
            "release_dir",
            "private_key_path",
            "obfuscator_path",
            "base_update_url",
        }
        for key, var in self.path_vars.items():
            if key not in allowed_path_args:
                continue
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

    def _validate_before_run(self) -> bool:
        mode = self.mode_var.get()
        priv_key = self.path_vars["private_key_path"].get().strip()
        obfus = self.path_vars["obfuscator_path"].get().strip()
        base_url = self.path_vars["base_update_url"].get().strip()

        if not priv_key:
            messagebox.showerror("缺少私钥", "dev/release 模式都需要私钥签名 manifest，请选择或生成 release_private.pem")
            return False

        if not base_url:
            url_hint = "https://example.com/updates/internal/win-x64/1.6.1-test" if mode == "dev" else "https://your-domain.com/updates/stable/win-x64/1.6.1"
            messagebox.showerror("缺少更新服务器 URL", f"请填写更新服务器 URL。\n示例: {url_hint}")
            return False

        if mode == "release":
            if not obfus:
                messagebox.showerror("缺少混淆器", "release 模式必须配置真实混淆器，不能假混淆。")
                return False

        return True

    def _run_in_thread(self, target_fn):
        t = threading.Thread(target=target_fn, daemon=True)
        t.start()

    def _log(self, msg: str):
        self.log_text.insert(tk.END, f"[{datetime.now():%H:%M:%S}] {msg}\n")
        self.log_text.see(tk.END)

    def _log_pipeline(self, args: list):
        self._log(f"\n{'='*60}")
        self._log(f"执行命令: {' '.join(args)}")
        self._log(f"{'='*60}\n")

    def _reader_thread(self, pipe, output_queue):
        try:
            for line in iter(pipe.readline, ""):
                output_queue.put(line)
        except Exception as e:
            output_queue.put(f"[读取输出异常] {e}\n")
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    def _run_pipeline_with_timeout(self, args: list, timeout: int):
        self._log_pipeline(args)
        self._task_cancelled = False

        output_queue = queue.Queue()

        try:
            self._current_proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            reader = threading.Thread(
                target=self._reader_thread,
                args=(self._current_proc.stdout, output_queue),
                daemon=True
            )
            reader.start()

            start_time = time.time()

            while True:
                while True:
                    try:
                        line = output_queue.get_nowait()
                    except queue.Empty:
                        break
                    if line:
                        self.log_text.insert(tk.END, line)
                        self.log_text.see(tk.END)

                if self._task_cancelled:
                    self._terminate_current_proc()
                    self._log("任务已停止")
                    break

                if time.time() - start_time > timeout:
                    self._log(f"任务超时（{timeout}秒），已终止")
                    self._terminate_current_proc()
                    break

                rc = self._current_proc.poll()
                if rc is not None:
                    while True:
                        try:
                            line = output_queue.get_nowait()
                        except queue.Empty:
                            break
                        if line:
                            self.log_text.insert(tk.END, line)
                            self.log_text.see(tk.END)

                    self._log(f"\n>>> 进程返回码: {rc}")
                    if rc == 0:
                        self._log(">>> 任务完成")
                    else:
                        self._log(">>> 任务失败")
                    break

                time.sleep(0.1)

        except Exception as e:
            self._log(f"执行异常: {e}")
        finally:
            self._current_proc = None

    def _run_pipeline(self):
        if not self._validate_before_run():
            return
        args = self._gather_args()
        self._run_pipeline_with_timeout(args, TASK_TIMEOUTS["onekey"])

    def _step_check_env(self):
        self._log("检查环境...")
        self._log(f"项目根目录: {PROJECT_ROOT}")
        self._log(f"Python: {sys.executable}")
        paths_to_check = [
            ("项目目录", self.path_vars["project_root"].get() or PROJECT_ROOT),
            ("dist 目录", self.path_vars["dist_dir"].get()),
            ("release 目录", self.path_vars["release_dir"].get()),
            ("私钥", self.path_vars["private_key_path"].get()),
            ("混淆器", self.path_vars["obfuscator_path"].get()),
        ]
        all_ok = True
        for name, p in paths_to_check:
            exists = os.path.exists(p) if p else False
            self._log(f"  {name}: {'✓' if exists else '✗'} {p}")
            if not exists and p:
                all_ok = False
        if all_ok:
            self._log("环境检查通过。")
        else:
            self._log("环境检查有警告，请留意。")

    def _step_build(self):
        self._log("当前按钮暂未单独实现，请使用一键发布")

    def _step_protect(self):
        mode = self.mode_var.get().strip()
        dist_dir = self.path_vars["dist_dir"].get().strip()
        release_dir = self.path_vars["release_dir"].get().strip()
        obfus = self.path_vars["obfuscator_path"].get().strip()

        input_dir = os.path.join(dist_dir, "CoreService")
        version = self.version_var.get().strip()
        output_dir = os.path.join(release_dir, f"AutoDoorPro-{version}", "dist", "CoreService")

        if mode == "release" and not obfus:
            self._log("release 模式必须配置混淆器路径")
            return

        ps1_path = os.path.join(TOOLS_DIR, "protect_csharp.ps1")
        args = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", ps1_path,
            "-InputDir", input_dir,
            "-OutputDir", output_dir,
            "-ObfuscatorPath", obfus,
            "-Mode", mode,
        ]
        self._run_in_thread(lambda: self._run_pipeline_with_timeout(args, TASK_TIMEOUTS["protect"]))

    def _step_manifest(self):
        self._log("当前按钮暂未单独实现，请使用一键发布")

    def _step_sign(self):
        self._log("当前按钮暂未单独实现，请使用一键发布")

    def _step_update_pkg(self):
        self._log("当前按钮暂未单独实现，请使用一键发布")

    def _step_check_pkg(self):
        self._log("当前按钮暂未单独实现，请使用一键发布")

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
            "base_update_url": self.path_vars["base_update_url"].get(),
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
