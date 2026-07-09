import sys
import os
import traceback

from bt_utils.brand_manager import user_data_dir
_USER_DATA_DIR = user_data_dir()
LOG_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", _USER_DATA_DIR)
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "startup_error.log")

def write_log(msg):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass

write_log("=== Application startup begin ===")
write_log(f"Python version: {sys.version}")
write_log(f"Working directory: {os.getcwd()}")
write_log(f"sys.executable: {sys.executable}")
write_log(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'Not set')}")

def setup_error_logging():
    def exception_hook(exctype, value, tb):
        error_msg = ''.join(traceback.format_exception(exctype, value, tb))
        write_log(f"EXCEPTION: {error_msg}")
        print(f"STARTUP ERROR - Log file: {LOG_FILE}")
        print(error_msg)
        sys.__excepthook__(exctype, value, tb)
    
    sys.excepthook = exception_hook
    return LOG_FILE

LOG_FILE_RESULT = setup_error_logging()
print(f"Error logging initialized. Log file: {LOG_FILE}")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

write_log("Importing dpi_awareness...")
try:
    from bt_utils.dpi_awareness import initialize_dpi_awareness
    initialize_dpi_awareness()
    write_log("dpi_awareness initialized successfully")
except Exception as e:
    write_log(f"DPI awareness initialization failed: {e}")
    traceback.print_exc()

write_log("Importing json and logging...")
import json
import logging
write_log("json and logging imported successfully")

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def load_version():
    build_info_file = get_resource_path('bt_utils/build_info.json')
    
    if os.path.exists(build_info_file):
        try:
            with open(build_info_file, 'r', encoding='utf-8') as f:
                build_info = json.load(f)
                return build_info.get('version', '1.0.0')
        except Exception:
            pass
    
    return "1.2.2a"

def load_github_info():
    from bt_utils.brand_manager import get
    owner = get("repo_owner", "")
    repo = get("repo_name", "")
    if owner and repo:
        return owner, repo
    
    build_info_file = get_resource_path('bt_utils/build_info.json')
    if os.path.exists(build_info_file):
        try:
            with open(build_info_file, 'r', encoding='utf-8') as f:
                build_info = json.load(f)
                github = build_info.get('github', {})
                return github.get('owner', ''), github.get('repo', '')
        except Exception:
            pass
    return '', ''

VERSION = load_version()
write_log(f"Version loaded: {VERSION}")

write_log("Importing version_checker...")
from bt_utils.version_checker import BetaExpirationChecker
write_log("version_checker imported successfully")

beta_checker = BetaExpirationChecker()
if beta_checker.check_expiration():
    write_log("Beta expiration detected, showing dialog")
    beta_checker.show_expiration_dialog()
    sys.exit(0)

write_log("Importing customtkinter...")
import customtkinter as ctk
write_log("customtkinter imported successfully")

write_log("Importing BehaviorTreeApp...")
from bt_gui.app import BehaviorTreeApp
write_log("BehaviorTreeApp imported successfully")

write_log("Importing registry...")
from bt_core.registry import register_all_nodes
write_log("registry imported successfully")


def ensure_workspace_exists():
    from config.settings_manager import SettingsManager
    
    settings_manager = SettingsManager()
    saved_path = settings_manager.get("default_project_path", "")
    
    if saved_path and os.path.exists(saved_path):
        return
    
    workspace_dir = SettingsManager.get_default_workspace_path()
    
    try:
        os.makedirs(workspace_dir, exist_ok=True)
    except Exception:
        pass


def check_vcredist():
    try:
        import onnxruntime
        return True
    except ImportError as e:
        if "DLL load failed" in str(e) or "onnxruntime_pybind11_state" in str(e):
            return False
        raise
    except Exception:
        return False


def initialize_ocr():
    try:
        if not check_vcredist():
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            
            messagebox.showwarning(
                "缺少运行时库",
                "程序检测到缺少 Visual C++ Redistributable 运行时库。\n\n"
                "OCR 相关功能将无法使用。\n\n"
                "请下载并安装：\n"
                "https://aka.ms/vs/17/release/vc_redist.x64.exe\n\n"
                "安装后重启程序即可使用 OCR 功能。\n\n"
                "其他功能不受影响，可正常使用。"
            )
            
            root.destroy()
            
            from bt_utils.ocr_manager import OCRManager
            OCRManager.set_unavailable("缺少 Visual C++ Redistributable 运行时库")
            
            return False
        
        from bt_utils.ocr_manager import OCRManager
        OCRManager.initialize()
        return True
        
    except Exception as e:
        from bt_utils.ocr_manager import OCRManager
        OCRManager.set_unavailable(str(e))
        
        return False


def initialize_input():
    try:
        from bt_utils.input_controller_factory import InputController
        InputController()
        return True
    except Exception:
        return False


def check_admin_for_driver(method: str, display_name: str, is_available_fn):
    from config.settings_manager import SettingsManager
    from bt_utils.app_restarter import is_admin, restart_as_admin

    settings = SettingsManager.get_instance()
    kb_method = settings.get("input.keyboard_method", "pyautogui")
    ms_method = settings.get("input.mouse_method", "pyautogui")

    if kb_method != method and ms_method != method:
        return True

    if not is_available_fn():
        write_log(f"{display_name} DLL not found, falling back to PyAutoGUI")
        if kb_method == method:
            settings.set("input.keyboard_method", "pyautogui")
        if ms_method == method:
            settings.set("input.mouse_method", "pyautogui")
        return True

    if is_admin():
        write_log(f"{display_name}: already running as admin")
        return True

    write_log(f"{display_name}: not admin, requesting elevation")

    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()

    result = messagebox.askyesno(
        "需要管理员权限",
        f"{display_name}需要管理员权限才能正常工作。\n\n"
        "是否以管理员身份重新启动应用？\n\n"
        "点击「否」将使用 PyAutoGUI 模式启动。",
        icon='warning'
    )
    root.destroy()

    if result:
        success = restart_as_admin()
        if success:
            write_log("Admin restart initiated, exiting current process")
            sys.exit(0)
        else:
            write_log("Admin restart failed (UAC denied or error)")
            root2 = tk.Tk()
            root2.withdraw()
            messagebox.showwarning(
                "权限获取失败",
                "无法获取管理员权限，将使用 PyAutoGUI 模式启动。"
            )
            root2.destroy()

    write_log("Falling back to PyAutoGUI mode")
    if kb_method == method:
        settings.set("input.keyboard_method", "pyautogui")
    if ms_method == method:
        settings.set("input.mouse_method", "pyautogui")
    return True


def should_skip_license_check():
    build_type = os.environ.get("AUTODOOR_BUILD_TYPE", "release").lower()
    if build_type == "debug":
        write_log("Debug build: skipping license check")
        return True
    skip_env = os.environ.get("AUTODOOR_SKIP_LICENSE", "0")
    if skip_env == "1":
        write_log("AUTODOOR_SKIP_LICENSE=1: skipping license check")
        return True
    return False


def check_license_before_app():
    from config.settings_manager import SettingsManager
    from bt_bridge.core_process import is_commercial_bundle
    from bt_bridge.license_session import LicenseSession
    from bt_gui.dialogs.activation_dialog import ActivationDialog
    from bt_utils.log_manager import LogManager

    settings = SettingsManager.get_instance()
    commercial = is_commercial_bundle()
    use_csharp = settings.get("runtime.use_csharp_core", False)

    # 商业包强制启用 C# CoreService 授权，不允许跳过
    if commercial:
        use_csharp = True
        write_log("商业包模式：强制启用 C# CoreService 授权")

    if not use_csharp:
        write_log("源码开发模式：runtime.use_csharp_core=false，跳过 CoreService 授权检查")
        return True

    session = LicenseSession()

    write_log("Starting CoreService for license check...")
    if not session.ensure_ready():
        write_log(f"CoreService not ready: {session.last_error}")
        if is_commercial_bundle():
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "授权服务错误",
                session.last_error
            )
            root.destroy()
            return False
        else:
            write_log("源码模式：CoreService 不可用，已切回 Python 运行时")
            LogManager.debug_print("[WARN] 未找到 CoreService，已切回 Python 运行时")
            # 自动 fallback: 把本次运行改为 False，不持久化
            settings.set("runtime.use_csharp_core", False, auto_save=False)
            return True

    write_log("Checking license status...")
    result = session.status()
    if result.get("success"):
        data = result.get("data", {})
        if data.get("valid"):
            write_log("License valid, proceeding to main UI")
            return True

    write_log("License not valid, showing activation dialog")

    dialog = ActivationDialog(session)
    dialog.wait_window()

    if dialog.activated:
        write_log("Activation successful, proceeding to main UI")
        return True

    write_log("Activation cancelled, exiting")
    return False


def login_gate() -> bool:
    write_log("Showing login dialog...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
    except Exception:
        pass

    from bt_gui.dialogs.login_dialog import LoginDialog
    dialog = LoginDialog()
    dialog.wait_window()

    if not dialog.logged_in:
        write_log("Login cancelled, exiting")
        return False

    from bt_bridge.login_context import LoginContext
    LoginContext.set_session(getattr(dialog, "login_session", ""))

    write_log("Login successful")
    return True


def main():
    if not login_gate():
        sys.exit(1)

    if not should_skip_license_check():
        if not check_license_before_app():
            sys.exit(1)

    ensure_workspace_exists()

    from bt_utils.app_restarter import is_dd_available, is_ib_available
    check_admin_for_driver("dd", "DD虚拟键盘", is_dd_available)
    check_admin_for_driver("ib", "IbInputSimulator", is_ib_available)
    
    initialize_ocr()
    initialize_input()
    
    register_all_nodes()
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = BehaviorTreeApp()
    
    from bt_utils.version_checker import VersionChecker
    github_owner, github_repo = load_github_info()
    if github_owner and github_repo:
        version_checker = VersionChecker(
            app=app,
            owner=github_owner,
            repo=github_repo,
            current_version=VERSION
        )
        app._version_checker = version_checker
        version_checker.check_force_update()
        version_checker.start_auto_check(app)
    
    app.mainloop()


if __name__ == "__main__":
    main()
elif os.environ.get("AUTODOOR_TEST_IMPORT_ONLY") == "1":
    pass
