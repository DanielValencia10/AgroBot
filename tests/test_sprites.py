"""
Archivo:       tests/test_sprites.py
Objetivo:      Verificar que gui/cargador_sprites.py carga todos los sprites de
               assets/sprites/ y que gui/animacion.py elige bien los cuadros.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_sprites
"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # sin ventana real
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame  # noqa: E402

from agrobot.gui import animacion  # noqa: E402
from agrobot.gui.cargador_sprites import (  # noqa: E402
    cargar_sprites,
    obtener_nombre_sprite_por_codigo,
)


class TestCargadorSprites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((64, 64))
        cls.sprites = cargar_sprites()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_cantidad_de_imagenes_por_grupo(self):
        s = self.sprites
        self.assertEqual(len(s.robot), 4 * 3)
        self.assertEqual(len(s.robot_giro), 4)
        self.assertEqual(len(s.avioneta), 8 * 3)
        self.assertEqual(len(s.cultivo), 9)

    def test_todas_son_de_64x64(self):
        s = self.sprites
        imagenes = [
            *s.robot.values(), *s.robot_giro.values(), *s.avioneta.values(), *s.cultivo,
            s.avioneta_base, s.deposito, s.casilla_libre, s.obstaculo,
        ]
        for imagen in imagenes:
            self.assertEqual(imagen.get_size(), (64, 64))

    def test_nombre_por_codigo_tiene_imagen(self):
        for codigo in range(6):
            self.assertIsNotNone(self.sprites.estatico(obtener_nombre_sprite_por_codigo(codigo)))
        with self.assertRaises(ValueError):
            obtener_nombre_sprite_por_codigo(6)

    def test_falta_un_archivo(self):
        with self.assertRaises(FileNotFoundError):
            cargar_sprites(Path(__file__).parent)


class TestAnimacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((64, 64))
        cls.sprites = cargar_sprites()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_camino_de_giro_toma_el_lado_corto(self):
        self.assertEqual(animacion.camino_giro("n", "e"), ["ne", "e"])
        self.assertEqual(animacion.camino_giro("n", "o"), ["no", "o"])
        self.assertEqual(animacion.camino_giro("e", "o"), ["se", "s", "so", "o"])

    def test_robot_en_reposo_usa_el_cuadro_0(self):
        robot = animacion.ActorRobot(self.sprites)
        self.assertIs(robot.imagen(), self.sprites.robot[("s", 0)])

    def test_robot_pasa_por_la_diagonal_al_girar(self):
        robot = animacion.ActorRobot(self.sprites, "n")
        robot.mirar("e")
        robot.update(animacion.MS_GIRO)
        self.assertIs(robot.imagen(), self.sprites.robot_giro["ne"])
        robot.update(animacion.MS_GIRO)
        self.assertEqual(robot.direccion, "e")

    def test_robot_camina_solo_si_se_mueve(self):
        robot = animacion.ActorRobot(self.sprites)
        robot.update(animacion.MS_PASO)
        self.assertIs(robot.imagen(), self.sprites.robot[("s", 0)])
        robot.moviendo = True
        self.assertIs(robot.imagen(), self.sprites.robot[("s", 1)])

    def test_planta_pasa_de_seca_a_tratada(self):
        planta = animacion.PlantaCultivo(self.sprites)
        self.assertFalse(planta.tratada)
        planta.regar()
        for _ in range(8):
            planta.update(animacion.MS_CRECIMIENTO)
        self.assertTrue(planta.tratada)
        self.assertIs(planta.imagen(), self.sprites.cultivo[8])


if __name__ == "__main__":
    unittest.main()
