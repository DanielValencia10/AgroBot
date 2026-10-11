"""
Archivo:       tests/test_panel_mundo.py
Objetivo:      Verificar gui/panel_mundo.py dibujando sobre una ventana "dummy" (sin
               pantalla real) y comparando lo que queda en cada casilla.
Responsabilidad:
    QUE VERIFICA:
        - La geometria: la cuadricula mide 640 x 640 y cada casilla 64 x 64 (o el doble
          con escala 2); una escala que no sea entera se rechaza.
        - Que en el estado inicial se vean los cultivos secos, el deposito, la avioneta
          y el robot mirando hacia abajo.
        - Que un cultivo fuera de P se dibuje como tratado.
        - Que la avioneta desaparezca de su casilla cuando el robot ya se subio o se
          agoto, y que el robot se dibuje como avioneta mientras va montado.
Importa de:
    - gui.panel_mundo, gui.cargador_sprites, archivos.lector_mundo, modelo.estado.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_panel_mundo
"""
import os
import sys
import unittest
from dataclasses import replace
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pygame  # noqa: E402

from agrobot.archivos.lector_mundo import leer_mundo_desde_archivo  # noqa: E402
from agrobot.gui.cargador_sprites import cargar_sprites  # noqa: E402
from agrobot.gui.panel_mundo import PanelMundo  # noqa: E402
from agrobot.modelo.estado import construir_estado_inicial  # noqa: E402


def igual(superficie_a, superficie_b) -> bool:
    return pygame.image.tobytes(superficie_a, "RGBA") == pygame.image.tobytes(superficie_b, "RGBA")


class TestPanelMundo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.pantalla = pygame.display.set_mode((800, 800))
        cls.sprites = cargar_sprites()
        cls.mundo = leer_mundo_desde_archivo(RAIZ / "mundos" / "Prueba1.txt")
        cls.inicial = construir_estado_inicial(cls.mundo)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.panel = PanelMundo(self.mundo, self.sprites, origen=(10, 20))
        self.pantalla.fill((0, 0, 0))

    def casilla(self, coordenada):
        return self.pantalla.subsurface(self.panel.rect_de_casilla(coordenada)).copy()

    def esperado(self, *imagenes):
        """Lo que queda al apilar sprites sobre la tierra (como en el panel)."""
        resultado = pygame.Surface((64, 64), pygame.SRCALPHA)
        resultado.blit(self.sprites.casilla_libre, (0, 0))
        for imagen in imagenes:
            resultado.blit(imagen, (0, 0))
        return resultado

    def test_geometria(self):
        self.assertEqual(self.panel.rect, pygame.Rect(10, 20, 640, 640))
        self.assertEqual(self.panel.rect_de_casilla((2, 3)), pygame.Rect(10 + 3 * 64, 20 + 2 * 64, 64, 64))
        doble = PanelMundo(self.mundo, self.sprites, escala=2)
        self.assertEqual(doble.rect.size, (1280, 1280))
        for escala in (0, 1.5):
            with self.assertRaises(ValueError):
                PanelMundo(self.mundo, self.sprites, escala=escala)

    def test_estado_inicial(self):
        self.panel.dibujar(self.pantalla)
        self.assertTrue(igual(self.casilla((4, 3)), self.esperado(self.sprites.cultivo[0])))
        self.assertTrue(igual(self.casilla((0, 6)), self.esperado(self.sprites.avioneta_base)))
        self.assertTrue(igual(self.casilla((0, 2)), self.esperado(self.sprites.deposito)))
        self.assertTrue(igual(self.casilla((4, 0)), self.esperado(self.sprites.robot[("s", 0)])))
        self.assertTrue(igual(self.casilla((0, 0)), self.sprites.obstaculo))

    def test_cultivo_tratado(self):
        tratado = replace(self.inicial, pendientes=self.inicial.pendientes - {(4, 3)})
        self.panel.dibujar(self.pantalla, tratado)
        self.assertTrue(igual(self.casilla((4, 3)), self.esperado(self.sprites.cultivo[-1])))
        self.assertTrue(igual(self.casilla((5, 3)), self.esperado(self.sprites.cultivo[0])))

    def test_la_avioneta_se_va_con_el_robot_y_no_vuelve_al_agotarse(self):
        montado = replace(self.inicial, fila=3, columna=3, en_avioneta=True, combustible=20)
        self.panel.dibujar(self.pantalla, montado, "e")
        self.assertTrue(igual(self.casilla((0, 6)), self.esperado()))
        self.assertTrue(igual(self.casilla((3, 3)), self.esperado(self.sprites.avioneta[("e", 0)])))

        self.pantalla.fill((0, 0, 0))
        agotada = replace(self.inicial, fila=3, columna=3, combustible=0)
        self.panel.dibujar(self.pantalla, agotada, "n")
        self.assertTrue(igual(self.casilla((0, 6)), self.esperado()))
        self.assertTrue(igual(self.casilla((3, 3)), self.esperado(self.sprites.robot[("n", 0)])))


if __name__ == "__main__":
    unittest.main()
