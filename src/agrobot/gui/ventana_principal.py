"""
Archivo:       src/agrobot/gui/ventana_principal.py
Objetivo:      Ensamblar la ventana principal de la aplicacion, integrando el mundo, la
               animacion, el arbol de exploracion y el reporte en una sola interfaz
               coherente, con los colores y tipografias de estilo.py.
Responsabilidad:
    SI hace:
        - Disponer en la ventana (1120 x 760, la misma de las pantallas de inicio): el
          mundo a la izquierda y, a la derecha, el reporte, el arbol de exploracion y
          los botones (Pausar/Seguir, Paso, Reiniciar, Inicio).
        - Coordinar el flujo entre paneles: la animacion reproduce el camino de la
          EjecucionBusqueda; cada vez que el robot llega a una casilla nueva, se agrega
          al arbol el paso y sus alternativas; el reporte muestra el estado actual.
        - Atender el teclado y el mouse: Espacio (pausa), flecha derecha (un paso),
          R (reiniciar), flechas arriba/abajo (velocidad), Esc o "Inicio" (volver a la
          seleccion) y cerrar la ventana (salir).
        - Guardar en cada nodo del arbol su estado y su costo acumulado, y pasar el arbol
          a pantalla_resultados para que alli se puedan elegir nodos y ver su estado.
    NO hace:
        - No ejecuta la busqueda ni carga archivos: recibe una EjecucionBusqueda ya
          hecha (panel_control.ejecutar_seleccion).
        - No dibuja el detalle de cada panel: eso vive en panel_mundo, animacion,
          arbol_exploracion y panel_reporte.
Importa de:
    - gui.panel_mundo, gui.animacion, gui.arbol_exploracion, gui.panel_reporte,
      gui.cargador_sprites, gui.estilo, gui.panel_control (EjecucionBusqueda).
    - pygame (pygame-ce).
Lo importan:
    - main.py (unico punto que crea la ventana principal).
Origen:        Disposicion y atajos tomados de Demo/main.py (panel derecho con estadisticas,
               arbol y boton de reiniciar).
Contrato previsto:
    - VentanaPrincipal(pantalla, ejecucion, sprites=None):
        - procesar_evento(evento): aplica un evento; retorna "salir", "volver" o None.
        - actualizar(dt_ms): avanza la animacion y sincroniza el arbol.
        - dibujar(pantalla): pinta toda la ventana.
        - ejecutar(): bucle propio; retorna "salir" o "volver".
    - SALIR y VOLVER: los valores que retornan procesar_evento y ejecutar.
"""
from __future__ import annotations

import pygame

from . import estilo, pantalla_resultados
from .animacion import PanelAnimacion
from .arbol_exploracion import ArbolExploracion, alternativas_del_paso
from .cargador_sprites import cargar_sprites
from .panel_mundo import PanelMundo
from .panel_reporte import ALTO_RECOMENDADO, PanelReporte

SALIR = "salir"
VOLVER = "volver"

ORIGEN_MUNDO = (40, 60)
COLUMNA_X = 720
COLUMNA_ANCHO = 360
AREA_REPORTE = pygame.Rect(COLUMNA_X, 60, COLUMNA_ANCHO, ALTO_RECOMENDADO)
AREA_ARBOL = pygame.Rect(COLUMNA_X, 60 + ALTO_RECOMENDADO + 16, COLUMNA_ANCHO, 220)
ALTO_BOTON = 34
SEPARACION_BOTONES = 14
ANCHO_BOTON = (COLUMNA_ANCHO - SEPARACION_BOTONES) // 2
TAMANO_LETRA_BOTON = 15
NIVELES_VISIBLES_ARBOL = 6
FACTOR_VELOCIDAD = 1.25
RETRASO_RESULTADOS_MS = 1200  # pausa tras llegar a la meta, antes de mostrar los resultados


def _rect_boton(columna: int, fila: int) -> pygame.Rect:
    base_y = 700 - 2 * ALTO_BOTON - SEPARACION_BOTONES  # alineados con el borde del mundo
    return pygame.Rect(COLUMNA_X + columna * (ANCHO_BOTON + SEPARACION_BOTONES),
                       base_y + fila * (ALTO_BOTON + SEPARACION_BOTONES), ANCHO_BOTON, ALTO_BOTON)


BOTON_PAUSA = _rect_boton(0, 0)
BOTON_PASO = _rect_boton(1, 0)
BOTON_REINICIAR = _rect_boton(0, 1)
BOTON_INICIO = _rect_boton(1, 1)

AYUDA = "Espacio: pausa · Derecha: paso · R: reiniciar · Arriba/Abajo: velocidad"
AYUDA_SALIDA = "Esc: volver a la seleccion"


class VentanaPrincipal:
    def __init__(self, pantalla, ejecucion, sprites=None):
        self.ejecucion = ejecucion
        sprites = sprites or cargar_sprites()
        self.panel_mundo = PanelMundo(ejecucion.mundo, sprites, origen=ORIGEN_MUNDO)
        self.animacion = PanelAnimacion(self.panel_mundo, sprites, ejecucion.resultado,
                                        ejecucion.problema.estado_inicial())
        self.reporte = PanelReporte(ejecucion.resultado, ejecucion.algoritmo.value)
        self._construir_arbol()
        self._reiniciar_vista_final()

    # ------------------------------------------------------------ vista final
    def _reiniciar_vista_final(self) -> None:
        """La pantalla de resultados aparece sola una vez por reproduccion."""
        self.mostrando_resultados = False
        self._resultados_ya_mostrados = False
        self._ms_desde_la_meta = 0

    # ------------------------------------------------------------ arbol
    def _construir_arbol(self) -> None:
        estados = self.animacion.camino_de_estados
        # Cada nodo guarda su estado (y su costo acumulado) para poder mostrarlo luego.
        self.arbol = ArbolExploracion(estados[0].posicion, estado=estados[0], costo=0.0)
        self._agregar_alternativas(0)
        self._paso_del_arbol = 0

    def _agregar_alternativas(self, paso: int) -> None:
        self.arbol.agregar_alternativas(alternativas_del_paso(
            self.ejecucion.problema, self.animacion.camino_de_estados, paso))

    def _sincronizar_arbol(self) -> None:
        """Agrega al arbol cada casilla a la que el robot acaba de llegar."""
        estados = self.animacion.camino_de_estados
        while self._paso_del_arbol < self.animacion.paso:
            self._paso_del_arbol += 1
            estado = estados[self._paso_del_arbol]
            self.arbol.avanzar_a_hijo(estado.posicion, estado)
            self._agregar_alternativas(self._paso_del_arbol)

    # ------------------------------------------------------------ eventos
    def reiniciar(self) -> None:
        self.animacion.reiniciar()
        self._construir_arbol()
        self._reiniciar_vista_final()

    def procesar_evento(self, evento):
        """Aplica un evento de pygame. Retorna SALIR, VOLVER o None."""
        if evento.type == pygame.QUIT:
            return SALIR
        if self.mostrando_resultados:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return VOLVER
            return self._procesar_evento_resultados(evento)
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return VOLVER
            if evento.key == pygame.K_RETURN and self.animacion.terminada:
                self.mostrando_resultados = True
            elif evento.key == pygame.K_SPACE:
                self.animacion.alternar_pausa()
            elif evento.key == pygame.K_RIGHT:
                self.animacion.paso_siguiente()
            elif evento.key == pygame.K_r:
                self.reiniciar()
            elif evento.key == pygame.K_UP:
                self.animacion.ajustar_velocidad(FACTOR_VELOCIDAD)
            elif evento.key == pygame.K_DOWN:
                self.animacion.ajustar_velocidad(1 / FACTOR_VELOCIDAD)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if BOTON_PAUSA.collidepoint(evento.pos):
                if self.animacion.terminada:
                    self.mostrando_resultados = True
                else:
                    self.animacion.alternar_pausa()
            elif BOTON_PASO.collidepoint(evento.pos):
                self.animacion.paso_siguiente()
            elif BOTON_REINICIAR.collidepoint(evento.pos):
                self.reiniciar()
            elif BOTON_INICIO.collidepoint(evento.pos):
                return VOLVER
        return None

    def _procesar_evento_resultados(self, evento):
        """Eventos de la pantalla de resultados. Retorna VOLVER o None."""
        accion = pantalla_resultados.procesar_evento(evento, self.arbol)
        if accion == pantalla_resultados.VER_MAPA:
            self.arbol.deseleccionar()  # el arbol pequeno del mapa no marca nodos elegidos
            self.mostrando_resultados = False
        elif accion == pantalla_resultados.REINICIAR:
            self.reiniciar()
        elif accion == pantalla_resultados.VOLVER:
            return VOLVER
        return None

    # ------------------------------------------------------------ reloj y dibujo
    def actualizar(self, dt_ms: int) -> None:
        self.animacion.update(dt_ms)
        self._sincronizar_arbol()
        if self.animacion.terminada and not self._resultados_ya_mostrados:
            self._ms_desde_la_meta += dt_ms
            if self._ms_desde_la_meta >= RETRASO_RESULTADOS_MS:
                self.mostrando_resultados = True
                self._resultados_ya_mostrados = True

    def dibujar(self, pantalla) -> None:
        mouse = pygame.mouse.get_pos()
        pantalla.fill(estilo.COLOR_FONDO)

        titulo = self.ejecucion.algoritmo.value + " · " + self.ejecucion.ruta_mundo.name
        fuente_titulo = estilo.fuente_pixel(22, 700)
        estilo.texto(pantalla, estilo.recortar(titulo, fuente_titulo, self.panel_mundo.rect.w),
                     fuente_titulo, estilo.COLOR_SALVIA, (ORIGEN_MUNDO[0], 22))

        if self.mostrando_resultados:
            pantalla_resultados.dibujar(pantalla, self.reporte, self.animacion, self.arbol, mouse)
            return

        self.animacion.dibujar(pantalla)
        self.reporte.dibujar(pantalla, AREA_REPORTE, self.animacion)
        self.arbol.dibujar(pantalla, AREA_ARBOL, NIVELES_VISIBLES_ARBOL)

        if self.animacion.terminada:
            etiqueta_pausa = "Resultados"  # al terminar, este boton abre la pantalla final
        else:
            etiqueta_pausa = "Seguir" if self.animacion.pausada else "Pausar"
        for rect, etiqueta, activo in (
                (BOTON_PAUSA, etiqueta_pausa, True),
                (BOTON_PASO, "Paso", not self.animacion.terminada),
                (BOTON_REINICIAR, "Reiniciar", True),
                (BOTON_INICIO, "Inicio", True)):
            estilo.dibujar_boton(pantalla, rect, etiqueta, activo, rect.collidepoint(mouse),
                                 tamano=TAMANO_LETRA_BOTON)

        pie = estilo.fuente_texto(14, 400)
        estilo.texto(pantalla, AYUDA, pie, estilo.COLOR_SALVIA_TENUE, (41, 723), ancla="midleft")
        estilo.texto(pantalla, AYUDA_SALIDA, pie, estilo.COLOR_SALVIA_TENUE, (1079, 723),
                     ancla="midright")

    def ejecutar(self, pantalla) -> str:
        """Bucle de la ventana. Retorna SALIR (cerro la ventana) o VOLVER (a la seleccion)."""
        reloj = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                accion = self.procesar_evento(evento)
                if accion is not None:
                    return accion
            self.actualizar(reloj.get_time())
            self.dibujar(pantalla)
            pygame.display.flip()
            reloj.tick(60)