#!/usr/bin/env python
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path: str) -> str:
    full = os.path.join(PROJECT_ROOT, path)
    if not os.path.exists(full):
        return ""
    with open(full, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def exists(path: str) -> bool:
    return os.path.exists(os.path.join(PROJECT_ROOT, path))


def main() -> int:
    checks = []

    checks.append(("run_release_drill exists", exists("tools/run_release_drill.py")))

    drill = read("tools/run_release_drill.py")
    checks.append(("drill uses temp dir", "tempfile.mkdtemp" in drill and "autodoor_release_drill_" in drill))
    checks.append(("drill creates fake dist", "make_fake_dist" in drill and "AutoDoor.CoreService.dll" in drill))
    checks.append(("drill runs release_pipeline", "release_pipeline.py" in drill))
    checks.append(("drill runs dev mode", '"--mode", "dev"' in drill))
    checks.append(("drill handles release mode", '"--mode", "release"' in drill))
    checks.append(("drill blocks release when obfuscar missing", '"BLOCKED"' in drill and "Obfuscar not found" in drill))
    checks.append(("drill writes report", "RELEASE_DRILL_REPORT.md" in drill))
    checks.append(("drill removes temp root", "shutil.rmtree(temp_root" in drill))

    ok = True
    for name, result in checks:
        print(("PASS" if result else "FAIL") + ": " + name)
        if not result:
            ok = False

    if not ok:
        return 1

    print("check_release_drill OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
