"""
Archivo:       tests/test_arbol_exploracion.py
Objetivo:      Verificar gui/arbol_exploracion.py: la estructura del arbol, el calculo de
               alternativas y que el dibujo use la paleta del proyecto.
Responsabilidad:
    QUE VERIFICA:
        - agregar_hijos no mueve el nodo actual y no duplica hijos; avanzar_a_hijo mueve
          (y crea el hijo si falta); mover_a retrocede al padre, reutiliza o crea.
        - ruta_desde_raiz incluye todos los ancestros del nodo.
        - coordenadas_alternativas sobre Prueba1: desde el inicio ofrece los tres
          movimientos posibles, no ofrece volver al estado anterior, y en la meta no
          ofrece nada.
        - dibujar pinta el nodo actual en COLOR_LINO y la ruta en COLOR_OLIVA, y respeta
          el recorte (no dibuja fuera del area).
Importa de:
    - gui.arbol_exploracion, gui.estilo, busqueda.no_informada.amplitud,
      problema.agrobot_problema, archivos.lector_mundo.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_arbol_exploracion
"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pygame  # noqa: E402

from agrobot.archivos.lector_mundo import leer_mundo_desde_archivo  # noqa: E402
from agrobot.busqueda.no_informada.amplitud import buscar_amplitud  # noqa: E402
from agrobot.gui import estilo  # noqa: E402
from agrobot.gui.arbol_exploracion import (  # noqa: E402
    ArbolExploracion,
    coordenadas_alternativas,
)
from agrobot.problema.agrobot_problema import AgroBotProblema  # noqa: E402


class TestEstructura(unittest.TestCase):
    def test_agregar_hijos_no_mueve_ni_duplica(self):
        arbol = ArbolExploracion((4, 0))
        arbol.agregar_hijos([(3, 0), (5, 0)])
        arbol.agregar_hijos([(3, 0)])
        self.assertIs(arbol.actual, arbol.raiz)
        self.assertEqual([h.coordenada for h in arbol.raiz.hijos], [(3, 0), (5, 0)])

    def test_avanzar_a_hijo_existente_y_nuevo(self):
        arbol = ArbolExploracion((4, 0))
        arbol.agregar_hijos([(3, 0)])
        hijo = arbol.raiz.hijos[0]
        arbol.avanzar_a_hijo((3, 0))
        self.assertIs(arbol.actual, hijo)
        arbol.avanzar_a_hijo((2, 0))
        self.assertEqual(arbol.actual.coordenada, (2, 0))
        self.assertEqual(len(hijo.hijos), 1)

    def test_mover_a_retrocede_reutiliza_o_crea(self):
        arbol = ArbolExploracion((4, 0))
        arbol.mover_a((3, 0))
        arbol.mover_a((2, 0))
        arbol.mover_a((3, 0))  # vuelve al padre
        self.assertEqual(arbol.actual.coordenada, (3, 0))
        arbol.mover_a((2, 0))  # reutiliza el hijo ya creado
        self.assertEqual(len(arbol.actual.padre.hijos), 1)

    def test_ruta_desde_raiz(self):
        arbol = ArbolExploracion((4, 0))
        arbol.avanzar_a_hijo((3, 0))
        arbol.avanzar_a_hijo((2, 0))
        self.assertEqual({n.coordenada for n in arbol.actual.ruta_desde_raiz()},
                         {(4, 0), (3, 0), (2, 0)})

    def test_reiniciar(self):
        arbol = ArbolExploracion((4, 0))
        arbol.avanzar_a_hijo((3, 0))
        arbol.reiniciar((1, 1))
        self.assertEqual(arbol.raiz.coordenada, (1, 1))
        self.assertIs(arbol.actual, arbol.raiz)
        self.assertEqual(arbol.raiz.hijos, [])


class TestAlternativas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mundo = leer_mundo_desde_archivo(RAIZ / "mundos" / "Prueba1.txt")
        cls.problema = AgroBotProblema(mundo)
        cls.camino = list(buscar_amplitud(cls.problema).camino_de_estados)

    def test_desde_el_inicio_hay_tres_movimientos(self):
        self.assertEqual(coordenadas_alternativas(self.problema, self.camino, 0),
                         [(3, 0), (5, 0), (4, 1)])

    def test_no_ofrece_volver_al_estado_anterior(self):
        alternativas = coordenadas_alternativas(self.problema, self.camino, 1)
        self.assertNotIn(self.camino[0].posicion, alternativas)

    def test_en_la_meta_no_hay_alternativas(self):
        self.assertEqual(
            coordenadas_alternativas(self.problema, self.camino, len(self.camino) - 1), [])


class TestDibujo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.pantalla = pygame.display.set_mode((400, 400))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def colores_en(self, area):
        sub = self.pantalla.subsurface(area)
        return {tuple(sub.get_at((x, y)))[:3]
                for x in range(sub.get_width()) for y in range(sub.get_height())}

    def test_pinta_ruta_y_nodo_actual_con_la_paleta(self):
        arbol = ArbolExploracion((4, 0))
        arbol.agregar_hijos([(3, 0), (5, 0)])
        arbol.avanzar_a_hijo((3, 0))
        self.pantalla.fill((0, 0, 0))
        area = pygame.Rect(50, 50, 200, 300)
        arbol.dibujar(self.pantalla, area, ultimos_niveles=6)
        colores = self.colores_en(area)
        self.assertIn(estilo.COLOR_TARJETA, colores)
        self.assertIn(estilo.COLOR_LINO, colores)    # nodo actual
        self.assertIn(estilo.COLOR_OLIVA, colores)   # ruta

    def test_no_dibuja_fuera_del_area(self):
        arbol = ArbolExploracion((4, 0))
        for i in range(30):  # un arbol muy ancho y hondo
            arbol.agregar_hijos([(i, c) for c in range(8)])
            arbol.avanzar_a_hijo((i, 0))
        self.pantalla.fill((0, 0, 0))
        area = pygame.Rect(100, 100, 150, 150)
        arbol.dibujar(self.pantalla, area)
        self.assertEqual(self.colores_en(pygame.Rect(0, 0, 400, 90)), {(0, 0, 0)})
        self.assertEqual(self.colores_en(pygame.Rect(0, 260, 400, 140)), {(0, 0, 0)})
        self.assertEqual(self.colores_en(pygame.Rect(0, 0, 90, 400)), {(0, 0, 0)})
        self.assertEqual(self.colores_en(pygame.Rect(260, 0, 140, 400)), {(0, 0, 0)})


if __name__ == "__main__":
    unittest.main()
