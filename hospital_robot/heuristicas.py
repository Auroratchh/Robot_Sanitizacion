from __future__ import annotations
from collections.abc import Callable
from .modelos import Estado

Heuristica = Callable[[Estado], int]

def heuristica_nula(_estado: Estado) -> int:
    return 0
def crear_heuristica_manhattan(meta: tuple[int, int], costo_minimo: int) -> Heuristica:
    x_meta, y_meta = meta

    def h(estado: Estado) -> int:
        return (abs(x_meta - estado.x) + abs(y_meta - estado.y)) * costo_minimo
    return h