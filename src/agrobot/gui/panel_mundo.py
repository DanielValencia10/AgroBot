"""
Archivo:       src/agrobot/gui/panel_mundo.py
Objetivo:      Dibujar la cuadricula 10x10 del mundo en su estado inicial: obstaculos,
               deposito, avioneta, cultivos secos y posicion inicial del robot.
Responsabilidad:
    SI hace:
        - Recorrer el Mundo cargado y dibujar cada casilla segun su tipo (libre,
          obstaculo, robot, cultivo seco, deposito, avioneta), usando los codigos de
          constantes.py como referencia de que representa cada uno.
    NO hace:
        - No anima movimientos (eso es responsabilidad de animacion.py).
        - No calcula ni conoce la solucion de busqueda.
        - No lee archivos de texto (recibe un Mundo ya construido).
Importa de:
    - modelo.mundo (Mundo): para conocer los elementos fijos del mundo a dibujar.
    - constantes: para los codigos de celda usados al decidir como dibujar cada
      casilla.
    - gui.cargador_sprites: Sprites.estatico(obtener_nombre_sprite_por_codigo(codigo))
      da la imagen de cada codigo de celda (es el unico archivo que conoce la ruta de
      assets/sprites/).
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
    - gui/animacion.py (puede reutilizar el dibujo base de la cuadricula antes de
      animar sobre ella).
Contrato previsto:
    - PanelMundo(mundo, sprites, origen=(0, 0), escala=1): componente de interfaz que
      dibuja la cuadricula 10x10 con su esquina superior izquierda en `origen`. `escala`
      es un factor ENTERO (1 = sprites de 64 px; 2 = 128 px...) para no deformar el
      pixel art.
    - dibujar(pantalla, estado=None, direccion="s"): dibuja el mundo en el estado dado
      (por omision, el inicial): casillas, obstaculos, deposito, la avioneta si sigue
      sin usar, los cultivos pendientes (secos) y los ya tratados, y al robot (a pie o
      en avioneta) mirando hacia `direccion` ("n", "e", "s" u "o").
    - dibujar_fondo(pantalla), dibujar_avioneta(pantalla, estado) y
      dibujar_cultivos(pantalla, estado) (dibujar_elementos hace las dos ultimas): las
      piezas de dibujar, para que animacion.py las combine con los actores en
      movimiento y con sus propias plantas animadas.
    - ampliar(imagen): la imagen a la escala del panel, para dibujar fuera de el.
    - rect_de_casilla(coordenada): pygame.Rect de una casilla (fila, columna) en pantalla.
    - rect: pygame.Rect de toda la cuadricula.
Decisiones de equipo:
    - La avioneta solo se dibuja en su casilla mientras no se ha usado (e=falso y
      k=COMBUSTIBLE_INICIAL_AVIONETA); al subirse el robot se va con el, y una vez
      agotada no vuelve a aparecer.
    - Una casilla de cultivo ya tratado (esta en Mundo.cultivos_secos pero no en P) se
      dibuja con el ultimo cuadro de la planta (verde).
Vista previa:
    Desde la carpeta src/:   python -m agrobot.gui.panel_mundo [archivo.txt]
"""
from __future__ import annotations

import sys
from pathlib import Path

import pygame

from .. import constantes
from ..modelo.estado import construir_estado_inicial
from ..modelo.mundo import Mundo
from . import estilo
from .cargador_sprites import Sprites

LADO_SPRITE = 64
GROSOR_MARCO = 2


class PanelMundo:
    def __init__(self, mundo: Mundo, sprites: Sprites, origen=(0, 0), escala: int = 1):
        if escala < 1 or int(escala) != escala:
            raise ValueError("La escala debe ser un entero mayor o igual a 1.")
        self.mundo = mundo
        self.sprites = sprites
        self.escala = int(escala)
        self.lado = LADO_SPRITE * self.escala
        lado_total = self.lado * constantes.TAMANO_CUADRICULA
        self.rect = pygame.Rect(origen[0], origen[1], lado_total, lado_total)
        self._ampliadas: dict = {}
        self._fondo = self._construir_fondo()

    # ------------------------------------------------------------ geometria
    def rect_de_casilla(self, coordenada) -> pygame.Rect:
        fila, columna = coordenada
        return pygame.Rect(self.rect.x + columna * self.lado,
                           self.rect.y + fila * self.lado, self.lado, self.lado)

    def ampliar(self, imagen: pygame.Surface) -> pygame.Surface:
        """La imagen a la escala del panel (sin suavizar), calculada una sola vez."""
        if self.escala == 1:
            return imagen
        clave = id(imagen)
        if clave not in self._ampliadas:
            self._ampliadas[clave] = pygame.transform.scale(imagen, (self.lado, self.lado))
        return self._ampliadas[clave]

    # ------------------------------------------------------------ dibujo
    def _construir_fondo(self) -> pygame.Surface:
        """Parte que nunca cambia: tierra, obstaculos y deposito."""
        fondo = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        suelo = self.ampliar(self.sprites.casilla_libre)
        obstaculo = self.ampliar(self.sprites.obstaculo)
        deposito = self.ampliar(self.sprites.deposito)
        for fila in range(constantes.TAMANO_CUADRICULA):
            for columna in range(constantes.TAMANO_CUADRICULA):
                destino = (columna * self.lado, fila * self.lado)
                if self.mundo.es_obstaculo((fila, columna)):
                    fondo.blit(obstaculo, destino)
                else:
                    fondo.blit(suelo, destino)
        fondo.blit(deposito, (self.mundo.deposito[1] * self.lado,
                              self.mundo.deposito[0] * self.lado))
        return fondo

    def dibujar_fondo(self, pantalla) -> None:
        pantalla.blit(self._fondo, self.rect)
        pygame.draw.rect(pantalla, estilo.COLOR_BORDE,
                         self.rect.inflate(2 * GROSOR_MARCO, 2 * GROSOR_MARCO),
                         GROSOR_MARCO)

    def dibujar_elementos(self, pantalla, estado=None) -> None:
        """Avioneta sin usar y cultivos (secos y tratados); no dibuja al robot."""
        if estado is None:
            estado = self._estado_inicial()
        self.dibujar_avioneta(pantalla, estado)
        self.dibujar_cultivos(pantalla, estado)

    def dibujar_avioneta(self, pantalla, estado) -> None:
        """La avioneta en su casilla original, solo mientras no se ha usado."""
        sin_usar = (not estado.en_avioneta
                    and estado.combustible == constantes.COMBUSTIBLE_INICIAL_AVIONETA)
        if sin_usar:
            pantalla.blit(self.ampliar(self.sprites.avioneta_base),
                          self.rect_de_casilla(self.mundo.avioneta))

    def dibujar_cultivos(self, pantalla, estado) -> None:
        """Cada cultivo del mundo: seco si sigue en P, tratado si ya salio de P."""
        seco = self.ampliar(self.sprites.cultivo[0])
        tratado = self.ampliar(self.sprites.cultivo[-1])
        for coordenada in self.mundo.cultivos_secos:
            imagen = seco if coordenada in estado.pendientes else tratado
            pantalla.blit(imagen, self.rect_de_casilla(coordenada))

    def dibujar(self, pantalla, estado=None, direccion: str = "s") -> None:
        if estado is None:
            estado = self._estado_inicial()
        self.dibujar_fondo(pantalla)
        self.dibujar_elementos(pantalla, estado)
        grupo = self.sprites.avioneta if estado.en_avioneta else self.sprites.robot
        pantalla.blit(self.ampliar(grupo[(direccion, 0)]),
                      self.rect_de_casilla(estado.posicion))

    def _estado_inicial(self):
        return construir_estado_inicial(self.mundo)


def _vista_previa() -> None:
    """Abre una ventana con el mundo en su estado inicial (no es el punto de entrada)."""
    from ..archivos.lector_mundo import leer_mundo_desde_archivo
    from .cargador_sprites import cargar_sprites

    raiz = Path(__file__).resolve().parents[3]
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "mundos" / "Prueba1.txt"
    pantalla = _abrir_ventana()
    panel = PanelMundo(leer_mundo_desde_archivo(ruta), cargar_sprites(), origen=(0, 0))
    panel.rect.center = pantalla.get_rect().center
    reloj = pygame.time.Clock()
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (
                    evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                ejecutando = False
        pantalla.fill(estilo.COLOR_FONDO)
        panel.dibujar(pantalla)
        pygame.display.flip()
        reloj.tick(30)
    pygame.quit()


def _abrir_ventana():
    from .pantalla_inicio import crear_ventana
    return crear_ventana()


if __name__ == "__main__":
    _vista_previa()

