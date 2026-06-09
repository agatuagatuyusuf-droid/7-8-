import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os

from .theme import Theme
from .widgets import CardFrame, AnimatedButton, create_section_title, create_divider
from bt_utils.resource_manager import ResourceManager


class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        
        self._dark_colors = Theme.get_dark_colors()
        self.configure(fg_color=self._dark_colors['bg_primary'], corner_radius=0)
        
        self._init_variables()
        self._create_ui()
    
    def _init_variables(self):
        default_alarm_sound = ResourceManager().get_alarm_sound_path()
        if not os.path.exists(default_alarm_sound):
            default_alarm_sound = ""
        
        self.alarm_sound_path = tk.StringVar(value=default_alarm_sound)
        self.alarm_volume = tk.IntVar(value=70)
        self.alarm_volume_str = tk.StringVar(value="70")
        
        default_project_path = self._get_default_project_path()
        self.default_project_path = tk.StringVar(value=default_project_path)
        
        self.start_shortcut_var = tk.StringVar(value="F10")
        self.stop_shortcut_var = tk.StringVar(value="F12")
        self.record_hotkey_var = tk.StringVar(value="F11")
        
        from config.settings_manager import SettingsManager
        settings = SettingsManager()
        self._current_keyboard_method = settings.get("input.keyboard_method", "pyautogui")
        self._current_mouse_method = settings.get("input.mouse_method", "pyautogui")
    
    def _get_default_project_path(self) -> str:
        """获取默认项目保存路径
        
        Returns:
            默认项目保存路径
        """
        from config.settings_manager import SettingsManager
        settings_manager = SettingsManager()
        saved_path = settings_manager.get("default_project_path", "")
        
        if saved_path and os.path.exists(saved_path):
            return saved_path
        
        return SettingsManager.get_default_workspace_path()
    
    def _create_ui(self):
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=Theme.DIMENSIONS['spacing_md'], pady=Theme.DIMENSIONS['spacing_md'])
        
        self._create_project_section(scroll_frame)
        self._create_alarm_section(scroll_frame)
        self._create_shortcut_section(scroll_frame)
        self._create_input_method_section(scroll_frame)
    
    def _create_project_section(self, parent):
        project_frame = CardFrame(parent)
        project_frame.pack(fill="x", pady=(0, Theme.DIMENSIONS['spacing_md']))
        
        project_header = ctk.CTkFrame(project_frame, fg_color="transparent")
        project_header.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(Theme.DIMENSIONS['spacing_md'], Theme.DIMENSIONS['spacing_sm']))
        create_section_title(project_header, "项目设置", level=1).pack(side="left")
        
        create_divider(project_frame)
        
        project_row = ctk.CTkFrame(project_frame, fg_color="transparent")
        project_row.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(Theme.DIMENSIONS['spacing_sm'], Theme.DIMENSIONS['spacing_md']))
        
        ctk.CTkLabel(project_row, text="默认保存位置:", font=Theme.get_font("sm"), text_color=self._dark_colors['text_secondary']).pack(side="left")
        
        self.project_path_entry = ctk.CTkEntry(
            project_row, 
            textvariable=self.default_project_path, 
            height=28, 
            state="disabled",
            fg_color=self._dark_colors['bg_tertiary'],
            text_color=self._dark_colors['text_primary']
        )
        self.project_path_entry.pack(side="left", fill="x", expand=True, padx=(Theme.DIMENSIONS['spacing_sm'], Theme.DIMENSIONS['spacing_sm']))
        
        self.browse_project_btn = AnimatedButton(
            project_row, 
            text="浏览", 
            font=Theme.get_font("xs"), 
            width=50, 
            height=28,
            corner_radius=Theme.DIMENSIONS['button_corner_radius'], 
            fg_color=Theme.COLORS['primary'],
            hover_color=Theme.COLORS['primary_hover'],
            command=self._browse_project_path
        )
        self.browse_project_btn.pack(side="left")
    
    def _create_alarm_section(self, parent):
        alarm_frame = CardFrame(parent)
        alarm_frame.pack(fill="x", pady=(0, Theme.DIMENSIONS['spacing_md']))
        
        alarm_header = ctk.CTkFrame(alarm_frame, fg_color="transparent")
        alarm_header.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(Theme.DIMENSIONS['spacing_md'], Theme.DIMENSIONS['spacing_sm']))
        create_section_title(alarm_header, "报警设置", level=1).pack(side="left")
        
        create_divider(alarm_frame)
        
        alarm_row1 = ctk.CTkFrame(alarm_frame, fg_color="transparent")
        alarm_row1.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=Theme.DIMENSIONS['spacing_sm'])
        
        ctk.CTkLabel(alarm_row1, text="声音:", font=Theme.get_font("sm"), text_color=self._dark_colors['text_secondary']).pack(side="left")
        
        alarm_sound_entry = ctk.CTkEntry(
            alarm_row1, 
            textvariable=self.alarm_sound_path, 
            height=28, 
            state="disabled",
            fg_color=self._dark_colors['bg_tertiary'],
            text_color=self._dark_colors['text_primary']
        )
        alarm_sound_entry.pack(side="left", fill="x", expand=True, padx=(Theme.DIMENSIONS['spacing_sm'], Theme.DIMENSIONS['spacing_sm']))
        
        alarm_sound_btn = AnimatedButton(
            alarm_row1, 
            text="浏览", 
            font=Theme.get_font("xs"), 
            width=50, 
            height=28,
            corner_radius=Theme.DIMENSIONS['button_corner_radius'], 
            fg_color=Theme.COLORS['primary'],
            hover_color=Theme.COLORS['primary_hover'],
            command=self._browse_alarm_sound
        )
        alarm_sound_btn.pack(side="left")
        
        alarm_row2 = ctk.CTkFrame(alarm_frame, fg_color="transparent")
        alarm_row2.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(Theme.DIMENSIONS['spacing_sm'], Theme.DIMENSIONS['spacing_md']))
        
        ctk.CTkLabel(alarm_row2, text="音量:", font=Theme.get_font("sm"), text_color=self._dark_colors['text_secondary']).pack(side="left")
        
        def update_volume_display(*args):
            self.alarm_volume_str.set(str(self.alarm_volume.get()))
        
        self.alarm_volume.trace_add("write", update_volume_display)
        
        volume_slider = ctk.CTkSlider(
            alarm_row2, 
            from_=0, 
            to=100, 
            variable=self.alarm_volume, 
            width=200,
            progress_color=Theme.COLORS['primary'],
            button_color=Theme.COLORS['text_primary']
        )
        volume_slider.pack(side="left", padx=(Theme.DIMENSIONS['spacing_sm'], Theme.DIMENSIONS['spacing_sm']))
        
        volume_label = ctk.CTkLabel(
            alarm_row2, 
            textvariable=self.alarm_volume_str, 
            font=Theme.get_font("sm"), 
            width=40,
            text_color=self._dark_colors['text_primary']
        )
        volume_label.pack(side="left")
    
    def _create_shortcut_section(self, parent):
        shortcut_frame = CardFrame(parent)
        shortcut_frame.pack(fill="x", pady=(0, Theme.DIMENSIONS['spacing_md']))
        
        shortcut_header = ctk.CTkFrame(shortcut_frame, fg_color="transparent")
        shortcut_header.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(Theme.DIMENSIONS['spacing_md'], Theme.DIMENSIONS['spacing_sm']))
        create_section_title(shortcut_header, "快捷键设置", level=1).pack(side="left")
        
        create_divider(shortcut_frame)
        
        shortcuts = [
            ("开始运行:", "F10", self.start_shortcut_var),
            ("停止运行:", "F12", self.stop_shortcut_var),
            ("录制按钮:", "F11", self.record_hotkey_var)
        ]
        
        for label, default, var in shortcuts:
            row = ctk.CTkFrame(shortcut_frame, fg_color="transparent")
            row.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=Theme.DIMENSIONS['spacing_sm'])
            
            ctk.CTkLabel(row, text=label, font=Theme.get_font("sm"), text_color=self._dark_colors['text_secondary']).pack(side="left")
            
            entry = ctk.CTkEntry(
                row, 
                textvariable=var, 
                width=80, 
                height=24, 
                state="disabled",
                fg_color=self._dark_colors['bg_tertiary'],
                text_color=self._dark_colors['text_primary']
            )
            entry.pack(side="left", padx=(Theme.DIMENSIONS['spacing_sm'], Theme.DIMENSIONS['spacing_xs']))
            
            btn = AnimatedButton(
                row, 
                text="修改", 
                font=Theme.get_font("xs"), 
                width=40, 
                height=24, 
                corner_radius=Theme.DIMENSIONS['button_corner_radius'],
                fg_color=Theme.COLORS['primary'], 
                hover_color=Theme.COLORS['primary_hover']
            )
            btn.configure(command=lambda e=entry, b=btn: self._start_key_listening(e, b))
            btn.pack(side="left")
        
        ctk.CTkFrame(shortcut_frame, height=6, fg_color="transparent").pack()
    
    def _create_input_method_section(self, parent):
        from bt_utils.input_manager import InputControllerManager
        from bt_utils.base_input import InputLevel
        from bt_utils.app_restarter import is_admin

        manager = InputControllerManager()
        available_methods = manager.get_available_methods()

        input_frame = CardFrame(parent)
        input_frame.pack(fill="x", pady=(0, Theme.DIMENSIONS['spacing_md']))

        input_header = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_header.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(Theme.DIMENSIONS['spacing_md'], Theme.DIMENSIONS['spacing_sm']))
        create_section_title(input_header, "输入方式", level=1).pack(side="left")

        create_divider(input_frame)

        # 构建选项和映射
        self._method_key_to_label = {}
        self._method_label_to_key = {}
        method_options = []

        for method_key, method_info in available_methods.items():
            label = method_info['name']
            if not method_info["available"]:
                label += "（不可用）"
            self._method_key_to_label[method_key] = label
            self._method_label_to_key[label] = method_key
            method_options.append(label)

        # ── 键盘引擎 ComboBox ──
        kb_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        kb_row.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=Theme.DIMENSIONS['spacing_sm'])

        ctk.CTkLabel(kb_row, text="键盘引擎:", font=Theme.get_font("sm"), text_color=self._dark_colors['text_secondary']).pack(side="left")

        current_kb_label = self._method_key_to_label.get(self._current_keyboard_method, method_options[0])
        self._kb_combo_var = tk.StringVar(value=current_kb_label)

        self.keyboard_method_combo = ctk.CTkComboBox(
            kb_row,
            values=method_options,
            variable=self._kb_combo_var,
            command=self._on_keyboard_method_changed,
            font=Theme.get_font("sm"),
            width=300,
            fg_color=self._dark_colors['bg_tertiary'],
            text_color=self._dark_colors['text_primary'],
            button_color=Theme.COLORS['primary'],
            button_hover_color=Theme.COLORS['primary_hover'],
        )
        self.keyboard_method_combo.pack(side="left", padx=(Theme.DIMENSIONS['spacing_sm'], 0))

        # ── 鼠标引擎 ComboBox ──
        ms_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        ms_row.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=Theme.DIMENSIONS['spacing_sm'])

        ctk.CTkLabel(ms_row, text="鼠标引擎:", font=Theme.get_font("sm"), text_color=self._dark_colors['text_secondary']).pack(side="left")

        current_ms_label = self._method_key_to_label.get(self._current_mouse_method, method_options[0])
        self._ms_combo_var = tk.StringVar(value=current_ms_label)

        self.mouse_method_combo = ctk.CTkComboBox(
            ms_row,
            values=method_options,
            variable=self._ms_combo_var,
            command=self._on_mouse_method_changed,
            font=Theme.get_font("sm"),
            width=300,
            fg_color=self._dark_colors['bg_tertiary'],
            text_color=self._dark_colors['text_primary'],
            button_color=Theme.COLORS['primary'],
            button_hover_color=Theme.COLORS['primary_hover'],
        )
        self.mouse_method_combo.pack(side="left", padx=(Theme.DIMENSIONS['spacing_sm'], 0))

        # ── IB 子驱动选项（键盘或鼠标任一选择 IB 时显示） ──
        self._ib_sub_frame = ctk.CTkFrame(input_frame, fg_color="transparent")

        ib_sub_row = ctk.CTkFrame(self._ib_sub_frame, fg_color="transparent")
        ib_sub_row.pack(fill="x", pady=Theme.DIMENSIONS['spacing_xs'])

        ctk.CTkLabel(ib_sub_row, text="IB驱动模式:", font=Theme.get_font("sm"),
                     text_color=self._dark_colors['text_secondary']).pack(side="left")

        ib_mode_labels = {
            "any_driver": "自动检测",
            "logitech": "Logitech LGS",
            "logitech_ghub_new": "Logitech G HUB (新版)",
            "razer": "Razer Synapse",
            "mou_class": "MouClassInputInjection",
            "send_input": "SendInput",
        }

        # 检测本机已安装的驱动
        try:
            from bt_utils.ib_input import detect_ib_driver_status
            driver_status = detect_ib_driver_status()
        except Exception:
            driver_status = {}

        ib_mode_options = []
        self._ib_mode_label_to_key = {}
        for mode_key, mode_label in ib_mode_labels.items():
            status = driver_status.get(mode_key, {})
            installed = status.get("installed", None)
            if installed is True:
                display = f"{mode_label}（已安装）"
            elif installed is False:
                display = f"{mode_label}（未安装）"
            else:
                display = mode_label
            ib_mode_options.append(display)
            self._ib_mode_label_to_key[display] = mode_key

        from config.settings_manager import SettingsManager
        current_ib_mode = SettingsManager.get_instance().get("input.ib_send_mode", "any_driver")
        current_ib_label = ib_mode_labels.get(current_ib_mode, "自动检测")
        for opt in ib_mode_options:
            if opt.startswith(current_ib_label):
                current_ib_label = opt
                break

        self._ib_mode_var = tk.StringVar(value=current_ib_label)

        self._ib_mode_combo = ctk.CTkComboBox(
            ib_sub_row,
            values=ib_mode_options,
            variable=self._ib_mode_var,
            command=self._on_ib_mode_changed,
            font=Theme.get_font("sm"),
            width=260,
            fg_color=self._dark_colors['bg_tertiary'],
            text_color=self._dark_colors['text_primary'],
            button_color=Theme.COLORS['primary'],
            button_hover_color=Theme.COLORS['primary_hover'],
        )
        self._ib_mode_combo.pack(side="left", padx=(Theme.DIMENSIONS['spacing_sm'], 0))

        # IB PID 输入（仅 MCII 模式需要）
        self._ib_pid_frame = ctk.CTkFrame(input_frame, fg_color="transparent")

        ib_pid_row = ctk.CTkFrame(self._ib_pid_frame, fg_color="transparent")
        ib_pid_row.pack(fill="x", pady=Theme.DIMENSIONS['spacing_xs'])

        ctk.CTkLabel(ib_pid_row, text="目标进程PID:", font=Theme.get_font("sm"),
                     text_color=self._dark_colors['text_secondary']).pack(side="left")

        current_pid = SettingsManager.get_instance().get("input.ib_target_pid", 0)
        self._ib_pid_var = tk.StringVar(value=str(current_pid))

        self._ib_pid_entry = ctk.CTkEntry(
            ib_pid_row,
            textvariable=self._ib_pid_var,
            width=80,
            height=24,
            font=Theme.get_font("sm"),
            fg_color=self._dark_colors['bg_tertiary'],
            text_color=self._dark_colors['text_primary'],
        )
        self._ib_pid_entry.pack(side="left", padx=(Theme.DIMENSIONS['spacing_sm'], 0))

        ctk.CTkLabel(ib_pid_row, text="（仅MCII模式需要）", font=Theme.get_font("xs"),
                     text_color=self._dark_colors['text_secondary']).pack(side="left", padx=(Theme.DIMENSIONS['spacing_xs'], 0))

        # 根据当前引擎决定是否显示子选项
        self._update_ib_sub_frame_visibility()

        # 状态信息
        status_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        status_row.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(0, Theme.DIMENSIONS['spacing_sm']))

        kb_name = available_methods.get(self._current_keyboard_method, {}).get("name", self._current_keyboard_method)
        ms_name = available_methods.get(self._current_mouse_method, {}).get("name", self._current_mouse_method)
        admin_status = "管理员" if is_admin() else "普通用户"
        status_text = f"当前状态: 键盘={kb_name}, 鼠标={ms_name} ({admin_status})"
        self._status_label = ctk.CTkLabel(
            status_row,
            text=status_text,
            font=Theme.get_font("xs"),
            text_color=self._dark_colors['primary']
        )
        self._status_label.pack(anchor="w")

        # 警告
        warn_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        warn_row.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(0, Theme.DIMENSIONS['spacing_md']))

        ctk.CTkLabel(
            warn_row,
            text="⚠ 切换输入方式后需要重启应用才能生效",
            font=Theme.get_font("xs"),
            text_color=self._dark_colors['warning']
        ).pack(anchor="w")

    def _update_ib_sub_frame_visibility(self):
        """根据键盘/鼠标引擎是否选择 IB 来决定 IB 子选项的显示"""
        show_ib = (self._current_keyboard_method == "ib" or self._current_mouse_method == "ib")
        if show_ib:
            self._ib_sub_frame.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(0, Theme.DIMENSIONS['spacing_sm']))
            current_ib_mode_key = self._ib_mode_label_to_key.get(self._ib_mode_var.get(), "any_driver")
            if current_ib_mode_key == "mou_class":
                self._ib_pid_frame.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(0, Theme.DIMENSIONS['spacing_sm']))
            else:
                self._ib_pid_frame.pack_forget()
        else:
            self._ib_sub_frame.pack_forget()
            self._ib_pid_frame.pack_forget()

    def _on_ib_mode_changed(self, choice=None):
        """IB 子驱动模式切换"""
        mode_key = self._ib_mode_label_to_key.get(choice, "any_driver")

        # 保存到设置
        from config.settings_manager import SettingsManager
        SettingsManager.get_instance().set("input.ib_send_mode", mode_key, auto_save=True)

        # MCII 模式显示 PID 输入
        if mode_key == "mou_class":
            self._ib_pid_frame.pack(fill="x", padx=Theme.DIMENSIONS['spacing_md'], pady=(0, Theme.DIMENSIONS['spacing_sm']))
        else:
            self._ib_pid_frame.pack_forget()

    def _on_keyboard_method_changed(self, choice=None):
        """键盘引擎切换"""
        new_method = self._method_label_to_key.get(choice, self._current_keyboard_method)
        if new_method == self._current_keyboard_method:
            return
        self._handle_method_change("keyboard", new_method)

    def _on_mouse_method_changed(self, choice=None):
        """鼠标引擎切换"""
        new_method = self._method_label_to_key.get(choice, self._current_mouse_method)
        if new_method == self._current_mouse_method:
            return
        self._handle_method_change("mouse", new_method)

    def _handle_method_change(self, which: str, new_method: str):
        """处理引擎切换逻辑"""
        from bt_utils.input_manager import InputControllerManager

        manager = InputControllerManager()
        methods = manager.get_available_methods()
        method_info = methods.get(new_method, {})

        if method_info.get("requires_admin", False):
            result = messagebox.askyesno(
                "切换输入方式",
                f"{method_info.get('name', new_method)}需要管理员权限才能正常工作。\n"
                "切换后应用将以管理员身份重新启动。\n\n"
                "是否立即重启？",
                icon='warning'
            )
            if result:
                self._save_ib_pid()
                if hasattr(self.app, '_restart_with_methods'):
                    kb = new_method if which == "keyboard" else self._current_keyboard_method
                    ms = new_method if which == "mouse" else self._current_mouse_method
                    self.app._restart_with_methods(kb, ms, as_admin=True)
            else:
                if which == "keyboard":
                    self._kb_combo_var.set(self._method_key_to_label.get(self._current_keyboard_method, ""))
                else:
                    self._ms_combo_var.set(self._method_key_to_label.get(self._current_mouse_method, ""))
        else:
            result = messagebox.askyesno(
                "切换输入方式",
                f"切换到 {method_info.get('name', new_method)}后，应用将重新启动。\n\n"
                "是否立即重启？",
                icon='question'
            )
            if result:
                self._save_ib_pid()
                if hasattr(self.app, '_restart_with_methods'):
                    kb = new_method if which == "keyboard" else self._current_keyboard_method
                    ms = new_method if which == "mouse" else self._current_mouse_method
                    self.app._restart_with_methods(kb, ms, as_admin=False)
            else:
                if which == "keyboard":
                    self._kb_combo_var.set(self._method_key_to_label.get(self._current_keyboard_method, ""))
                else:
                    self._ms_combo_var.set(self._method_key_to_label.get(self._current_mouse_method, ""))

    def _save_ib_pid(self):
        """保存 IB 目标进程 PID"""
        try:
            pid_str = self._ib_pid_var.get()
            pid = int(pid_str) if pid_str.isdigit() else 0
            from config.settings_manager import SettingsManager
            SettingsManager.get_instance().set("input.ib_target_pid", pid, auto_save=True)
        except Exception:
            pass
    
    def _browse_project_path(self):
        folder_path = filedialog.askdirectory(
            title="选择默认项目保存位置"
        )
        if folder_path:
            self.default_project_path.set(folder_path)
            self._ensure_workspace_exists()
    
    def _ensure_workspace_exists(self):
        """确保workspace文件夹存在"""
        workspace_path = self.default_project_path.get()
        if workspace_path:
            try:
                os.makedirs(workspace_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建workspace文件夹: {str(e)}")
    
    def _browse_alarm_sound(self):
        file_path = filedialog.askopenfilename(
            title="选择报警声音文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.ogg"), ("所有文件", "*.*")]
        )
        if file_path:
            self.alarm_sound_path.set(file_path)
    
    def _start_key_listening(self, entry, btn):
        btn.configure(text="请按键...", fg_color=Theme.COLORS['warning'])
        
        from pynput import keyboard
        from bt_utils.key_name_resolver import resolve_key_name
        
        def on_press(key):
            key_name = resolve_key_name(key)
            if key_name:
                display_name = key_name.upper() if len(key_name) > 1 else key_name
                try:
                    self.after(0, lambda: self._apply_settings_captured_key(entry, btn, display_name))
                except Exception:
                    pass
                return False
        
        self._settings_listener = keyboard.Listener(on_press=on_press)
        self._settings_listener.start()
        
        def reset_listening():
            self._stop_settings_listener()
            try:
                btn.configure(text="修改", fg_color=Theme.COLORS['primary'])
            except Exception:
                pass
        
        self._settings_timeout = self.after(10000, reset_listening)
    
    def _apply_settings_captured_key(self, entry, btn, key_name):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, key_name)
        entry.configure(state="disabled")
        
        btn.configure(text="修改", fg_color=Theme.COLORS['primary'])
        
        self._stop_settings_listener()
        self._update_editor_shortcuts()
    
    def _stop_settings_listener(self):
        if hasattr(self, '_settings_listener') and self._settings_listener:
            try:
                self._settings_listener.stop()
            except Exception:
                pass
            self._settings_listener = None
        if hasattr(self, '_settings_timeout') and self._settings_timeout:
            self.after_cancel(self._settings_timeout)
            self._settings_timeout = None
    
    def _update_editor_shortcuts(self):
        """更新编辑器的快捷键绑定"""
        try:
            from config.settings_manager import SettingsManager
            
            start_key = self.start_shortcut_var.get()
            stop_key = self.stop_shortcut_var.get()
            record_key = self.record_hotkey_var.get()
            
            settings_manager = SettingsManager.get_instance()
            settings_manager.set("shortcuts.start", start_key, auto_save=True)
            settings_manager.set("shortcuts.stop", stop_key, auto_save=True)
            settings_manager.set("shortcuts.record", record_key, auto_save=True)
            
            if hasattr(self.app, 'behavior_tree') and hasattr(self.app.behavior_tree, 'update_run_shortcuts'):
                self.app.behavior_tree.update_run_shortcuts(start_key, stop_key, record_key)
        except Exception:
            pass
    
    def get_settings(self):
        return {
            "alarm_sound_path": self.alarm_sound_path.get(),
            "alarm_volume": self.alarm_volume.get(),
            "default_project_path": self.default_project_path.get(),
            "shortcuts": {
                "start": self.start_shortcut_var.get(),
                "stop": self.stop_shortcut_var.get(),
                "record": self.record_hotkey_var.get()
            },
            "keyboard_method": self._current_keyboard_method,
            "mouse_method": self._current_mouse_method,
        }
    
    def load_settings(self, settings):
        default_alarm_sound = ResourceManager().get_alarm_sound_path()
        if not os.path.exists(default_alarm_sound):
            default_alarm_sound = ""
        
        default_project_path = self._get_default_project_path()
        
        if "alarm_sound_path" in settings and settings["alarm_sound_path"]:
            if os.path.exists(settings["alarm_sound_path"]):
                self.alarm_sound_path.set(settings["alarm_sound_path"])
            else:
                self.alarm_sound_path.set(default_alarm_sound)
        else:
            self.alarm_sound_path.set(default_alarm_sound)
        
        if "alarm_volume" in settings:
            self.alarm_volume.set(settings["alarm_volume"])
            self.alarm_volume_str.set(str(settings["alarm_volume"]))
        
        if "default_project_path" in settings and settings["default_project_path"]:
            if os.path.exists(settings["default_project_path"]):
                self.default_project_path.set(settings["default_project_path"])
            else:
                self.default_project_path.set(default_project_path)
        else:
            self.default_project_path.set(default_project_path)
        
        self._ensure_workspace_exists()
        
        if "shortcuts" in settings:
            shortcuts = settings["shortcuts"]
            if "start" in shortcuts:
                self.start_shortcut_var.set(shortcuts["start"])
            if "stop" in shortcuts:
                self.stop_shortcut_var.set(shortcuts["stop"])
            if "record" in shortcuts:
                self.record_hotkey_var.set(shortcuts["record"])
        
        if "input" in settings:
            input_settings = settings["input"]
            if "keyboard_method" in input_settings:
                self._current_keyboard_method = input_settings["keyboard_method"]
                if hasattr(self, '_kb_combo_var') and hasattr(self, '_method_key_to_label'):
                    label = self._method_key_to_label.get(input_settings["keyboard_method"], "")
                    if label:
                        self._kb_combo_var.set(label)
            if "mouse_method" in input_settings:
                self._current_mouse_method = input_settings["mouse_method"]
                if hasattr(self, '_ms_combo_var') and hasattr(self, '_method_key_to_label'):
                    label = self._method_key_to_label.get(input_settings["mouse_method"], "")
                    if label:
                        self._ms_combo_var.set(label)
