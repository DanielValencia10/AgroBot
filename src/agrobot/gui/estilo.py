"""
Archivo:       src/agrobot/gui/estilo.py
Objetivo:      Reunir lo que comparten las pantallas de inicio (bienvenida y seleccion):
               paleta de colores, tipografias, la matica en pixel art y funciones de
               dibujo de texto.
Responsabilidad:
    SI hace:
        - Definir la paleta y el tamano de ventana de las pantallas de inicio, tomados
          de los mockups "1 - Bienvenida" y "2 - Seleccion".
        - Cargar las tipografias: Pixelify Sans (pesos 500 y 700) para el titulo
          "AgroBot", "Bienvenido a", los titulos de los pasos, los nombres de los
          algoritmos y los botones; y DM Sans (pesos 400, 500 y 700) para subtitulos,
          descripciones, nombres de archivo y textos de apoyo.
        - Dibujar la matica (pixel art) a cualquier escala.
        - Ofrecer utilidades de texto: dibujar con ancla, con espaciado entre letras,
          recortar con "..." y partir en lineas.
    NO hace:
        - No conoce ninguna pantalla ni su logica de eleccion.
        - No lee assets/: las fuentes viven en gui/fuentes/ (junto al codigo) y la
          matica se dibuja con rectangulos, asi que no depende de cargador_sprites.py.
Importa de:    pygame (pygame-ce).
Lo importan:   gui/pantalla_bienvenida.py, gui/pantalla_seleccion.py y
               gui/pantalla_inicio.py.
Fuentes (carpeta gui/fuentes/, ver el README que hay dentro):
    Pixelify Sans:  PixelifySans-Medium.ttf, PixelifySans-Bold.ttf
    DM Sans:        DMSans-Regular.ttf, DMSans-Medium.ttf, DMSans-Bold.ttf
    Se aceptan tambien las variantes de nombre que trae la descarga de Google Fonts
    (por ejemplo DMSans_18pt-Regular.ttf). Si falta alguna fuente se usa una del
    sistema: la pantalla funciona igual, pero sin el aspecto pixel del mockup.
"""
from __future__ import annotations

from pathlib import Path

import pygame

# ---------------------------------------------------------------- ventana
ANCHO_VENTANA = 1120
ALTO_VENTANA = 760
TAMANO_VENTANA = (ANCHO_VENTANA, ALTO_VENTANA)

# ---------------------------------------------------------------- colores
# Todos salen de los mockups.
COLOR_FONDO = (31, 59, 46)           # #1F3B2E fondo de la ventana
COLOR_TARJETA = (41, 70, 50)         # #294632 tarjetas
COLOR_CIRCULO = (43, 71, 51)         # #2B4733 circulo detras de la matica
COLOR_BORDE = (60, 90, 58)           # #3C5A3A bordes y boton deshabilitado
COLOR_OLIVA = (141, 164, 50)         # #8DA432 acento: botones, numeros, seleccion
COLOR_OLIVA_OSCURO = (54, 80, 4)     # #365004 sombra del boton
COLOR_LINO = (237, 227, 131)         # #EDE383 resaltados y mensajes
COLOR_SALVIA = (199, 213, 166)       # #C7D5A6 titulos
COLOR_SALVIA_TENUE = (163, 177, 138) # #A3B18A subtitulos y ayudas
COLOR_CREMA = (220, 210, 181)        # #DCD2B5 texto principal
COLOR_TEXTO_DESHABILITADO = (109, 121, 102)  # #6D7966
COLOR_FILA_ENCIMA = (36, 66, 49)     # fila bajo el mouse (entre fondo y tarjeta)
COLOR_ALERTA = (214, 122, 92)        # #D67A5C avisos de error (sin solucion)

# ---------------------------------------------------------------- fuentes
CARPETA_FUENTES = Path(__file__).resolve().parent / "fuentes"

# peso -> patrones de archivo, del mas especifico al mas general
_PATRONES_PIXEL = {
    500: ("pixelifysans*medium*.ttf", "pixelifysans*.ttf"),
    700: ("pixelifysans*bold*.ttf", "pixelifysans*.ttf"),
}
_PATRONES_TEXTO = {
    400: ("dmsans*regular*.ttf", "dmsans*.ttf"),
    500: ("dmsans*medium*.ttf", "dmsans*.ttf"),
    700: ("dmsans*bold*.ttf", "dmsans*.ttf"),
}
_RESPALDO_PIXEL = "menlo,couriernew,courier,dejavusansmono"
_RESPALDO_TEXTO = "avenirnext,segoeui,helveticaneue,helvetica,arial,dejavusans"

_cache_fuentes: dict = {}


def _buscar_archivo(patrones):
    """Primer archivo de gui/fuentes/ que cumple algun patron (sin distinguir mayusculas)."""
    if not CARPETA_FUENTES.is_dir():
        return None
    archivos = sorted(CARPETA_FUENTES.iterdir(), key=lambda ruta: ruta.name.lower())
    for patron in patrones:
        for ruta in archivos:
            if ruta.match(patron) or Path(ruta.name.lower()).match(patron):
                return ruta
    return None


def fuente_pixel(tamano: int, peso: int = 700):
    """Pixelify Sans (peso 500 o 700) o, si falta, una fuente monoespaciada del sistema."""
    return _fuente("pixel", tamano, peso)


def fuente_texto(tamano: int, peso: int = 400):
    """DM Sans (peso 400, 500 o 700) o, si falta, una sans del sistema."""
    return _fuente("texto", tamano, peso)


def _fuente(familia, tamano, peso):
    clave = (familia, tamano, peso)
    if clave in _cache_fuentes:
        try:
            _cache_fuentes[clave].size("")
        except pygame.error:  # pygame se cerro y se volvio a iniciar: la fuente quedo invalida
            del _cache_fuentes[clave]
    if clave not in _cache_fuentes:
        patrones = (_PATRONES_PIXEL if familia == "pixel" else _PATRONES_TEXTO)[peso]
        ruta = _buscar_archivo(patrones)
        if ruta is not None:
            _cache_fuentes[clave] = pygame.font.Font(str(ruta), tamano)
        else:
            nombres = _RESPALDO_PIXEL if familia == "pixel" else _RESPALDO_TEXTO
            _cache_fuentes[clave] = pygame.font.SysFont(nombres, tamano, bold=peso >= 700)
    return _cache_fuentes[clave]


def fuente_pixel_ajustada(texto: str, ancho: int, peso: int = 700):
    """Pixelify Sans con el tamano en el que `texto` mide `ancho` pixeles.

    Sirve para el titulo grande: el mockup lo fija por ancho, y asi se ve igual aunque
    se use una fuente de respaldo con otras proporciones.
    """
    medida = fuente_pixel(100, peso).size(texto)[0]
    return fuente_pixel(max(8, round(100 * ancho / max(1, medida))), peso)


# ---------------------------------------------------------------- matica
# Pixel art del mockup (16 x 19 pixeles). Cada letra es un color de MATICA_COLORES.
MATICA = (
    "..aaa...........",
    ".abbba..........",
    "abcbbba..aaa....",
    "abbbbba.abbba...",
    ".abbba..abbba...",
    "..aaa....aaa....",
    "...d......d.....",
    "...d......d..bcb",
    "...d......daaaa.",
    "...d......d.....",
    "..eeeeeeeeee....",
    ".ffffffffffff...",
    ".gggggggggggg...",
    "..hhhhhhhhii....",
    "..hgggggghii....",
    "..hgggggghii....",
    "..hhhhhhhhii....",
    "..hhhhhhhhii....",
    "...iiiiiiii.....",
)
MATICA_COLORES = {
    "a": (107, 142, 35),    # borde de las hojas
    "b": (199, 213, 166),   # hojas
    "c": (237, 227, 131),   # brillo
    "d": (163, 177, 138),   # tallos
    "e": (53, 25, 3),       # tierra
    "f": (217, 164, 65),    # borde claro de la maceta
    "g": (181, 122, 30),    # maceta (cara iluminada)
    "h": (146, 94, 6),      # maceta
    "i": (110, 70, 4),      # sombra de la maceta
}
MATICA_COLUMNAS = len(MATICA[0])
MATICA_FILAS = len(MATICA)


def dibujar_matica(pantalla, x: int, y: int, unidad: int) -> None:
    """Dibuja la matica con su esquina superior izquierda en (x, y); `unidad` = lado de cada pixel."""
    for fila, texto in enumerate(MATICA):
        for columna, letra in enumerate(texto):
            if letra != ".":
                pygame.draw.rect(pantalla, MATICA_COLORES[letra],
                                 pygame.Rect(x + columna * unidad, y + fila * unidad,
                                             unidad, unidad))


# ---------------------------------------------------------------- texto
def texto(pantalla, contenido, fuente, color, posicion, ancla="topleft") -> pygame.Rect:
    """Dibuja `contenido` con la esquina o punto de anclaje indicado; retorna su rectangulo."""
    superficie = fuente.render(contenido, True, color)
    rect = superficie.get_rect()
    setattr(rect, ancla, posicion)
    pantalla.blit(superficie, rect)
    return rect


def texto_linea_base(pantalla, contenido, fuente, color, x, y_base) -> pygame.Rect:
    """Dibuja el texto con su linea base (donde "apoyan" las letras) en y_base.

    Asi el titulo queda a la misma altura con cualquier tipografia, la del mockup o una
    de respaldo.
    """
    ascenso = fuente.get_ascent() if hasattr(fuente, "get_ascent") else int(fuente.size("A")[1] * 0.8)
    return texto(pantalla, contenido, fuente, color, (x, y_base - ascenso))


def ancho_espaciado(contenido, fuente, espacio: int) -> int:
    return sum(fuente.size(letra)[0] for letra in contenido) + espacio * max(0, len(contenido) - 1)


def texto_espaciado(pantalla, contenido, fuente, color, centro, espacio: int) -> None:
    """Dibuja el texto letra por letra con `espacio` pixeles extra, centrado en `centro`."""
    x = centro[0] - ancho_espaciado(contenido, fuente, espacio) // 2
    for letra in contenido:
        rect = texto(pantalla, letra, fuente, color, (x, centro[1]), ancla="midleft")
        x += rect.w + espacio


def recortar(contenido, fuente, ancho_maximo) -> str:
    """Acorta el texto con '...' si no cabe en el ancho dado."""
    if fuente.size(contenido)[0] <= ancho_maximo:
        return contenido
    while len(contenido) > 1 and fuente.size(contenido + "...")[0] > ancho_maximo:
        contenido = contenido[:-1]
    return contenido + "..."


def envolver(contenido, fuente, ancho_maximo) -> list:
    """Parte el texto en lineas que quepan en el ancho dado (por palabras)."""
    lineas = []
    actual = ""
    for palabra in contenido.split():
        prueba = palabra if actual == "" else actual + " " + palabra
        if actual != "" and fuente.size(prueba)[0] > ancho_maximo:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual != "":
        lineas.append(actual)
    return lineas


# ---------------------------------------------------------------- formas
def dibujar_tarjeta(pantalla, rect, radio: int = 18) -> None:
    pygame.draw.rect(pantalla, COLOR_TARJETA, rect, border_radius=radio)
    pygame.draw.rect(pantalla, COLOR_BORDE, rect, 2, border_radius=radio)


def dibujar_borde_punteado(pantalla, rect, color, trazo: int = 6, hueco: int = 5) -> None:
    """Borde de rayas (lo usa el aviso 'agrega mas archivos')."""
    x = rect.x
    while x < rect.right:
        ancho = min(trazo, rect.right - x)
        pygame.draw.rect(pantalla, color, pygame.Rect(x, rect.y, ancho, 2))
        pygame.draw.rect(pantalla, color, pygame.Rect(x, rect.bottom - 2, ancho, 2))
        x += trazo + hueco
    y = rect.y
    while y < rect.bottom:
        alto = min(trazo, rect.bottom - y)
        pygame.draw.rect(pantalla, color, pygame.Rect(rect.x, y, 2, alto))
        pygame.draw.rect(pantalla, color, pygame.Rect(rect.right - 2, y, 2, alto))
        y += trazo + hueco


def dibujar_boton(pantalla, rect, etiqueta, habilitado: bool, con_mouse: bool) -> None:
    """Boton grande de las pantallas de inicio (con sombra cuando esta habilitado)."""
    fuente = fuente_pixel(22, 700)
    if habilitado:
        pygame.draw.rect(pantalla, COLOR_OLIVA_OSCURO, rect.move(0, 6), border_radius=12)
        relleno = COLOR_LINO if con_mouse else COLOR_OLIVA
        pygame.draw.rect(pantalla, relleno, rect, border_radius=12)
        color_texto = COLOR_FONDO
    else:
        pygame.draw.rect(pantalla, COLOR_BORDE, rect, border_radius=12)
        color_texto = COLOR_TEXTO_DESHABILITADO
    texto_espaciado(pantalla, etiqueta.upper(), fuente, color_texto, rect.center, 3)


def crear_icono_ventana(unidad: int = 2):
    """Superficie con la matica para usarla como icono de la ventana."""
    superficie = pygame.Surface((MATICA_COLUMNAS * unidad, MATICA_FILAS * unidad), pygame.SRCALPHA)
    dibujar_matica(superficie, 0, 0, unidad)
    return superficie
