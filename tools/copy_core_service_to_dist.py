import json
import os
import shutil
import sys


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Read version
    build_config_path = os.path.join(project_root, "build_config.json")
    if not os.path.exists(build_config_path):
        print("ERROR: build_config.json not found")
        sys.exit(1)

    with open(build_config_path, "r", encoding="utf-8") as f:
        build_config = json.load(f)

    version = build_config.get("version", "0.0.0")
    dist_dir_name = f"autodoor-pro-{version}"
    dist_dir = os.path.join(project_root, "dist", dist_dir_name)

    if not os.path.exists(dist_dir):
        print(f"ERROR: dist directory not found: {dist_dir}")
        sys.exit(1)

    # Find C# publish directory
    publish_dir = os.path.join(
        project_root, "csharp", "AutoDoor.CoreService",
        "src", "AutoDoor.CoreService", "bin", "Release",
        "net8.0-windows", "win-x64", "publish"
    )

    if not os.path.exists(publish_dir):
        # Try build directory
        publish_dir = os.path.join(
            project_root, "csharp", "AutoDoor.CoreService",
            "src", "AutoDoor.CoreService", "bin", "Release",
            "net8.0-windows", "win-x64"
        )
        if not os.path.exists(os.path.join(publish_dir, "AutoDoor.CoreService.exe")):
            print(f"ERROR: CoreService publish directory not found")
            sys.exit(1)

    core_service_dir = os.path.join(dist_dir, "CoreService")
    os.makedirs(core_service_dir, exist_ok=True)

    debug_mode = os.environ.get("AUTODOOR_DEBUG_BUILD", "").lower() in ("1", "true", "yes")

    for item in os.listdir(publish_dir):
        # Skip .pdb files unless Debug mode
        if item.endswith(".pdb") and not debug_mode:
            continue
        # Skip .xml documentation files
        if item.endswith(".xml"):
            continue
        src_path = os.path.join(publish_dir, item)
        dst_path = os.path.join(core_service_dir, item)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)

    # Verify
    required_files = [
        os.path.join(core_service_dir, "AutoDoor.CoreService.exe"),
        os.path.join(core_service_dir, "appsettings.json"),
    ]
    for req in required_files:
        if not os.path.exists(req):
            print(f"ERROR: Required file missing: {req}")
            sys.exit(1)

    # Copy OCRWorker from PyInstaller output
    ocr_src = os.path.join(project_root, "build", "ocr_worker", "OCRWorker.exe")
    if not os.path.exists(ocr_src):
        print(f"ERROR: OCRWorker.exe not found after PyInstaller build: {ocr_src}")
        print("Run: pyinstaller tools/ocr_worker.spec --clean --distpath build\\ocr_worker --workpath build\\ocr_worker_build")
        sys.exit(1)

    ocr_dir = os.path.join(dist_dir, "OCRWorker")
    os.makedirs(ocr_dir, exist_ok=True)
    ocr_dst = os.path.join(ocr_dir, "OCRWorker.exe")
    shutil.copy2(ocr_src, ocr_dst)

    if not os.path.exists(ocr_dst):
        print(f"ERROR: OCRWorker.exe copy failed: {ocr_dst}")
        sys.exit(1)

    print(f"CoreService copied to {core_service_dir}")
    print(f"OCRWorker copied to {ocr_dst}")


if __name__ == "__main__":
    main()
