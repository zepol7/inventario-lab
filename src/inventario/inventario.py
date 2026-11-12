"""Logica de negocio: registro, prestamos y reportes."""

import json
from datetime import date
from pathlib import Path

from inventario.modelos import Equipo, Estado


class InventarioError(Exception):
    """Error de reglas de negocio del inventario."""


class Inventario:
    """Coleccion de equipos indexada por serial."""

    def __init__(self) -> None:
        self._equipos: dict[str, Equipo] = {}

    def __len__(self) -> int:
        return len(self._equipos)

    def agregar(self, equipo: Equipo) -> None:
        if equipo.serial in self._equipos:
            raise InventarioError(f"El serial {equipo.serial} ya existe")
        self._equipos[equipo.serial] = equipo

    def obtener(self, serial: str) -> Equipo:
        clave = serial.strip().upper()
        if clave not in self._equipos:
            raise InventarioError(f"No existe el equipo {clave}")
        return self._equipos[clave]

    def prestar(self, serial: str, estudiante: str) -> None:
        equipo = self.obtener(serial)
        if equipo.estado is not Estado.DISPONIBLE:
            raise InventarioError(
                f"El equipo {equipo.serial} no esta disponible ({equipo.estado.value})"
            )
        if not estudiante.strip():
            raise InventarioError("Debe indicar el estudiante")
        equipo.estado = Estado.PRESTADO
        equipo.prestado_a = estudiante.strip()
        equipo.historial.append(f"prestado a {equipo.prestado_a}")

    def devolver(self, serial: str) -> None:
        equipo = self.obtener(serial)
        if equipo.estado is not Estado.PRESTADO:
            raise InventarioError(f"El equipo {equipo.serial} no esta prestado")
        equipo.historial.append(f"devuelto por {equipo.prestado_a}")
        equipo.estado = Estado.DISPONIBLE
        equipo.prestado_a = None

    def enviar_a_mantenimiento(self, serial: str) -> None:
        equipo = self.obtener(serial)
        if equipo.estado is Estado.PRESTADO:
            raise InventarioError("Primero debe devolverse el equipo")
        equipo.estado = Estado.MANTENIMIENTO
        equipo.historial.append("enviado a mantenimiento")

    def disponibles(self, tipo: str | None = None) -> list[Equipo]:
        return [
            e for e in self._equipos.values()
            if e.estado is Estado.DISPONIBLE
            and (tipo is None or e.tipo.lower() == tipo.lower())
        ]

    def reporte_por_estado(self) -> dict[str, int]:
        conteo = {estado.value: 0 for estado in Estado}
        for equipo in self._equipos.values():
            conteo[equipo.estado.value] += 1
        return conteo

    def valor_total(self, hoy: date) -> float:
        return round(sum(e.valor_actual(hoy) for e in self._equipos.values()), 2)

    def guardar(self, ruta: Path) -> None:
        datos = [
            {
                "serial": e.serial, "tipo": e.tipo, "marca": e.marca,
                "valor_compra": e.valor_compra,
                "fecha_compra": e.fecha_compra.isoformat(),
                "estado": e.estado.value, "prestado_a": e.prestado_a,
                "historial": e.historial,
            }
            for e in self._equipos.values()
        ]
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def cargar(cls, ruta: Path) -> "Inventario":
        inventario = cls()
        for d in json.loads(ruta.read_text(encoding="utf-8")):
            inventario.agregar(Equipo(
                serial=d["serial"], tipo=d["tipo"], marca=d["marca"],
                valor_compra=d["valor_compra"],
                fecha_compra=date.fromisoformat(d["fecha_compra"]),
                estado=Estado(d["estado"]), prestado_a=d["prestado_a"],
                historial=d["historial"],
            ))
        return inventario
    def conteo_por_tipo(self) -> dict[str, int]:
        conteo: dict[str, int] = {}
        for equipo in self._equipos.values():
            conteo[equipo.tipo] = conteo.get(equipo.tipo, 0) + 1
        return conteo