#!/usr/bin/env python
import importlib.util
import os
import shutil
import sys
import tempfile
import zipfile


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_PIPELINE_PATH = os.path.join(PROJECT_ROOT, "tools", "release_pipeline.py")


def load_release_pipeline():
    spec = importlib.util.spec_from_file_location("release_pipeline_under_test", RELEASE_PIPELINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load release_pipeline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_text(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def write_bytes(path: str, content: bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def make_zip_from_dist(zip_path: str, dist_dir: str):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _, filenames in os.walk(dist_dir):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, dist_dir).replace("\\", "/")
                zf.write(full_path, rel_path)


def main() -> int:
    rp = load_release_pipeline()

    temp_root = tempfile.mkdtemp(prefix="autodoor_release_pipeline_smoke_")
    try:
        version = "9.9.9-test"
        platform = "win-x64"

        protected_dist = os.path.join(temp_root, "protected_dist")
        core_dir = os.path.join(protected_dist, "CoreService")
        update_dir = os.path.join(temp_root, "update")
        zip_path = os.path.join(update_dir, f"AutoDoorPro-{version}-{platform}.zip")

        write_bytes(os.path.join(core_dir, "AutoDoor.CoreService.dll"), b"protected-core-dll")
        write_text(os.path.join(core_dir, "AutoDoor.CoreService.runtimeconfig.json"), "{}")
        write_text(os.path.join(core_dir, "AutoDoor.CoreService.deps.json"), "{}")
        write_text(os.path.join(core_dir, "appsettings.json"), "{}")
        write_text(os.path.join(protected_dist, "AutoDoorPro.exe"), "fake-app")

        make_zip_from_dist(zip_path, protected_dist)

        ok = rp.verify_update_zip_contains_protected_core(
            update_dir=update_dir,
            version=version,
            platform=platform,
            protected_dist_dir=protected_dist,
        )
        if not ok:
            print("FAIL: expected protected CoreService zip verification to pass")
            return 1

        # Corrupt zip CoreService DLL and ensure verification fails.
        corrupt_dist = os.path.join(temp_root, "corrupt_dist")
        shutil.copytree(protected_dist, corrupt_dist)
        write_bytes(os.path.join(corrupt_dist, "CoreService", "AutoDoor.CoreService.dll"), b"raw-or-wrong-core-dll")
        make_zip_from_dist(zip_path, corrupt_dist)

        bad = rp.verify_update_zip_contains_protected_core(
            update_dir=update_dir,
            version=version,
            platform=platform,
            protected_dist_dir=protected_dist,
        )
        if bad:
            print("FAIL: expected corrupted CoreService zip verification to fail")
            return 1

        print("PASS: release pipeline protected CoreService zip smoke test")
        print("check_release_pipeline_smoke OK")
        return 0

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
