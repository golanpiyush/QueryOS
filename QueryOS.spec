# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['bin\\queryos.py'],
    pathex=[],
    binaries=[],
    datas=[('classes', 'classes'), ('utils', 'utils'), ('user', 'user'), ('inputs', 'inputs'), ('errors', 'errors'), ('config', 'config')],
    hiddenimports=['pyttsx3', 'pyttsx3.drivers', 'pyttsx3.drivers.sapi5', 'speech_recognition', 'pyaudio', 'requests', 'json', 'threading', 'tkinter', 'win32api', 'win32con', 'win32gui', 'comtypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pandas', 'matplotlib', 'torch', 'tensorflow'],
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
    name='QueryOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['queryos.ico'],
)
