from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Orientacion(Enum):
    NORTE = (0, 1, "N", "^", "Norte")
    ESTE = (1, 0, "E", ">", "Este")
    SUR = (0, -1, "S", "v", "Sur")
    OESTE = (-1, 0, "O", "<", "Oeste")

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    @property
    def letra(self) -> str:
        return self.value[2]

    @property
    def flecha(self) -> str:
        return self.value[3]

    @property
    def nombre(self) -> str:
        return self.value[4]

    def girar_derecha(self) -> Orientacion:
        orden = list(Orientacion)
        return orden[(orden.index(self) + 1) % len(orden)]

    def girar_izquierda(self) -> Orientacion:
        orden = list(Orientacion)
        return orden[(orden.index(self) - 1) % len(orden)]

    @classmethod
    def desde_texto(cls, texto: str) -> Orientacion:
        texto = texto.strip().lower()
        for orientacion in cls:
            if texto in (orientacion.letra.lower(), orientacion.nombre.lower()):
                return orientacion
        raise ValueError(f"Orientación no válida: {texto!r} (use N, E, S u O)")


class Accion(Enum):
    AVANZAR = "Avanzar"
    GIRAR_IZQUIERDA = "Girar Izq"
    GIRAR_DERECHA = "Girar Der"
    RETROCEDER = "Retroceder"


@dataclass(frozen=True)
class Estado:
    x: int
    y: int
    orientacion: Orientacion

    @property
    def posicion(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __str__(self) -> str:
        return f"(({self.x}, {self.y}), {self.orientacion.nombre})"