"""Punto de entrada principal de GEN_DNI_ESP."""

import logging

from src.config import DEBUG
from src.dni_gui import main as run_gui


def main() -> None:
    """Función principal: inicia la aplicación gráfica de DNI."""
    if DEBUG:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s %(name)s: %(message)s",
        )
    run_gui()


if __name__ == "__main__":
    main()
