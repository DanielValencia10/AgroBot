"""
Archivo:       src/agrobot/gui/pantalla_resultados.py
Objetivo:      Mostrar, cuando el robot termina el recorrido, el reporte de la busqueda y
               el arbol de exploracion COMPLETO (desde la raiz), con los botones
               agrupados abajo. Al elegir un nodo del arbol, el panel de la izquierda
               muestra el estado que habia en ese nodo.
Responsabilidad:
    SI hace:
        - Dibujar la tarjeta de informacion (izquierda): algoritmo, mensaje (META
          ALCANZADA / SIN SOLUCION, o el tipo de nodo si hay uno elegido), metricas de la
          busqueda (nodos expandidos, profundidad, tiempo y, si aplica, costo total) y el
          estado del robot: el final, o el del nodo elegido (con su costo acumulado si
          el algoritmo lo calcula).
        - Dibujar el arbol de exploracion (derecha) completo, desde la raiz hasta la
          meta, en toda el area disponible, marcando el nodo elegido y el que toca el
          mouse.
        - Dibujar tres botones centrados abajo: Ver mapa, Reiniciar e Inicio.
        - Traducir un evento de teclado o de mouse en una accion (VER_MAPA, REINICIAR o
          VOLVER), o None si el evento no hace nada aqui. Un clic dentro del arbol elige
          el nodo tocado (o quita la eleccion si no toca ninguno) y las flechas mueven la
          eleccion; en ambos casos retorna None porque no cambia de pantalla.
    NO hace:
        - No calcula metricas ni construye el arbol: usa el PanelReporte y el
          ArbolExploracion que le entrega la ventana principal.
        - No maneja el cierre de la ventana ni Esc: eso lo resuelve ventana_principal.py
          antes de delegar aqui.
        - No tiene bucle propio: la ventana principal decide cuando mostrarla.
Importa de:
    - gui.estilo (colores, fuentes, tarjeta y boton).
    - gui.panel_reporte (PanelReporte): para reutilizar las filas de metricas.
Lo importan:
    - gui/ventana_principal.py.
Contrato previsto:
    - dibujar(pantalla, reporte, animacion, arbol, mouse): pinta la pantalla completa
      (sin el titulo, que lo pinta la ventana principal).
    - procesar_evento(evento, arbol=None): retorna VER_MAPA, REINICIAR, VOLVER o None.
      Con `arbol` tambien atiende la eleccion de nodos (clic y flechas).
    - contenido_de_informacion(reporte, animacion, arbol): (mensaje, subtitulo, filas)
      de la parte "estado del robot" del panel, segun haya o no un nodo elegido.
"""
from __future__ import annotations

import pygame

from . import estilo
from .panel_reporte import PanelReporte

VER_MAPA = "ver_mapa"
REINICIAR = "reiniciar"
VOLVER = "volver"

AREA_INFO = pygame.Rect(40, 64, 420, 570)
AREA_ARBOL = pygame.Rect(480, 64, 600, 570)

ANCHO_BOTON = 240
ALTO_BOTON = 46
SEPARACION_BOTONES = 20
Y_BOTONES = 668
TAMANO_LETRA_BOTON = 17
_X_BOTONES = (estilo.ANCHO_VENTANA - (3 * ANCHO_BOTON + 2 * SEPARACION_BOTONES)) // 2


def _rect_boton(posicion: int) -> pygame.Rect:
    return pygame.Rect(_X_BOTONES + posicion * (ANCHO_BOTON + SEPARACION_BOTONES),
                       Y_BOTONES, ANCHO_BOTON, ALTO_BOTON)


BOTON_MAPA = _rect_boton(0)
BOTON_REINICIAR = _rect_boton(1)
BOTON_INICIO = _rect_boton(2)

ESCALA_ARBOL = 1.0          # con el arbol completo, la escala normal es la que mejor cabe
NIVELES_VISIBLES_ARBOL = None  # None = dibujar el arbol completo desde la raiz

DIRECCIONES_TECLADO = {
    pygame.K_UP: "arriba",
    pygame.K_DOWN: "abajo",
    pygame.K_LEFT: "izquierda",
    pygame.K_RIGHT: "derecha",
}

MARGEN = 26
ALTO_FILA = 36
AYUDA = ("Clic o flechas: ver un nodo · Clic fuera: volver al final · "
         "Enter: ver mapa · R: reiniciar · Esc: volver a la seleccion")


def procesar_evento(evento, arbol=None):
    """Retorna VER_MAPA, REINICIAR, VOLVER o None segun el evento. Si se pasa el arbol,
    un clic dentro de el elige el nodo tocado y las flechas mueven la eleccion."""
    if evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_RETURN:
            return VER_MAPA
        if evento.key == pygame.K_r:
            return REINICIAR
        if arbol is not None and evento.key in DIRECCIONES_TECLADO:
            arbol.mover_seleccion(DIRECCIONES_TECLADO[evento.key])
    elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
        if BOTON_MAPA.collidepoint(evento.pos):
            return VER_MAPA
        if BOTON_REINICIAR.collidepoint(evento.pos):
            return REINICIAR
        if BOTON_INICIO.collidepoint(evento.pos):
            return VOLVER
        if arbol is not None and AREA_ARBOL.collidepoint(evento.pos):
            arbol.seleccionar_en(evento.pos)
    return None


def _mensaje_del_nodo(reporte, animacion, arbol, nodo):
    """(texto, color) que describe el nodo elegido."""
    if not reporte.resultado.solucion_encontrada:
        return reporte.mensaje(animacion)
    if nodo is arbol.actual and animacion.terminada:
        return "META ALCANZADA", estilo.COLOR_LINO
    if arbol.esta_en_la_ruta(nodo):
        return "NODO DE LA RUTA", estilo.COLOR_OLIVA
    return "NODO ALTERNATIVO", estilo.COLOR_SALVIA_TENUE


def contenido_de_informacion(reporte, animacion, arbol=None):
    """(mensaje, subtitulo, filas) de la parte "estado del robot" del panel.

    Sin nodo elegido es el estado final de la animacion. Con un nodo elegido (y con
    estado conocido) es el estado que habia en ese nodo: su paso, su posicion, el
    fertilizante, el combustible, etc., y su costo acumulado si el algoritmo lo calcula."""
    nodo = arbol.seleccionado if arbol is not None else None
    if nodo is None or nodo.estado is None:
        return (reporte.mensaje(animacion), "ESTADO FINAL DEL ROBOT",
                PanelReporte.filas_del_robot(animacion))

    profundidad = nodo.profundidad
    if arbol.esta_en_la_ruta(nodo):
        paso = str(profundidad) + "/" + str(animacion.total_pasos)
    else:
        paso = str(profundidad) + " · alternativa"
    costo = nodo.costo if reporte.resultado.costo_total is not None else None
    return (_mensaje_del_nodo(reporte, animacion, arbol, nodo), "ESTADO EN EL NODO",
            PanelReporte.filas_del_estado(nodo.estado, paso, costo))


def _dibujar_filas(pantalla, filas, izquierda, derecha, y, alto_fila=ALTO_FILA) -> int:
    """Pinta pares (etiqueta, valor) en letra grande; retorna la y donde terminan."""
    fuente_etiqueta = estilo.fuente_texto(19, 400)
    fuente_valor = estilo.fuente_texto(22, 700)
    for etiqueta, valor in filas:
        resaltada = etiqueta in ("Costo total", "Costo acumulado")
        color_valor = estilo.COLOR_LINO if resaltada else estilo.COLOR_CREMA
        estilo.texto(pantalla, etiqueta, fuente_etiqueta, estilo.COLOR_SALVIA_TENUE,
                     (izquierda, y + 6))
        estilo.texto(pantalla, valor, fuente_valor, color_valor, (derecha, y), ancla="topright")
        y += alto_fila
    return y


def _dibujar_subtitulo(pantalla, texto, izquierda, derecha, y) -> int:
    estilo.texto(pantalla, texto, estilo.fuente_pixel(14, 700), estilo.COLOR_OLIVA, (izquierda, y))
    pygame.draw.line(pantalla, estilo.COLOR_BORDE, (izquierda, y + 22), (derecha, y + 22), 2)
    return y + 32


def _dibujar_informacion(pantalla, reporte, animacion, arbol=None) -> None:
    area = AREA_INFO
    estilo.dibujar_tarjeta(pantalla, area, radio=18)
    izquierda = area.x + MARGEN
    derecha = area.right - MARGEN
    y = area.y + MARGEN

    titulo = estilo.fuente_pixel(26, 700)
    estilo.texto(pantalla, estilo.recortar(reporte.algoritmo, titulo, derecha - izquierda),
                 titulo, estilo.COLOR_SALVIA, (izquierda, y))
    y += 48

    mensaje, subtitulo, filas_robot = contenido_de_informacion(reporte, animacion, arbol)
    if mensaje is not None:
        estilo.texto(pantalla, mensaje[0], estilo.fuente_pixel(20, 700), mensaje[1], (izquierda, y))
    y += 44

    # Si hay filas de mas (costo acumulado), las filas se juntan un poco para que quepan.
    filas_busqueda = reporte.filas_de_busqueda()
    fijo = 32 + 12 + 32  # dos subtitulos y el espacio entre bloques
    disponible = area.bottom - MARGEN - y - fijo
    alto_fila = max(24, min(ALTO_FILA, disponible // (len(filas_busqueda) + len(filas_robot))))

    y = _dibujar_subtitulo(pantalla, "BÚSQUEDA", izquierda, derecha, y)
    y = _dibujar_filas(pantalla, filas_busqueda, izquierda, derecha, y, alto_fila)
    y += 12
    y = _dibujar_subtitulo(pantalla, subtitulo, izquierda, derecha, y)
    _dibujar_filas(pantalla, filas_robot, izquierda, derecha, y, alto_fila)


def dibujar(pantalla, reporte, animacion, arbol, mouse) -> None:
    """Pinta la informacion grande, el arbol completo y los tres botones."""
    _dibujar_informacion(pantalla, reporte, animacion, arbol)
    arbol.dibujar(pantalla, AREA_ARBOL, NIVELES_VISIBLES_ARBOL, escala=ESCALA_ARBOL, mouse=mouse)

    for rect, etiqueta in ((BOTON_MAPA, "Ver mapa"), (BOTON_REINICIAR, "Reiniciar"),
                           (BOTON_INICIO, "Inicio")):
        estilo.dibujar_boton(pantalla, rect, etiqueta, True, rect.collidepoint(mouse),
                             tamano=TAMANO_LETRA_BOTON)

    estilo.texto(pantalla, AYUDA, estilo.fuente_texto(14, 400), estilo.COLOR_SALVIA_TENUE,
                 (estilo.ANCHO_VENTANA // 2, 742), ancla="center")