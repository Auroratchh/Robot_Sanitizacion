import unittest

from hospital_robot import (
    ESCENARIOS,
    CostosConfig,
    Estado,
    Orientacion,
    ProblemaRuta,
    a_estrella,
    costo_uniforme,
)
from hospital_robot.mapa import Mapa
from hospital_robot.modelos import Accion


class PruebasOrientacion(unittest.TestCase):
    def test_giros_son_inversos(self):
        for o in Orientacion:
            self.assertEqual(o.girar_derecha().girar_izquierda(), o)

    def test_cuatro_giros_regresan(self):
        o = Orientacion.NORTE
        for _ in range(4):
            o = o.girar_derecha()
        self.assertEqual(o, Orientacion.NORTE)

    def test_desde_texto(self):
        self.assertEqual(Orientacion.desde_texto("n"), Orientacion.NORTE)
        self.assertEqual(Orientacion.desde_texto("Oeste"), Orientacion.OESTE)
        with self.assertRaises(ValueError):
            Orientacion.desde_texto("x")


class PruebasProblema(unittest.TestCase):
    def setUp(self):
        self.mapa = Mapa.desde_texto("pasillo", "...\n.~.\n...")

    def test_ejemplo_de_la_propuesta(self):
        p = ProblemaRuta(self.mapa, Estado(0, 0, Orientacion.NORTE), (2, 2))
        sucesores = {a: (s, c) for a, s, c in p.sucesores(Estado(0, 0, Orientacion.NORTE))}
        self.assertEqual(sucesores[Accion.AVANZAR], (Estado(0, 1, Orientacion.NORTE), 1))
        self.assertNotIn(Accion.RETROCEDER, sucesores)

    def test_avanzar_a_zona_congestionada_cuesta_3(self):
        p = ProblemaRuta(self.mapa, Estado(1, 0, Orientacion.NORTE), (2, 2))
        costo = next(c for a, _, c in p.sucesores(p.estado_inicial) if a == Accion.AVANZAR)
        self.assertEqual(costo, 3)

    def test_inicio_o_meta_invalidos(self):
        mapa = Mapa.desde_texto("m", ".#.")
        with self.assertRaises(ValueError):
            ProblemaRuta(mapa, Estado(1, 0, Orientacion.ESTE), (2, 0))
        with self.assertRaises(ValueError):
            ProblemaRuta(mapa, Estado(0, 0, Orientacion.ESTE), (5, 0))


class PruebasBusqueda(unittest.TestCase):
    def test_a_estrella_y_ucs_dan_el_mismo_costo_optimo(self):
        for esc in ESCENARIOS.values():
            with self.subTest(esc.clave):
                p = ProblemaRuta(esc.mapa, esc.inicio, esc.meta)
                a, u = a_estrella(p), costo_uniforme(p)
                self.assertTrue(a.exito and u.exito)
                self.assertEqual(a.costo, u.costo)
                self.assertLessEqual(a.nodos_expandidos, u.nodos_expandidos)

    def test_costo_de_la_ruta_coincide_con_g(self):
        esc = ESCENARIOS["general"]
        p = ProblemaRuta(esc.mapa, esc.inicio, esc.meta)
        r = a_estrella(p)
        total = 0
        for anterior, accion, siguiente in zip(r.estados, r.acciones, r.estados[1:]):
            total += next(c for a, s, c in p.sucesores(anterior) if a == accion and s == siguiente)
        self.assertEqual(total, r.costo)

    def test_cambiar_inicio_y_meta(self):
        esc = ESCENARIOS["clinica"]
        r1 = a_estrella(ProblemaRuta(esc.mapa, Estado(0, 0, Orientacion.ESTE), (11, 5)))
        r2 = a_estrella(ProblemaRuta(esc.mapa, Estado(11, 0, Orientacion.OESTE), (0, 3)))
        self.assertTrue(r1.exito and r2.exito)
        self.assertNotEqual(r1.costo, r2.costo)

    def test_inicio_en_la_meta(self):
        mapa = Mapa.desde_texto("m", "...")
        r = a_estrella(ProblemaRuta(mapa, Estado(1, 0, Orientacion.ESTE), (1, 0)))
        self.assertTrue(r.exito)
        self.assertEqual(r.costo, 0)
        self.assertEqual(r.acciones, [])

    def test_meta_inalcanzable(self):
        mapa = Mapa.desde_texto("m", "..#.")
        r = a_estrella(ProblemaRuta(mapa, Estado(0, 0, Orientacion.ESTE), (3, 0)))
        self.assertFalse(r.exito)

    def test_retroceder_solo_conviene_si_girar_es_caro(self):
        mapa = Mapa.desde_texto("m", "....")
        inicio = Estado(3, 0, Orientacion.ESTE)
        normal = a_estrella(ProblemaRuta(mapa, inicio, (2, 0)))
        girar_caro = a_estrella(ProblemaRuta(mapa, inicio, (2, 0), CostosConfig(giro=10)))
        self.assertEqual(normal.reversas, 0)
        self.assertEqual(girar_caro.reversas, 1)


if __name__ == "__main__":
    unittest.main()