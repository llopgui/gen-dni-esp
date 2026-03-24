"""Tests del módulo de configuración por defecto."""

from src.config import (
    APP_NAME,
    APP_VERSION,
    COLORES,
    DEBUG,
    LOTE_MAX,
    LOTE_MIN,
    SEPARADORES,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_TITLE,
)


def test_config_constants_exist() -> None:
    """Las constantes de configuración están definidas y son coherentes."""
    assert APP_NAME == "GEN_DNI_ESP"
    assert APP_VERSION == "1.0.1"
    assert len(WINDOW_TITLE) > 0
    assert isinstance(DEBUG, bool)
    assert WINDOW_MIN_WIDTH > 0 and WINDOW_MIN_HEIGHT > 0
    assert LOTE_MIN >= 1 and LOTE_MAX >= LOTE_MIN
    assert "\n" in SEPARADORES.values()
    assert "fondo" in COLORES and "primario" in COLORES
