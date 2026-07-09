import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    env = os.environ.copy()
    env["AUTODOOR_TEST_IMPORT_ONLY"] = "1"

    cmd = [
        sys.executable,
        "-c",
        "import sys; sys.path.insert(0, '.'); import main; print('main import ok')"
    ]

    p = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    output = p.stdout + p.stderr

    if p.returncode != 0:
        print(output)
        sys.exit(1)

    if "CoreService.exe not found" in output and "已切回 Python" not in output:
        print(output)
        print("FAIL: 源码启动不应因 CoreService 缺失阻塞")
        sys.exit(1)

    print("check_source_gui_launch OK")


if __name__ == "__main__":
    main()