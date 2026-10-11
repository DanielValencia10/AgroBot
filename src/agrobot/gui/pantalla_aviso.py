"""
Archivo:       src/agrobot/gui/pantalla_aviso.py
Objetivo:      Mostrar un aviso sencillo sobre fondo oscuro (por ejemplo "este algoritmo aun
               no esta implementado" o "el archivo de mundo no es valido") y esperar a
               que el usuario lo cierre.
Responsabilidad:
    SI hace:
        - Dibujar una tarjeta con titulo, mensaje (en varias lineas si hace falta) y un
          boton "Volver", con la paleta y tipografias de estilo.py.
        - Cerrarse con el boton, Enter o Esc.
    NO hace:
        - No decide cuando mostrar un aviso ni que hacer despues: lo hace main.py.
Importa de:
    - gui.estilo, pygame (pygame-ce).
Lo importan:
    - main.py.
Contrato previsto:
    - mostrar_aviso(pantalla, titulo, mensaje): bloquea hasta que el usuario lo cierre.
      Retorna True, o False si cerro la ventana (la aplicacion debe terminar).
    - procesar_evento(evento): "cerrar", "salir" o None (sin dibujo; se puede probar).
"""
from __future__ import annotations

import pygame

from . import estilo

TARJETA = pygame.Rect(240, 250, 640, 260)
BOTON = pygame.Rect(440, 430, 240, 52)
ANCHO_TEXTO = TARJETA.w - 80


def procesar_evento(evento):
    """Retorna "cerrar" (boton, Enter o Esc), "salir" (cerro la ventana) o None."""
    if evento.type == pygame.QUIT:
        return "salir"
    if evento.type == pygame.KEYDOWN and evento.key in (
            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
        return "cerrar"
    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and BOTON.collidepoint(evento.pos):
        return "cerrar"
    return None


def _dibujar(pantalla, titulo, mensaje) -> None:
    pantalla.fill(estilo.COLOR_FONDO)
    estilo.dibujar_tarjeta(pantalla, TARJETA)
    estilo.texto(pantalla, titulo, estilo.fuente_pixel(26, 700), estilo.COLOR_LINO,
                 (TARJETA.centerx, TARJETA.y + 30), ancla="midtop")
    fuente = estilo.fuente_texto(18, 400)
    y = TARJETA.y + 86
    for linea in estilo.envolver(mensaje, fuente, ANCHO_TEXTO):
        estilo.texto(pantalla, linea, fuente, estilo.COLOR_CREMA, (TARJETA.centerx, y),
                     ancla="midtop")
        y += 26
    estilo.dibujar_boton(pantalla, BOTON, "Volver", True, BOTON.collidepoint(pygame.mouse.get_pos()))


def mostrar_aviso(pantalla, titulo: str, mensaje: str) -> bool:
    reloj = pygame.time.Clock()
    while True:
        for evento in pygame.event.get():
            accion = procesar_evento(evento)
            if accion == "salir":
                return False
            if accion == "cerrar":
                return True
        _dibujar(pantalla, titulo, mensaje)
        pygame.display.flip()
        reloj.tick(60)
