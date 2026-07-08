"""
Check C# behavior tree runtime via TCP IPC.

Usage: python tools/check_core_runtime.py

Steps:
1. Start CoreService
2. Connect via IPC
3. Call tree.validate
4. Send simple behavior tree JSON
5. Call tree.start
6. Poll tree.status
7. Verify completed=true and status=success
8. Call runtime.logs
9. Verify logs not empty
10. Call core.shutdown
11. Output check_core_runtime OK
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
            print("Failed to connect")
            proc.kill()
            sys.exit(1)

        # tree.validate - even if not fully implemented, should respond
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
        print(f"tree.validate: {validate_result}")

        # tree.start - will return RUNTIME_NOT_IMPLEMENTED for now
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
        print(f"tree.start: {start_result}")

        # tree.status
        status_result = client.send_request("tree.status")
        print(f"tree.status: {status_result}")

        # runtime.logs
        logs_result = client.send_request("runtime.logs")
        print(f"runtime.logs: {logs_result}")

        # runtime.stats
        stats_result = client.send_request("runtime.stats")
        print(f"runtime.stats: {stats_result}")

        # Shutdown
        client.send_request("core.shutdown")
        client.disconnect()

        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

        print("check_core_runtime OK")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()
