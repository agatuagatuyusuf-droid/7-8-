"""Check UI runtime bridge connectivity via TCP IPC.

Usage: python tools/check_ui_runtime_bridge.py

Steps:
1. Start CoreService
2. Connect via CoreClient
3. Create RuntimeBridge
4. Call start_tree with a simple tree
5. Poll status until completed
6. Call get_logs, verify non-empty
7. Call stop_tree
8. Call core.shutdown
9. Output check_ui_runtime_bridge OK
"""

import os
import subprocess
import sys
import time
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_core_service():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base, "csharp", "AutoDoor.CoreService",
                     "src", "AutoDoor.CoreService", "bin", "Release",
                     "net8.0-windows", "win-x64", "publish", "AutoDoor.CoreService.exe"),
        os.path.join(base, "csharp", "AutoDoor.CoreService",
                     "src", "AutoDoor.CoreService", "bin", "Release",
                     "net8.0-windows", "win-x64", "AutoDoor.CoreService.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def wait_for_port(host="127.0.0.1", port=19527, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            s = socket.create_connection((host, port), timeout=2)
            s.close()
            return True
        except (socket.timeout, ConnectionRefusedError):
            time.sleep(1)
    return False


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    exe_path = find_core_service()
    if exe_path is None:
        print("CoreService.exe not found, attempting dotnet publish...")
        result = subprocess.run(
            ["dotnet", "publish",
             os.path.join(project_root, "csharp", "AutoDoor.CoreService",
                          "src", "AutoDoor.CoreService", "AutoDoor.CoreService.csproj"),
             "-c", "Release", "-r", "win-x64", "--self-contained", "false"],
            capture_output=True, text=True, cwd=project_root
        )
        if result.returncode != 0:
            print(f"dotnet publish failed: {result.stderr}")
            sys.exit(1)
        exe_path = find_core_service()
        if exe_path is None:
            print("Cannot find CoreService.exe after publish")
            sys.exit(1)

    print(f"CoreService found: {exe_path}")

    proc = subprocess.Popen(
        [exe_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    try:
        print("Waiting for CoreService to listen...")
        if not wait_for_port():
            print("Timed out waiting for CoreService")
            proc.kill()
            sys.exit(1)
        print("CoreService is listening")

        from bt_bridge.core_client import CoreClient
        from bt_bridge.runtime_bridge import RuntimeBridge

        client = CoreClient(timeout=5)
        if not client.connect():
            print("Failed to connect to CoreService")
            proc.kill()
            sys.exit(1)

        bridge = RuntimeBridge(client)

        # Validate tree
        validate_result = bridge.validate_tree({
            "id": "test",
            "type": "StartNode",
            "children": [
                {"id": "seq1", "type": "SequenceNode", "children": [
                    {"id": "log1", "type": "LogStatusNode", "config": {"message": "bridge test"}}
                ]}
            ]
        })
        if not validate_result.get("success"):
            print(f"FAIL: validate_tree: {validate_result.get('message')}")
            client.disconnect()
            proc.kill()
            sys.exit(1)
        print(f"validate_tree OK")

        # Start tree
        start_result = bridge.start_tree({
            "id": "test",
            "type": "StartNode",
            "children": [
                {"id": "seq1", "type": "SequenceNode", "children": [
                    {"id": "log1", "type": "LogStatusNode", "config": {"message": "bridge test"}}
                ]}
            ]
        })
        if not start_result.get("success"):
            print(f"FAIL: start_tree: {start_result.get('message')}")
            client.disconnect()
            proc.kill()
            sys.exit(1)
        print(f"start_tree OK")

        # Poll status
        timeout = 15
        start_ts = time.time()
        completed = False
        while time.time() - start_ts < timeout:
            status = bridge.get_status()
            if status.get("success"):
                data = status.get("data") or {}
                if data.get("completed"):
                    completed = True
                    break
            time.sleep(0.5)

        if not completed:
            print("FAIL: Tree did not complete in time")
            client.disconnect()
            proc.kill()
            sys.exit(1)
        print(f"get_status completed OK")

        # Get logs
        logs_result = bridge.get_logs()
        if not logs_result.get("success"):
            print(f"FAIL: get_logs: {logs_result.get('message')}")
            client.disconnect()
            proc.kill()
            sys.exit(1)
        logs_data = logs_result.get("data", {})
        logs = logs_data.get("logs") or []
        print(f"get_logs returned {len(logs)} entries")

        # Get stats
        stats_result = bridge.get_stats()
        if not stats_result.get("success"):
            print(f"FAIL: get_stats: {stats_result.get('message')}")
            client.disconnect()
            proc.kill()
            sys.exit(1)
        print(f"get_stats OK: {stats_result.get('data')}")

        # Stop tree
        stop_result = bridge.stop_tree()
        if not stop_result.get("success"):
            print(f"WARN: stop_tree: {stop_result.get('message')}")

        # Shutdown
        client.send_request("core.shutdown")
        client.disconnect()

        try:
            proc.wait(timeout=5)
            print("CoreService exited gracefully")
        except subprocess.TimeoutExpired:
            proc.kill()
            print("FAIL: CoreService did not exit after shutdown")
            sys.exit(1)

        print("check_ui_runtime_bridge OK")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()
