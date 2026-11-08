"""Prueba de integracion: inventario + sistema de archivos (JSON)."""

from inventario.inventario import Inventario
from inventario.modelos import Estado


def test_guardar_y_cargar_conserva_estado(inventario, tmp_path):
    inventario.prestar("LAB-001", "Maria Peña")
    archivo = tmp_path / "inventario.json"

    inventario.guardar(archivo)
    recuperado = Inventario.cargar(archivo)

    assert len(recuperado) == 2
    equipo = recuperado.obtener("LAB-001")
    assert equipo.estado is Estado.PRESTADO
    assert equipo.prestado_a == "Maria Peña"
    assert equipo.historial == ["prestado a Maria Peña"]
