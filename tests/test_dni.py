"""
Tests unitarios para el módulo dni.

Cubre cálculo de letra, validación, generación individual y por lotes,
y funciones de seguridad para el portapapeles.
"""

import pytest

from src.dni import (
    LETRAS_DNI,
    calcular_letra_dni,
    es_texto_seguro_para_clipboard,
    generar_dni_aleatorio,
    generar_dni_lote,
    truncar_para_clipboard,
    validar_dni_completo,
)


class TestCalcularLetraDni:
    """Tests para calcular_letra_dni."""

    def test_dni_12345678_devuelve_z(self) -> None:
        """El DNI 12345678 tiene letra Z."""
        assert calcular_letra_dni(12345678) == "Z"

    def test_dni_string_12345678_devuelve_z(self) -> None:
        """Acepta número como string."""
        assert calcular_letra_dni("12345678") == "Z"

    def test_dni_00000000_devuelve_t(self) -> None:
        """DNI 00000000 tiene letra T (resto 0)."""
        assert calcular_letra_dni(0) == "T"
        assert calcular_letra_dni("00000000") == "T"

    def test_dni_99999999_devuelve_r(self) -> None:
        """DNI 99999999 tiene letra R (resto 1)."""
        assert calcular_letra_dni(99999999) == "R"

    def test_numero_invalido_fuera_rango_raise(self) -> None:
        """Número fuera de rango lanza ValueError."""
        with pytest.raises(ValueError, match="entre 0 y 99999999"):
            calcular_letra_dni(100_000_000)

    def test_string_vacio_raise(self) -> None:
        """String vacío o sin dígitos lanza ValueError."""
        with pytest.raises(ValueError):
            calcular_letra_dni("")
        with pytest.raises(ValueError):
            calcular_letra_dni("abcdefgh")

    def test_string_siete_digitos_raise(self) -> None:
        """String con 7 dígitos lanza ValueError."""
        with pytest.raises(ValueError, match="exactamente 8"):
            calcular_letra_dni("1234567")

    def test_string_nueve_digitos_raise(self) -> None:
        """String con 9 dígitos lanza ValueError."""
        with pytest.raises(ValueError, match="exactamente 8"):
            calcular_letra_dni("123456789")

    def test_tipo_no_valido_raise(self) -> None:
        """Tipo no str ni int lanza ValueError."""
        with pytest.raises(ValueError, match="string o entero"):
            calcular_letra_dni(123.45)  # type: ignore[arg-type]


class TestValidarDniCompleto:
    """Tests para validar_dni_completo."""

    def test_dni_valido_12345678z(self) -> None:
        """12345678Z es válido."""
        assert validar_dni_completo("12345678Z") is True

    def test_dni_valido_minusculas(self) -> None:
        """Acepta minúsculas."""
        assert validar_dni_completo("12345678z") is True

    def test_dni_invalido_letra_incorrecta(self) -> None:
        """12345678A es inválido (letra correcta es Z)."""
        assert validar_dni_completo("12345678A") is False

    def test_dni_formato_corto(self) -> None:
        """Menos de 9 caracteres es inválido."""
        assert validar_dni_completo("1234567") is False
        assert validar_dni_completo("12345678") is False

    def test_dni_formato_largo(self) -> None:
        """Más de 9 caracteres es inválido."""
        assert validar_dni_completo("12345678ZA") is False

    def test_dni_con_letras_en_numero(self) -> None:
        """Número con letras es inválido."""
        assert validar_dni_completo("1234567Z") is False

    def test_string_vacio(self) -> None:
        """String vacío es inválido."""
        assert validar_dni_completo("") is False

    def test_none_o_no_string(self) -> None:
        """None o no-string devuelve False."""
        assert validar_dni_completo(None) is False  # type: ignore[arg-type]
        num = 12345678
        assert validar_dni_completo(num) is False  # type: ignore[arg-type]


class TestGenerarDniAleatorio:
    """Tests para generar_dni_aleatorio."""

    def test_formato_correcto(self) -> None:
        """Genera DNI con 8 dígitos + 1 letra."""
        dni = generar_dni_aleatorio()
        assert len(dni) == 9
        assert dni[:8].isdigit()
        assert dni[8].isalpha() and dni[8].isupper()

    def test_dni_generado_es_valido(self) -> None:
        """El DNI generado pasa la validación."""
        dni = generar_dni_aleatorio()
        assert validar_dni_completo(dni) is True

    def test_rango_numerico(self) -> None:
        """El número está en rango 10M-99M."""
        dni = generar_dni_aleatorio()
        numero = int(dni[:8])
        assert 10_000_000 <= numero <= 99_999_999

    def test_letra_correcta(self) -> None:
        """La letra corresponde al algoritmo."""
        dni = generar_dni_aleatorio()
        letra_calculada = calcular_letra_dni(dni[:8])
        assert dni[8] == letra_calculada


class TestGenerarDniLote:
    """Tests para generar_dni_lote."""

    def test_cantidad_correcta(self) -> None:
        """Genera la cantidad solicitada."""
        dnis = generar_dni_lote(5)
        assert len(dnis) == 5

    def test_todos_unicos(self) -> None:
        """No hay duplicados en el lote."""
        dnis = generar_dni_lote(100)
        assert len(dnis) == len(set(dnis))

    def test_todos_validos(self) -> None:
        """Todos los DNIs son válidos."""
        dnis = generar_dni_lote(20)
        for dni in dnis:
            assert validar_dni_completo(dni) is True

    def test_cantidad_cero_raise(self) -> None:
        """Cantidad 0 lanza ValueError."""
        with pytest.raises(ValueError, match="entre"):
            generar_dni_lote(0)

    def test_cantidad_excesiva_raise(self) -> None:
        """Cantidad > 10000 lanza ValueError."""
        with pytest.raises(ValueError, match="entre"):
            generar_dni_lote(10_001)

    def test_un_solo_dni(self) -> None:
        """Cantidad 1 funciona."""
        dnis = generar_dni_lote(1)
        assert len(dnis) == 1
        assert validar_dni_completo(dnis[0]) is True

    def test_unicos_imposible_lanza_valueerror(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Si ``randint`` solo devuelve el mismo número, no hay DNIs únicos
        suficientes; debe lanzarse ValueError (no lista incompleta).
        """
        import src.dni as dni_mod

        class _RngFijo:
            """Generador que siempre repite el mismo DNI numérico."""

            def randint(self, a: int, b: int) -> int:
                return 12_345_678

        monkeypatch.setattr(dni_mod, "_get_rng", lambda: _RngFijo())

        with pytest.raises(ValueError, match="No se pudieron generar"):
            generar_dni_lote(5, unicos=True)


class TestClipboardSeguridad:
    """Tests para funciones de seguridad del portapapeles."""

    def test_texto_pequeno_es_seguro(self) -> None:
        """Texto pequeño es seguro."""
        assert es_texto_seguro_para_clipboard("12345678Z") is True
        assert es_texto_seguro_para_clipboard("a" * 1000) is True

    def test_texto_no_string_no_es_seguro(self) -> None:
        """No-string devuelve False."""
        assert es_texto_seguro_para_clipboard(123) is (  # type: ignore[arg-type]
            False
        )
        assert es_texto_seguro_para_clipboard(None) is (  # type: ignore[arg-type]
            False
        )

    def test_truncar_texto_pequeno_no_trunca(self) -> None:
        """Texto pequeño no se trunca."""
        texto = "12345678Z\n87654321A"
        resultado, fue_truncado = truncar_para_clipboard(texto)
        assert resultado == texto
        assert fue_truncado is False

    def test_truncar_texto_grande_trunca(self) -> None:
        """Texto > 1MB se trunca."""
        texto = "12345678Z\n" * 200_000  # ~2MB
        resultado, fue_truncado = truncar_para_clipboard(texto)
        assert len(resultado.encode("utf-8")) <= 1_048_576
        assert fue_truncado is True

    def test_truncar_no_string_devuelve_vacio(self) -> None:
        """No-string devuelve tupla vacía."""
        resultado, fue_truncado = truncar_para_clipboard(  # type: ignore[arg-type]
            123,
        )
        assert resultado == ""
        assert fue_truncado is True


class TestLetrasDni:
    """Tests de cobertura del algoritmo de letras."""

    def test_todas_las_letras_aparecen(self) -> None:
        """Las 23 letras del algoritmo están en LETRAS_DNI."""
        assert len(LETRAS_DNI) == 23
        assert len(set(LETRAS_DNI)) == 23

    def test_restos_0_a_22_mapean_correctamente(self) -> None:
        """Cada resto 0-22 produce la letra esperada."""
        for i, letra in enumerate(LETRAS_DNI):
            # Número que da resto i: por ejemplo 23*k + i
            numero = 23 * 1000 + i
            assert calcular_letra_dni(numero) == letra
