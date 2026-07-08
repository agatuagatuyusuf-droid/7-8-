"""
End-to-end license activation test: server -> CoreService -> activation.

Usage: python tools/check_license_e2e.py

Steps:
1. Start the ASP.NET license server
2. Start CoreService
3. Activate via POST /api/client/activate (TEST-ACTIVATE-123456)
4. Save ticket to CoreService license cache
5. Call core.status via IPC, verify valid=true
6. Cleanup: stop both processes
7. Output check_license_e2e OK
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


SERVER_URL = "http://localhost:5000"
ACTIVATE_CODE = "TEST-ACTIVATE-123456"
MACHINE_CODE = "TEST-MACHINE-001"


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


def find_server_project():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "server", "AutoDoor.Server",
                        "src", "AutoDoor.Api", "AutoDoor.Api.csproj")
    if os.path.exists(path):
        return path
    return None


def wait_for_url(url, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = urllib.request.urlopen(url, timeout=5)
            r.read()
            return True
        except (urllib.error.URLError, ConnectionRefusedError, socket.timeout):
            time.sleep(1)
    return False


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


def http_post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{SERVER_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    r = urllib.request.urlopen(req)
    return json.loads(r.read().decode("utf-8"))


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processes = []

    try:
        # Start server
        server_project = find_server_project()
        if server_project is None:
            print("Server project not found")
            sys.exit(1)

        print("Starting license server...")
        server_proc = subprocess.Popen(
            ["dotnet", "run", "--project", server_project],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(("server", server_proc))

        if not wait_for_url(f"{SERVER_URL}/api/dev-admin/dashboard"):
            print("Timed out waiting for license server")
            sys.exit(1)
        print("License server is running")

        # Start CoreService
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
        core_proc = subprocess.Popen(
            [exe_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        processes.append(("core", core_proc))

        if not wait_for_port():
            print("Timed out waiting for CoreService")
            sys.exit(1)
        print("CoreService is listening")

        # Activate via server API
        print(f"Activating with code {ACTIVATE_CODE}...")
        activate_result = http_post("/api/client/activate", {
            "activation_code": ACTIVATE_CODE,
            "machine_code": MACHINE_CODE
        })
        if not activate_result.get("success"):
            print(f"Activation failed: {activate_result.get('message')}")
            sys.exit(1)
        print(f"Activation successful")

        ticket = activate_result.get("ticket", {})
        if not ticket.get("signature"):
            print("FAIL: No signature in activation response")
            sys.exit(1)
        print(f"Signature present: {ticket['signature'][:20]}...")

        # Save ticket to CoreService cache
        from bt_bridge.core_client import CoreClient
        client = CoreClient(timeout=5)
        if not client.connect():
            print("Failed to connect to CoreService")
            sys.exit(1)

        save_result = client.send_request("license.save_ticket", {
            "ticket_json": json.dumps(ticket)
        })
        if not save_result.get("success"):
            print(f"FAIL: license.save_ticket failed: {save_result.get('message')}")
            client.disconnect()
            sys.exit(1)
        print("Ticket saved to CoreService cache")

        # Reload cache
        reload_result = client.send_request("license.reload")
        if not reload_result.get("success"):
            print(f"FAIL: license.reload failed: {reload_result.get('message')}")
            client.disconnect()
            sys.exit(1)
        print("CoreService cache reloaded")

        # Check status
        status_result = client.send_request("license.status")
        if not status_result.get("success"):
            print(f"FAIL: license.status failed: {status_result.get('message')}")
            client.disconnect()
            sys.exit(1)

        activated = status_result.get("activated", False)
        valid = status_result.get("valid", False)

        if not activated:
            print("FAIL: license.status shows not activated")
            client.disconnect()
            sys.exit(1)

        if not valid:
            print("FAIL: license.status shows not valid (signature verification failed)")
            client.disconnect()
            sys.exit(1)

        print(f"License status: activated={activated}, valid={valid}")
        print(f"  edition: {status_result.get('edition')}")
        print(f"  license_id: {status_result.get('license_id')}")
        print(f"  expire_at: {status_result.get('expire_at')}")

        # Shutdown CoreService
        client.send_request("core.shutdown")
        client.disconnect()
        try:
            core_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            core_proc.kill()

        # Stop server
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()

        print("check_license_e2e OK")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        for name, proc in processes:
            if proc.poll() is None:
                proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()
