from __future__ import annotations
import heapq
import time
from dataclasses import dataclass, field
from itertools import count
from .heuristicas import Heuristica, crear_heuristica_manhattan, heuristica_nula
from .modelos import Accion, Estado
from .problema import ProblemaRuta


@dataclass
class Nodo:
    estado: Estado
    padre: Nodo | None
    accion: Accion | None
    g: int
    h: int

    @property
    def f(self) -> int:
        return self.g + self.h


@dataclass
class Resultado:
    algoritmo: str
    exito: bool
    estados: list[Estado] = field(default_factory=list)
    acciones: list[Accion] = field(default_factory=list)
    costo: int | None = None
    nodos_expandidos: int = 0
    tiempo_ms: float = 0.0

    @property
    def avances(self) -> int:
        return self.acciones.count(Accion.AVANZAR)

    @property
    def giros(self) -> int:
        return self.acciones.count(Accion.GIRAR_IZQUIERDA) + self.acciones.count(
            Accion.GIRAR_DERECHA
        )

    @property
    def reversas(self) -> int:
        return self.acciones.count(Accion.RETROCEDER)


def _reconstruir(nodo: Nodo) -> tuple[list[Estado], list[Accion]]:
    estados: list[Estado] = []
    acciones: list[Accion] = []
    while nodo is not None:
        estados.append(nodo.estado)
        if nodo.accion is not None:
            acciones.append(nodo.accion)
        nodo = nodo.padre
    estados.reverse()
    acciones.reverse()
    return estados, acciones


def _buscar(problema: ProblemaRuta, heuristica: Heuristica, nombre: str) -> Resultado:
    t0 = time.perf_counter()

    raiz = Nodo(problema.estado_inicial, None, None, 0, heuristica(problema.estado_inicial))
    desempate = count()
    frontera: list[tuple[int, int, int, Nodo]] = [(raiz.f, raiz.h, next(desempate), raiz)]
    mejor_g: dict[Estado, int] = {raiz.estado: 0}

    expandidos = 0

    while frontera:
        _, _, _, nodo = heapq.heappop(frontera)
        if nodo.g > mejor_g[nodo.estado]:
            continue

        if problema.es_meta(nodo.estado):
            estados, acciones = _reconstruir(nodo)
            return Resultado(
                algoritmo=nombre,
                exito=True,
                estados=estados,
                acciones=acciones,
                costo=nodo.g,
                nodos_expandidos=expandidos,
                tiempo_ms=(time.perf_counter() - t0) * 1000,
            )

        expandidos += 1
        for accion, siguiente, costo in problema.sucesores(nodo.estado):
            g = nodo.g + costo
            if g < mejor_g.get(siguiente, float("inf")):
                mejor_g[siguiente] = g
                hijo = Nodo(siguiente, nodo, accion, g, heuristica(siguiente))
                heapq.heappush(frontera, (hijo.f, hijo.h, next(desempate), hijo))

    return Resultado(
        algoritmo=nombre,
        exito=False,
        nodos_expandidos=expandidos,
        tiempo_ms=(time.perf_counter() - t0) * 1000,
    )


def a_estrella(problema: ProblemaRuta) -> Resultado:
    h = crear_heuristica_manhattan(problema.meta, problema.costos.costo_minimo_desplazamiento)
    return _buscar(problema, h, "A*")


def costo_uniforme(problema: ProblemaRuta) -> Resultado:
    return _buscar(problema, heuristica_nula, "UCS")