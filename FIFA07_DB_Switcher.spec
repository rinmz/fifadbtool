# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['fifa_db_switcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/fifa.db', 'data'),
        ('data/fifa_patched.db', 'data'),
        ('assets/button_install.png', 'assets'),
        ('assets/button_restore.png', 'assets'),
        ('assets/button_browse.png', 'assets'),
        ('assets/path_holder.png', 'assets'),
        ('assets/app_icon.png', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FIFA07_DB_Switcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=['assets/app_icon.ico'],
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
