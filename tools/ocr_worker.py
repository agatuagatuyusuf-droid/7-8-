"""OCR worker script for C# CoreService integration.

Usage: python tools/ocr_worker.py
Reads JSON from stdin, outputs JSON to stdout.

Input:  {"action": "recognize", "image_path": "..."}
Output: {"success": true, "text": "...", "confidence": 0.95}
"""

import json
import sys
import os


def recognize(image_path):
    try:
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
                return {"success": True, "text": "\n".join(texts), "confidence": avg_conf}
            return {"success": True, "text": "", "confidence": 0.0}
        except ImportError:
            try:
                import pytesseract
                from PIL import Image
                text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim+eng')
                return {"success": True, "text": text.strip(), "confidence": 0.5}
            except ImportError:
                return {"success": False, "text": "No OCR engine available (install rapidocr_onnxruntime or pytesseract)", "confidence": 0.0}
    except Exception as e:
        return {"success": False, "text": str(e), "confidence": 0.0}


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        action = input_data.get("action", "")
        
        if action == "recognize":
            result = recognize(input_data.get("image_path", ""))
        elif action == "recognize_region":
            result = {"success": False, "text": "Region OCR not supported via worker", "confidence": 0.0}
        else:
            result = {"success": False, "text": f"Unknown action: {action}", "confidence": 0.0}
        
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "text": str(e), "confidence": 0.0}))


if __name__ == "__main__":
    main()
