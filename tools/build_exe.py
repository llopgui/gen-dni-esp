#!/usr/bin/env python3
"""
Construye el ejecutable con PyInstaller usando ``GeneradorDNI.spec``.

Ejecutar desde cualquier directorio; el script usa la raíz del repositorio
como directorio de trabajo. Recomendado tener PyInstaller instalado
(``pip install -r requirements-dev.txt``).

Uso::

    python tools/build_exe.py

    python tools/build_exe.py --clean
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _raiz_repo() -> Path:
    """Directorio raíz del proyecto (padre de ``tools``)."""
    return Path(__file__).resolve().parent.parent


def _ruta_spec(raiz: Path) -> Path:
    """Ruta absoluta al fichero ``GeneradorDNI.spec``."""
    return raiz / "GeneradorDNI.spec"


def construir_exe(raiz: Path, limpiar_build: bool) -> None:
    """
    Lanza ``python -m PyInstaller`` con el spec del proyecto.

    Args:
        raiz: Carpeta raíz del repositorio (cwd del proceso).
        limpiar_build: Si es True, borra ``build/`` antes de compilar.

    Raises:
        FileNotFoundError: Si no existe ``GeneradorDNI.spec``.
        subprocess.CalledProcessError: Si PyInstaller termina con error.
    """
    spec = _ruta_spec(raiz)
    if not spec.is_file():
        raise FileNotFoundError(f"No se encuentra el spec: {spec}")

    build_dir = raiz / "build"
    if limpiar_build and build_dir.is_dir():
        shutil.rmtree(build_dir)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec),
        "--noconfirm",
    ]
    subprocess.run(cmd, cwd=raiz, check=True)


def _argumentos() -> argparse.Namespace:
    """Parsea argumentos CLI."""
    p = argparse.ArgumentParser(
        description=(
            "Genera GeneradorDNI.exe con PyInstaller (GeneradorDNI.spec)."
        ),
    )
    p.add_argument(
        "--clean",
        action="store_true",
        help="Elimina la carpeta build/ antes de compilar.",
    )
    return p.parse_args()


def main() -> int:
    """Punto de entrada del script."""
    raiz = _raiz_repo()
    args = _argumentos()

    try:
        construir_exe(raiz, limpiar_build=args.clean)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(
            f"PyInstaller falló con código {exc.returncode}.",
            file=sys.stderr,
        )
        return exc.returncode or 1

    dist_exe = raiz / "dist" / "GeneradorDNI.exe"
    if dist_exe.is_file():
        print(f"Ejecutable generado: {dist_exe}")
    else:
        print(
            "Compilación finalizada; revisa la carpeta dist/.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
