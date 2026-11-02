from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from .mapa import Mapa
from .modelos import Accion, Estado


@dataclass(frozen=True)
class CostosConfig:
    pasillo: int = 1
    congestionado: int = 3
    giro: int = 1
    retroceso: int = 4

    def __post_init__(self) -> None:
        if min(self.pasillo, self.congestionado, self.giro, self.retroceso) <= 0:
            raise ValueError("Todos los costos deben ser positivos")

    @property
    def costo_minimo_desplazamiento(self) -> int:
        return min(self.pasillo, self.congestionado, self.retroceso)


class ProblemaRuta:
    def __init__(
        self,
        mapa: Mapa,
        inicio: Estado,
        meta: tuple[int, int],
        costos: CostosConfig | None = None,
    ) -> None:
        self.mapa = mapa
        self.estado_inicial = inicio
        self.meta = meta
        self.costos = costos or CostosConfig()
        self._validar()

    def _validar(self) -> None:
        if not self.mapa.es_transitable(*self.estado_inicial.posicion):
            raise ValueError(
                f"El inicio {self.estado_inicial.posicion} está fuera del mapa o en un muro"
            )
        if not self.mapa.es_transitable(*self.meta):
            raise ValueError(f"La meta {self.meta} está fuera del mapa o en un muro")

    def es_meta(self, estado: Estado) -> bool:
        return estado.posicion == self.meta

    def _costo_celda(self, x: int, y: int) -> int:
        if self.mapa.es_congestionada(x, y):
            return self.costos.congestionado
        return self.costos.pasillo

    def sucesores(self, estado: Estado) -> Iterator[tuple[Accion, Estado, int]]:
        o = estado.orientacion

        nx, ny = estado.x + o.dx, estado.y + o.dy
        if self.mapa.es_transitable(nx, ny):
            yield Accion.AVANZAR, Estado(nx, ny, o), self._costo_celda(nx, ny)

        yield Accion.GIRAR_IZQUIERDA, Estado(estado.x, estado.y, o.girar_izquierda()), self.costos.giro
        yield Accion.GIRAR_DERECHA, Estado(estado.x, estado.y, o.girar_derecha()), self.costos.giro

        rx, ry = estado.x - o.dx, estado.y - o.dy
        if self.mapa.es_transitable(rx, ry):
            yield Accion.RETROCEDER, Estado(rx, ry, o), self.costos.retroceso