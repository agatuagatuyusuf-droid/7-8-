import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    full_path = os.path.join(PROJECT_ROOT, path)
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    checks = []

    tcp = read("csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/Ipc/TcpIpcServer.cs")
    checks.append(("auth.login exists", "auth.login" in tcp))
    checks.append(("auth.status exists", "auth.status" in tcp))
    checks.append(("auth.logout exists", "auth.logout" in tcp))
    checks.append(("LOGIN_REQUIRED exists", "LOGIN_REQUIRED" in tcp))
    checks.append(("RequireLogin exists", "RequireLogin" in tcp))
    checks.append(("tree.start protected", "tree.start" in tcp and "RequireLogin" in tcp))
    checks.append(("tree pause passes payload", '"tree.pause" => HandleTreePause(payload)' in tcp))
    checks.append(("tree resume passes payload", '"tree.resume" => HandleTreeResume(payload)' in tcp))
    checks.append(("tree stop passes payload", '"tree.stop" => HandleTreeStop(payload)' in tcp))
    checks.append(("no RequireLogin default", "RequireLogin(default)" not in tcp))

    login_service = read("csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/Security/LoginSessionService.cs")
    checks.append(("LoginSessionService exists", "class LoginSessionService" in login_service))
    checks.append(("password hash used", "TestPasswordSha256" in login_service))
    checks.append(("admin123 not compared plaintext", 'password == "admin123"' not in login_service))

    runtime_bridge = read("bt_bridge/runtime_bridge.py")
    checks.append(("RuntimeBridge imports LoginContext", "LoginContext" in runtime_bridge))
    checks.append(("RuntimeBridge sends login_session", "login_session" in runtime_bridge and "LoginContext.get_session" in runtime_bridge))

    login_context = read("bt_bridge/login_context.py")
    checks.append(("LoginContext exists", "class LoginContext" in login_context))
    checks.append(("LoginContext has get_session", "def get_session" in login_context))

    login_dialog = read("bt_gui/dialogs/login_dialog.py")
    checks.append(("LoginDialog has login_session", "self.login_session" in login_dialog))
    checks.append(("LoginDialog calls core login", "auth_login" in login_dialog))
    checks.append(("commercial bundle uses core login", "is_commercial_bundle" in login_dialog))
    checks.append(("login dialog connects CoreClient", ".connect()" in login_dialog and "auth_login" in login_dialog))
    checks.append(("login dialog has no max attempts", "MAX_ATTEMPTS" not in login_dialog and "attempts >=" not in login_dialog and "错误次数过多" not in login_dialog))

    main_py = read("main.py")
    checks.append(("main stores LoginContext", "LoginContext.set_session" in main_py))

    guard = read("csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/Security/SecurityGuard.cs")
    checks.append(("SecurityGuard exists", "class SecurityGuard" in guard))
    checks.append(("debugger check exists", "Debugger.IsAttached" in guard or "IsDebuggerPresent" in guard))
    checks.append(("CoreService exits itself only", "Environment.Exit" in guard))
    checks.append(("no shutdown command", "shutdown" not in guard.lower()))

    ok = True
    for name, result in checks:
        print(("PASS" if result else "FAIL") + ": " + name)
        if not result:
            ok = False

    if not ok:
        sys.exit(1)

    print("check_core_login_gate OK")


if __name__ == "__main__":
    main()
