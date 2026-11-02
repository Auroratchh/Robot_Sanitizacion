const TAM = 40;
const MARGEN = 24;
const COLORES = { ".": "white", "~": "orange", "#": "gray" };
const FLECHAS = { N: "▲", E: "▶", S: "▼", O: "◀" };

const lienzo = document.getElementById("lienzo");
const ctx = lienzo.getContext("2d");
let escenarios = [];
let mapa = [];

function leer(id) {
  return parseInt(document.getElementById(id).value, 10) || 0;
}

function dibujar(ruta) {
  const alto = mapa.length;
  const ancho = mapa[0].length;
  lienzo.width = MARGEN + ancho * TAM;
  lienzo.height = alto * TAM + MARGEN;

  const px = (x) => MARGEN + x * TAM;
  const py = (y) => (alto - 1 - y) * TAM;

  ctx.strokeStyle = "black";
  for (let y = 0; y < alto; y++) {
    for (let x = 0; x < ancho; x++) {
      ctx.fillStyle = COLORES[mapa[alto - 1 - y][x]];
      ctx.fillRect(px(x), py(y), TAM, TAM);
      ctx.strokeRect(px(x), py(y), TAM, TAM);
    }
  }

  ctx.fillStyle = "#37474f";
  ctx.font = "13px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let x = 0; x < ancho; x++) ctx.fillText(x, px(x) + TAM / 2, alto * TAM + MARGEN / 2);
  for (let y = 0; y < alto; y++) ctx.fillText(y, MARGEN / 2, py(y) + TAM / 2);

  if (ruta) {
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ruta.forEach((p, i) => {
      const cx = px(p.x) + TAM / 2;
      const cy = py(p.y) + TAM / 2;
      if (i) ctx.lineTo(cx, cy);
      else ctx.moveTo(cx, cy);
    });
    ctx.stroke();
    ctx.lineWidth = 1;
  }

  ctx.fillStyle = "green";
  ctx.fillRect(px(leer("ix")) + 8, py(leer("iy")) + 8, TAM - 16, TAM - 16);
  ctx.fillStyle = "white";
  ctx.fillText(
    FLECHAS[document.getElementById("io").value],
    px(leer("ix")) + TAM / 2,
    py(leer("iy")) + TAM / 2
  );
  ctx.fillStyle = "red";
  ctx.fillRect(px(leer("mx")) + 8, py(leer("my")) + 8, TAM - 16, TAM - 16);
}

function limpiarResultados() {
  document.getElementById("cuerpo").innerHTML = "";
  document.getElementById("secuencia").textContent = "";
  document.getElementById("mensaje").textContent = "";
  dibujar();
}

function cargarEscenario() {
  const esc = escenarios[document.getElementById("escenario").value];
  mapa = esc.mapa;
  document.getElementById("ix").value = esc.inicio.x;
  document.getElementById("iy").value = esc.inicio.y;
  document.getElementById("io").value = esc.inicio.o;
  document.getElementById("mx").value = esc.meta.x;
  document.getElementById("my").value = esc.meta.y;
  limpiarResultados();
}

function agrupar(acciones) {
  const grupos = [];
  acciones.forEach((a) => {
    const ultimo = grupos[grupos.length - 1];
    if (ultimo && ultimo.nombre === a) ultimo.n++;
    else grupos.push({ nombre: a, n: 1 });
  });
  return grupos.map((g) => (g.n > 1 ? g.nombre + " x" + g.n : g.nombre)).join(", ");
}

async function ejecutar() {
  const datos = {
    mapa: mapa,
    inicio: { x: leer("ix"), y: leer("iy"), orientacion: document.getElementById("io").value },
    meta: { x: leer("mx"), y: leer("my") },
  };
  const respuesta = await fetch("/api/ruta", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  const resultado = await respuesta.json();

  if (!respuesta.ok) {
    document.getElementById("mensaje").textContent = resultado.detail;
    return;
  }

  document.getElementById("mensaje").textContent = "";
  let filas = "";
  let texto = "";
  resultado.forEach((r) => {
    filas += `<tr><td>${r.algoritmo}</td><td>${r.exito ? r.costo : "sin ruta"}</td><td>${r.expandidos}</td><td>${r.tiempo_ms.toFixed(3)}</td><td>${r.giros}</td><td>${r.reversas}</td></tr>`;
    texto += `[${r.algoritmo}] ${r.exito ? agrupar(r.acciones) : "No existe ruta"}\n`;
  });
  document.getElementById("cuerpo").innerHTML = filas;
  document.getElementById("secuencia").textContent = texto;
  dibujar(resultado[0].exito ? resultado[0].ruta : null);
}

async function iniciar() {
  const respuesta = await fetch("/api/escenarios");
  escenarios = await respuesta.json();
  const selector = document.getElementById("escenario");
  escenarios.forEach((esc, i) => selector.add(new Option(esc.nombre, i)));
  selector.addEventListener("change", cargarEscenario);
  ["ix", "iy", "io", "mx", "my"].forEach((id) =>
    document.getElementById(id).addEventListener("input", limpiarResultados)
  );
  document.getElementById("ejecutar").addEventListener("click", ejecutar);
  cargarEscenario();
}

iniciar();