"""
Archivo:       src/agrobot/gui/pantalla_inicio.py
Objetivo:      Coordinar las dos pantallas con que arranca AgroBot: la bienvenida y la
               seleccion de mundo y algoritmo.
Responsabilidad:
    SI hace:
        - Abrir la bienvenida; al pulsar "Iniciar" pasar a la seleccion; si el usuario
          pulsa "Volver al inicio", regresar a la bienvenida.
        - Entregar a quien la llamo lo que se eligio (SeleccionInicio) o None si el
          usuario cerro la aplicacion.
        - Crear la ventana de pygame de las pantallas de inicio (vista previa).
    NO hace:
        - No dibuja ni decide nada de cada pantalla: eso es de pantalla_bienvenida.py y
          pantalla_seleccion.py.
        - No ejecuta el algoritmo ni abre la ventana principal.
Importa de:
    - gui.pantalla_bienvenida, gui.pantalla_seleccion, gui.estilo.
    - pygame (pygame-ce).
Lo importan:
    - main.py / gui/ventana_principal.py (cuando se integre).
Contrato previsto:
    - ejecutar_inicio(pantalla, carpeta_mundos, saltar_bienvenida=False): bloquea hasta
      que el usuario elige. Retorna una SeleccionInicio, o None si cierra la ventana o
      pulsa Esc.
    - crear_ventana(): inicia pygame y retorna la superficie de la ventana de 1120x760.
    - SeleccionInicio y listar_mundos se re-exportan desde pantalla_seleccion.py.
Vista previa:
    Desde la carpeta src/:   python -m agrobot.gui.pantalla_inicio
Integracion:   main.py la usa para abrir la aplicacion y para volver a la seleccion desde
               la ventana principal.
"""
from __future__ import annotations

from pathlib import Path

import pygame

from . import estilo
from .pantalla_bienvenida import PantallaBienvenida
from .pantalla_seleccion import (  # noqa: F401  (se re-exportan para quien integre)
    VOLVER,
    PantallaSeleccion,
    SeleccionInicio,
    listar_mundos,
)


def crear_ventana():
    """Inicia pygame y crea la ventana de las pantallas de inicio."""
    pygame.init()
    pantalla = pygame.display.set_mode(estilo.TAMANO_VENTANA)
    pygame.display.set_caption("AgroBot")
    try:
        pygame.display.set_icon(estilo.crear_icono_ventana())
    except Exception:  # el icono es solo un adorno: nunca debe impedir abrir la ventana
        pass
    return pantalla


def ejecutar_inicio(pantalla, carpeta_mundos, saltar_bienvenida=False):
    """Bienvenida -> seleccion. Retorna SeleccionInicio, o None si el usuario cierra.

    Con saltar_bienvenida=True se abre directo la seleccion (por ejemplo, al volver desde
    la ventana principal); si ahi pulsa "Volver al inicio" si se muestra la bienvenida.
    """
    bienvenida = PantallaBienvenida()
    seleccion = PantallaSeleccion(carpeta_mundos)
    while True:
        if saltar_bienvenida:
            saltar_bienvenida = False
        elif bienvenida.ejecutar(pantalla) is None:
            return None
        resultado = seleccion.ejecutar(pantalla)
        if resultado == VOLVER:
            continue
        return resultado


def _vista_previa() -> None:
    """Abre solo las pantallas de inicio para probarlas (no es el punto de entrada)."""
    carpeta_mundos = Path(__file__).resolve().parents[3] / "mundos"
    pantalla = crear_ventana()
    seleccion = ejecutar_inicio(pantalla, carpeta_mundos)
    pygame.quit()
    if seleccion is None:
        print("Se cerro la pantalla sin elegir.")
    else:
        print("Mundo:", seleccion.ruta_mundo)
        print("Tipo:", seleccion.tipo.value)
        print("Algoritmo:", seleccion.algoritmo.value)


if __name__ == "__main__":
    _vista_previa()
