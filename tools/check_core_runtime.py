"""
Check C# behavior tree runtime via TCP IPC with real assertions.

Usage: python tools/check_core_runtime.py

Steps:
1. Start CoreService
2. Connect via IPC
3. Call tree.validate - assert success
4. Call tree.start - assert success
5. Poll tree.status until completed=true
6. Assert completed=true
7. Call runtime.logs - assert not-empty
8. Call core.shutdown
9. Assert process exits within 5s
10. Output check_core_runtime OK
"""

import json
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
                     "net8.0", "win-x64", "publish", "AutoDoor.CoreService.exe"),
        os.path.join(base, "csharp", "AutoDoor.CoreService",
                     "src", "AutoDoor.CoreService", "bin", "Release",
                     "net8.0", "win-x64", "AutoDoor.CoreService.exe"),
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


def assert_ok(result, label):
    if not result.get("success"):
        msg = result.get("message") or result.get("error_code") or "no message"
        print(f"FAIL: {label} - {msg}")
        sys.exit(1)
    print(f"OK: {label}")


def poll_status(client, expected_key="completed", expected_value=True, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        status = client.send_request("tree.status")
        if status.get("success"):
            data = status.get("data") or {}
            if data.get(expected_key) == expected_value:
                return status
        time.sleep(0.5)
    print(f"FAIL: Timed out waiting for {expected_key}={expected_value}")
    sys.exit(1)


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
        client = CoreClient(timeout=5)
        if not client.connect():
            print("Failed to connect to CoreService")
            proc.kill()
            sys.exit(1)

        # tree.validate
        validate_result = client.send_request("tree.validate", {
            "tree": {
                "id": "test",
                "type": "StartNode",
                "children": [
                    {"id": "seq1", "type": "SequenceNode", "children": [
                        {"id": "delay1", "type": "DelayNode", "config": {"delay_ms": 100}},
                        {"id": "log1", "type": "LogStatusNode", "config": {"message": "hello"}}
                    ]}
                ]
            }
        })
        assert_ok(validate_result, "tree.validate")
        print(f"  validate result: {validate_result}")

        # tree.start
        start_result = client.send_request("tree.start", {
            "tree": {
                "id": "test",
                "type": "StartNode",
                "children": [
                    {"id": "seq1", "type": "SequenceNode", "children": [
                        {"id": "delay1", "type": "DelayNode", "config": {"delay_ms": 100}},
                        {"id": "log1", "type": "LogStatusNode", "config": {"message": "hello"}}
                    ]}
                ]
            }
        })
        assert_ok(start_result, "tree.start")
        print(f"  start result: {start_result}")

        # Poll tree.status until completed=true
        status_result = poll_status(client, "completed", True)
        assert_ok(status_result, "tree.status (completed=true)")
        print(f"  status result: {status_result}")

        # runtime.logs
        logs_result = client.send_request("runtime.logs")
        assert_ok(logs_result, "runtime.logs")
        logs_data = logs_result.get("data", {})
        logs = logs_data.get("logs") or []
        if not logs:
            print("FAIL: runtime.logs returned empty")
            sys.exit(1)
        print(f"  logs contain {len(logs)} entries: {[l.get('message') for l in logs[:3]]}")

        # runtime.stats
        stats_result = client.send_request("runtime.stats")
        assert_ok(stats_result, "runtime.stats")
        stats_data = stats_result.get("data", {})
        print(f"  stats: {stats_data}")

        # Shutdown
        shutdown_result = client.send_request("core.shutdown")
        assert_ok(shutdown_result, "core.shutdown")
        client.disconnect()

        try:
            proc.wait(timeout=5)
            print("CoreService exited gracefully")
        except subprocess.TimeoutExpired:
            proc.kill()
            print("FAIL: CoreService did not exit after shutdown")
            sys.exit(1)

        print("check_core_runtime OK")
        sys.exit(0)

    except AssertionError:
        proc.kill()
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()
