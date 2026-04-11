# -*- mode: python ; coding: utf-8 -*-
"""
QualityPulse — PyInstaller Build Spec
One-file executable, no console window.

Build command:
    pyinstaller build.spec
"""

import sys
from pathlib import Path

block_cipher = None
APP_DIR = Path(".")

a = Analysis(
    [str(APP_DIR / "main.py")],
    pathex=[str(APP_DIR)],
    binaries=[],
    datas=[
        # Include the SQLite DB (will be created at runtime if missing)
        (str(APP_DIR / "quality.db"), "."),
        # Assets
        (str(APP_DIR / "assets"), "assets"),
        # App modules
        (str(APP_DIR / "pages"),      "pages"),
        (str(APP_DIR / "components"), "components"),
        (str(APP_DIR / "utils"),      "utils"),
        (str(APP_DIR / "db"),         "db"),
        # Streamlit static assets
        ("venv/Lib/site-packages/streamlit", "streamlit"),
    ],
    hiddenimports=[
        "streamlit",
        "streamlit.web.cli",
        "streamlit.runtime.scriptrunner.magic_funcs",
        "webview",
        "webview.platforms.edgechromium",
        "plotly",
        "plotly.express",
        "plotly.graph_objects",
        "pandas",
        "sqlite3",
        "packaging.version",
        "packaging.specifiers",
        "packaging.requirements",
        "altair",
        "pyarrow",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy.testing", "IPython", "ipykernel"],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(APP_DIR / "assets" / "icon.ico"),
    onefile=True,
)
