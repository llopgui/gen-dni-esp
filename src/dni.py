"""
Módulo para el cálculo y generación de DNI español.

Contiene las funciones para obtener la letra de control de un DNI,
validar DNIs completos y generar DNIs aleatorios válidos de forma segura.
"""

import logging
import re
import secrets

from src.config import LOTE_MAX, LOTE_MIN

# Cadena de letras de control del DNI español (posición = resto de número % 23)
LETRAS_DNI: str = "TRWAGMYFPDXBNJZSQVHLCKE"

# Regex para validar formato: 8 dígitos + 1 letra mayúscula
_PATRON_DNI_COMPLETO: re.Pattern[str] = re.compile(r"^\d{8}[A-Z]$")
# Patrón para localizar DNIs dentro de un texto (sin ^$)
_PATRON_DNI_SUBSTRING: re.Pattern[str] = re.compile(r"\d{8}[A-Z]")

# Rango válido para números de DNI (evita ceros a la izquierda en generación)
_DNI_MIN: int = 10_000_000
_DNI_MAX: int = 99_999_999

# Límite máximo de bytes para copiar al portapapeles (1 MB)
_CLIPBOARD_MAX_BYTES: int = 1_048_576

# Nivel de logging por defecto del módulo (sin .env ni variables externas)
_LOG_LEVEL_DEFAULT: int = logging.WARNING

# Singleton de generador seguro (evita crear instancia en cada llamada)
_rng: secrets.SystemRandom | None = None


def _get_rng() -> secrets.SystemRandom:
    """Devuelve la instancia singleton de SystemRandom."""
    global _rng
    if _rng is None:
        _rng = secrets.SystemRandom()
    return _rng


def _configurar_logging() -> None:
    """
    Configura el nivel de logging del paquete con el valor por defecto.
    """
    logging.getLogger("src.dni").setLevel(_LOG_LEVEL_DEFAULT)


_configurar_logging()
logger = logging.getLogger(__name__)


def _sanitizar_numero(numero: str | int) -> int:
    """
    Sanitiza y convierte un valor a número de DNI válido.

    Args:
        numero: Número como string o int.

    Returns:
        Número entero validado.

    Raises:
        ValueError: Si el valor no es válido.
    """
    if isinstance(numero, int):
        if not 0 <= numero <= 99_999_999:
            raise ValueError("El número de DNI debe estar entre 0 y 99999999")
        return numero

    if not isinstance(numero, str):
        raise ValueError("El número de DNI debe ser un string o entero")

    # Eliminar espacios y caracteres no numéricos
    limpio = "".join(c for c in numero.strip() if c.isdigit())

    if not limpio:
        raise ValueError("No se encontraron dígitos válidos")

    if len(limpio) != 8:
        raise ValueError("El DNI debe tener exactamente 8 dígitos")

    return int(limpio)


def calcular_letra_dni(numero: int | str) -> str:
    """
    Calcula la letra de control correspondiente a un número de DNI.

    Args:
        numero: Número del DNI (8 dígitos, sin letra). Acepta int o str.

    Returns:
        La letra de control del DNI.

    Raises:
        ValueError: Si el número no está en el rango válido (0-99999999).

    Example:
        >>> calcular_letra_dni(12345678)
        'Z'
        >>> calcular_letra_dni("12345678")
        'Z'
    """
    num = _sanitizar_numero(numero)
    letra = LETRAS_DNI[num % 23]
    logger.debug("Letra calculada para %s: %s", num, letra)
    return letra


def validar_dni_completo(dni: str) -> bool:
    """
    Valida que un DNI completo (número + letra) sea correcto.

    Args:
        dni: DNI en formato "12345678A" (8 dígitos + 1 letra).

    Returns:
        True si el DNI es válido, False en caso contrario.
    """
    if not dni or not isinstance(dni, str):
        return False

    dni_norm = dni.strip().upper()
    if not _PATRON_DNI_COMPLETO.match(dni_norm):
        return False

    try:
        numero = int(dni_norm[:8])
        letra_introducida = dni_norm[8]
        letra_correcta = calcular_letra_dni(numero)
        return letra_introducida == letra_correcta
    except (ValueError, IndexError):
        return False


def generar_dni_aleatorio() -> str:
    """
    Genera un DNI español aleatorio válido de forma criptográficamente segura.

    Usa secrets.SystemRandom para evitar predicciones en generación aleatoria.
    El número se genera en el rango 10000000-99999999 para evitar
    DNIs con ceros a la izquierda que podrían parecer inválidos.

    Returns:
        DNI completo con formato "12345678A" (8 dígitos + letra).
    """
    rng = _get_rng()
    numero = rng.randint(_DNI_MIN, _DNI_MAX)
    letra = calcular_letra_dni(numero)
    dni = f"{numero}{letra}"
    logger.debug("DNI aleatorio generado: %s", dni[:4] + "****" + dni[-1])
    return dni


def generar_dni_lote(cantidad: int, unicos: bool = True) -> list[str]:
    """
    Genera un lote de DNIs aleatorios válidos de forma segura.

    Usa un algoritmo eficiente con set para evitar duplicados
    sin cargar todo el espacio de búsqueda en memoria.

    Args:
        cantidad: Número de DNIs a generar (rango ``LOTE_MIN``–``LOTE_MAX`` en
            ``src.config``).
        unicos: Si True, garantiza que no haya duplicados en el lote.

    Returns:
        Lista de DNIs completos con formato "12345678A".

    Raises:
        ValueError: Si cantidad está fuera del rango permitido, o si con
            ``unicos=True`` no se alcanza la cantidad tras el límite de intentos.
    """
    if not LOTE_MIN <= cantidad <= LOTE_MAX:
        raise ValueError(f"La cantidad debe estar entre {LOTE_MIN} y {LOTE_MAX}")

    rng = _get_rng()
    resultado: list[str] = []
    vistos: set[str] = set()

    intentos_max = cantidad * 100  # Evitar bucle infinito
    intentos = 0

    while len(resultado) < cantidad and intentos < intentos_max:
        intentos += 1
        numero = rng.randint(_DNI_MIN, _DNI_MAX)
        letra = calcular_letra_dni(numero)
        dni = f"{numero}{letra}"

        if unicos and dni in vistos:
            continue
        vistos.add(dni)
        resultado.append(dni)

    if len(resultado) < cantidad:
        raise ValueError(
            f"No se pudieron generar {cantidad} DNIs únicos "
            f"(obtenidos: {len(resultado)}). Reduce la cantidad o usa "
            "generar_dni_lote(..., unicos=False)."
        )

    logger.debug("Lote de %d DNIs generado", len(resultado))
    return resultado


def es_texto_seguro_para_clipboard(texto: str) -> bool:
    """
    Comprueba si un texto es seguro para copiar al portapapeles.

    Evita bloquear la app o consumir demasiada memoria.

    Args:
        texto: Texto a validar.

    Returns:
        True si el tamaño está dentro del límite permitido.
    """
    if not isinstance(texto, str):
        return False
    return len(texto.encode("utf-8")) <= _CLIPBOARD_MAX_BYTES


def truncar_para_clipboard(texto: str) -> tuple[str, bool]:
    """
    Trunca el texto si excede el límite seguro para el portapapeles.

    Localiza el último DNI completo (8 dígitos + 1 letra) para evitar
    cortar por la mitad, independientemente del separador usado.

    Args:
        texto: Texto a procesar.

    Returns:
        Tupla (texto_truncado, fue_truncado).
    """
    if not isinstance(texto, str):
        return ("", True)
    if es_texto_seguro_para_clipboard(texto):
        return (texto, False)
    encoded = texto.encode("utf-8")
    truncated = encoded[:_CLIPBOARD_MAX_BYTES].decode("utf-8", errors="ignore")
    matches = list(_PATRON_DNI_SUBSTRING.finditer(truncated))
    if matches:
        truncated = truncated[: matches[-1].end()]
    return (truncated.rstrip(), True)
