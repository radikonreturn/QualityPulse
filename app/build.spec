# -*- mode: python ; coding: utf-8 -*-
"""
QualityPulse — PyInstaller Build Spec (NiceGUI Version)
One-file executable, no console window.

Build command (run from app/ directory):
    pyinstaller build.spec --clean --noconfirm
"""

import sys
import os
import nicegui
from pathlib import Path

nicegui_path = os.path.dirname(nicegui.__file__)

block_cipher = None
APP_DIR = Path(".")

a = Analysis(
    [str(APP_DIR / "main.py")],
    pathex=[str(APP_DIR)],
    binaries=[],
    datas=[
        # Assets
        (str(APP_DIR / "assets"),      "assets"),
        # App modules
        (str(APP_DIR / "pages"),       "pages"),
        (str(APP_DIR / "components"),  "components"),
        (str(APP_DIR / "utils"),       "utils"),
        (str(APP_DIR / "db"),          "db"),
        # NiceGUI static files
        (nicegui_path,                 "nicegui"),
    ],
    hiddenimports=[
        # NiceGUI internals
        "nicegui",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "engineio.async_drivers.aiohttp",
        # Data / charting
        "plotly",
        "plotly.express",
        "plotly.graph_objects",
        "plotly.subplots",
        "pandas",
        "numpy",
        # Excel export
        "openpyxl",
        # DB / packaging
        "sqlite3",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "IPython",
        "ipykernel",
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
    name="QualityPulse",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # no black terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(APP_DIR / "assets" / "icon.ico"), # ensure this exists
    onefile=True,                   # single .exe file
    version_file=None,
)
