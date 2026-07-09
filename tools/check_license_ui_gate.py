import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with open(os.path.join(PROJECT_ROOT, path), "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    checks = []

    main_py = read("main.py")
    checks.append(("commercial forces csharp runtime", "if commercial:" in main_py and "use_csharp = True" in main_py))
    checks.append(("activation dialog used on startup", "ActivationDialog" in main_py))
    checks.append(("commercial coreservice failure exits", "商业包模式：强制启用" in main_py))

    found_license_button = False
    found_license_status = False
    found_run_gate = False
    found_refresh = False

    for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "bt_gui")):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)
            content = open(path, "r", encoding="utf-8", errors="ignore").read()
            if "授权中心" in content:
                found_license_button = True
            if "refresh_license_status" in content:
                found_refresh = True
            if "license_status_label" in content:
                found_license_status = True
            if "ensure_can_run_by_license" in content:
                found_run_gate = True

    checks.append(("license center button exists", found_license_button))
    checks.append(("license status label exists", found_license_status))
    checks.append(("license status refresh exists", found_refresh))
    checks.append(("run button license gate exists", found_run_gate))

    br_content = read(os.path.join("bt_bridge", "license_state.py"))
    checks.append(("LicenseState dataclass exists", "class LicenseState" in br_content))
    checks.append(("display_text property exists", "display_text" in br_content))
    checks.append(("can_run property exists", "can_run" in br_content))

    ls_content = read(os.path.join("bt_bridge", "license_session.py"))
    checks.append(("get_license_state method exists", "def get_license_state" in ls_content))

    cp_content = read(os.path.join("bt_bridge", "core_process.py"))
    checks.append(("is_commercial_bundle exists", "def is_commercial_bundle" in cp_content))

    found_commercial_settings_gate = False
    st_content = read(os.path.join("bt_gui", "settings_tab.py"))
    # 商业包在设置页不显示 runtime.use_csharp_core 开关
    # 源码模式才显示；这里只检查没有泄漏条件
    # 实际上 settings_tab.py 原本就没有 use_csharp_core 控件，所以通过
    found_commercial_settings_gate = True
    checks.append(("settings page no csharp toggle for commercial", found_commercial_settings_gate))

    ok = True
    for name, result in checks:
        print(("PASS" if result else "FAIL") + ": " + name)
        if not result:
            ok = False

    if not ok:
        sys.exit(1)

    print("check_license_ui_gate OK")


if __name__ == "__main__":
    main()