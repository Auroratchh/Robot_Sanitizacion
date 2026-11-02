# Robot de sanitización hospitalaria

Planificación de rutas de menor costo para un robot de desinfección con lámparas UV-C que se mueve en una planta hospitalaria representada como una cuadrícula discreta. El robot tiene orientación (Norte, Este, Sur, Oeste) y debe encontrar la secuencia de acciones de menor costo acumulado desde su estación de carga hasta la sala meta.

Se comparan dos algoritmos de búsqueda:

- **A\*** con heurística Manhattan.
- **Costo Uniforme (UCS)**, equivalente a A\* con h(n) = 0.

## Modelado del problema

### Estado

`((x, y), Orientación)`. El origen `(0, 0)` es la esquina inferior izquierda y `y` crece hacia arriba.

### Acciones y costos

| Acción | Efecto | Costo |
|---|---|---|
| Avanzar | Mueve una celda hacia donde mira el robot | 1 en pasillo libre, 3 en zona congestionada (según la celda a la que entra) |
| Girar Izq / Der | Gira 90° sin cambiar de celda | 1 |
| Retroceder | Mueve una celda hacia atrás sin girar | 4 |

Los muros no son transitables, y tampoco lo es salir del mapa.

### Estado inicial y meta

- Estado inicial: posición y orientación de la estación de carga.
- Meta: una celda `(x, y)` con **cualquier orientación**.

### Función de costo g(n)

g(n) es el costo acumulado del camino desde el estado inicial hasta el nodo n:

```
g(raíz) = 0
g(hijo) = g(padre) + costo(acción)
```

Es decir, la suma de los costos de todas las acciones ejecutadas hasta llegar a n. Es la cantidad que minimizan tanto UCS como A\*.

### Heurística h(n)

```
h(n) = (|x_meta - x| + |y_meta - y|) * c_min
```

con `c_min = min(pasillo, congestionado, retroceso) = 1`.

Es **admisible** (h(n) ≤ h\*(n)) porque cada acción que acerca al robot a la meta mueve como máximo una celda y cuesta al menos `c_min`, mientras que los giros no acercan y cuestan 1. Nunca sobreestima el costo real, así que A\* devuelve una ruta óptima. También es **consistente**, por lo que no hace falta reabrir nodos.

### Evaluación

A\* se evalúa con f(n) = g(n) + h(n), UCS con f(n) = g(n). Para cada ejecución se reporta:

- Costo total de la ruta
- Nodos expandidos
- Tiempo de ejecución (ms)
- Cantidad de giros
- Cantidad de reversas

## Escenarios

Todos los hospitales son de 10x10 y están definidos en `hospital_robot/escenarios.py` con los símbolos `.` pasillo, `~` zona congestionada y `#` muro.

| Clave | Hospital | Inicio | Meta |
|---|---|---|---|
| `general` | Hospital General | (0, 0) Norte | (3, 7) |
| `clinica` | Clínica de Especialidades | (0, 0) Este | (9, 5) |
| `pediatrico` | Hospital Pediátrico | (0, 0) Este | (7, 7) |

### Resultados con los valores por defecto

| Hospital | Algoritmo | Costo | Expandidos | Giros | Reversas |
|---|---|---|---|---|---|
| General | A\* | 13 | 62 | 3 | 0 |
| General | UCS | 13 | 160 | 3 | 0 |
| Clínica | A\* | 15 | 15 | 1 | 0 |
| Clínica | UCS | 15 | 192 | 1 | 0 |
| Pediátrico | A\* | 19 | 130 | 3 | 0 |
| Pediátrico | UCS | 19 | 244 | 3 | 0 |

Ambos algoritmos encuentran el mismo costo óptimo, A\* expande menos nodos gracias a la heurística.

## Estructura

```
.
├── api.py                  API FastAPI y servidor del frontend
├── main.py                 Interfaz de línea de comandos
├── requirements.txt
├── tests/
│   └── test_busqueda.py    Pruebas unitarias
├── hospital_robot/
│   ├── __init__.py
│   ├── busqueda.py         A* y costo uniforme
│   ├── escenarios.py       Hospitales, inicio y meta por defecto
│   ├── heuristicas.py      Heurística nula y Manhattan
│   ├── mapa.py             Mapa de la cuadrícula
│   ├── modelos.py          Estado, Orientación y Acción
│   ├── problema.py         Sucesores y costos
│   ├── reporte.py          Tabla, CSV y secuencia de acciones
│   └── visualizacion.py    Mapa ASCII y gráficas PNG
└── frontend/
    ├── index.html
    ├── app.js
    └── style.css
```

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows se activa con `.venv\Scripts\activate`.

## Uso

### Interfaz web

```bash
uvicorn api:app --reload
```

Abrir `http://127.0.0.1:8000`. Se elige el hospital, se ajustan el estado inicial, la orientación y la meta, y se presiona **Ejecutar búsqueda**. Se muestran la ruta sobre el mapa, la tabla comparativa y la secuencia de acciones de cada algoritmo.

### Línea de comandos

```bash
python main.py --listar
python main.py --escenario clinica
python main.py --escenario general --inicio 0,0,N --meta 9,9
python main.py --todos --csv resultados/tabla.csv --graficas graficas
```

| Opción | Descripción |
|---|---|
| `--listar` | Muestra los escenarios disponibles |
| `--escenario` | `general`, `clinica` o `pediatrico` |
| `--inicio x,y,orientación` | Estado inicial (orientación: N, E, S u O) |
| `--meta x,y` | Celda meta |
| `--todos` | Ejecuta los tres escenarios con sus valores por defecto |
| `--csv ruta` | Exporta la tabla de resultados |
| `--graficas carpeta` | Guarda un PNG por escenario (requiere matplotlib) |

### Pruebas

```bash
python -m unittest discover -s tests -t .
```

### API

- `GET /api/escenarios`: lista los hospitales con su mapa, inicio y meta por defecto.
- `POST /api/ruta`: recibe `mapa`, `inicio` y `meta`, y devuelve los resultados de A\* y UCS.