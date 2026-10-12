"""
Archivo:       src/agrobot/gui/arbol_exploracion.py
Objetivo:      Mostrar el arbol de exploracion que va armando la busqueda mientras el
               robot recorre el camino solucion: la ruta elegida y las alternativas que
               el algoritmo genero en cada paso. Permite elegir un nodo (con el mouse o
               las flechas) para que la pantalla de resultados muestre su estado.
Responsabilidad:
    SI hace:
        - Guardar el arbol (NodoArbol / ArbolExploracion): cada nodo es una coordenada
          (fila, columna), con su padre, sus hijos y, si se conocen, el Estado del
          problema en ese nodo y el costo acumulado hasta el.
        - Acomodar los nodos (una hoja por columna, un nivel por fila) y dibujar el
          arbol en un rectangulo, resaltando la ruta desde la raiz hasta el nodo actual.
          Puede mostrar solo los ultimos N niveles (vista del mapa) o el arbol COMPLETO
          desde la raiz (pantalla de resultados), ajustando el tamano de los nodos y la
          frecuencia de las etiquetas para que siga siendo legible.
        - Recordar donde dibujo cada nodo para saber cual esta bajo el mouse, y guardar
          el nodo seleccionado (clic o flechas) y el nodo resaltado al pasar el mouse.
        - Calcular las alternativas de un paso (alternativas_del_paso y
          coordenadas_alternativas).
    NO hace:
        - No ejecuta la busqueda ni conoce algoritmos: recibe el problema y el camino ya
          calculado, y usa solo su contrato (sucesores).
        - No decide que se muestra de un nodo seleccionado: eso es de
          pantalla_resultados.py (aqui solo se guarda cual esta seleccionado).
        - No lee archivos ni sprites; los colores y las tipografias salen de estilo.py.
Importa de:
    - gui.estilo: paleta, tipografias y dibujar_tarjeta.
    - pygame (pygame-ce).
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
    - gui/pantalla_resultados.py (lo dibuja completo y atiende la seleccion de nodos).
Origen:        Demo/arbol.py (prototipo del equipo), con la paleta del proyecto: la ruta
               en COLOR_OLIVA, el nodo actual en COLOR_LINO y las ramas fuera de la ruta
               en COLOR_TEXTO_DESHABILITADO, sobre una tarjeta de estilo.py.
Contrato previsto:
    - NodoArbol(coordenada, padre=None, estado=None, costo=None): agregar_hijo,
      buscar_hijo, ruta_desde_raiz y la propiedad `profundidad` (niveles hasta la raiz).
    - ArbolExploracion(coordenada_inicial, estado=None, costo=None):
        - reiniciar(coordenada_inicial, estado=None, costo=None): vuelve a un arbol de
          un solo nodo y quita la seleccion.
        - agregar_hijos(coordenadas): agrega al nodo actual las alternativas generadas,
          sin moverse (quedan como ramas tenues hasta que se elija una).
        - agregar_alternativas(alternativas): igual, pero con (coordenada, estado,
          costo_del_paso) por cada hijo, para que cada nodo conozca su estado y costo.
        - avanzar_a_hijo(coordenada, estado=None): mueve el nodo actual a ese hijo (lo
          crea si falta).
        - mover_a(coordenada): modo manual; retrocede si vuelve al padre, reutiliza el
          hijo o crea uno.
        - nodo_en(punto) / seleccionar_en(punto): nodo dibujado bajo un punto de la
          pantalla (segun el ultimo dibujar); seleccionar_en lo deja en `seleccionado`
          o, si no hay ninguno, quita la seleccion.
        - mover_seleccion(direccion): "arriba" (padre), "abajo" (hijo de la ruta o el
          primero), "izquierda" / "derecha" (hermano). Sin seleccion, "arriba" elige el
          nodo actual (la meta) y las demas eligen la raiz.
        - deseleccionar(), esta_en_la_ruta(nodo).
        - dibujar(pantalla, area, ultimos_niveles=None, escala=1.0, mouse=None): dibuja
          el arbol en `area`. Con ultimos_niveles=None se dibuja completo desde la raiz.
          Si se pasa `mouse`, el nodo bajo el puntero se marca con un aro.
    - alternativas_del_paso(problema, camino_de_estados, paso): lista de (coordenada,
      estado, costo_del_paso) a las que se podia ir desde el estado `paso` del camino,
      sin contar las que vuelven a un estado ya presente en la ruta. Lista vacia si
      `paso` es el ultimo (la meta).
    - coordenadas_alternativas(problema, camino_de_estados, paso): lo mismo, pero solo
      las coordenadas.
"""
from __future__ import annotations

import math

import pygame

from . import estilo

COLOR_RUTA = estilo.COLOR_OLIVA
COLOR_NODO_ACTUAL = estilo.COLOR_LINO
COLOR_TENUE = estilo.COLOR_TEXTO_DESHABILITADO  # ramas fuera de la ruta actual
COLOR_SELECCION = estilo.COLOR_CREMA
RADIO_NODO = 5
RADIO_MINIMO = 2
ALCANCE_MINIMO = 7     # radio (px) alrededor de un nodo donde un clic lo elige
DX_MAX = 46
DY_MAX = 34
DX_MIN_ETIQUETA = 26   # si hay menos espacio, solo se etiquetan los nodos de la ruta
TITULO = "ÁRBOL DE EXPLORACIÓN"


class NodoArbol:
    def __init__(self, coordenada, padre=None, estado=None, costo=None):
        self.coordenada = coordenada
        self.padre = padre
        self.estado = estado   # Estado del problema en este nodo (None si no se conoce)
        self.costo = costo     # costo acumulado desde la raiz (None si no se conoce)
        self.hijos = []
        self.slot = 0.0
        self.nivel = 0         # nivel respecto a la raiz VISIBLE (lo fija el dibujo)

    @property
    def profundidad(self) -> int:
        """Niveles que hay entre este nodo y la raiz del arbol."""
        niveles = 0
        nodo = self
        while nodo.padre is not None:
            nodo = nodo.padre
            niveles += 1
        return niveles

    def agregar_hijo(self, coordenada, estado=None, costo=None):
        hijo = NodoArbol(coordenada, padre=self, estado=estado, costo=costo)
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
    def __init__(self, coordenada_inicial, estado=None, costo=None):
        self._escala = 1.0       # se fija en cada llamada a dibujar
        self._radio = RADIO_NODO
        self._paso_etiqueta = 1  # cada cuantos niveles se etiqueta la ruta
        self._zona = None        # zona donde se dibujo el arbol la ultima vez
        self._posiciones = {}    # nodo -> (x, y) en pantalla, de la ultima vez que se dibujo
        self._resaltado = None   # nodo bajo el mouse en el ultimo dibujo
        self.reiniciar(coordenada_inicial, estado, costo)

    # ---------------- Datos ----------------
    def reiniciar(self, coordenada_inicial, estado=None, costo=None):
        self.raiz = NodoArbol(coordenada_inicial, estado=estado, costo=costo)
        self.actual = self.raiz
        self.seleccionado = None
        self._posiciones = {}
        self._resaltado = None

    def agregar_hijos(self, coordenadas):
        """(Busqueda) Agrega al nodo actual los hijos que el algoritmo genero, SIN
        moverse. Quedan como ramas tenues hasta que se elija una."""
        self.agregar_alternativas([(coordenada, None, None) for coordenada in coordenadas])

    def agregar_alternativas(self, alternativas):
        """(Busqueda) Como agregar_hijos, pero cada alternativa trae su estado y el costo
        del paso: (coordenada, estado, costo_del_paso). El costo acumulado del hijo se
        calcula si el nodo actual conoce el suyo."""
        for coordenada, estado, costo_del_paso in alternativas:
            if self.actual.buscar_hijo(coordenada) is not None:
                continue
            costo = None
            if costo_del_paso is not None and self.actual.costo is not None:
                costo = self.actual.costo + costo_del_paso
            self.actual.agregar_hijo(coordenada, estado, costo)

    def avanzar_a_hijo(self, coordenada, estado=None):
        """(Busqueda) Mueve el nodo actual a uno de sus hijos (lo crea si no existe).
        Si se pasa `estado`, el nodo queda con ese estado."""
        hijo = self.actual.buscar_hijo(coordenada)
        if hijo is None:
            hijo = self.actual.agregar_hijo(coordenada, estado)
        elif estado is not None:
            hijo.estado = estado
        self.actual = hijo

    def mover_a(self, nueva_posicion):
        """(Modo manual) Retrocede si vuelve al padre, reutiliza hijo o crea uno."""
        if self.actual.padre is not None and self.actual.padre.coordenada == nueva_posicion:
            self.actual = self.actual.padre
            return
        existente = self.actual.buscar_hijo(nueva_posicion)
        self.actual = existente if existente else self.actual.agregar_hijo(nueva_posicion)

    # ---------------- Seleccion ----------------
    def esta_en_la_ruta(self, nodo) -> bool:
        """True si el nodo esta en la ruta de la raiz al nodo actual."""
        return nodo in self.actual.ruta_desde_raiz()

    def nodo_en(self, punto):
        """Nodo dibujado mas cerca de `punto` (dentro de su alcance), o None. Usa las
        posiciones del ultimo dibujar."""
        if self._zona is None or not self._zona.inflate(8, 8).collidepoint(punto):
            return None
        alcance = max(self._radio + 4, ALCANCE_MINIMO)
        mejor, mejor_distancia = None, alcance * alcance + 1
        for nodo, (x, y) in self._posiciones.items():
            distancia = (x - punto[0]) ** 2 + (y - punto[1]) ** 2
            if distancia <= alcance * alcance and distancia < mejor_distancia:
                mejor, mejor_distancia = nodo, distancia
        return mejor

    def seleccionar_en(self, punto):
        """Selecciona el nodo bajo `punto`; si no hay ninguno, quita la seleccion."""
        self.seleccionado = self.nodo_en(punto)
        return self.seleccionado

    def deseleccionar(self) -> None:
        self.seleccionado = None

    def mover_seleccion(self, direccion):
        """Mueve la seleccion con el teclado: "arriba" (padre), "abajo" (hijo que sigue
        la ruta, o el primero), "izquierda" / "derecha" (hermano). Retorna la seleccion."""
        nodo = self.seleccionado
        if nodo is None:
            self.seleccionado = self.actual if direccion == "arriba" else self.raiz
            return self.seleccionado
        destino = None
        if direccion == "arriba":
            destino = nodo.padre
        elif direccion == "abajo":
            ruta = self.actual.ruta_desde_raiz()
            candidatos = [hijo for hijo in nodo.hijos if hijo in ruta] or nodo.hijos
            destino = candidatos[0] if candidatos else None
        elif nodo.padre is not None:
            hermanos = nodo.padre.hijos
            posicion = hermanos.index(nodo) + (1 if direccion == "derecha" else -1)
            if 0 <= posicion < len(hermanos):
                destino = hermanos[posicion]
        if destino is not None:
            self.seleccionado = destino
        return self.seleccionado

    # ---------------- Dibujo ----------------
    def dibujar(self, pantalla, area, ultimos_niveles=None, escala=1.0, mouse=None):
        """Dibuja el arbol en `area`.

        Si ultimos_niveles es un numero, solo se muestran los ultimos N niveles hasta el
        nodo actual (asi el arbol no se hace diminuto cuando la ruta es larga). Si es
        None, se dibuja el arbol COMPLETO desde la raiz: los nodos se encogen si hay
        muchas hojas y las etiquetas de la ruta se espacian segun la altura disponible.
        `escala` agranda nodos, lineas, separaciones y letra (1.0 = tamano normal).
        `mouse` (opcional) es la posicion del puntero, para marcar el nodo que toca."""
        self._escala = escala
        self._radio = max(1, round(RADIO_NODO * escala))
        estilo.dibujar_tarjeta(pantalla, area, radio=10)
        fuente_titulo = estilo.fuente_pixel(round(16 * escala), 700)
        estilo.texto(pantalla, estilo.recortar(TITULO, fuente_titulo, area.w - 16),
                     fuente_titulo, estilo.COLOR_SALVIA,
                     (area.centerx, area.y + round(8 * escala)), ancla="midtop")

        arriba = round(34 * escala)
        abajo = round(22 * escala)
        zona = pygame.Rect(area.x + 8, area.y + arriba, area.w - 16, area.h - arriba - abajo)

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

        dx = min(DX_MAX * escala, zona.w / n_hojas)
        dy = min(DY_MAX * escala, (zona.h - 2 * self._radio) / max(profundidad, 1))

        # Si el arbol es muy denso, los nodos se encogen para no solaparse.
        self._radio = max(RADIO_MINIMO, min(self._radio, int(min(dx, dy) / 2) + 1))
        # Si los niveles quedan muy juntos, se etiqueta la ruta solo cada cierto nivel.
        alto_etiqueta = round(11 * escala) + 2
        self._paso_etiqueta = max(1, math.ceil(alto_etiqueta / max(dy, 1)))

        offset_x = zona.x + (zona.w - n_hojas * dx) / 2
        geom = (zona, offset_x, dx, dy)

        # Posiciones en pantalla: sirven para dibujar y para saber que nodo se toca.
        self._zona = zona
        self._posiciones = {}
        self._registrar_posiciones(raiz_visible, geom)
        self._resaltado = self.nodo_en(mouse) if mouse is not None else None

        ruta = self.actual.ruta_desde_raiz()
        clip_anterior = pantalla.get_clip()
        pantalla.set_clip(zona.inflate(8, 8))
        self._dibujar_aristas(pantalla, raiz_visible, ruta, False, geom)
        self._dibujar_aristas(pantalla, raiz_visible, ruta, True, geom)
        self._dibujar_nodos(pantalla, raiz_visible, ruta, geom)
        pantalla.set_clip(clip_anterior)

        if ocultos > 0:
            estilo.texto(pantalla, "(+" + str(ocultos) + " niveles arriba)",
                         estilo.fuente_texto(round(12 * escala), 400), estilo.COLOR_SALVIA_TENUE,
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

    def _posicion(self, nodo, geom):
        zona, offset_x, dx, dy = geom
        x = offset_x + (nodo.slot + 0.5) * dx
        y = zona.y + self._radio + nodo.nivel * dy
        return int(x), int(y)

    def _registrar_posiciones(self, nodo, geom):
        self._posiciones[nodo] = self._posicion(nodo, geom)
        for hijo in nodo.hijos:
            self._registrar_posiciones(hijo, geom)

    def _dibujar_aristas(self, pantalla, nodo, ruta, activas, geom):
        pos_padre = self._posicion(nodo, geom)
        for hijo in nodo.hijos:
            en_ruta = hijo in ruta
            if en_ruta == activas:
                color = COLOR_RUTA if en_ruta else COLOR_TENUE
                grosor = max(1, round((3 if en_ruta else 1) * self._escala))
                pygame.draw.line(pantalla, color, pos_padre,
                                 self._posicion(hijo, geom), grosor)
            self._dibujar_aristas(pantalla, hijo, ruta, activas, geom)

    def _debe_etiquetar(self, nodo, ruta, dx, es_raiz_visible):
        """Decide si un nodo lleva etiqueta (fila,columna)."""
        if nodo is self.actual or nodo is self.seleccionado or nodo is self._resaltado:
            return True
        if es_raiz_visible:
            return True
        if nodo in ruta:
            if self._paso_etiqueta <= 1:
                return True
            # Cada `paso` niveles, y sin pisar la etiqueta del nodo actual.
            return (nodo.nivel % self._paso_etiqueta == 0
                    and self.actual.nivel - nodo.nivel >= self._paso_etiqueta)
        return dx >= DX_MIN_ETIQUETA * self._escala

    def _dibujar_nodos(self, pantalla, nodo, ruta, geom, es_raiz_visible=True):
        zona = geom[0]
        dx = geom[2]
        x, y = self._posiciones[nodo]
        if nodo is self.actual:
            color = COLOR_NODO_ACTUAL
        elif nodo in ruta:
            color = COLOR_RUTA
        else:
            color = COLOR_TENUE
        pygame.draw.circle(pantalla, color, (x, y), self._radio)

        if nodo is self.seleccionado:
            grosor = max(1, round(2 * self._escala))
            pygame.draw.circle(pantalla, COLOR_SELECCION, (x, y), self._radio + 4, grosor)
        elif nodo is self._resaltado:
            pygame.draw.circle(pantalla, color, (x, y), self._radio + 3, 1)

        if self._debe_etiquetar(nodo, ruta, dx, es_raiz_visible):
            fila, columna = nodo.coordenada
            color_etiqueta = COLOR_SELECCION if nodo is self.seleccionado else color
            etiqueta = estilo.fuente_texto(round(11 * self._escala), 500).render(
                "(" + str(fila) + "," + str(columna) + ")", True, color_etiqueta)
            margen = self._radio + (6 if nodo is self.seleccionado else 2)
            if x + margen + etiqueta.get_width() > zona.right:
                rect = etiqueta.get_rect(midright=(x - margen, y))
            else:
                rect = etiqueta.get_rect(midleft=(x + margen, y))
            pantalla.blit(etiqueta, rect)

        for hijo in nodo.hijos:
            self._dibujar_nodos(pantalla, hijo, ruta, geom, es_raiz_visible=False)


def alternativas_del_paso(problema, camino_de_estados, paso: int) -> list:
    """Lista de (coordenada, estado, costo_del_paso) que el algoritmo pudo generar desde
    el estado `paso` del camino, sin las que vuelven a un estado ya presente en la ruta
    hasta ahi."""
    if paso >= len(camino_de_estados) - 1:
        return []  # en la meta la busqueda ya no expande
    ruta = camino_de_estados[:paso + 1]
    return [
        (estado.posicion, estado, costo)
        for _, estado, costo in problema.sucesores(camino_de_estados[paso], ruta)
    ]


def coordenadas_alternativas(problema, camino_de_estados, paso: int) -> list:
    """Posiciones que el algoritmo pudo generar desde el estado `paso` del camino,
    sin las que vuelven a un estado ya presente en la ruta hasta ahi."""
    return [coordenada
            for coordenada, _, _ in alternativas_del_paso(problema, camino_de_estados, paso)]