from datetime import date

import pytest

from inventario.modelos import Equipo, Estado


def test_serial_se_normaliza(portatil):
    assert portatil.serial == "LAB-001"
    assert portatil.estado is Estado.DISPONIBLE


@pytest.mark.parametrize("serial", ["", "   "])
def test_serial_vacio_es_invalido(serial):
    with pytest.raises(ValueError):
        Equipo(serial, "portatil", "HP", 1, date(2024, 1, 1))


def test_valor_negativo_es_invalido():
    with pytest.raises(ValueError):
        Equipo("X1", "portatil", "HP", -1, date(2024, 1, 1))


@pytest.mark.parametrize(
    "hoy, esperado",
    [
        (date(2024, 1, 1), 3_000_000),      # recien comprado
        (date(2026, 7, 2), 1_500_000.0),    # mitad de vida util
        (date(2035, 1, 1), 0.0),            # vida util agotada: no negativo
    ],
)
def test_depreciacion_linea_recta(portatil, hoy, esperado):
    assert portatil.valor_actual(hoy) == pytest.approx(esperado, rel=1e-3)


def test_vida_util_invalida(portatil):
    with pytest.raises(ValueError):
        portatil.valor_actual(date(2025, 1, 1), vida_util_anios=0)
