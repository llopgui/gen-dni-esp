#!/usr/bin/env python3
"""
Genera ``assets/icon.ico`` a partir de un PNG fuente (por defecto ``assets/icon.png``).

Incluye varias resoluciones típicas de Windows para que el .exe y la barra de tareas
se vean nítidos. Requiere Pillow (``pip install -r requirements-dev.txt``).

Uso desde la raíz del repositorio::

    python tools/generate_icons.py

    python tools/generate_icons.py --source assets/mi_logo.png --out-ico assets/icon.ico
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image as PilImage

# Tamaños estándar para iconos de escritorio Windows (explorador, barra de tareas, etc.)
_TAMANOS_ICO_DEFECTO: tuple[int, ...] = (16, 24, 32, 48, 64, 128, 256)


def _raiz_repo() -> Path:
    """Directorio raíz del proyecto (padre de ``tools``)."""
    return Path(__file__).resolve().parent.parent


def _normalizar_cuadrado_rgba(imagen: PilImage) -> PilImage:
    """
    Centra la imagen en un lienzo cuadrado transparente (RGBA).

    Args:
        imagen: Imagen en modo RGBA.

    Returns:
        Nueva imagen cuadrada RGBA.
    """
    from PIL import Image

    ancho, alto = imagen.size
    lado = max(ancho, alto)
    lienzo = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    x = (lado - ancho) // 2
    y = (lado - alto) // 2
    lienzo.paste(imagen, (x, y), imagen)
    return lienzo


def generar_icono_ico(
    ruta_png: Path,
    ruta_ico: Path,
    tamanos: tuple[int, ...] = _TAMANOS_ICO_DEFECTO,
) -> None:
    """
    Crea un fichero ``.ico`` con varias resoluciones a partir de un PNG.

    Args:
        ruta_png: Imagen fuente (se convierte a RGBA si hace falta).
        ruta_ico: Ruta de salida del ``.ico``.
        tamanos: Lista de lados en píxeles (cuadrados).

    Raises:
        FileNotFoundError: Si no existe el PNG de entrada.
        ValueError: Si ``tamanos`` está vacío.
    """
    from PIL import Image

    if not ruta_png.is_file():
        raise FileNotFoundError(f"No se encuentra la imagen fuente: {ruta_png}")
    if not tamanos:
        raise ValueError("Debe indicarse al menos un tamaño para el ICO.")

    try:
        with Image.open(ruta_png) as img:
            img_rgba = img.convert("RGBA")
            cuadrada = _normalizar_cuadrado_rgba(img_rgba)

            # Lista de ``Image.Image`` (Pillow); sin anotar con PilImage (solo TYPE_CHECKING).
            variantes = []
            for lado in tamanos:
                if lado <= 0:
                    raise ValueError(f"Tamaño inválido: {lado}")
                red = cuadrada.resize((lado, lado), Image.Resampling.LANCZOS)
                variantes.append(red)

            ruta_ico.parent.mkdir(parents=True, exist_ok=True)
            primera, *resto = variantes
            primera.save(
                ruta_ico,
                format="ICO",
                append_images=list(resto),
            )
    except OSError as exc:
        raise OSError(f"No se pudo leer o escribir las imágenes: {exc}") from exc


def _parsear_tamanos(cadena: str) -> tuple[int, ...]:
    """Parsea ``"16,32,256"`` en una tupla de enteros."""
    partes = [p.strip() for p in cadena.split(",") if p.strip()]
    try:
        return tuple(int(p) for p in partes)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Tamaños inválidos (use enteros separados por coma): {cadena!r}"
        ) from exc


def _argumentos() -> argparse.Namespace:
    """Construye y parsea los argumentos de línea de comandos."""
    raiz = _raiz_repo()
    pred_png = raiz / "assets" / "icon.png"
    pred_ico = raiz / "assets" / "icon.ico"

    p = argparse.ArgumentParser(
        description="Genera icon.ico multi-resolución desde un PNG (requiere Pillow)."
    )
    p.add_argument(
        "--source",
        type=Path,
        default=pred_png,
        help=f"PNG fuente (por defecto: {pred_png})",
    )
    p.add_argument(
        "--out-ico",
        type=Path,
        default=pred_ico,
        help=f"Salida .ico (por defecto: {pred_ico})",
    )
    p.add_argument(
        "--sizes",
        type=_parsear_tamanos,
        default=None,
        help=(
            "Tamaños separados por coma, p. ej. 16,32,48,256 "
            f"(por defecto: {','.join(map(str, _TAMANOS_ICO_DEFECTO))})"
        ),
    )
    return p.parse_args()


def main() -> int:
    """Punto de entrada del script."""
    try:
        import PIL  # noqa: F401  # comprobar que Pillow está instalado
    except ImportError:
        print(
            "Falta Pillow. Instala dependencias de desarrollo:\n"
            "  pip install -r requirements-dev.txt",
            file=sys.stderr,
        )
        return 1

    args = _argumentos()
    raiz = _raiz_repo()
    # Rutas relativas al cwd del usuario; si son relativas, anclar a la raíz del repo
    fuente = args.source if args.source.is_absolute() else (raiz / args.source)
    salida = args.out_ico if args.out_ico.is_absolute() else (raiz / args.out_ico)
    tamanos = args.sizes if args.sizes is not None else _TAMANOS_ICO_DEFECTO

    try:
        generar_icono_ico(fuente, salida, tamanos=tamanos)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"ICO generado: {salida} ({len(tamanos)} resoluciones)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
