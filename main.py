from __future__ import annotations
import argparse
import sys
from pathlib import Path

from hospital_robot import (
    ESCENARIOS,
    Estado,
    Orientacion,
    ProblemaRuta,
    a_estrella,
    costo_uniforme,
    obtener_escenario,
)
from hospital_robot.escenarios import Escenario
from hospital_robot.reporte import exportar_csv, secuencia_acciones, tabla_texto
from hospital_robot.visualizacion import dibujar_ascii, guardar_png

def parsear_inicio(texto: str) -> Estado:
    try:
        x, y, orientacion = texto.split(",")
        return Estado(int(x), int(y), Orientacion.desde_texto(orientacion))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Inicio inválido {texto!r}, usar x,y,orientación") from exc


def parsear_meta(texto: str) -> tuple[int, int]:
    try:
        x, y = texto.split(",")
        return int(x), int(y)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Meta inválida {texto!r}, usar x,y") from exc


def crear_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rutas de menor costo para un robot de sanitización hospitalaria")
    p.add_argument("--listar", action="store_true", help="muestra los escenarios disponibles")
    p.add_argument("--escenario", choices=list(ESCENARIOS), default="general", help="hospital a utilizar")
    p.add_argument("--todos", action="store_true", help="ejecuta todos los escenarios con sus inicios/metas por defecto")
    p.add_argument("--inicio", type=parsear_inicio, help="estado inicial: x,y,orientación")
    p.add_argument("--meta", type=parsear_meta, help="celda meta: x,y")
    p.add_argument("--csv", type=Path, help="exporta la tabla de resultados a un CSV")
    p.add_argument("--graficas", type=Path, help="carpeta donde guardar PNG con las rutas")
    return p


def ejecutar_escenario(esc: Escenario, inicio: Estado, meta: tuple[int, int], carpeta_graficas: Path | None):
    problema = ProblemaRuta(esc.mapa, inicio, meta)
    resultados = [a_estrella(problema), costo_uniforme(problema)]

    print(f"\n=== {esc.mapa.nombre} ===")
    print(f"Inicio: {inicio}   Meta: {meta}")
    print(dibujar_ascii(esc.mapa, inicio, meta, resultados[0]))
    for r in resultados:
        if r.exito:
            print(f"\n[{r.algoritmo}] {secuencia_acciones(r)}")
    if carpeta_graficas is not None:
        destino = carpeta_graficas / f"ruta_{esc.clave}.png"
        if guardar_png(esc.mapa, inicio, meta, resultados, destino):
            print(f"\nGráfica guardada en {destino}")
        else:
            print("\n(matplotlib no está instalado: se omite la gráfica)")
    return [(esc.mapa.nombre, r) for r in resultados]


def main(argv: list[str] | None = None) -> int:
    args = crear_parser().parse_args(argv)

    if args.listar:
        for esc in ESCENARIOS.values():
            print(f"{esc.clave:<11} {esc.mapa.nombre:<34} inicio={esc.inicio} meta={esc.meta}")
        return 0

    try:
        filas = []
        if args.todos:
            for esc in ESCENARIOS.values():
                filas += ejecutar_escenario(esc, esc.inicio, esc.meta, args.graficas)
        else:
            esc = obtener_escenario(args.escenario)
            filas += ejecutar_escenario(esc, args.inicio or esc.inicio, args.meta or esc.meta, args.graficas)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("\n" + tabla_texto(filas))
    if args.csv:
        exportar_csv(filas, args.csv)
        print(f"\nResultados exportados a {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())