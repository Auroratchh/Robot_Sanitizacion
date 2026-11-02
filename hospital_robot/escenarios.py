from __future__ import annotations

from dataclasses import dataclass

from .mapa import Mapa
from .modelos import Estado, Orientacion


@dataclass(frozen=True)
class Escenario:
    clave: str
    mapa: Mapa
    inicio: Estado
    meta: tuple[int, int]
    descripcion: str

_HOSPITAL_GENERAL = Mapa.desde_texto(
    "Hospital General (10x10)",
    """
    ..........
    .####.###.
    .#..~.~.#.
    .#.##.#.#.
    ....~.~...
    .##.###.#.
    .#~.~...#.
    .#.####.#.
    ...~~.....
    ..........
    """,
)

_CLINICA = Mapa.desde_texto(
    "Clínica de Especialidades (10x10)",
    """
    ..........
    .####.####
    .~~~~.~...
    .####.#.##
    ...~..#...
    .##.#.#.#.
    .#..~...#.
    .#.###.##.
    ...~......
    ..........
    """,
)

_PEDIATRICO = Mapa.desde_texto(
    "Hospital Pediátrico (10x10)",
    """
    ..........
    .#####.##.
    .#..~...#.
    .#.####.#.
    ...~~~..#.
    .###.##.#.
    .~...#..~.
    .#####.##.
    ......~...
    ..........
    """,
)

ESCENARIOS: dict[str, Escenario] = {
    "general": Escenario(
        "general",
        _HOSPITAL_GENERAL,
        Estado(0, 0, Orientacion.NORTE),
        (3, 7),
        "Hospital de tamaño medio con pasillos congestionados en el centro.",
    ),
    "clinica": Escenario(
        "clinica",
        _CLINICA,
        Estado(0, 0, Orientacion.ESTE),
        (9, 5),
        "Clínica con un pasillo principal y consultorios laterales.",
    ),
    "pediatrico": Escenario(
        "pediatrico",
        _PEDIATRICO,
        Estado(0, 0, Orientacion.ESTE),
        (7, 7),
        "Hospital con corredor perimetral y zonas de alto tráfico.",
    ),
}


def obtener_escenario(clave: str) -> Escenario:
    try:
        return ESCENARIOS[clave]
    except KeyError as exc:
        disponibles = ", ".join(ESCENARIOS)
        raise ValueError(f"Escenario desconocido {clave!r}. Disponibles: {disponibles}") from exc