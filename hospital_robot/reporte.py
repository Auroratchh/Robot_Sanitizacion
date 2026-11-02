from __future__ import annotations

import csv
from pathlib import Path

from .busqueda import Resultado

COLUMNAS = (
    "Escenario",
    "Algoritmo",
    "Costo",
    "Expandidos",
    "Tiempo (ms)",
    "Giros",
    "Reversas",
)


def _fila(escenario: str, r: Resultado) -> list[str]:
    if not r.exito:
        return [escenario, r.algoritmo, "sin ruta", str(r.nodos_expandidos), f"{r.tiempo_ms:.3f}", "-", "-"]
    return [escenario, r.algoritmo, str(r.costo), str(r.nodos_expandidos), f"{r.tiempo_ms:.3f}",
            str(r.giros), str(r.reversas)]


def tabla_texto(filas: list[tuple[str, Resultado]]) -> str:
    datos = [list(COLUMNAS)] + [_fila(nombre, r) for nombre, r in filas]
    anchos = [max(len(f[i]) for f in datos) for i in range(len(COLUMNAS))]
    lineas = []
    for i, fila in enumerate(datos):
        lineas.append("  ".join(celda.ljust(anchos[j]) for j, celda in enumerate(fila)))
        if i == 0:
            lineas.append("  ".join("-" * a for a in anchos))
    return "\n".join(lineas)


def exportar_csv(filas: list[tuple[str, Resultado]], ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(COLUMNAS)
        for nombre, r in filas:
            escritor.writerow(_fila(nombre, r))


def secuencia_acciones(r: Resultado) -> str:
    if not r.acciones:
        return "(ya está en la meta)"
    grupos: list[tuple[str, int]] = []
    for accion in r.acciones:
        if grupos and grupos[-1][0] == accion.value:
            grupos[-1] = (accion.value, grupos[-1][1] + 1)
        else:
            grupos.append((accion.value, 1))
    return ", ".join(f"{nombre} x{n}" if n > 1 else nombre for nombre, n in grupos)