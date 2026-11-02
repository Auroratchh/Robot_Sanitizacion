from __future__ import annotations
from pathlib import Path
from .busqueda import Resultado
from .mapa import CONGESTIONADO, MURO, Mapa
from .modelos import Estado


def dibujar_ascii(mapa: Mapa, inicio: Estado, meta: tuple[int, int], ruta: Resultado | None = None) -> str:
    marcas: dict[tuple[int, int], str] = {}
    if ruta and ruta.exito:
        for estado in ruta.estados:
            marcas[estado.posicion] = estado.orientacion.flecha
    marcas[inicio.posicion] = "S"
    marcas[meta] = "M"

    lineas = []
    for y in range(mapa.alto - 1, -1, -1):
        fila = "".join(marcas.get((x, y), mapa.celda(x, y)) for x in range(mapa.ancho))
        lineas.append(f"{y:>2} {fila}")
    eje = "   " + "".join(str(x % 10) for x in range(mapa.ancho))
    lineas.append(eje)
    return "\n".join(lineas)


def guardar_png(
    mapa: Mapa,
    inicio: Estado,
    meta: tuple[int, int],
    resultados: list[Resultado],
    destino: Path,
) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    destino.parent.mkdir(parents=True, exist_ok=True)
    fig, ejes = plt.subplots(1, len(resultados), figsize=(6 * len(resultados), 6), squeeze=False)
    for eje, r in zip(ejes[0], resultados):
        for y in range(mapa.alto):
            for x in range(mapa.ancho):
                celda = mapa.celda(x, y)
                color = {MURO: "#37474f", CONGESTIONADO: "#ffcc80"}.get(celda, "#ffffff")
                eje.add_patch(plt.Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor=color, edgecolor="#cfd8dc"))
        if r.exito:
            xs = [e.x for e in r.estados]
            ys = [e.y for e in r.estados]
            eje.plot(xs, ys, "-", color="#1565c0", linewidth=2)
        eje.plot(inicio.x, inicio.y, "o", color="#2e7d32", markersize=12, label="Inicio")
        eje.plot(meta[0], meta[1], "*", color="#f9a825", markersize=18, label="Meta")
        titulo = f"{r.algoritmo} — costo {r.costo}, expandidos {r.nodos_expandidos}" if r.exito else f"{r.algoritmo} — sin ruta"
        eje.set_title(titulo)
        eje.set_xlim(-0.5, mapa.ancho - 0.5)
        eje.set_ylim(-0.5, mapa.alto - 0.5)
        eje.set_aspect("equal")
        eje.set_xticks(range(mapa.ancho))
        eje.set_yticks(range(mapa.alto))
        eje.legend(loc="upper right")
    fig.suptitle(mapa.nombre)
    fig.tight_layout()
    fig.savefig(destino, dpi=120)
    plt.close(fig)
    return True