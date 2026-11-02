from __future__ import annotations
from dataclasses import dataclass

PASILLO = "."
CONGESTIONADO = "~"
MURO = "#"
SIMBOLOS_VALIDOS = {PASILLO, CONGESTIONADO, MURO}

@dataclass(frozen=True)
class Mapa:
    nombre: str
    filas: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.filas:
            raise ValueError("El mapa no puede estar vacío")
        ancho = len(self.filas[0])
        for fila in self.filas:
            if len(fila) != ancho:
                raise ValueError("Todas las filas del mapa deben medir lo mismo")
            invalidos = set(fila) - SIMBOLOS_VALIDOS
            if invalidos:
                raise ValueError(f"Símbolos no válidos en el mapa: {invalidos}")

    @classmethod
    def desde_texto(cls, nombre: str, texto: str) -> Mapa:
        filas = tuple(linea.strip() for linea in texto.strip().splitlines())
        return cls(nombre=nombre, filas=filas)

    @property
    def ancho(self) -> int:
        return len(self.filas[0])

    @property
    def alto(self) -> int:
        return len(self.filas)
    def dentro(self, x: int, y: int) -> bool:
        return 0 <= x < self.ancho and 0 <= y < self.alto
    def celda(self, x: int, y: int) -> str:
        return self.filas[self.alto - 1 - y][x]
    def es_transitable(self, x: int, y: int) -> bool:
        return self.dentro(x, y) and self.celda(x, y) != MURO
    def es_congestionada(self, x: int, y: int) -> bool:
        return self.celda(x, y) == CONGESTIONADO