"""
Archivo:       tests/test_seleccion_nodos.py
Objetivo:      Verificar que en la pantalla de resultados se pueden elegir los nodos del
               arbol de exploracion y que el panel de informacion cambia segun el nodo.
Responsabilidad:
    QUE VERIFICA:
        - Cada nodo del arbol guarda su estado y su costo acumulado: los de la ruta
          coinciden con el camino de estados y el costo de la meta es la suma de los
          costos de los pasos.
        - ArbolExploracion: nodo_en / seleccionar_en encuentran el nodo bajo un punto,
          un clic en el vacio quita la seleccion, y las flechas (mover_seleccion)
          recorren padre, hijos y hermanos.
        - pantalla_resultados: sin nodo elegido el panel muestra el estado final; con un
          nodo de la ruta o un nodo alternativo muestra el estado de ese nodo (y su
          costo acumulado cuando el algoritmo lo calcula).
        - VentanaPrincipal: un clic en un nodo del arbol, las flechas y "Ver mapa"
          (que quita la eleccion) funcionan, y la pantalla se dibuja con un nodo elegido.
Importa de:
    - gui.arbol_exploracion, gui.panel_reporte, gui.pantalla_resultados,
      gui.ventana_principal, gui.panel_control.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_seleccion_nodos
"""
import dataclasses
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pygame  # noqa: E402

from agrobot.gui import pantalla_resultados, ventana_principal  # noqa: E402
from agrobot.gui.arbol_exploracion import (  # noqa: E402
    alternativas_del_paso,
    coordenadas_alternativas,
)
from agrobot.gui.catalogo_algoritmos import Algoritmo  # noqa: E402
from agrobot.gui.panel_control import ejecutar_seleccion  # noqa: E402
from agrobot.gui.panel_reporte import PanelReporte  # noqa: E402
from agrobot.gui.pantalla_seleccion import SeleccionInicio  # noqa: E402
from agrobot.gui.ventana_principal import VentanaPrincipal  # noqa: E402

PRUEBA1 = RAIZ / "mundos" / "Prueba1.txt"


def tecla(clave):
    return pygame.event.Event(pygame.KEYDOWN, key=clave)


def clic_en(punto):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=punto)


class PruebaConResultados(unittest.TestCase):
    """Una ventana principal con el recorrido terminado y la pantalla de resultados."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.pantalla = pygame.display.set_mode((1120, 760))
        cls.ejecucion = ejecutar_seleccion(SeleccionInicio(PRUEBA1, Algoritmo.AMPLITUD))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def ventana_con_resultados(self):
        ventana = VentanaPrincipal(self.pantalla, self.ejecucion)
        while not ventana.animacion.terminada:
            ventana.actualizar(16)
        ventana.actualizar(ventana_principal.RETRASO_RESULTADOS_MS + 100)
        self.assertTrue(ventana.mostrando_resultados)
        ventana.dibujar(self.pantalla)  # fija las posiciones de los nodos en pantalla
        return ventana


class TestEstadoYCostoDeLosNodos(PruebaConResultados):
    def test_los_nodos_de_la_ruta_guardan_el_estado_del_camino(self):
        ventana = self.ventana_con_resultados()
        estados = ventana.animacion.camino_de_estados
        nodo = ventana.arbol.raiz
        for estado in estados:
            self.assertEqual(nodo.estado, estado)
            hijos_en_ruta = [h for h in nodo.hijos if h in ventana.arbol.actual.ruta_desde_raiz()]
            nodo = hijos_en_ruta[0] if hijos_en_ruta else None
        self.assertIsNone(nodo)  # la meta es el ultimo nodo de la ruta

    def test_todos_los_nodos_tienen_estado(self):
        ventana = self.ventana_con_resultados()
        pendientes = [ventana.arbol.raiz]
        while pendientes:
            nodo = pendientes.pop()
            self.assertIsNotNone(nodo.estado, nodo.coordenada)
            self.assertEqual(nodo.estado.posicion, nodo.coordenada)
            pendientes.extend(nodo.hijos)

    def test_el_costo_acumulado_de_la_meta_es_la_suma_de_los_pasos(self):
        ventana = self.ventana_con_resultados()
        problema = self.ejecucion.problema
        estados = ventana.animacion.camino_de_estados
        total = 0.0
        for i in range(len(estados) - 1):
            costos = [costo for _, estado, costo in problema.sucesores(estados[i], estados[:i + 1])
                      if estado == estados[i + 1]]
            self.assertEqual(len(costos), 1)
            total += costos[0]
        self.assertAlmostEqual(ventana.arbol.actual.costo, total)
        self.assertEqual(ventana.arbol.raiz.costo, 0.0)
        costo_total = self.ejecucion.resultado.costo_total
        if costo_total is not None:  # Costo uniforme y A*
            self.assertAlmostEqual(ventana.arbol.actual.costo, costo_total)

    def test_alternativas_del_paso_coincide_con_coordenadas_alternativas(self):
        estados = list(self.ejecucion.resultado.camino_de_estados)
        problema = self.ejecucion.problema
        for paso in (0, 1, len(estados) - 1):
            alternativas = alternativas_del_paso(problema, estados, paso)
            self.assertEqual([a[0] for a in alternativas],
                             coordenadas_alternativas(problema, estados, paso))
            for coordenada, estado, costo in alternativas:
                self.assertEqual(estado.posicion, coordenada)
                self.assertGreater(costo, 0)


class TestSeleccionEnElArbol(PruebaConResultados):
    def test_un_clic_sobre_un_nodo_lo_elige(self):
        arbol = self.ventana_con_resultados().arbol
        for nodo in (arbol.raiz, arbol.actual, arbol.raiz.hijos[0]):
            x, y = arbol._posiciones[nodo]
            self.assertIs(arbol.seleccionar_en((x, y)), nodo)
            self.assertIs(arbol.seleccionado, nodo)

    def test_un_clic_en_el_vacio_quita_la_seleccion(self):
        arbol = self.ventana_con_resultados().arbol
        arbol.seleccionado = arbol.raiz
        area = pantalla_resultados.AREA_ARBOL
        vacio = None
        for x in range(area.x + 12, area.right - 12, 4):
            for y in range(area.y + 40, area.bottom - 24, 4):
                if all((x - nx) ** 2 + (y - ny) ** 2 > 30 ** 2
                       for nx, ny in arbol._posiciones.values()):
                    vacio = (x, y)
                    break
            if vacio:
                break
        self.assertIsNotNone(vacio)
        self.assertIsNone(arbol.seleccionar_en(vacio))
        self.assertIsNone(arbol.seleccionado)

    def test_flechas_recorren_padre_hijos_y_hermanos(self):
        arbol = self.ventana_con_resultados().arbol
        # Sin seleccion: "arriba" elige la meta; cualquier otra, la raiz.
        self.assertIs(arbol.mover_seleccion("arriba"), arbol.actual)
        arbol.deseleccionar()
        self.assertIs(arbol.mover_seleccion("abajo"), arbol.raiz)
        # Hacia abajo sigue la ruta de la solucion, hasta la meta.
        for _ in range(arbol.actual.profundidad):
            arbol.mover_seleccion("abajo")
        self.assertIs(arbol.seleccionado, arbol.actual)
        self.assertIs(arbol.mover_seleccion("abajo"), arbol.actual)  # la meta no tiene hijos
        # Hacia arriba vuelve al padre.
        self.assertIs(arbol.mover_seleccion("arriba"), arbol.actual.padre)
        # Hermanos: los tres hijos de la raiz, de izquierda a derecha.
        arbol.seleccionado = arbol.raiz.hijos[0]
        self.assertIs(arbol.mover_seleccion("izquierda"), arbol.raiz.hijos[0])  # no hay mas
        self.assertIs(arbol.mover_seleccion("derecha"), arbol.raiz.hijos[1])
        self.assertIs(arbol.mover_seleccion("derecha"), arbol.raiz.hijos[2])
        self.assertIs(arbol.mover_seleccion("derecha"), arbol.raiz.hijos[2])  # no hay mas
        # La raiz no tiene padre ni hermanos.
        arbol.seleccionado = arbol.raiz
        self.assertIs(arbol.mover_seleccion("arriba"), arbol.raiz)
        self.assertIs(arbol.mover_seleccion("derecha"), arbol.raiz)

    def test_reiniciar_el_arbol_quita_la_seleccion(self):
        arbol = self.ventana_con_resultados().arbol
        arbol.seleccionado = arbol.actual
        arbol.reiniciar((0, 0))
        self.assertIsNone(arbol.seleccionado)


class TestPanelSegunElNodo(PruebaConResultados):
    def alternativo(self, arbol):
        ruta = arbol.actual.ruta_desde_raiz()
        for nodo in arbol.raiz.hijos:
            if nodo not in ruta:
                return nodo
        self.fail("la raiz no tiene alternativas")

    def test_sin_seleccion_muestra_el_estado_final(self):
        ventana = self.ventana_con_resultados()
        mensaje, subtitulo, filas = pantalla_resultados.contenido_de_informacion(
            ventana.reporte, ventana.animacion, ventana.arbol)
        self.assertEqual(subtitulo, "ESTADO FINAL DEL ROBOT")
        self.assertEqual(mensaje[0], "META ALCANZADA")
        self.assertEqual(filas, PanelReporte.filas_del_robot(ventana.animacion))

    def test_nodo_de_la_ruta_muestra_su_estado(self):
        ventana = self.ventana_con_resultados()
        estados = ventana.animacion.camino_de_estados
        ventana.arbol.mover_seleccion("abajo")  # sin seleccion: elige la raiz
        for _ in range(5):
            nodo = ventana.arbol.mover_seleccion("abajo")  # sigue la ruta de la solucion
        self.assertEqual(nodo.profundidad, 5)
        mensaje, subtitulo, filas = pantalla_resultados.contenido_de_informacion(
            ventana.reporte, ventana.animacion, ventana.arbol)
        self.assertEqual(subtitulo, "ESTADO EN EL NODO")
        self.assertEqual(mensaje[0], "NODO DE LA RUTA")
        self.assertEqual(filas, PanelReporte.filas_del_estado(estados[5], "5/" + str(len(estados) - 1)))
        self.assertEqual(dict(filas)["Posición"],
                         "(" + str(estados[5].fila) + ", " + str(estados[5].columna) + ")")

    def test_la_meta_elegida_dice_meta_alcanzada(self):
        ventana = self.ventana_con_resultados()
        ventana.arbol.seleccionado = ventana.arbol.actual
        mensaje, _, filas = pantalla_resultados.contenido_de_informacion(
            ventana.reporte, ventana.animacion, ventana.arbol)
        self.assertEqual(mensaje[0], "META ALCANZADA")
        self.assertEqual(filas, PanelReporte.filas_del_robot(ventana.animacion))

    def test_nodo_alternativo_muestra_su_propio_estado(self):
        ventana = self.ventana_con_resultados()
        nodo = self.alternativo(ventana.arbol)
        ventana.arbol.seleccionado = nodo
        mensaje, subtitulo, filas = pantalla_resultados.contenido_de_informacion(
            ventana.reporte, ventana.animacion, ventana.arbol)
        self.assertEqual(mensaje[0], "NODO ALTERNATIVO")
        self.assertEqual(subtitulo, "ESTADO EN EL NODO")
        datos = dict(filas)
        self.assertEqual(datos["Paso"], "1 · alternativa")
        self.assertEqual(datos["Posición"], "(" + str(nodo.coordenada[0]) + ", "
                         + str(nodo.coordenada[1]) + ")")
        self.assertNotEqual(filas, PanelReporte.filas_del_robot(ventana.animacion))

    def test_costo_acumulado_solo_si_el_algoritmo_calcula_costo(self):
        ventana = self.ventana_con_resultados()
        nodo = self.alternativo(ventana.arbol)
        ventana.arbol.seleccionado = nodo
        _, _, sin_costo = pantalla_resultados.contenido_de_informacion(
            ventana.reporte, ventana.animacion, ventana.arbol)
        self.assertNotIn("Costo acumulado", dict(sin_costo))

        reporte = PanelReporte(dataclasses.replace(ventana.reporte.resultado, costo_total=25.0),
                               ventana.reporte.algoritmo)
        _, _, con_costo = pantalla_resultados.contenido_de_informacion(
            reporte, ventana.animacion, ventana.arbol)
        self.assertEqual(dict(con_costo)["Costo acumulado"], f"{nodo.costo:g}")

    def test_dibuja_con_nodo_elegido_incluso_con_costo(self):
        ventana = self.ventana_con_resultados()
        ventana.reporte = PanelReporte(
            dataclasses.replace(ventana.reporte.resultado, costo_total=25.0),
            ventana.reporte.algoritmo)
        for nodo in (ventana.arbol.raiz, self.alternativo(ventana.arbol), ventana.arbol.actual):
            ventana.arbol.seleccionado = nodo
            ventana.dibujar(self.pantalla)  # no debe fallar


class TestEventosEnLaVentana(PruebaConResultados):
    def test_clic_en_un_nodo_cambia_el_panel_y_clic_fuera_lo_restablece(self):
        ventana = self.ventana_con_resultados()
        arbol = ventana.arbol
        nodo = arbol.raiz.hijos[0]
        ventana.procesar_evento(clic_en(arbol._posiciones[nodo]))
        self.assertIs(arbol.seleccionado, nodo)
        ventana.dibujar(self.pantalla)
        # Un clic dentro de la tarjeta de informacion no toca el arbol.
        ventana.procesar_evento(clic_en(pantalla_resultados.AREA_INFO.center))
        self.assertIs(arbol.seleccionado, nodo)
        # Un clic en el vacio del arbol quita la eleccion.
        esquina = (pantalla_resultados.AREA_ARBOL.x + 12, pantalla_resultados.AREA_ARBOL.bottom - 8)
        self.assertIsNone(arbol.nodo_en(esquina))
        ventana.procesar_evento(clic_en(esquina))
        self.assertIsNone(arbol.seleccionado)

    def test_flechas_en_resultados_mueven_la_seleccion_y_no_cambian_la_velocidad(self):
        ventana = self.ventana_con_resultados()
        velocidad = ventana.animacion.ms_por_paso
        self.assertIsNone(ventana.procesar_evento(tecla(pygame.K_UP)))
        self.assertIs(ventana.arbol.seleccionado, ventana.arbol.actual)
        self.assertIsNone(ventana.procesar_evento(tecla(pygame.K_UP)))
        self.assertIs(ventana.arbol.seleccionado, ventana.arbol.actual.padre)
        self.assertEqual(ventana.animacion.ms_por_paso, velocidad)
        self.assertTrue(ventana.mostrando_resultados)

    def test_ver_mapa_quita_la_seleccion(self):
        ventana = self.ventana_con_resultados()
        ventana.arbol.seleccionado = ventana.arbol.raiz
        ventana.procesar_evento(tecla(pygame.K_RETURN))
        self.assertFalse(ventana.mostrando_resultados)
        self.assertIsNone(ventana.arbol.seleccionado)
        ventana.dibujar(self.pantalla)  # el mapa se dibuja sin nodo elegido

    def test_reiniciar_quita_la_seleccion(self):
        ventana = self.ventana_con_resultados()
        ventana.arbol.seleccionado = ventana.arbol.raiz
        ventana.procesar_evento(tecla(pygame.K_r))
        self.assertIsNone(ventana.arbol.seleccionado)

    def test_esc_sigue_volviendo_a_la_seleccion(self):
        ventana = self.ventana_con_resultados()
        ventana.arbol.seleccionado = ventana.arbol.raiz
        self.assertEqual(ventana.procesar_evento(tecla(pygame.K_ESCAPE)), ventana_principal.VOLVER)


if __name__ == "__main__":
    unittest.main()