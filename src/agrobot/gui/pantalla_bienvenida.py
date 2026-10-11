"""
Archivo:       src/agrobot/gui/pantalla_bienvenida.py
Objetivo:      Mostrar la primera pantalla de AgroBot: el saludo "Bienvenido a AgroBot"
               con la matica y el boton "Iniciar" que lleva a la pantalla de seleccion.
Responsabilidad:
    SI hace:
        - Dibujar la bienvenida segun el mockup "1 - Bienvenida": saludo, titulo,
          matica sobre un circulo, boton "Iniciar" y la ayuda de teclas.
        - Avisar a quien la llamo cuando el usuario pulsa "Iniciar" (clic o Enter) o
          quiere salir (cerrar la ventana o Esc).
    NO hace:
        - No elige mundo ni algoritmo (eso es de pantalla_seleccion.py).
        - No decide que pantalla viene despues: lo hace pantalla_inicio.py.
Importa de:
    - gui.estilo: colores, tipografias, matica y utilidades de dibujo.
    - pygame (pygame-ce).
Lo importan:   gui/pantalla_inicio.py.
Contrato previsto:
    - PantallaBienvenida().ejecutar(pantalla): muestra la pantalla sobre la superficie de
      pygame dada y bloquea hasta que el usuario decide. Retorna "iniciar" o None
      (None = cerrar la aplicacion).
    - PantallaBienvenida().procesar_evento(evento): aplica un evento y retorna
      "iniciar", "salir" o None (se puede probar sin abrir una ventana).
"""
from __future__ import annotations

import pygame

from . import estilo

BOTON_INICIAR = pygame.Rect(431, 594, 257, 66)
CENTRO_CIRCULO = (560, 388)
RADIO_CIRCULO = 210
UNIDAD_MATICA = 13
ESQUINA_MATICA = (463, 317)
ANCHO_TITULO = 512
LINEA_BASE_TITULO = 238     # donde apoyan las letras de 'AgroBot' en el mockup


class PantallaBienvenida:
    # ================================================================
    # Eventos (sin dibujo: se puede probar sin ventana)
    # ================================================================
    def procesar_evento(self, evento):
        """Aplica un evento de pygame. Retorna "iniciar", "salir" o None."""
        if evento.type == pygame.QUIT:
            return "salir"
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "salir"
            if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "iniciar"
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if BOTON_INICIAR.collidepoint(evento.pos):
                return "iniciar"
        return None

    # ================================================================
    # Bucle principal
    # ================================================================
    def ejecutar(self, pantalla):
        """Muestra la pantalla. Retorna "iniciar", o None si se cierra."""
        reloj = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                accion = self.procesar_evento(evento)
                if accion == "salir":
                    return None
                if accion == "iniciar":
                    return "iniciar"
            self._dibujar(pantalla)
            pygame.display.flip()
            reloj.tick(60)

    # ================================================================
    # Dibujo
    # ================================================================
    def _dibujar(self, pantalla) -> None:
        mouse = pygame.mouse.get_pos()
        pantalla.fill(estilo.COLOR_FONDO)
        centro_x = estilo.ANCHO_VENTANA // 2

        estilo.texto_espaciado(pantalla, "BIENVENIDO A", estilo.fuente_pixel(22, 700),
                               estilo.COLOR_SALVIA, (centro_x, 117), 5)

        # Circulo y matica (el circulo va detras del titulo)
        pygame.draw.circle(pantalla, estilo.COLOR_CIRCULO, CENTRO_CIRCULO, RADIO_CIRCULO)
        estilo.dibujar_matica(pantalla, ESQUINA_MATICA[0], ESQUINA_MATICA[1], UNIDAD_MATICA)

        self._dibujar_titulo(pantalla, centro_x)
        estilo.dibujar_boton(pantalla, BOTON_INICIAR, "Iniciar", True,
                             BOTON_INICIAR.collidepoint(mouse))

        pie = estilo.fuente_texto(14, 400)
        estilo.texto(pantalla, "Inteligencia Artificial · Universidad del Valle", pie,
                     estilo.COLOR_SALVIA_TENUE, (41, 723), ancla="midleft")
        estilo.texto(pantalla, "Enter: iniciar · Esc: salir", pie,
                     estilo.COLOR_SALVIA_TENUE, (1079, 723), ancla="midright")

    @staticmethod
    def _dibujar_titulo(pantalla, centro_x) -> None:
        """'AgroBot' en dos tonos: 'Agro' en salvia y 'Bot' en lino, centrado y de 512 px."""
        fuente = estilo.fuente_pixel_ajustada("AgroBot", ANCHO_TITULO, 700)
        ancho_agro = fuente.size("Agro")[0]
        ancho_bot = fuente.size("Bot")[0]
        x = centro_x - (ancho_agro + ancho_bot) // 2
        estilo.texto_linea_base(pantalla, "Agro", fuente, estilo.COLOR_SALVIA, x, LINEA_BASE_TITULO)
        estilo.texto_linea_base(pantalla, "Bot", fuente, estilo.COLOR_LINO, x + ancho_agro,
                                LINEA_BASE_TITULO)
