"""
AutoDoor Pro Update Agent

独立进程，负责替换文件并重启主程序。
不依赖任何第三方库，只使用 Python 标准库。

启动参数：
  --app-dir      安装目录
  --package-dir  更新包解压目录
  --main-exe     主程序 exe 文件名
  --pid          主程序进程 ID
"""

import argparse
import os
import shutil
import subprocess
import sys
import time


UPDATE_LOG_PATH = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "AutoDoorPro", "logs", "update.log"
)


def log(msg: str):
    os.makedirs(os.path.dirname(UPDATE_LOG_PATH), exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(UPDATE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[update_agent] {msg}")


def wait_for_process_exit(pid: int, timeout: int = 60):
    """等待主进程退出"""
    try:
        import signal
        proc = None
        try:
            proc = __import__("psutil", globals(), locals(), [], 0)
        except ImportError:
            proc = None
        if proc and hasattr(proc, "Process"):
            p = proc.Process(pid)
            p.wait(timeout=timeout)
            return
    except Exception:
        pass

    # Fallback: simple polling
    for _ in range(timeout * 2):
        try:
            if os.name == "nt":
                subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True, timeout=5
                )
            else:
                os.kill(pid, 0)
        except Exception:
            return
        time.sleep(0.5)
    log(f"主进程 {pid} 在 {timeout}s 内未退出，继续执行")


def stop_core_service(app_dir: str):
    log("停止 CoreService")
    cs_path = os.path.join(app_dir, "CoreService", "AutoDoor.CoreService.exe")
    if os.path.exists(cs_path):
        try:
            subprocess.run(["taskkill", "/F", "/IM", "AutoDoor.CoreService.exe"],
                           capture_output=True, timeout=10)
        except Exception:
            pass


def backup_current(app_dir: str, backup_dir: str) -> str:
    version_dir = os.path.basename(app_dir.rstrip("\\/"))
    backup_path = os.path.join(
        backup_dir,
        f"{version_dir}-{time.strftime('%Y%m%d%H%M%S')}"
    )
    log(f"备份当前版本到: {backup_path}")
    if os.path.exists(app_dir):
        shutil.copytree(app_dir, backup_path, ignore=shutil.ignore_patterns(
            "*.log", "*.tmp", "cache", "projects", "license", "config.json"
        ))
    return backup_path


def replace_files(app_dir: str, package_dir: str):
    log(f"替换文件: {package_dir} -> {app_dir}")
    for item in os.listdir(package_dir):
        src = os.path.join(package_dir, item)
        dst = os.path.join(app_dir, item)
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copy2(src, dst)


def verify_files(app_dir: str, main_exe: str) -> bool:
    exe_path = os.path.join(app_dir, main_exe)
    if not os.path.exists(exe_path):
        log(f"验证失败: {exe_path} 不存在")
        return False
    return True


def restore_backup(app_dir: str, backup_path: str):
    log(f"回滚: {backup_path} -> {app_dir}")
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
    shutil.copytree(backup_path, app_dir)


def launch_main(app_dir: str, main_exe: str):
    exe_path = os.path.join(app_dir, main_exe)
    log(f"启动主程序: {exe_path}")
    try:
        subprocess.Popen([exe_path], cwd=app_dir)
    except Exception as e:
        log(f"启动失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="AutoDoor Pro Update Agent")
    parser.add_argument("--app-dir", required=True, help="安装目录")
    parser.add_argument("--package-dir", required=True, help="更新包目录")
    parser.add_argument("--main-exe", default="AutoDoorPro.exe", help="主程序 exe")
    parser.add_argument("--pid", type=int, default=0, help="主程序进程 ID")
    args = parser.parse_args()

    log("=== UpdateAgent 启动 ===")
    log(f"app-dir: {args.app_dir}")
    log(f"package-dir: {args.package_dir}")
    log(f"main-exe: {args.main_exe}")
    log(f"pid: {args.pid}")

    if not os.path.exists(args.package_dir):
        log(f"更新包目录不存在: {args.package_dir}")
        sys.exit(1)

    if args.pid > 0:
        log("等待主程序退出...")
        wait_for_process_exit(args.pid)

    stop_core_service(args.app_dir)

    backup_path = ""
    try:
        from bt_utils.update_paths import get_backup_dir
        backup_dir = get_backup_dir()
    except ImportError:
        backup_dir = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")),
            "AutoDoorPro", "backups"
        )

    try:
        backup_path = backup_current(args.app_dir, backup_dir)
        replace_files(args.app_dir, args.package_dir)

        if not verify_files(args.app_dir, args.main_exe):
            if backup_path:
                restore_backup(args.app_dir, backup_path)
            log("更新失败，已回滚")
            sys.exit(1)

        log("更新成功")
        launch_main(args.app_dir, args.main_exe)
        sys.exit(0)

    except Exception as e:
        log(f"更新异常: {e}")
        if backup_path and os.path.exists(backup_path):
            try:
                restore_backup(args.app_dir, backup_path)
                log("已回滚到备份版本")
            except Exception as re:
                log(f"回滚失败: {re}")
        sys.exit(1)


if __name__ == "__main__":
    main()
