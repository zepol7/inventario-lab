"""Modelos de dominio del inventario."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Estado(str, Enum):
    """Estados posibles de un equipo."""

    DISPONIBLE = "disponible"
    PRESTADO = "prestado"
    MANTENIMIENTO = "mantenimiento"
    DADO_DE_BAJA = "dado_de_baja"


@dataclass
class Equipo:
    """Equipo de computo registrado en el laboratorio."""

    serial: str
    tipo: str
    marca: str
    valor_compra: float
    fecha_compra: date
    estado: Estado = Estado.DISPONIBLE
    prestado_a: str | None = None
    historial: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.serial or not self.serial.strip():
            raise ValueError("El serial es obligatorio")
        if self.valor_compra < 0:
            raise ValueError("El valor de compra no puede ser negativo")
        self.serial = self.serial.strip().upper()

    def valor_actual(self, hoy: date, vida_util_anios: int = 5) -> float:
        """Depreciacion en linea recta; nunca baja de cero."""
        if vida_util_anios <= 0:
            raise ValueError("La vida util debe ser positiva")
        anios = (hoy - self.fecha_compra).days / 365
        factor = max(0.0, 1 - anios / vida_util_anios)
        return round(self.valor_compra * factor, 2)
