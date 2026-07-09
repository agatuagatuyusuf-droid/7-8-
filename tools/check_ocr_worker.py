import json
import os
import subprocess
import sys
import tempfile
from PIL import Image, ImageDraw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_worker():
    candidates = [
        os.path.join(PROJECT_ROOT, "build", "ocr_worker", "OCRWorker.exe"),
        os.path.join(PROJECT_ROOT, "dist", "OCRWorker", "OCRWorker.exe"),
        os.path.join(PROJECT_ROOT, "tools", "ocr_worker.py"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def call_worker(worker_path, payload):
    if worker_path.lower().endswith(".exe"):
        cmd = [worker_path]
    else:
        cmd = [sys.executable, worker_path]

    proc = subprocess.run(
        cmd,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )

    if proc.returncode != 0:
        print(proc.stderr)
        return None

    return json.loads(proc.stdout)


def main():
    worker = find_worker()
    if not worker:
        print("FAIL: OCRWorker.exe or tools/ocr_worker.py not found")
        sys.exit(1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        img_path = tmp.name

    try:
        img = Image.new("RGB", (240, 80), "white")
        draw = ImageDraw.Draw(img)
        draw.text((20, 25), "AUTO DOOR", fill="black")
        img.save(img_path)

        result = call_worker(worker, {
            "action": "recognize",
            "image_path": img_path,
        })

        if not result or "success" not in result:
            print(f"FAIL: invalid recognize result: {result}")
            sys.exit(1)

        region_result = call_worker(worker, {
            "action": "recognize_region",
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100,
        })

        if not region_result or "success" not in region_result:
            print(f"FAIL: invalid recognize_region result: {region_result}")
            sys.exit(1)

        if region_result.get("text") == "Region OCR not supported via worker":
            print("FAIL: recognize_region still not supported")
            sys.exit(1)

        print("check_ocr_worker OK")
        sys.exit(0)

    finally:
        try:
            os.remove(img_path)
        except Exception:
            pass


if __name__ == "__main__":
    main()
