from datetime import date

import pytest

from inventario.inventario import InventarioError
from inventario.modelos import Equipo, Estado


def test_agregar_duplicado_falla(inventario):
    with pytest.raises(InventarioError):
        inventario.agregar(Equipo("lab-001", "portatil", "HP", 1, date(2024, 1, 1)))


def test_obtener_inexistente(inventario):
    with pytest.raises(InventarioError):
        inventario.obtener("NO-EXISTE")


def test_ciclo_prestamo_devolucion(inventario):
    inventario.prestar("lab-001", "Ana Ruiz")
    equipo = inventario.obtener("LAB-001")
    assert equipo.estado is Estado.PRESTADO
    assert equipo.prestado_a == "Ana Ruiz"

    inventario.devolver("LAB-001")
    assert equipo.estado is Estado.DISPONIBLE
    assert equipo.prestado_a is None
    assert equipo.historial == ["prestado a Ana Ruiz", "devuelto por Ana Ruiz"]


def test_no_se_presta_dos_veces(inventario):
    inventario.prestar("LAB-001", "Ana")
    with pytest.raises(InventarioError):
        inventario.prestar("LAB-001", "Luis")


def test_prestamo_sin_estudiante(inventario):
    with pytest.raises(InventarioError):
        inventario.prestar("LAB-001", "  ")


def test_devolver_no_prestado(inventario):
    with pytest.raises(InventarioError):
        inventario.devolver("LAB-001")


def test_mantenimiento_requiere_devolucion(inventario):
    inventario.prestar("LAB-001", "Ana")
    with pytest.raises(InventarioError):
        inventario.enviar_a_mantenimiento("LAB-001")
    inventario.devolver("LAB-001")
    inventario.enviar_a_mantenimiento("LAB-001")
    assert inventario.obtener("LAB-001").estado is Estado.MANTENIMIENTO


def test_disponibles_filtra_por_tipo(inventario):
    assert len(inventario.disponibles()) == 2
    assert [e.serial for e in inventario.disponibles("PROYECTOR")] == ["LAB-002"]


def test_reporte_por_estado(inventario):
    inventario.prestar("LAB-002", "Luis")
    reporte = inventario.reporte_por_estado()
    assert reporte["disponible"] == 1
    assert reporte["prestado"] == 1
    assert sum(reporte.values()) == len(inventario)


def test_valor_total(inventario):
    assert inventario.valor_total(date(2024, 1, 1)) > 0
