# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller: el icono del .exe es el mismo que la app (assets/icon.ico).
Ejecutar: python -m PyInstaller GeneradorDNI.spec
"""
import os

_root = os.path.dirname(os.path.abspath(SPEC))
_assets_ico = os.path.join(_root, "assets", "icon.ico")
_assets_png = os.path.join(_root, "assets", "icon.png")

# Icono del ejecutable en el explorador de Windows (mismo fichero que usa la ventana tkinter)
_exe_icon = os.path.abspath(_assets_ico) if os.path.isfile(_assets_ico) else None

# Recursos para que la GUI cargue el mismo icono al ejecutar el .exe
_datas = []
if os.path.isfile(_assets_ico):
    _datas.append((os.path.abspath(_assets_ico), "assets"))
if os.path.isfile(_assets_png):
    _datas.append((os.path.abspath(_assets_png), "assets"))

a = Analysis(
    ["src\\main.py"],
    pathex=[_root],
    binaries=[],
    datas=_datas,
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
    name="GeneradorDNI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX en el .exe final suele dejar el icono genérico de PyInstaller en Windows.
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_exe_icon,
)
