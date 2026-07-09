"""
Check server with PostgreSQL database.

Usage: python tools/check_server_postgres.py

Steps:
1. Check if Docker is available
2. docker compose up -d postgres (if docker-compose.yml exists)
3. Start server with PostgreSQL env vars
4. GET /health
5. GET /ready
6. Call /api/client/version/latest
7. Shut down
8. Output check_server_postgres OK or SKIP
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
import socket


SERVER_URL = "http://127.0.0.1:5001"


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


def check_port_in_use(host="127.0.0.1", port=5001):
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Check if docker is available
    docker_available = False
    try:
        subprocess.run(["docker", "--version"], capture_output=True, timeout=10)
        docker_available = True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if not docker_available:
        print("SKIP: Docker not available")
        print("check_server_postgres SKIP (Docker not available)")
        sys.exit(0)

    print("Docker available")

    # Start postgres
    compose_dir = os.path.join(project_root, "server", "AutoDoor.Server")
    compose_file = os.path.join(compose_dir, "docker-compose.yml")

    if not os.path.exists(compose_file):
        print("SKIP: docker-compose.yml not found")
        print("check_server_postgres SKIP")
        sys.exit(0)

    print("Starting PostgreSQL...")
    subprocess.run(
        ["docker", "compose", "up", "-d", "postgres"],
        cwd=compose_dir,
        capture_output=True,
        timeout=120
    )

    # Wait for postgres to be ready
    print("Waiting for PostgreSQL to be ready...")
    time.sleep(10)

    if check_port_in_use():
        print("FAIL: Port 5001 already in use")
        sys.exit(1)

    server_project = find_server_project()
    if server_project is None:
        print("Server project not found")
        sys.exit(1)

    print("Starting server with PostgreSQL...")
    server_env = os.environ.copy()
    server_env["ASPNETCORE_ENVIRONMENT"] = "Development"
    server_env["AUTODOOR_DB_PROVIDER"] = "PostgreSQL"
    server_env["AUTODOOR_DB_CONNECTION_STRING"] = (
        "Host=localhost;Port=5432;Database=autodoor;Username=autodoor;Password=autodoor_dev_password"
    )
    # Use port 5001 to avoid conflict with default
    server_proc = subprocess.Popen(
        ["dotnet", "run", "--project", server_project, "--", "5001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=server_env
    )

    try:
        if not wait_for_url(f"{SERVER_URL}/health"):
            print("FAIL: Timed out waiting for server")
            server_proc.kill()
            sys.exit(1)
        print("Server is running with PostgreSQL")

        # /health
        health = http_get("/health")
        if not health.get("success"):
            print(f"FAIL: /health: {health}")
            server_proc.kill()
            sys.exit(1)
        print(f"/health: {health.get('status')}")

        # /ready
        ready = http_get("/ready")
        print(f"/ready: database={ready.get('database')}, signing_key={ready.get('signing_key')}")

        # /api/client/version/latest
        version = http_get("/api/client/version/latest")
        if not version.get("success"):
            print(f"FAIL: /api/client/version/latest: {version}")
            server_proc.kill()
            sys.exit(1)
        print(f"/api/client/version/latest OK")

        print("check_server_postgres OK")
        server_proc.kill()
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        server_proc.kill()
        sys.exit(1)
    finally:
        # Stop postgres
        subprocess.run(
            ["docker", "compose", "down"],
            cwd=compose_dir,
            capture_output=True,
            timeout=60
        )


if __name__ == "__main__":
    main()