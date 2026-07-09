"""
构建 UpdateAgent 可执行文件（PyInstaller）
"""
import os
import subprocess
import sys


def main():
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    agent_script = os.path.join(tools_dir, "update_agent.py")

    if not os.path.exists(agent_script):
        print(f"Error: {agent_script} not found")
        sys.exit(1)

    output_dir = os.path.join(tools_dir, "..", "dist", "update_agent")
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name", "update_agent",
        "--distpath", output_dir,
        agent_script,
    ]

    print("Building UpdateAgent...")
    result = subprocess.run(cmd, cwd=tools_dir)
    if result.returncode != 0:
        print("Build failed")
        sys.exit(1)

    exe_path = os.path.join(output_dir, "update_agent.exe")
    if os.path.exists(exe_path):
        print(f"UpdateAgent built: {exe_path}")
    else:
        print("Build completed but exe not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
