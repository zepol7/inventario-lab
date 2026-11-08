from datetime import date

import pytest

from inventario.inventario import Inventario
from inventario.modelos import Equipo


@pytest.fixture
def portatil():
    return Equipo("lab-001", "portatil", "Lenovo", 3_000_000, date(2024, 1, 1))


@pytest.fixture
def inventario(portatil):
    inv = Inventario()
    inv.agregar(portatil)
    inv.agregar(Equipo("LAB-002", "proyector", "Epson", 2_000_000, date(2023, 6, 1)))
    return inv
