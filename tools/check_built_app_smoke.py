"""
Check built app smoke test via CoreService.

Usage: python tools/check_built_app_smoke.py [dist_dir]

Steps:
1. Find dist/autodoor-pro-* directory
2. Find CoreService/AutoDoor.CoreService.exe
3. Start CoreService
4. Connect via CoreClient
5. Call core.hello - verify success
6. Call license.status - verify no crash (may return activated=false)
7. Call core.shutdown
8. Process exits within 5s
9. Output check_built_app_smoke OK
"""

import glob
import os
import subprocess
import sys
import time
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_dist_dir(dist_base):
    """Find autodoor-pro-* directory"""
    if not os.path.isdir(dist_base):
        return None
    pattern = os.path.join(dist_base, "autodoor-pro-*")
    dirs = sorted(glob.glob(pattern))
    return dirs[-1] if dirs else None


def find_core_service(dist_dir):
    cs_exe = os.path.join(dist_dir, "CoreService", "AutoDoor.CoreService.exe")
    return cs_exe if os.path.exists(cs_exe) else None


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
    dist_base = sys.argv[1] if len(sys.argv) > 1 else "dist"

    dist_dir = find_dist_dir(dist_base)
    if dist_dir is None:
        print("FAIL: dist/autodoor-pro-* not found")
        sys.exit(1)

    print(f"Dist directory: {dist_dir}")

    cs_exe = find_core_service(dist_dir)
    if cs_exe is None:
        print("FAIL: CoreService/AutoDoor.CoreService.exe not found")
        sys.exit(1)

    print(f"CoreService exe: {cs_exe}")

    proc = subprocess.Popen(
        [cs_exe],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    try:
        print("Waiting for CoreService to listen on port 19527...")
        if not wait_for_port():
            print("FAIL: Timed out waiting for CoreService")
            proc.kill()
            sys.exit(1)
        print("CoreService is listening")

        from bt_bridge.core_client import CoreClient
        client = CoreClient(timeout=5)
        if not client.connect():
            print("FAIL: Failed to connect to CoreService")
            proc.kill()
            sys.exit(1)

        # core.hello
        hello = client.send_request("core.hello")
        if not hello.get("success"):
            print(f"FAIL: core.hello failed: {hello.get('message')}")
            client.disconnect()
            proc.kill()
            sys.exit(1)
        print(f"core.hello: {hello.get('message')}")

        # license.status (unactivated - should not crash)
        status = client.send_request("license.status")
        if not status.get("success"):
            print(f"WARN: license.status returned success=false (expected if not activated): {status.get('message')}")
        else:
            data = status.get("data") or {}
            activated = data.get("activated", False)
            print(f"license.status: activated={activated}")
        print("license.status did not crash - OK")

        # core.shutdown
        shutdown = client.send_request("core.shutdown")
        if not shutdown.get("success"):
            print(f"WARN: core.shutdown: {shutdown.get('message')}")
        client.disconnect()

        try:
            proc.wait(timeout=5)
            print("CoreService exited gracefully")
        except subprocess.TimeoutExpired:
            proc.kill()
            print("FAIL: CoreService did not exit after core.shutdown")
            sys.exit(1)

        print("check_built_app_smoke OK")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        proc.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()