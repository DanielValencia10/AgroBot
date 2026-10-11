"""
Archivo:       src/agrobot/gui/cargador_sprites.py
Objetivo:      Cargar los sprites desde assets/sprites/ y entregarlos ya organizados a los
               paneles que dibujan la cuadricula y la animacion, siendo el unico archivo
               del proyecto que conoce la ruta de assets/.
Responsabilidad:
    SI hace:
        - Cargar desde disco cada imagen de las subcarpetas de assets/sprites/ (robot/,
          avioneta/, cultivo/, deposito/ y mundo/; ver assets/README.md) y mantenerlas
          en memoria, agrupadas en un objeto Sprites.
        - Comprobar al cargar que no falte ningun archivo, con un error que diga cual.
        - Exponer la correspondencia entre cada codigo de celda del archivo de mundo
          (0 a 5, segun constantes.py) y el nombre del sprite que le corresponde por
          defecto (por ejemplo, codigo 3 -> "cultivo"; el cambio a la planta tratada y
          el robot sobre la avioneta lo decide cada panel segun el estado dinamico).
    NO hace:
        - No decide en que posicion de la cuadricula se dibuja cada sprite ni cuando
          cambia de cuadro: los tiempos y los giros son de animacion.py.
        - No conoce Estado ni logica de busqueda: solo traduce codigos / nombres a
          imagenes.
        - No lo usa ningun archivo fuera de gui/ (es el unico que conoce assets/).
Importa de:
    - pygame (pygame-ce).
    - (constantes.py, cuando defina los CODIGO_*: hoy los codigos 0 a 5 van literales).
Lo importan:
    - gui/panel_mundo.py (dibujo base de la cuadricula).
    - gui/animacion.py (cuadros de caminata, giro, helice y crecimiento de la planta).
Contrato previsto:
    - cargar_sprites(raiz=RAIZ_SPRITES): retorna un Sprites con las imagenes cargadas.
      Lanza FileNotFoundError si falta algun archivo esperado.
    - Sprites: robot[(dir, k)] (dir en "nseo", k en 0..2: 0 = reposo, 1 = paso hacia
      adelante, 2 = paso hacia atras), robot_giro[dir] (dir en "ne", "no", "se", "so"),
      avioneta[(dir, k)] (8 direcciones, k en 0..2: cuadros de la helice; es el robot ya
      montado), avioneta_base (avioneta vacia, codigo 5), cultivo[i] (i en 0..8: 0 =
      seco, 8 = tratado), deposito, casilla_libre y obstaculo.
    - Sprites.estatico(nombre): imagen fija de un nombre devuelto por
      obtener_nombre_sprite_por_codigo.
    - obtener_nombre_sprite_por_codigo(codigo_de_celda): retorna el nombre de sprite
      por defecto de un codigo de celda (0 a 5).
PENDIENTE:
    - Escalado de los sprites (hoy 64x64 originales; si se agrandan, usar
      pygame.transform.scale con factor entero y sin suavizado, una sola vez aqui).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

RAIZ_SPRITES = Path(__file__).resolve().parents[3] / "assets" / "sprites"

DIRECCIONES_CARDINALES = ("n", "e", "s", "o")
DIRECCIONES_DIAGONALES = ("ne", "no", "se", "so")
# Las 8 direcciones en el orden en que gira un actor (sentido horario desde el norte).
ANILLO_DIRECCIONES = ("n", "ne", "e", "se", "s", "so", "o", "no")
CUADROS_POR_DIRECCION = 3
CUADROS_CULTIVO = 9

# Codigos de celda del archivo de mundo (ver constantes.py, aun sin implementar):
# 0 libre, 1 obstaculo, 2 AgroBot, 3 cultivo seco, 4 deposito, 5 avioneta.
# TODO: usar los CODIGO_* de constantes.py cuando ese archivo los defina.
_NOMBRE_POR_CODIGO = {
    0: "casilla_libre",
    1: "obstaculo",
    2: "robot",
    3: "cultivo",
    4: "deposito",
    5: "avioneta_base",
}


@dataclass(frozen=True)
class Sprites:
    robot: dict
    robot_giro: dict
    avioneta: dict
    avioneta_base: "pygame.Surface"
    cultivo: tuple
    deposito: "pygame.Surface"
    casilla_libre: "pygame.Surface"
    obstaculo: "pygame.Surface"

    def estatico(self, nombre: str) -> "pygame.Surface":
        """Imagen fija de un nombre de obtener_nombre_sprite_por_codigo."""
        if nombre == "robot":
            return self.robot[("s", 0)]  # antes del primer movimiento mira hacia abajo
        if nombre == "cultivo":
            return self.cultivo[0]
        return getattr(self, nombre)


def obtener_nombre_sprite_por_codigo(codigo_de_celda: int) -> str:
    """Nombre del sprite por defecto de un codigo de celda (0 a 5)."""
    try:
        return _NOMBRE_POR_CODIGO[codigo_de_celda]
    except KeyError:
        raise ValueError("Codigo de celda desconocido: " + str(codigo_de_celda)) from None


def _cargar_imagen(ruta: Path) -> "pygame.Surface":
    if not ruta.is_file():
        raise FileNotFoundError("Falta el sprite: " + str(ruta))
    imagen = pygame.image.load(str(ruta))
    # convert_alpha necesita una ventana creada; sin ella se deja la imagen tal cual.
    return imagen.convert_alpha() if pygame.display.get_surface() else imagen


def cargar_sprites(raiz: Path = RAIZ_SPRITES) -> Sprites:
    """Carga todos los sprites de assets/sprites/ (ver assets/README.md)."""
    raiz = Path(raiz)

    robot = {
        (d, k): _cargar_imagen(raiz / "robot" / f"robot_{d}_{k}.png")
        for d in DIRECCIONES_CARDINALES
        for k in range(CUADROS_POR_DIRECCION)
    }
    robot_giro = {
        d: _cargar_imagen(raiz / "robot" / f"robot_trans_{d}.png")
        for d in DIRECCIONES_DIAGONALES
    }
    avioneta = {
        (d, k): _cargar_imagen(raiz / "avioneta" / f"avioneta_{d}_{k}.png")
        for d in ANILLO_DIRECCIONES
        for k in range(CUADROS_POR_DIRECCION)
    }
    cultivo = tuple(
        _cargar_imagen(raiz / "cultivo" / f"planta_trans_{i}.png")
        for i in range(CUADROS_CULTIVO)
    )
    return Sprites(
        robot=robot,
        robot_giro=robot_giro,
        avioneta=avioneta,
        avioneta_base=_cargar_imagen(raiz / "avioneta" / "avioneta base.png"),
        cultivo=cultivo,
        deposito=_cargar_imagen(raiz / "deposito" / "deposito.png"),
        casilla_libre=_cargar_imagen(raiz / "mundo" / "casilla_libre.png"),
        obstaculo=_cargar_imagen(raiz / "mundo" / "obstaculo.png"),
    )
