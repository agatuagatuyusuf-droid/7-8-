"""OCR worker script for C# CoreService integration.

Usage:
    OCRWorker.exe
    or
    python tools/ocr_worker.py

Reads JSON from stdin, outputs JSON to stdout.

Input examples:
    {"action": "recognize", "image_path": "C:/tmp/a.png"}
    {"action": "recognize_region", "x": 0, "y": 0, "width": 300, "height": 120}

Output:
    {"success": true, "text": "...", "confidence": 0.95}
"""

import json
import os
import sys
import tempfile
from typing import Any, Dict


def _run_ocr_on_image(image_path: str) -> Dict[str, Any]:
    if not os.path.exists(image_path):
        return {"success": False, "text": "Image file not found", "confidence": 0.0}

    try:
        from rapidocr_onnxruntime import RapidOCR

        engine = RapidOCR()
        result, _ = engine(image_path)

        if result and len(result) > 0:
            texts = []
            confidences = []

            for box in result:
                if len(box) >= 2:
                    texts.append(str(box[1]))
                    confidences.append(float(box[2]) if len(box) > 2 else 0.0)

            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            return {
                "success": True,
                "text": "\n".join(texts),
                "confidence": avg_conf,
            }

        return {"success": True, "text": "", "confidence": 0.0}

    except Exception as rapid_error:
        try:
            import pytesseract
            from PIL import Image

            text = pytesseract.image_to_string(Image.open(image_path), lang="chi_sim+eng")
            return {"success": True, "text": text.strip(), "confidence": 0.5}

        except Exception as tess_error:
            return {
                "success": False,
                "text": (
                    "No OCR engine available or OCR failed. "
                    f"rapidocr_error={rapid_error}; tesseract_error={tess_error}"
                ),
                "confidence": 0.0,
            }


def recognize(image_path: str) -> Dict[str, Any]:
    try:
        return _run_ocr_on_image(image_path)
    except Exception as e:
        return {"success": False, "text": str(e), "confidence": 0.0}


def recognize_region(x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    try:
        if width <= 0 or height <= 0:
            return {
                "success": False,
                "text": "Invalid region: width and height must be greater than 0",
                "confidence": 0.0,
            }

        try:
            import pyautogui
        except Exception as e:
            return {
                "success": False,
                "text": f"pyautogui not available for region OCR: {e}",
                "confidence": 0.0,
            }

        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp_path = tmp.name

        try:
            screenshot.save(tmp_path)
            return _run_ocr_on_image(tmp_path)
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    except Exception as e:
        return {"success": False, "text": str(e), "confidence": 0.0}


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({
                "success": False,
                "text": "Empty stdin",
                "confidence": 0.0,
            }, ensure_ascii=False))
            return

        input_data = json.loads(raw)
        action = input_data.get("action", "")

        if action == "recognize":
            result = recognize(input_data.get("image_path", ""))

        elif action == "recognize_region":
            result = recognize_region(
                int(input_data.get("x", 0)),
                int(input_data.get("y", 0)),
                int(input_data.get("width", 0)),
                int(input_data.get("height", 0)),
            )

        else:
            result = {
                "success": False,
                "text": f"Unknown action: {action}",
                "confidence": 0.0,
            }

        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "text": str(e),
            "confidence": 0.0,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
