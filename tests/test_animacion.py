"""
Archivo:       tests/test_animacion.py
Objetivo:      Verificar gui/animacion.py (PanelAnimacion) y gui/panel_reporte.py sin
               ventana real (driver "dummy"), avanzando el reloj a mano.
Responsabilidad:
    QUE VERIFICA:
        - PanelAnimacion reproduce toda la solucion de Prueba1: `paso` sube de uno en uno,
          termina en la meta y las plantas quedan tratadas.
        - Entre dos casillas la posicion dibujada se interpola, y el robot gira antes de
          caminar.
        - Pausa: no avanza; paso_siguiente recorre exactamente un movimiento y queda en
          pausa; reiniciar vuelve al principio; ajustar_velocidad respeta sus limites.
        - Una solucion que sube a la avioneta y la agota cambia de actor (robot ->
          avioneta -> robot).
        - Un Resultado sin solucion no rompe nada: queda en el estado inicial.
        - PanelReporte: metricas (costo solo si el Resultado lo trae), estado del robot,
          mensajes de estado y que no dibuje fuera de su area.
Importa de:
    - gui.animacion, gui.panel_reporte, gui.panel_mundo, gui.cargador_sprites,
      busqueda.resultado, busqueda.no_informada.amplitud, problema.*.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_animacion
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
from agrobot.busqueda.resultado import Resultado  # noqa: E402
from agrobot.gui import animacion, estilo  # noqa: E402
from agrobot.gui.cargador_sprites import cargar_sprites  # noqa: E402
from agrobot.gui.panel_mundo import PanelMundo  # noqa: E402
from agrobot.gui.panel_reporte import ALTO_RECOMENDADO, PanelReporte  # noqa: E402
from agrobot.modelo.estado import Estado  # noqa: E402
from agrobot.modelo.movimiento import Movimiento  # noqa: E402
from agrobot.problema.agrobot_problema import AgroBotProblema  # noqa: E402

PASO_DE_RELOJ = 16


class PruebaConAnimacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.pantalla = pygame.display.set_mode((1120, 760))
        cls.sprites = cargar_sprites()
        cls.mundo = leer_mundo_desde_archivo(RAIZ / "mundos" / "Prueba1.txt")
        cls.problema = AgroBotProblema(cls.mundo)
        cls.resultado = buscar_amplitud(cls.problema)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def nueva_animacion(self, resultado=None):
        panel = PanelMundo(self.mundo, self.sprites, origen=(40, 60))
        return PanelAnimacion(panel, self.sprites, resultado or self.resultado,
                              self.problema.estado_inicial())

    def avanzar(self, anim, milisegundos):
        for _ in range(milisegundos // PASO_DE_RELOJ):
            anim.update(PASO_DE_RELOJ)


PanelAnimacion = animacion.PanelAnimacion


class TestReproduccion(PruebaConAnimacion):
    def test_recorre_toda_la_solucion(self):
        anim = self.nueva_animacion()
        anterior = 0
        for _ in range(200_000 // PASO_DE_RELOJ):
            anim.update(PASO_DE_RELOJ)
            self.assertIn(anim.paso - anterior, (0, 1))  # llega casilla por casilla
            anterior = anim.paso
            anim.dibujar(self.pantalla)
            if anim.terminada and all(p.tratada for p in anim._plantas.values()):
                break
        self.assertTrue(anim.terminada)
        self.assertEqual(anim.paso, 30)
        self.assertTrue(self.problema.es_meta(anim.estado_actual))
        self.assertTrue(all(p.tratada for p in anim._plantas.values()))

    def test_gira_antes_de_caminar_y_la_posicion_se_interpola(self):
        anim = self.nueva_animacion()
        anim.update(PASO_DE_RELOJ)
        self.assertTrue(anim._actor.girando)
        self.assertFalse(anim._actor.moviendo)
        origen = anim.panel.rect_de_casilla(anim.estado_actual.posicion)
        self.assertEqual(anim._posicion_del_actor(), origen.topleft)

        while anim._actor.girando:
            anim.update(PASO_DE_RELOJ)
        anim.update(anim.ms_por_paso // 2)
        destino = anim.panel.rect_de_casilla(anim._estados[1].posicion)
        x, y = anim._posicion_del_actor()
        self.assertTrue(anim._actor.moviendo)
        self.assertEqual(x, origen.x)  # primer movimiento: hacia arriba
        self.assertLess(destino.y, y)
        self.assertLess(y, origen.y)

    def test_pausa_y_paso_siguiente(self):
        anim = self.nueva_animacion()
        anim.alternar_pausa()
        self.avanzar(anim, 3000)
        self.assertEqual(anim.paso, 0)
        anim.paso_siguiente()
        self.avanzar(anim, 3000)
        self.assertEqual(anim.paso, 1)
        self.assertTrue(anim.pausada)
        self.avanzar(anim, 3000)
        self.assertEqual(anim.paso, 1)
        anim.alternar_pausa()
        self.avanzar(anim, 3000)
        self.assertGreater(anim.paso, 1)

    def test_reiniciar(self):
        anim = self.nueva_animacion()
        self.avanzar(anim, 10_000)
        anim.reiniciar()
        self.assertEqual(anim.paso, 0)
        self.assertFalse(anim.pausada)
        self.assertEqual(anim.estado_actual, self.problema.estado_inicial())
        self.assertFalse(any(p.tratada for p in anim._plantas.values()))

    def test_velocidad_con_limites(self):
        anim = self.nueva_animacion()
        for _ in range(10):
            anim.ajustar_velocidad(2)
        self.assertEqual(anim.ms_por_paso, animacion.MS_POR_PASO_MIN)
        for _ in range(10):
            anim.ajustar_velocidad(0.5)
        self.assertEqual(anim.ms_por_paso, animacion.MS_POR_PASO_MAX)


class TestAvioneta(PruebaConAnimacion):
    def resultado_con_vuelo(self):
        """Estados armados a mano: sube a la avioneta en (0,6), vuela y se agota."""
        pendientes = frozenset(self.mundo.cultivos_secos)
        estados = [
            Estado(1, 6, 0, False, 30, pendientes),   # a pie, junto a la avioneta
            Estado(0, 6, 0, True, 30, pendientes),    # sube sin gastar combustible
            Estado(1, 6, 0, True, 1, pendientes),     # vuela
            Estado(1, 5, 0, False, 0, pendientes),    # se agota: baja a pie
        ]
        movimientos = (Movimiento.ARRIBA, Movimiento.ABAJO, Movimiento.IZQUIERDA)
        return Resultado(movimientos, 1, len(movimientos), 0.0, None, tuple(estados)), estados

    def test_cambia_de_actor_al_montarse_y_al_agotarse(self):
        resultado, estados = self.resultado_con_vuelo()
        panel = PanelMundo(self.mundo, self.sprites, origen=(40, 60))
        anim = PanelAnimacion(panel, self.sprites, resultado, estados[0])
        clases = []
        anterior = -1
        for _ in range(60_000 // PASO_DE_RELOJ):
            anim.update(PASO_DE_RELOJ)
            anim.dibujar(self.pantalla)
            if anim.paso != anterior:
                clases.append(type(anim._actor))
                anterior = anim.paso
            if anim.terminada:
                break
        self.assertEqual(clases, [animacion.ActorRobot, animacion.ActorAvioneta,
                                  animacion.ActorAvioneta, animacion.ActorRobot])


class TestSinSolucion(PruebaConAnimacion):
    def test_queda_en_el_estado_inicial(self):
        sin_solucion = Resultado((), 1, 0, 0.0, solucion_encontrada=False)
        anim = self.nueva_animacion(sin_solucion)
        self.assertEqual(anim.total_pasos, 0)
        self.assertTrue(anim.terminada)
        self.avanzar(anim, 1000)
        anim.paso_siguiente()
        anim.dibujar(self.pantalla)
        self.assertEqual(anim.estado_actual, self.problema.estado_inicial())


class TestReporte(PruebaConAnimacion):
    def test_metricas_sin_costo_para_amplitud(self):
        filas = dict(PanelReporte(self.resultado, "Amplitud").filas_de_busqueda())
        self.assertEqual(filas["Nodos expandidos"], "1563")
        self.assertEqual(filas["Profundidad"], "30")
        self.assertNotIn("Costo total", filas)

    def test_muestra_costo_cuando_el_resultado_lo_trae(self):
        con_costo = Resultado((), 10, 3, 0.5, costo_total=15.5)
        filas = dict(PanelReporte(con_costo, "A*").filas_de_busqueda())
        self.assertEqual(filas["Costo total"], "15.5")

    def test_filas_del_robot_y_mensajes(self):
        anim = self.nueva_animacion()
        reporte = PanelReporte(self.resultado, "Amplitud")
        filas = dict(reporte.filas_del_robot(anim))
        self.assertEqual(filas["Paso"], "0/30")
        self.assertEqual(filas["Posición"], "(4, 0)")
        self.assertEqual(filas["Fertilizante"], "0/2")
        self.assertEqual(filas["Combustible"], "30/30")
        self.assertEqual(filas["Cultivos secos"], "3")
        self.assertEqual(filas["En avioneta"], "No")

        self.assertEqual(reporte.mensaje(anim)[0], "REPRODUCIENDO")
        anim.alternar_pausa()
        self.assertEqual(reporte.mensaje(anim)[0], "PAUSADO")
        self.avanzar(anim, 1000)
        anim.reiniciar()
        self.avanzar(anim, 200_000)
        self.assertEqual(reporte.mensaje(anim), ("META ALCANZADA", estilo.COLOR_LINO))
        sin = PanelReporte(Resultado((), 1, 0, 0.0, solucion_encontrada=False), "Amplitud")
        self.assertEqual(sin.mensaje(), ("SIN SOLUCIÓN", estilo.COLOR_ALERTA))

    def test_no_dibuja_fuera_de_su_area(self):
        anim = self.nueva_animacion()
        self.pantalla.fill((0, 0, 0))
        area = pygame.Rect(300, 100, 320, ALTO_RECOMENDADO)
        PanelReporte(self.resultado, "Amplitud").dibujar(self.pantalla, area, anim)
        marco = area.inflate(2, 2)
        for zona in (pygame.Rect(0, 0, 1120, marco.top), pygame.Rect(0, marco.bottom, 1120, 100),
                     pygame.Rect(0, 0, marco.left, 760), pygame.Rect(marco.right, 0, 400, 760)):
            sub = self.pantalla.subsurface(zona)
            colores = {tuple(sub.get_at((x, y)))[:3]
                       for x in range(0, sub.get_width(), 3) for y in range(0, sub.get_height(), 3)}
            self.assertEqual(colores, {(0, 0, 0)})
        self.assertNotEqual(tuple(self.pantalla.get_at((310, 110)))[:3], (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
