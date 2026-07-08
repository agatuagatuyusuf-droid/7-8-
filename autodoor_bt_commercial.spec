# -*- mode: python ; coding: utf-8 -*-
#
# AutoDoor Pro Commercial Build Spec
# No source .py files are included as data files.

block_cipher = None

import os
import sys
import json
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

project_root = os.path.abspath('.')

def get_version():
    """从 build_config.json 读取版本号"""
    config_file = os.path.join(project_root, 'build_config.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            version = config.get('version', '0.0.0')
            return version
    except Exception:
        return "0.0.0"

def is_debug_build():
    """检查是否为 debug 构建"""
    config_file = os.path.join(project_root, 'build_config.json')
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('build_type', 'release') == 'debug'
    except Exception:
        return False

VERSION = get_version()
DEBUG_BUILD = is_debug_build()

# Only resource files, NO .py source code as datas
data_files = [
    (os.path.join(project_root, 'assets/sounds/alarm.mp3'), 'assets/sounds'),
    (os.path.join(project_root, 'assets/sounds/temp_reversed.mp3'), 'assets/sounds'),
    (os.path.join(project_root, 'assets/icons/autodoor.ico'), 'assets/icons'),
    (os.path.join(project_root, 'assets/icons/autodoor.png'), 'assets/icons'),
    (os.path.join(project_root, 'config/settings.json'), 'config'),
    (os.path.join(project_root, 'bt_utils/build_info.json'), 'bt_utils'),
    (os.path.join(project_root, 'drivers/DD64.dll'), 'drivers'),
    (os.path.join(project_root, 'drivers/IbInputSimulator.dll'), 'drivers'),
] + collect_data_files('rapidocr')

try:
    import rapidocr
    rapidocr_path = os.path.dirname(rapidocr.__file__)
    for root, dirs, files in os.walk(rapidocr_path):
        for file in files:
            if file.endswith('.onnx') or file.endswith('.json'):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, rapidocr_path)
                dst_path = os.path.join('rapidocr', os.path.dirname(rel_path))
                data_files.append((src_path, dst_path))
except ImportError:
    pass

binaries = []

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=binaries,
    datas=data_files,
    hiddenimports=[
        'bt_core',
        'bt_core.blackboard',
        'bt_core.config',
        'bt_core.context',
        'bt_core.engine',
        'bt_core.nodes',
        'bt_core.registry',
        'bt_core.serializer',
        'bt_core.status',
        'bt_core.tree_instance',
        'bt_core.tree_manager',
        'bt_core.file_watcher',
        'bt_core.cycle_detector',
        
        'bt_gui',
        'bt_gui.app',
        'bt_gui.script_tab',
        'bt_gui.schedule_tab',
        'bt_gui.settings_tab',
        'bt_gui.theme',
        'bt_gui.widgets',
        'bt_gui.bt_editor',
        'bt_gui.bt_editor.canvas',
        'bt_gui.bt_editor.constants',
        'bt_gui.bt_editor.editor',
        'bt_gui.bt_editor.node_item',
        'bt_gui.bt_editor.palette',
        'bt_gui.bt_editor.property',
        'bt_gui.bt_editor.toolbar',
        'bt_gui.bt_editor.undo_redo',
        'bt_gui.bt_editor.log_panel',
        'bt_gui.bt_editor.multi_tree_panel',
        'bt_gui.bt_editor.tab_bar',
        'bt_gui.bt_editor.gui_tab_manager',
        'bt_gui.dialogs',
        'bt_gui.dialogs.new_project_dialog',
        'bt_gui.editor',
        
        'bt_nodes',
        'bt_nodes.actions',
        'bt_nodes.actions.alarm',
        'bt_nodes.actions.code',
        'bt_nodes.actions.delay',
        'bt_nodes.actions.keyboard',
        'bt_nodes.actions.log_status',
        'bt_nodes.actions.mouse',
        'bt_nodes.actions.run_program',
        'bt_nodes.actions.script',
        'bt_nodes.actions.scroll',
        'bt_nodes.actions.set_display',
        'bt_nodes.actions.start_tree',
        'bt_nodes.actions.stop_tree',
        'bt_nodes.actions.text_input',
        'bt_nodes.actions.variable',
        'bt_nodes.conditions',
        'bt_nodes.conditions.color',
        'bt_nodes.conditions.common',
        'bt_nodes.conditions.image',
        'bt_nodes.conditions.number',
        'bt_nodes.conditions.ocr',
        'bt_nodes.conditions.text_extract',
        'bt_nodes.conditions.variable',
        
        'bt_utils',
        'bt_utils.alarm',
        'bt_utils.app_restarter',
        'bt_utils.auto_save',
        'bt_utils.base_input',
        'bt_utils.bg_input',
        'bt_utils.consistency_checker',
        'bt_utils.coordinate',
        'bt_utils.crash_recovery',
        'bt_utils.dd_input',
        'bt_utils.direction',
        'bt_utils.dpi_awareness',
        'bt_utils.exception_handler',
        'bt_utils.global_hotkey',
        'bt_utils.helpers',
        'bt_utils.ib_input',
        'bt_utils.image_processor',
        'bt_utils.input_controller_factory',
        'bt_utils.input_manager',
        'bt_utils.key_name_resolver',
        'bt_utils.log_manager',
        'bt_utils.magnifier',
        'bt_utils.ocr_manager',
        'bt_utils.offset_tool',
        'bt_utils.package_exporter',
        'bt_utils.package_importer',
        'bt_utils.path_resolver',
        'bt_utils.project_manager',
        'bt_utils.proxies',
        'bt_utils.recognizers',
        'bt_utils.recorder',
        'bt_utils.resource_importer',
        'bt_utils.resource_manager',
        'bt_utils.resource_service',
        'bt_utils.screen_service',
        'bt_utils.screen_utils',
        'bt_utils.screenshot',
        'bt_utils.script_executor',
        'bt_utils.singleton',
        'bt_utils.stats',
        'bt_utils.ui_dispatcher',
        'bt_utils.version_checker',
        'bt_utils.vk_mapping',
        'bt_utils.window_capture',
        'bt_utils.window_manager',
        'bt_utils.brand_manager',
        
        'config',
        'config.settings_manager',
        
        'pygame',
        'pygame.mixer',
        'tkinter',
        'tkinter.ttk',
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL.ImageGrab',
        'rapidocr',
        'onnxruntime',
        'screeninfo',
        'screeninfo.common',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        'pydub',
        'requests',
        'numpy',
        'numpy.core',
        'numpy.core.multiarray',
        'six',
        'imagehash',
        'cv2',
        
        'win32gui',
        'win32ui',
        'win32con',
        'win32api',
        'win32process',
        'pywintypes',
        'pythoncom',
        'ctypes',
    ] + collect_submodules('bt_core') + collect_submodules('bt_gui') + collect_submodules('bt_nodes') + collect_submodules('bt_utils') + collect_submodules('rapidocr'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'tensorflow', 'keras', 'scipy', 'pandas', 'matplotlib',
        'sklearn', 'xgboost', 'lightgbm', 'catboost', 'seaborn',
        'statsmodels', 'plotly', 'bokeh', 'networkx', 'nltk',
        'spacy', 'transformers', 'torchvision', 'torchaudio', 'onnx',
        'jax', 'jaxlib', 'timm', 'diffusers', 'peft',
        'gradio', 'streamlit', 'dash',
        
        'flask', 'django', 'fastapi', 'uvicorn', 'gunicorn',
        'beautifulsoup4', 'selenium', 'webdriver_manager',
        
        'pyqt5', 'pyside6', 'wxpython', 'tkinterdnd2',
        
        'pillow_heif', 'PIL._tkinter_finder', 'PIL.ImageQt',
        
        'numpy.testing', 'numpy.f2py', 'numpy.distutils',
        
        'pkg_resources',
        'pycparser', 'cffi',
        'platformdirs', 'pyparsing', 'colorama', 'chardet'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exclude_binaries = [
    'onnxruntime_providers_cuda.dll',
    'onnxruntime_providers_tensorrt.dll',
]
a.binaries = [x for x in a.binaries if not any(ex in x[0] for ex in exclude_binaries)]

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=f'autodoor-pro-{VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=DEBUG_BUILD,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'assets', 'icons', 'autodoor.ico'),
    manifest='''
    <assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
      <application xmlns="urn:schemas-microsoft-com:asm.v3">
        <windowsSettings>
          <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
          <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2,PerMonitor</dpiAwareness>
        </windowsSettings>
      </application>
    </assembly>
    ''',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=f'autodoor-pro-{VERSION}',
)
