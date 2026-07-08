"""
End-to-end license activation test: server -> CoreService -> activation.

Usage: python tools/check_license_e2e.py

Steps:
1. Start the ASP.NET license server
2. Wait for server readiness
3. Get public key from server (/api/client/public-key)
4. Start CoreService with env AUTODOOR_LICENSE_SERVER_URL + TICKET_PUBLIC_KEY
5. Wait for CoreService port
6. Connect via CoreClient
7. Call license.machine_code, verify success
8. Call license.activate with TEST-ACTIVATE-123456, verify success
9. Call license.status, verify data.valid=true, data.activated=true, data.signature_valid=true
10. Call feature.list, verify expected features present
11. Call core.shutdown, verify CoreService exits within 5s
12. Stop server
13. Output check_license_e2e OK
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


SERVER_URL = "http://127.0.0.1:5000"
ACTIVATE_CODE = "TEST-ACTIVATE-123456"


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


def http_get(path):
    req = urllib.request.Request(f"{SERVER_URL}{path}", method="GET")
    r = urllib.request.urlopen(req)
    return json.loads(r.read().decode("utf-8"))


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


def check_port_in_use(host="127.0.0.1", port=5000):
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processes = []

    if check_port_in_use():
        print(f"FAIL: Port 5000 is already in use. A previous server may still be running.")
        sys.exit(1)

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

        # Get public key from server
        print("Fetching public key from server...")
        pubkey_result = http_get("/api/client/public-key")
        if not pubkey_result.get("success"):
            print(f"Failed to get public key: {pubkey_result}")
            sys.exit(1)
        public_key = pubkey_result.get("public_key", "")
        if not public_key:
            print("FAIL: Empty public key from server")
            sys.exit(1)
        print(f"Public key acquired ({len(public_key)} chars)")

        # Start CoreService with env vars
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

        core_env = os.environ.copy()
        core_env["AUTODOOR_LICENSE_SERVER_URL"] = "http://127.0.0.1:5000"
        core_env["TICKET_PUBLIC_KEY"] = public_key

        core_proc = subprocess.Popen(
            [exe_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=core_env,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        processes.append(("core", core_proc))

        if not wait_for_port():
            print("Timed out waiting for CoreService")
            sys.exit(1)
        print("CoreService is listening")

        # Connect via CoreClient
        from bt_bridge.core_client import CoreClient
        client = CoreClient(timeout=5)
        if not client.connect():
            print("Failed to connect to CoreService")
            sys.exit(1)
        print("Connected to CoreService")

        # Check machine_code
        mc_result = client.send_request("license.machine_code")
        if not mc_result.get("success"):
            print(f"FAIL: license.machine_code failed: {mc_result.get('message')}")
            client.disconnect()
            sys.exit(1)
        mc_data = mc_result.get("data") or {}
        machine_code = mc_data.get("machine_code", "")
        print(f"Machine code: {machine_code}")

        # Activate via CoreService
        print(f"Activating with code {ACTIVATE_CODE}...")
        activate_result = client.send_request("license.activate", {"code": ACTIVATE_CODE})
        if not activate_result.get("success"):
            print(f"FAIL: license.activate failed: {activate_result.get('message')}")
            client.disconnect()
            sys.exit(1)
        print("Activation successful")

        # Check license status
        status_result = client.send_request("license.status")
        if not status_result.get("success"):
            print(f"FAIL: license.status failed: {status_result.get('message')}")
            client.disconnect()
            sys.exit(1)

        status_data = status_result.get("data") or {}
        activated = status_data.get("activated", False)
        valid = status_data.get("valid", False)
        signature_valid = status_data.get("signature_valid", False)

        if not activated:
            print("FAIL: license.status shows not activated")
            client.disconnect()
            sys.exit(1)

        if not signature_valid:
            print("FAIL: license.status shows signature_valid=false")
            client.disconnect()
            sys.exit(1)

        if not valid:
            print("FAIL: license.status shows valid=false")
            client.disconnect()
            sys.exit(1)

        print(f"License status: activated={activated}, valid={valid}, signature_valid={signature_valid}")
        print(f"  edition: {status_data.get('edition')}")
        print(f"  license_id: {status_data.get('license_id')}")
        print(f"  expire_at: {status_data.get('expire_at')}")
        print(f"  error: {status_data.get('error')}")

        # Check features
        features_result = client.send_request("feature.list")
        if not features_result.get("success"):
            print(f"FAIL: feature.list failed: {features_result.get('message')}")
            client.disconnect()
            sys.exit(1)
        features_data = features_result.get("data") or {}
        features = features_data.get("features") or []
        print(f"Features: {features}")

        expected_features = {"basic_editor", "basic_input", "schedule", "ocr", "image_match"}
        for feat in expected_features:
            if feat not in features:
                print(f"FAIL: Expected feature '{feat}' not found in {features}")
                client.disconnect()
                sys.exit(1)
        print("All expected features present")

        # Shutdown CoreService
        client.send_request("core.shutdown")
        client.disconnect()
        try:
            core_proc.wait(timeout=5)
            print("CoreService exited gracefully")
        except subprocess.TimeoutExpired:
            core_proc.kill()
            print("FAIL: CoreService did not exit after core.shutdown")
            sys.exit(1)

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
