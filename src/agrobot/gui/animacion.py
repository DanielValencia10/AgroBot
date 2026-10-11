"""
Archivo:       src/agrobot/gui/animacion.py
Objetivo:      Reproducir visualmente, paso a paso, los movimientos del camino
               solucion contenido en un Resultado, sobre la cuadricula dibujada por
               panel_mundo.py.
Responsabilidad:
    SI hace:
        - Recorrer la lista de movimientos del Resultado en orden y, para cada uno,
          actualizar la posicion visual del robot (y, si aplica, de la avioneta) sobre
          la cuadricula.
        - Decidir QUE cuadro de cada sprite se ve en cada instante (caminata del robot,
          helice de la avioneta, giro por el anillo de 8 direcciones y crecimiento de la
          planta al fertilizarla), con los tiempos definidos aqui abajo.
    NO hace:
        - No calcula el camino solucion (eso lo hace el algoritmo de busqueda elegido).
        - No dibuja el estado inicial completo de la cuadricula (eso es de
          panel_mundo.py; animacion.py dibuja sobre esa base).
        - No lee archivos de imagen: recibe un Sprites ya cargado.
Importa de:
    - busqueda.resultado (Resultado): para leer el camino de movimientos a animar.
    - modelo.movimiento (Movimiento): para traducir cada movimiento en un
      desplazamiento visual (fila, columna).
    - modelo.mundo (Mundo): para conocer el contexto fijo sobre el que se anima
      (limites, obstaculos, etc.).
    - gui.cargador_sprites: Sprites y ANILLO_DIRECCIONES (es el unico archivo que conoce
      la ruta de assets/sprites/).
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
Contrato previsto:
    - camino_giro(origen, destino): direcciones intermedias, por el lado mas corto del
      anillo de 8 direcciones, hasta llegar a destino (incluido).
    - ActorRobot / ActorAvioneta(sprites, direccion="s"): mirar(destino), update(dt_ms),
      imagen(). Quien los use pone `moviendo = True` mientras avanzan de casilla; el robot solo
      camina (cuadros 0,1,0,2) cuando se mueve y no esta girando; la helice de la
      avioneta gira siempre. Entre dos direcciones no vecinas pasan por los cuadros
      intermedios de giro (diagonales del robot, 8 direcciones de la avioneta).
    - PlantaCultivo(sprites): regar(), reiniciar(), update(dt_ms), imagen(), y la
      propiedad `tratada`. Recorre los 9 cuadros de la transicion seca -> tratada.
    - PanelAnimacion: componente de interfaz que, dado un Resultado y el Mundo sobre
      el que se calculo, reproduce visualmente el camino de movimientos de la
      solucion (PENDIENTE: usa los actores de arriba).
PENDIENTE:
    - PanelAnimacion (depende de Resultado, Mundo y panel_mundo, aun sin implementar).
    - Velocidad/control de reproduccion de la animacion (automatica, paso a paso por
      el usuario, o ambas).
Referencia:
    La logica sale de assets/sprites/ejemplo_pygame.py y ejemplo_planta_pygame.py, que
    pueden ejecutarse solos para ver el resultado esperado.
"""
from __future__ import annotations

from .cargador_sprites import ANILLO_DIRECCIONES, DIRECCIONES_DIAGONALES, Sprites

MS_PASO = 170    # duracion de cada cuadro de la caminata del robot
MS_HELICE = 55   # duracion de cada estado de la helice
MS_GIRO = 70     # duracion de cada cuadro intermedio al girar
MS_CRECIMIENTO = 130  # duracion de cada cuadro de la transicion de la planta

CICLO_ROBOT = (0, 1, 0, 2)    # reposo, adelante, reposo, atras
CICLO_HELICE = (0, 1, 2, 1)


def camino_giro(origen: str, destino: str) -> list:
    """Direcciones intermedias por el lado mas corto del anillo (incluye el destino)."""
    n = len(ANILLO_DIRECCIONES)
    i, j = ANILLO_DIRECCIONES.index(origen), ANILLO_DIRECCIONES.index(destino)
    paso = 1 if (j - i) % n <= n // 2 else -1
    ruta = []
    while i != j:
        i = (i + paso) % n
        ruta.append(ANILLO_DIRECCIONES[i])
    return ruta


class _Actor:
    """Direccion, giro progresivo y reloj de animacion comunes al robot y la avioneta."""

    def __init__(self, sprites: Sprites, direccion: str = "s"):
        self._sprites = sprites
        self.direccion = direccion
        self.moviendo = False
        self._pendientes: list = []  # direcciones por mostrar antes de llegar al destino
        self._t_giro = 0
        self._t = 0

    @property
    def girando(self) -> bool:
        return bool(self._pendientes)

    def mirar(self, destino: str) -> None:
        ultimo = self._pendientes[-1] if self._pendientes else self.direccion
        if destino != ultimo:
            self._pendientes += camino_giro(ultimo, destino)

    def update(self, dt_ms: int) -> None:
        self._t += dt_ms
        if self._pendientes:
            self._t_giro += dt_ms
            if self._t_giro >= MS_GIRO:
                self._t_giro = 0
                self.direccion = self._pendientes.pop(0)


class ActorRobot(_Actor):
    """El robot a pie: camina al moverse y pasa por las diagonales al girar."""

    def imagen(self):
        if self.direccion in DIRECCIONES_DIAGONALES:
            return self._sprites.robot_giro[self.direccion]
        caminando = self.moviendo and not self.girando
        k = CICLO_ROBOT[(self._t // MS_PASO) % len(CICLO_ROBOT)] if caminando else 0
        return self._sprites.robot[(self.direccion, k)]


class ActorAvioneta(_Actor):
    """El robot montado en la avioneta: la helice gira siempre."""

    def imagen(self):
        k = CICLO_HELICE[(self._t // MS_HELICE) % len(CICLO_HELICE)]
        return self._sprites.avioneta[(self.direccion, k)]


class PlantaCultivo:
    """Un cultivo: seco al inicio, y al regarlo recorre la transicion hasta tratado."""

    def __init__(self, sprites: Sprites):
        self._cuadros = sprites.cultivo
        self._indice = 0
        self._animando = False
        self._t = 0

    @property
    def tratada(self) -> bool:
        return self._indice == len(self._cuadros) - 1

    def regar(self) -> None:
        if not self.tratada:
            self._animando = True

    def reiniciar(self) -> None:
        self._indice, self._animando, self._t = 0, False, 0

    def update(self, dt_ms: int) -> None:
        if not self._animando:
            return
        self._t += dt_ms
        if self._t >= MS_CRECIMIENTO:
            self._t = 0
            self._indice += 1
            if self.tratada:
                self._animando = False

    def imagen(self):
        return self._cuadros[self._indice]
