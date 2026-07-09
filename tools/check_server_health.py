"""
Check server health endpoint.

Usage: python tools/check_server_health.py

Steps:
1. Start server in Development mode
2. GET /health - must return success=true
3. GET /ready - Development may return database=false but should not crash
4. Output check_server_health OK
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
import socket


SERVER_URL = "http://127.0.0.1:5000"


def find_server_project():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "server", "AutoDoor.Server",
                        "src", "AutoDoor.Api", "AutoDoor.Api.csproj")
    return path if os.path.exists(path) else None


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


def check_port_in_use(host="127.0.0.1", port=5000):
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if check_port_in_use():
        print("FAIL: Port 5000 already in use")
        sys.exit(1)

    server_project = find_server_project()
    if server_project is None:
        print("Server project not found")
        sys.exit(1)

    print("Starting server...")
    server_env = os.environ.copy()
    server_env["ASPNETCORE_ENVIRONMENT"] = "Development"
    server_proc = subprocess.Popen(
        ["dotnet", "run", "--project", server_project],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=server_env
    )

    try:
        if not wait_for_url(f"{SERVER_URL}/health"):
            print("Timed out waiting for server /health")
            server_proc.kill()
            sys.exit(1)
        print("Server is running")

        # /health
        health = http_get("/health")
        if not health.get("success"):
            print(f"FAIL: /health success=false: {health}")
            server_proc.kill()
            sys.exit(1)
        if health.get("status") != "healthy":
            print(f"FAIL: /health status not healthy: {health}")
            server_proc.kill()
            sys.exit(1)
        print(f"/health: status={health.get('status')}")

        # /ready
        ready = http_get("/ready")
        if ready.get("success") is None:
            print(f"FAIL: /ready missing success field: {ready}")
            server_proc.kill()
            sys.exit(1)
        database = ready.get("database", False)
        signing_key = ready.get("signing_key", False)
        print(f"/ready: database={database}, signing_key={signing_key}")

        print("check_server_health OK")
        server_proc.kill()
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        server_proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()