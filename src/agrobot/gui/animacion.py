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
    - PanelAnimacion(panel_mundo, sprites, resultado, estado_inicial): reproduce el
      camino del Resultado sobre el PanelMundo con los actores de arriba: el robot gira,
      camina de una casilla a la otra, se monta en la avioneta (y baja cuando se agota)
      y las plantas pasan de secas a tratadas al fertilizarlas. Si el Resultado no tiene
      solucion solo muestra el estado inicial.
        - update(dt_ms) y dibujar(pantalla): avanzar el reloj y pintar el cuadro actual.
        - alternar_pausa(), paso_siguiente(), reiniciar(), ajustar_velocidad(factor).
        - paso, total_pasos, terminada, pausada, estado_actual, direccion_actual y
          en_movimiento: lo que la ventana necesita para sincronizar el arbol y el
          reporte. `paso` solo aumenta cuando el robot LLEGA a la siguiente casilla.
Decisiones de equipo (antes PENDIENTE):
    - Reproduccion automatica y paso a paso: en automatico los pasos se encadenan; con
      paso_siguiente() se pausa y se recorre UN movimiento completo (con su animacion).
    - Velocidad: ms_por_paso (400 por omision, como la Demo), entre 100 y 1200.
Referencia:
    La logica sale de assets/sprites/ejemplo_pygame.py y ejemplo_planta_pygame.py, que
    pueden ejecutarse solos para ver el resultado esperado.
"""
from __future__ import annotations

from ..modelo.movimiento import Movimiento
from .cargador_sprites import ANILLO_DIRECCIONES, DIRECCIONES_DIAGONALES, Sprites

MS_PASO = 170    # duracion de cada cuadro de la caminata del robot
MS_HELICE = 55   # duracion de cada estado de la helice
MS_GIRO = 70     # duracion de cada cuadro intermedio al girar
MS_CRECIMIENTO = 130  # duracion de cada cuadro de la transicion de la planta

MS_POR_PASO = 400     # tiempo que tarda el robot en cruzar una casilla (como la Demo)
MS_POR_PASO_MIN = 100
MS_POR_PASO_MAX = 1200

CICLO_ROBOT = (0, 1, 0, 2)    # reposo, adelante, reposo, atras
CICLO_HELICE = (0, 1, 2, 1)

DIRECCION_DE_MOVIMIENTO = {
    Movimiento.ARRIBA: "n",
    Movimiento.ABAJO: "s",
    Movimiento.IZQUIERDA: "o",
    Movimiento.DERECHA: "e",
}


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


class PanelAnimacion:
    """Reproduce el camino de un Resultado sobre un PanelMundo."""

    def __init__(self, panel_mundo, sprites: Sprites, resultado, estado_inicial):
        self.panel = panel_mundo
        self.sprites = sprites
        if resultado.solucion_encontrada and resultado.camino_de_estados:
            self._estados = tuple(resultado.camino_de_estados)
            self._movimientos = tuple(resultado.camino_de_movimientos)
        else:
            self._estados = (estado_inicial,)
            self._movimientos = ()
        self.ms_por_paso = MS_POR_PASO
        self.reiniciar()

    # ------------------------------------------------------------ estado
    @property
    def total_pasos(self) -> int:
        return len(self._movimientos)

    @property
    def terminada(self) -> bool:
        return self.paso >= self.total_pasos

    @property
    def estado_actual(self):
        """Estado de la ultima casilla a la que llego el robot."""
        return self._estados[self.paso]

    @property
    def direccion_actual(self) -> str:
        return self._actor.direccion

    @property
    def en_movimiento(self) -> bool:
        return self._en_movimiento

    # ------------------------------------------------------------ controles
    def reiniciar(self) -> None:
        self.paso = 0
        self.pausada = False
        self._solo_un_paso = False
        self._en_movimiento = False
        self._t_movimiento = 0
        self._plantas = {
            coordenada: PlantaCultivo(self.sprites)
            for coordenada in self.panel.mundo.cultivos_secos
        }
        self._actor = self._crear_actor(self._estados[0], "s")

    def alternar_pausa(self) -> None:
        self.pausada = not self.pausada
        self._solo_un_paso = False

    def paso_siguiente(self) -> None:
        """Pausa y recorre un movimiento completo (con su animacion)."""
        if self.terminada:
            return
        self.pausada = True
        self._solo_un_paso = True

    def ajustar_velocidad(self, factor: float) -> None:
        """factor > 1 acelera, factor < 1 ralentiza (limitado a 100-1200 ms por paso)."""
        nuevo = int(self.ms_por_paso / factor)
        self.ms_por_paso = max(MS_POR_PASO_MIN, min(MS_POR_PASO_MAX, nuevo))

    # ------------------------------------------------------------ reloj
    def update(self, dt_ms: int) -> None:
        self._actor.update(dt_ms)
        for planta in self._plantas.values():
            planta.update(dt_ms)

        puede_avanzar = (not self.pausada or self._solo_un_paso) and not self.terminada
        if not puede_avanzar:
            self._actor.moviendo = False
            return

        if not self._en_movimiento:
            self._en_movimiento = True
            self._t_movimiento = 0
            self._actor.mirar(DIRECCION_DE_MOVIMIENTO[self._movimientos[self.paso]])
        if self._actor.girando:  # primero gira, despues camina
            self._actor.moviendo = False
            return

        self._actor.moviendo = True
        self._t_movimiento += dt_ms
        if self._t_movimiento >= self.ms_por_paso:
            self._llegar()

    def _llegar(self) -> None:
        anterior = self._estados[self.paso]
        self.paso += 1
        nuevo = self._estados[self.paso]
        self._en_movimiento = False
        self._t_movimiento = 0
        self._solo_un_paso = False
        self._actor.moviendo = False
        for coordenada in anterior.pendientes - nuevo.pendientes:
            self._plantas[coordenada].regar()
        if nuevo.en_avioneta != anterior.en_avioneta:  # se monto o se agoto la avioneta
            self._actor = self._crear_actor(nuevo, self._actor.direccion)

    def _crear_actor(self, estado, direccion: str):
        clase = ActorAvioneta if estado.en_avioneta else ActorRobot
        return clase(self.sprites, direccion)

    # ------------------------------------------------------------ dibujo
    def dibujar(self, pantalla) -> None:
        panel = self.panel
        panel.dibujar_fondo(pantalla)
        panel.dibujar_avioneta(pantalla, self.estado_actual)
        for coordenada, planta in self._plantas.items():
            pantalla.blit(panel.ampliar(planta.imagen()), panel.rect_de_casilla(coordenada))
        pantalla.blit(panel.ampliar(self._actor.imagen()), self._posicion_del_actor())

    def _posicion_del_actor(self) -> tuple:
        origen = self.panel.rect_de_casilla(self.estado_actual.posicion)
        if not self._en_movimiento or self._actor.girando or self.terminada:
            return origen.topleft
        destino = self.panel.rect_de_casilla(self._estados[self.paso + 1].posicion)
        avance = min(1.0, self._t_movimiento / self.ms_por_paso)
        return (round(origen.x + (destino.x - origen.x) * avance),
                round(origen.y + (destino.y - origen.y) * avance))
