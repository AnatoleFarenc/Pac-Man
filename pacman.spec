# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import json

high_scores_path = 'data/high_scores.json'
if not os.path.exists(high_scores_path):
    with open(high_scores_path, 'w') as f:
        json.dump([], f)

if sys.platform == 'win32':
    icon = 'assets/sprites/pac_icone.ico'
else:
    icon = 'assets/sprites/pac_icone_l_m.png'

a = Analysis(
    ['pac-man.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('data/config.json', 'data'),
        ('data/sound', 'data/sound'),
        ('data/high_scores.json', 'data'),
    ],
    hiddenimports=['mazegenerator'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['flake8', 'mypy'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pacman',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    icon=icon,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
