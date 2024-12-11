# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('D:\\Job\\DocParser\\venv\\Lib\\site-packages\\pypdfium2_raw\\pdfium.dll', 'pypdfium2_raw'),
        ('D:\\Job\\DocParser\\venv\\Lib\\site-packages\\pypdfium2_raw\\version.json', 'pypdfium2_raw'),
        ('D:\\Job\\DocParser\\venv\\Lib\\site-packages\\pypdfium2\\version.json', 'pypdfium2')
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
    name='main',
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
)
