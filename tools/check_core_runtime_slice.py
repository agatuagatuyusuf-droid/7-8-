#!/usr/bin/env python
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path: str) -> str:
    full = os.path.join(PROJECT_ROOT, path)
    if not os.path.exists(full):
        return ""
    with open(full, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def exists(path: str) -> bool:
    return os.path.exists(os.path.join(PROJECT_ROOT, path))


def main() -> int:
    checks = []

    native_path = "csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/Runtime/NativeInput/NativeInputExecutor.cs"
    core_action_path = "csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/Runtime/CoreActionExecutor.cs"
    tcp_path = "csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/Ipc/TcpIpcServer.cs"
    program_path = "csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/Program.cs"

    checks.append(("NativeInputExecutor exists", exists(native_path)))
    checks.append(("CoreActionExecutor exists", exists(core_action_path)))

    native = read(native_path)
    checks.append(("native supports key press via SendInput", "KeyPressAsync" in native and "SendInput" in native and "SendKeys.SendWait" not in native))
    checks.append(("native supports text input via unicode SendInput", "TextInputAsync" in native and "KEYEVENTF_UNICODE" in native))
    checks.append(("native supports mouse click via SendInput", "MouseClickAsync" in native and "SetCursorPos" in native and "SendMouseButton" in native))
    checks.append(("native limits text length", "TEXT_TOO_LONG" in native and "2000" in native))

    core_action = read(core_action_path)
    checks.append(("core action wraps native input", "NativeInputExecutor" in core_action and "CoreActionExecutor" in core_action))

    program = read(program_path)
    checks.append(("Program registers NativeInputExecutor", "AddSingleton<NativeInputExecutor>" in program))
    checks.append(("Program registers CoreActionExecutor", "AddSingleton<CoreActionExecutor>" in program))

    tcp = read(tcp_path)
    checks.append(("tcp has key action", "core.input.key_press" in tcp))
    checks.append(("tcp has text action", "core.input.text_input" in tcp))
    checks.append(("tcp has mouse action", "core.input.mouse_click" in tcp))
    checks.append(("tcp has CoreRuntimeFeature", "CoreRuntimeFeature" in tcp and "core_runtime" in tcp))
    checks.append(("tcp has RequireLoginAndFeature", "RequireLoginAndFeature" in tcp and "FEATURE_NOT_AUTHORIZED" in tcp))
    checks.append(("key input requires feature gate", "HandleCoreInputKeyPressAsync" in tcp and "RequireLoginAndFeature(payload, CoreRuntimeFeature)" in tcp))
    checks.append(("text input requires feature gate", "HandleCoreInputTextInputAsync" in tcp and "RequireLoginAndFeature(payload, CoreRuntimeFeature)" in tcp))
    checks.append(("mouse input requires feature gate", "HandleCoreInputMouseClickAsync" in tcp and "RequireLoginAndFeature(payload, CoreRuntimeFeature)" in tcp))
    checks.append(("tcp returns LOGIN_REQUIRED", "LOGIN_REQUIRED" in tcp))
    checks.append(("tcp returns FEATURE_NOT_AUTHORIZED", "FEATURE_NOT_AUTHORIZED" in tcp))

    client = read("bt_bridge/core_client.py")
    checks.append(("python client key helper exists", "core_input_key_press" in client))
    checks.append(("python client text helper exists", "core_input_text_input" in client))
    checks.append(("python client mouse helper exists", "core_input_mouse_click" in client))
    checks.append(("python client uses core key action", "core.input.key_press" in client))
    checks.append(("python client uses core text action", "core.input.text_input" in client))
    checks.append(("python client uses core mouse action", "core.input.mouse_click" in client))

    checks.append(("core input security tests exist", exists("csharp/AutoDoor.CoreService/src/AutoDoor.CoreService.Tests/CoreInputSecurityTests.cs")))
    tests = read("csharp/AutoDoor.CoreService/src/AutoDoor.CoreService.Tests/CoreInputSecurityTests.cs")
    checks.append(("tests reject empty login token", "LoginSessionServiceRejectsEmptyToken" in tests and "Validate(\"\")" in tests))
    checks.append(("tests reject long text without sending input", "NativeInputExecutorRejectsLongText" in tests and "TEXT_TOO_LONG" in tests and "2001" in tests))
    checks.append(("core input tests avoid unused broad service usings", "AutoDoor.CoreService.Ipc" not in tests and "AutoDoor.CoreService.License" not in tests and "AutoDoor.CoreService.Common" not in tests))

    ok = True
    for name, result in checks:
        print(("PASS" if result else "FAIL") + ": " + name)
        if not result:
            ok = False

    if not ok:
        return 1

    print("check_core_runtime_slice OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
