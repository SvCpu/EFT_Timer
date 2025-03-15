# -*- mode: python ; coding: utf-8 -*-
# From Ai

import os

block_cipher = None

a = Analysis(
    ['eft_timer.py'],
    pathex=[],
    binaries=[],
    datas=[(os.path.join(os.path.dirname(os.path.abspath('eft_timer.py')), 'MindEscape.ttf'), '.')],
    hiddenimports=['tkinter', 'datetime', 'time', 'argparse','sys'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='eft_timer',
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
    onefile=True
)