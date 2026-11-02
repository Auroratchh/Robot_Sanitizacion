from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from hospital_robot import (
    ESCENARIOS,
    Estado,
    Orientacion,
    ProblemaRuta,
    a_estrella,
    costo_uniforme,
)
from hospital_robot.busqueda import Resultado
from hospital_robot.mapa import Mapa

FRONTEND = Path(__file__).parent / "frontend"

app = FastAPI(title="Robot de sanitización hospitalaria")

class InicioIn(BaseModel):
    x: int
    y: int
    orientacion: str

class MetaIn(BaseModel):
    x: int
    y: int

class RutaIn(BaseModel):
    mapa: list[str]
    inicio: InicioIn
    meta: MetaIn

def _resultado_a_dict(r: Resultado) -> dict:
    return {
        "algoritmo": r.algoritmo,
        "exito": r.exito,
        "costo": r.costo,
        "expandidos": r.nodos_expandidos,
        "tiempo_ms": r.tiempo_ms,
        "giros": r.giros,
        "reversas": r.reversas,
        "acciones": [a.value for a in r.acciones],
        "ruta": [{"x": e.x, "y": e.y, "o": e.orientacion.letra} for e in r.estados],
    }

@app.get("/api/escenarios")
def listar_escenarios() -> list[dict]:
    return [
        {
            "clave": esc.clave,
            "nombre": esc.mapa.nombre,
            "descripcion": esc.descripcion,
            "mapa": list(esc.mapa.filas),
            "inicio": {"x": esc.inicio.x, "y": esc.inicio.y, "o": esc.inicio.orientacion.letra},
            "meta": {"x": esc.meta[0], "y": esc.meta[1]},
        }
        for esc in ESCENARIOS.values()
    ]

@app.post("/api/ruta")
def calcular_ruta(datos: RutaIn) -> list[dict]:
    try:
        mapa = Mapa("Personalizado", tuple(f.strip() for f in datos.mapa if f.strip()))
        inicio = Estado(datos.inicio.x, datos.inicio.y, Orientacion.desde_texto(datos.inicio.orientacion))
        problema = ProblemaRuta(mapa, inicio, (datos.meta.x, datos.meta.y))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return [_resultado_a_dict(a_estrella(problema)), _resultado_a_dict(costo_uniforme(problema))]


app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")