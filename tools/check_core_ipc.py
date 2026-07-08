"""
Check CoreService TCP IPC connectivity.

Usage: python tools/check_core_ipc.py

Steps:
1. Find CoreService.exe
2. If not found, attempt dotnet publish
3. Start CoreService
4. Wait for port listening
5. Connect via CoreClient
6. Call core.hello
7. Verify success=true
8. Call core.shutdown
9. Close process
10. Output check_core_ipc OK
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

    # Step 1: Find CoreService.exe
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
            print("Still cannot find CoreService.exe after publish")
            sys.exit(1)

    print(f"CoreService found: {exe_path}")

    # Step 3: Start CoreService
    proc = subprocess.Popen(
        [exe_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    try:
        # Step 4: Wait for port
        print("Waiting for CoreService to listen on port 19527...")
        if not wait_for_port():
            print("Timed out waiting for CoreService")
            proc.kill()
            sys.exit(1)
        print("CoreService is listening")

        # Step 5 & 6: Connect and call core.hello
        from bt_bridge.core_client import CoreClient
        client = CoreClient(timeout=5)
        if not client.connect():
            print("Failed to connect to CoreService")
            proc.kill()
            sys.exit(1)

        # Step 7: Verify hello
        hello_result = client.send_request("core.hello")
        if not hello_result.get("success"):
            print(f"core.hello failed: {hello_result.get('message')}")
            client.disconnect()
            proc.kill()
            sys.exit(1)
        print(f"core.hello response: {hello_result}")

        # Step 8: Shutdown
        shutdown_result = client.send_request("core.shutdown")
        print(f"core.shutdown response: {shutdown_result}")
        client.disconnect()

        # Wait for process to exit
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

        print("check_core_ipc OK")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()
