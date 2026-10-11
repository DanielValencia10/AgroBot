"""
Archivo:       tests/test_flujo.py
Objetivo:      Verificar la integracion de la aplicacion: panel_control (seleccion ->
               busqueda), ventana_principal, pantalla_aviso y el flujo de main.py.
Responsabilidad:
    QUE VERIFICA:
        - ejecutar_seleccion resuelve Prueba1 con Amplitud, rechaza un algoritmo sin
          implementar (AlgoritmoNoDisponible) y un mundo invalido (ErrorMundo).
        - VentanaPrincipal: Espacio pausa, flecha derecha da un paso, R reinicia (y
          rehace el arbol), Esc vuelve, cerrar la ventana sale, los botones del mouse
          hacen lo mismo, y el arbol crece a medida que el robot llega a casillas.
        - pantalla_aviso: Enter, Esc o el boton cierran; cerrar la ventana sale.
        - main.punto_de_entrada (con las pantallas simuladas): selecciona, ejecuta, vuelve
          a la seleccion saltando la bienvenida, muestra un aviso ante un error y termina
          cuando se cierra la ventana.
Importa de:
    - gui.panel_control, gui.ventana_principal, gui.pantalla_aviso, main.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_flujo
"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pygame  # noqa: E402

from agrobot import main  # noqa: E402
from agrobot.archivos.lector_mundo import ErrorMundo  # noqa: E402
from agrobot.gui import pantalla_aviso, ventana_principal  # noqa: E402
from agrobot.gui.catalogo_algoritmos import Algoritmo  # noqa: E402
from agrobot.gui.panel_control import AlgoritmoNoDisponible, ejecutar_seleccion  # noqa: E402
from agrobot.gui.pantalla_seleccion import SeleccionInicio  # noqa: E402
from agrobot.gui.ventana_principal import VentanaPrincipal  # noqa: E402

PRUEBA1 = RAIZ / "mundos" / "Prueba1.txt"


def tecla(clave):
    return pygame.event.Event(pygame.KEYDOWN, key=clave)


def clic(rect):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)


class TestPanelControl(unittest.TestCase):
    def test_amplitud_sobre_prueba1(self):
        ejecucion = ejecutar_seleccion(SeleccionInicio(PRUEBA1, Algoritmo.AMPLITUD))
        self.assertEqual(ejecucion.algoritmo, Algoritmo.AMPLITUD)
        self.assertEqual(ejecucion.resultado.profundidad_de_la_solucion, 30)
        self.assertTrue(ejecucion.problema.es_meta(ejecucion.resultado.camino_de_estados[-1]))

    def test_algoritmo_sin_implementar(self):
        with self.assertRaises(AlgoritmoNoDisponible) as contexto:
            ejecutar_seleccion(SeleccionInicio(PRUEBA1, Algoritmo.A_ESTRELLA))
        self.assertEqual(contexto.exception.algoritmo, Algoritmo.A_ESTRELLA)
        self.assertIsInstance(contexto.exception, NotImplementedError)

    def test_mundo_invalido(self):
        with self.assertRaises(ErrorMundo):
            ejecutar_seleccion(SeleccionInicio(RAIZ / "mundos" / "no_existe.txt", Algoritmo.AMPLITUD))


class PruebaConVentana(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.pantalla = pygame.display.set_mode((1120, 760))
        cls.ejecucion = ejecutar_seleccion(SeleccionInicio(PRUEBA1, Algoritmo.AMPLITUD))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def nueva_ventana(self):
        return VentanaPrincipal(self.pantalla, self.ejecucion)

    def avanzar(self, ventana, milisegundos):
        for _ in range(milisegundos // 16):
            ventana.actualizar(16)


class TestVentanaPrincipal(PruebaConVentana):
    def test_teclado(self):
        ventana = self.nueva_ventana()
        self.assertIsNone(ventana.procesar_evento(tecla(pygame.K_SPACE)))
        self.assertTrue(ventana.animacion.pausada)
        ventana.procesar_evento(tecla(pygame.K_SPACE))
        self.assertFalse(ventana.animacion.pausada)
        antes = ventana.animacion.ms_por_paso
        ventana.procesar_evento(tecla(pygame.K_UP))
        self.assertLess(ventana.animacion.ms_por_paso, antes)
        ventana.procesar_evento(tecla(pygame.K_DOWN))
        ventana.procesar_evento(tecla(pygame.K_DOWN))
        self.assertGreater(ventana.animacion.ms_por_paso, antes)
        self.assertEqual(ventana.procesar_evento(tecla(pygame.K_ESCAPE)), ventana_principal.VOLVER)
        self.assertEqual(ventana.procesar_evento(pygame.event.Event(pygame.QUIT)),
                         ventana_principal.SALIR)

    def test_paso_siguiente_y_reiniciar(self):
        ventana = self.nueva_ventana()
        ventana.procesar_evento(tecla(pygame.K_RIGHT))
        self.avanzar(ventana, 4000)
        self.assertEqual(ventana.animacion.paso, 1)
        self.assertTrue(ventana.animacion.pausada)
        ventana.procesar_evento(tecla(pygame.K_r))
        self.assertEqual(ventana.animacion.paso, 0)
        self.assertEqual(ventana.arbol.actual, ventana.arbol.raiz)

    def test_el_arbol_crece_con_el_robot(self):
        ventana = self.nueva_ventana()
        self.avanzar(ventana, 8000)
        paso = ventana.animacion.paso
        self.assertGreater(paso, 3)
        recorrido = [ventana.arbol.actual]
        while recorrido[-1].padre is not None:
            recorrido.append(recorrido[-1].padre)
        self.assertEqual(len(recorrido), paso + 1)  # raiz + un nodo por paso
        self.assertEqual(ventana.arbol.actual.coordenada,
                         ventana.animacion.estado_actual.posicion)

    def test_botones_del_mouse(self):
        ventana = self.nueva_ventana()
        ventana.procesar_evento(clic(ventana_principal.BOTON_PAUSA))
        self.assertTrue(ventana.animacion.pausada)
        ventana.procesar_evento(clic(ventana_principal.BOTON_PASO))
        self.avanzar(ventana, 4000)
        self.assertEqual(ventana.animacion.paso, 1)
        ventana.procesar_evento(clic(ventana_principal.BOTON_REINICIAR))
        self.assertEqual(ventana.animacion.paso, 0)
        self.assertEqual(ventana.procesar_evento(clic(ventana_principal.BOTON_INICIO)),
                         ventana_principal.VOLVER)

    def test_los_botones_no_se_superponen_ni_salen_de_la_ventana(self):
        botones = [ventana_principal.BOTON_PAUSA, ventana_principal.BOTON_PASO,
                   ventana_principal.BOTON_REINICIAR, ventana_principal.BOTON_INICIO]
        pantalla = self.pantalla.get_rect()
        for i, a in enumerate(botones):
            self.assertTrue(pantalla.contains(a))
            for b in botones[i + 1:]:
                self.assertFalse(a.colliderect(b))
        self.assertFalse(ventana_principal.AREA_ARBOL.colliderect(ventana_principal.BOTON_PAUSA))
        self.assertFalse(ventana_principal.AREA_REPORTE.colliderect(ventana_principal.AREA_ARBOL))

    def test_dibuja_completo_hasta_el_final(self):
        ventana = self.nueva_ventana()
        for _ in range(200_000 // 16):
            ventana.actualizar(16)
            if ventana.animacion.terminada:
                break
        ventana.dibujar(self.pantalla)
        self.assertTrue(ventana.animacion.terminada)


class TestPantallaAviso(unittest.TestCase):
    def test_eventos(self):
        self.assertEqual(pantalla_aviso.procesar_evento(tecla(pygame.K_RETURN)), "cerrar")
        self.assertEqual(pantalla_aviso.procesar_evento(tecla(pygame.K_ESCAPE)), "cerrar")
        self.assertEqual(pantalla_aviso.procesar_evento(clic(pantalla_aviso.BOTON)), "cerrar")
        self.assertEqual(pantalla_aviso.procesar_evento(pygame.event.Event(pygame.QUIT)), "salir")
        self.assertIsNone(pantalla_aviso.procesar_evento(tecla(pygame.K_a)))
        self.assertIsNone(pantalla_aviso.procesar_evento(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5))))


class TestFlujoDeMain(unittest.TestCase):
    """main.punto_de_entrada con las pantallas bloqueantes reemplazadas por simulaciones."""

    def correr(self, selecciones, ventanas=(), avisos=(), ejecutar=None):
        secuencia = iter(selecciones)
        llamadas = []

        def inicio(pantalla, carpeta, saltar_bienvenida=False):
            llamadas.append(saltar_bienvenida)
            return next(secuencia)

        resultados_ventana = iter(ventanas)
        resultados_aviso = iter(avisos)
        avisos_mostrados = []

        def aviso(pantalla, titulo, mensaje):
            avisos_mostrados.append((titulo, mensaje))
            return next(resultados_aviso)

        class VentanaFalsa:
            def __init__(self, pantalla, ejecucion):
                pass

            def ejecutar(self, pantalla):
                return next(resultados_ventana)

        with mock.patch("agrobot.gui.pantalla_inicio.crear_ventana", return_value=object()), \
                mock.patch("agrobot.gui.pantalla_inicio.ejecutar_inicio", inicio), \
                mock.patch("agrobot.gui.pantalla_aviso.mostrar_aviso", aviso), \
                mock.patch("agrobot.gui.ventana_principal.VentanaPrincipal", VentanaFalsa), \
                mock.patch("agrobot.gui.panel_control.ejecutar_seleccion",
                           ejecutar or (lambda seleccion: object())), \
                mock.patch("pygame.quit"):
            codigo = main.punto_de_entrada()
        return codigo, llamadas, avisos_mostrados

    def test_cerrar_en_la_primera_pantalla_termina(self):
        codigo, llamadas, _ = self.correr([None])
        self.assertEqual((codigo, llamadas), (0, [False]))

    def test_volver_desde_la_ventana_reabre_la_seleccion_sin_bienvenida(self):
        codigo, llamadas, _ = self.correr(
            ["sel1", "sel2"], ventanas=[ventana_principal.VOLVER, ventana_principal.SALIR])
        self.assertEqual(codigo, 0)
        self.assertEqual(llamadas, [False, True])

    def test_error_de_mundo_muestra_aviso_y_vuelve(self):
        def falla(seleccion):
            raise ErrorMundo("archivo roto")

        codigo, llamadas, avisos = self.correr(["sel", None], avisos=[True], ejecutar=falla)
        self.assertEqual(codigo, 0)
        self.assertEqual(llamadas, [False, True])
        self.assertEqual(avisos, [("No se pudo cargar el mundo", "archivo roto")])

    def test_algoritmo_sin_implementar_muestra_aviso_con_los_disponibles(self):
        def falla(seleccion):
            raise AlgoritmoNoDisponible(Algoritmo.AVARA)

        codigo, _, avisos = self.correr(["sel"], avisos=[False], ejecutar=falla)
        self.assertEqual(codigo, 0)  # cerro la ventana en el aviso: termina
        self.assertEqual(avisos[0][0], "Algoritmo no disponible")
        self.assertIn("Avara", avisos[0][1])
        self.assertIn("Amplitud", avisos[0][1])


if __name__ == "__main__":
    unittest.main()
