# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec para IPTV Player (Windows, onedir)
#
# Uso:
#   pyinstaller iptv-player.spec
#
# Salida:
#   dist/IPTV-Player/IPTV-Player.exe  (+ dependencias Qt en la misma carpeta)
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
    # Excluir modulos pesados que no se usan
    excludes=["tkinter", "matplotlib", "numpy", "scipy", "PIL", "cv2"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,     # onedir: los binarios van a la carpeta COLLECT
    name="IPTV-Player",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX desactivado para mayor compatibilidad
    console=False,             # Sin ventana de consola (app de escritorio)
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
