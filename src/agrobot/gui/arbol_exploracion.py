"""
Archivo:       src/agrobot/gui/arbol_exploracion.py
Objetivo:      Mostrar el arbol de exploracion que va armando la busqueda mientras el
               robot recorre el camino solucion: la ruta elegida y las alternativas que
               el algoritmo genero en cada paso.
Responsabilidad:
    SI hace:
        - Guardar el arbol (NodoArbol / ArbolExploracion): cada nodo es una coordenada
          (fila, columna), con su padre y sus hijos.
        - Acomodar los nodos (una hoja por columna, un nivel por fila) y dibujar el
          arbol en un rectangulo, resaltando la ruta desde la raiz hasta el nodo actual
          y mostrando solo los ultimos N niveles cuando la ruta es larga.
        - Calcular las alternativas de un paso (coordenadas_alternativas).
    NO hace:
        - No ejecuta la busqueda ni conoce algoritmos: recibe el problema y el camino ya
          calculado, y usa solo su contrato (sucesores).
        - No lee archivos ni sprites; los colores y las tipografias salen de estilo.py.
Importa de:
    - gui.estilo: paleta, tipografias y dibujar_tarjeta.
    - pygame (pygame-ce).
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
Origen:        Demo/arbol.py (prototipo del equipo), con la paleta del proyecto: la ruta
               en COLOR_OLIVA, el nodo actual en COLOR_LINO y las ramas fuera de la ruta
               en COLOR_TEXTO_DESHABILITADO, sobre una tarjeta de estilo.py.
Contrato previsto:
    - NodoArbol(coordenada, padre=None): agregar_hijo, buscar_hijo, ruta_desde_raiz.
    - ArbolExploracion(coordenada_inicial):
        - reiniciar(coordenada_inicial): vuelve a un arbol de un solo nodo.
        - agregar_hijos(coordenadas): agrega al nodo actual las alternativas generadas,
          sin moverse (quedan como ramas tenues hasta que se elija una).
        - avanzar_a_hijo(coordenada): mueve el nodo actual a ese hijo (lo crea si falta).
        - mover_a(coordenada): modo manual; retrocede si vuelve al padre, reutiliza el
          hijo o crea uno.
        - dibujar(pantalla, area, ultimos_niveles=None): dibuja el arbol en `area`.
    - coordenadas_alternativas(problema, camino_de_estados, paso): posiciones a las que
      se podia ir desde el estado `paso` del camino, sin contar las que vuelven a un
      estado ya presente en la ruta. Lista vacia si `paso` es el ultimo (la meta).
"""
from __future__ import annotations

import pygame

from . import estilo

COLOR_RUTA = estilo.COLOR_OLIVA
COLOR_NODO_ACTUAL = estilo.COLOR_LINO
COLOR_TENUE = estilo.COLOR_TEXTO_DESHABILITADO  # ramas fuera de la ruta actual
RADIO_NODO = 5
DX_MAX = 46
DY_MAX = 34
DX_MIN_ETIQUETA = 26   # si hay menos espacio, solo se etiquetan los nodos de la ruta
TITULO = "ÁRBOL DE EXPLORACIÓN"


class NodoArbol:
    def __init__(self, coordenada, padre=None):
        self.coordenada = coordenada
        self.padre = padre
        self.hijos = []
        self.slot = 0.0
        self.nivel = 0

    def agregar_hijo(self, coordenada):
        hijo = NodoArbol(coordenada, padre=self)
        self.hijos.append(hijo)
        return hijo

    def buscar_hijo(self, coordenada):
        for hijo in self.hijos:
            if hijo.coordenada == coordenada:
                return hijo
        return None

    def ruta_desde_raiz(self):
        ruta = set()
        nodo = self
        while nodo is not None:
            ruta.add(nodo)
            nodo = nodo.padre
        return ruta


class ArbolExploracion:
    def __init__(self, coordenada_inicial):
        self.reiniciar(coordenada_inicial)

    # ---------------- Datos ----------------
    def reiniciar(self, coordenada_inicial):
        self.raiz = NodoArbol(coordenada_inicial)
        self.actual = self.raiz

    def agregar_hijos(self, coordenadas):
        """(Busqueda) Agrega al nodo actual los hijos que el algoritmo genero, SIN
        moverse. Quedan como ramas tenues hasta que se elija una."""
        for coordenada in coordenadas:
            if self.actual.buscar_hijo(coordenada) is None:
                self.actual.agregar_hijo(coordenada)

    def avanzar_a_hijo(self, coordenada):
        """(Busqueda) Mueve el nodo actual a uno de sus hijos (lo crea si no existe)."""
        hijo = self.actual.buscar_hijo(coordenada)
        if hijo is None:
            hijo = self.actual.agregar_hijo(coordenada)
        self.actual = hijo

    def mover_a(self, nueva_posicion):
        """(Modo manual) Retrocede si vuelve al padre, reutiliza hijo o crea uno."""
        if self.actual.padre is not None and self.actual.padre.coordenada == nueva_posicion:
            self.actual = self.actual.padre
            return
        existente = self.actual.buscar_hijo(nueva_posicion)
        self.actual = existente if existente else self.actual.agregar_hijo(nueva_posicion)

    # ---------------- Dibujo ----------------
    def dibujar(self, pantalla, area, ultimos_niveles=None):
        """Dibuja el arbol en `area`. Si ultimos_niveles es un numero, solo se muestran
        los ultimos N niveles hasta el nodo actual (asi el arbol no se hace diminuto
        cuando la ruta es larga)."""
        estilo.dibujar_tarjeta(pantalla, area, radio=10)
        fuente_titulo = estilo.fuente_pixel(16, 700)
        estilo.texto(pantalla, estilo.recortar(TITULO, fuente_titulo, area.w - 16),
                     fuente_titulo, estilo.COLOR_SALVIA,
                     (area.centerx, area.y + 8), ancla="midtop")

        zona = pygame.Rect(area.x + 8, area.y + 34, area.w - 16, area.h - 56)

        # Nodo desde el que se empieza a dibujar
        raiz_visible = self.raiz
        if ultimos_niveles is not None:
            nodo = self.actual
            subidos = 0
            while subidos < ultimos_niveles and nodo.padre is not None:
                nodo = nodo.padre
                subidos += 1
            raiz_visible = nodo

        # Cuantos niveles quedaron ocultos arriba
        ocultos = 0
        nodo = raiz_visible
        while nodo.padre is not None:
            nodo = nodo.padre
            ocultos += 1

        contador = [0]
        profundidad = self._calcular_layout(raiz_visible, 0, contador)
        n_hojas = max(contador[0], 1)

        dx = min(DX_MAX, zona.w / n_hojas)
        dy = min(DY_MAX, (zona.h - 2 * RADIO_NODO) / max(profundidad, 1))
        offset_x = zona.x + (zona.w - n_hojas * dx) / 2
        geom = (zona, offset_x, dx, dy)

        ruta = self.actual.ruta_desde_raiz()
        clip_anterior = pantalla.get_clip()
        pantalla.set_clip(zona.inflate(8, 8))
        self._dibujar_aristas(pantalla, raiz_visible, ruta, False, geom)
        self._dibujar_aristas(pantalla, raiz_visible, ruta, True, geom)
        self._dibujar_nodos(pantalla, raiz_visible, ruta, geom)
        pantalla.set_clip(clip_anterior)

        if ocultos > 0:
            estilo.texto(pantalla, "(+" + str(ocultos) + " niveles arriba)",
                         estilo.fuente_texto(12, 400), estilo.COLOR_SALVIA_TENUE,
                         (area.centerx, area.bottom - 6), ancla="midbottom")

    def _calcular_layout(self, nodo, nivel, contador):
        nodo.nivel = nivel
        if not nodo.hijos:
            nodo.slot = contador[0]
            contador[0] += 1
            return nivel
        profundidad = nivel
        for hijo in nodo.hijos:
            profundidad = max(profundidad, self._calcular_layout(hijo, nivel + 1, contador))
        nodo.slot = (nodo.hijos[0].slot + nodo.hijos[-1].slot) / 2
        return profundidad

    @staticmethod
    def _posicion(nodo, geom):
        zona, offset_x, dx, dy = geom
        x = offset_x + (nodo.slot + 0.5) * dx
        y = zona.y + RADIO_NODO + nodo.nivel * dy
        return int(x), int(y)

    def _dibujar_aristas(self, pantalla, nodo, ruta, activas, geom):
        pos_padre = self._posicion(nodo, geom)
        for hijo in nodo.hijos:
            en_ruta = hijo in ruta
            if en_ruta == activas:
                color = COLOR_RUTA if en_ruta else COLOR_TENUE
                pygame.draw.line(pantalla, color, pos_padre,
                                 self._posicion(hijo, geom), 3 if en_ruta else 1)
            self._dibujar_aristas(pantalla, hijo, ruta, activas, geom)

    def _dibujar_nodos(self, pantalla, nodo, ruta, geom):
        zona = geom[0]
        dx = geom[2]
        x, y = self._posicion(nodo, geom)
        if nodo is self.actual:
            color = COLOR_NODO_ACTUAL
        elif nodo in ruta:
            color = COLOR_RUTA
        else:
            color = COLOR_TENUE
        pygame.draw.circle(pantalla, color, (x, y), RADIO_NODO)

        if nodo in ruta or dx >= DX_MIN_ETIQUETA:
            fila, columna = nodo.coordenada
            etiqueta = estilo.fuente_texto(11, 500).render(
                "(" + str(fila) + "," + str(columna) + ")", True, color)
            if x + RADIO_NODO + 2 + etiqueta.get_width() > zona.right:
                rect = etiqueta.get_rect(midright=(x - RADIO_NODO - 2, y))
            else:
                rect = etiqueta.get_rect(midleft=(x + RADIO_NODO + 2, y))
            pantalla.blit(etiqueta, rect)

        for hijo in nodo.hijos:
            self._dibujar_nodos(pantalla, hijo, ruta, geom)


def coordenadas_alternativas(problema, camino_de_estados, paso: int) -> list:
    """Posiciones que el algoritmo pudo generar desde el estado `paso` del camino,
    sin las que vuelven a un estado ya presente en la ruta hasta ahi."""
    if paso >= len(camino_de_estados) - 1:
        return []  # en la meta la busqueda ya no expande
    ruta = camino_de_estados[:paso + 1]
    return [
        estado.posicion
        for _, estado, _ in problema.sucesores(camino_de_estados[paso], ruta)
    ]
