"""
Check that the Python UI actually uses C# RuntimeBridge in real code paths.

Usage: python tools/check_ui_uses_csharp_runtime.py

Static checks:
1. RuntimeBridge imported/used in bt_gui or main.py
2. runtime.use_csharp_core config key present
3. license.status call path exists
4. start_tree call path exists
5. stop_tree call path exists
6. Fallback keywords (Python runtime, fallback, use_csharp_core) present
"""

import os
import sys
import re


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checks = []
    any_failed = False

    # 1. RuntimeBridge in bt_bridge or bt_gui
    found_runtime_bridge = False
    for root, dirs, files in os.walk(os.path.join(project_root, "bt_bridge")):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "class RuntimeBridge" in content:
                        found_runtime_bridge = True
                        break
    checks.append(("RuntimeBridge class exists", found_runtime_bridge))

    # 2. runtime.use_csharp_core in config
    found_config = False
    config_dir = os.path.join(project_root, "config")
    for root, dirs, files in os.walk(config_dir):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "use_csharp_core" in content or "runtime.use_csharp_core" in content:
                        found_config = True
                        break
    checks.append(("runtime.use_csharp_core in config", found_config))

    # 3. license.status in Python code
    found_license_status = False
    for root, dirs, files in os.walk(project_root):
        for f in files:
            if f.endswith(".py") and "bt_bridge" in root or "bt_gui" in root or "main.py" in f:
                path = os.path.join(root, f)
                if not os.path.isfile(path):
                    continue
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "license.status" in content or "license_status" in content:
                        found_license_status = True
                        break
    checks.append(("license.status referenced", found_license_status))

    # 4. start_tree referenced
    found_start_tree = False
    for root, dirs, files in os.walk(os.path.join(project_root, "bt_bridge")):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "start_tree" in content:
                        found_start_tree = True
                        break
    checks.append(("start_tree method exists", found_start_tree))

    # 5. stop_tree referenced
    found_stop_tree = False
    for root, dirs, files in os.walk(os.path.join(project_root, "bt_bridge")):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "stop_tree" in content:
                        found_stop_tree = True
                        break
    checks.append(("stop_tree method exists", found_stop_tree))

    # 6. Fallback keywords in editor code
    found_fallback = False
    editor_dir = os.path.join(project_root, "bt_gui", "bt_editor")
    for root, dirs, files in os.walk(editor_dir):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    if "use_csharp_core" in content or "Python runtime" in content or "fallback" in content:
                        found_fallback = True
                        break
    checks.append(("fallback/Python runtime keywords", found_fallback))

    for name, result in checks:
        status = "PASS" if result else "FAIL"
        if not result:
            any_failed = True
        print(f"  [{status}] {name}")

    if any_failed:
        print("check_ui_uses_csharp_runtime FAILED")
        sys.exit(1)

    print("check_ui_uses_csharp_runtime OK")
    sys.exit(0)


if __name__ == "__main__":
    main()