# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec para IPTV Player (macOS, .app bundle)
#
# Uso:
#   pyinstaller iptv-player-mac.spec
#
# Salida:
#   dist/IPTV-Player.app
#
# Requisito en el sistema del usuario final:
#   VLC Media Player instalado (python-vlc lo busca en tiempo de ejecucion).

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=["PyQt6.sip"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "scipy", "PIL", "cv2"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="IPTV-Player",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="IPTV-Player",
)

app = BUNDLE(
    coll,
    name="IPTV-Player.app",
    icon=None,
    bundle_identifier="com.gerardbourguett.iptv-player",
)
