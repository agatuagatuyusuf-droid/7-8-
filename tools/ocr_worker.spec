# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

hiddenimports = [
    "json",
    "sys",
    "os",
    "tempfile",
    "PIL",
    "PIL.Image",
    "pyautogui",
    "pytesseract",
    "rapidocr_onnxruntime",
    "onnxruntime",
]

for package_name in [
    "rapidocr_onnxruntime",
    "onnxruntime",
    "PIL",
    "pyautogui",
]:
    try:
        hiddenimports += collect_submodules(package_name)
    except Exception:
        pass

datas = []

for package_name in [
    "rapidocr_onnxruntime",
    "onnxruntime",
]:
    try:
        datas += collect_data_files(package_name)
    except Exception:
        pass

a = Analysis(
    ["ocr_worker.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch",
        "tensorflow",
        "pandas",
        "matplotlib",
        "scipy",
        "sklearn",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="OCRWorker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
