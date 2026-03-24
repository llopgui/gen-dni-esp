"""
Configuración por defecto de la aplicación.

No se usa archivo .env: los valores están definidos aquí.
Para personalizar, modifica estas constantes o amplía este módulo.
"""

from typing import Final

# Identificación de la aplicación
APP_NAME: Final[str] = "GEN_DNI_ESP"
APP_VERSION: Final[str] = "1.0.1"

# Título de la ventana principal (Tkinter)
WINDOW_TITLE: Final[str] = "Generador DNI Español"

# Tamaño mínimo de la ventana (px)
WINDOW_MIN_WIDTH: Final[int] = 450
WINDOW_MIN_HEIGHT: Final[int] = 620

# Alto aproximado del logo junto al título (px; escala con subsample en tkinter)
ALTURA_LOGO_TITULO_PX: Final[int] = 40

# Límites de cantidad en generación por lotes (GUI y validación en ``dni``)
LOTE_MIN: Final[int] = 1
LOTE_MAX: Final[int] = 10_000

# Separadores para exportación / unión de DNIs en lote (etiqueta → carácter)
SEPARADORES: Final[dict[str, str]] = {
    "Línea nueva": "\n",
    "Coma": ",",
    "Punto y coma": ";",
    "Tabulación": "\t",
}

# Paleta de colores de la interfaz (inspirada en diseño SaaS)
COLORES: Final[dict[str, str]] = {
    "fondo": "#f8fafc",
    "superficie": "#ffffff",
    "borde": "#e2e8f0",
    "primario": "#2563eb",
    "primario_hover": "#1d4ed8",
    "exito": "#059669",
    "error": "#dc2626",
    "texto": "#1e293b",
    "texto_secundario": "#64748b",
    "acento_suave": "#dbeafe",
}

# Modo depuración (reservado para logging o mensajes extra en el futuro)
DEBUG: Final[bool] = False
