"""
Archivo:       src/agrobot/main.py
Objetivo:      Punto de entrada de la aplicacion AgroBot: crear la interfaz grafica y
               conectar todas las piezas del proyecto (modelo, problema, busqueda,
               archivos y gui).
Responsabilidad:
    SI hace:
        - Orquestar el flujo completo: ventana -> bienvenida -> seleccion de mundo y
          algoritmo -> busqueda -> ventana principal (animacion, arbol y reporte) -> de
          vuelta a la seleccion, hasta que el usuario cierre la aplicacion.
        - Mostrar un aviso (y volver a la seleccion) si el mundo no es valido o el
          algoritmo elegido aun no esta implementado.
        - Ser el unico archivo del proyecto que puede importar de todos los paquetes
          (modelo/, problema/, busqueda/ y gui/), ya que su rol es de composicion.
    NO hace:
        - No implementa logica propia de dominio, busqueda ni interfaz: delega todo en
          los paquetes correspondientes.
Importa de:
    - archivos.lector_mundo (ErrorMundo).
    - gui.pantalla_inicio, gui.panel_control, gui.ventana_principal, gui.pantalla_aviso.
Lo importan:
    - (ninguno; es el punto de entrada del programa, se ejecuta directamente).
Ejecucion:
    Desde la raiz del repositorio:   python ejecutar.py
    Desde la carpeta src/:           python -m agrobot.main
Contrato previsto:
    - punto_de_entrada(): corre la aplicacion y retorna el codigo de salida (0 si todo
      bien, 1 si falta pygame-ce).
"""
from __future__ import annotations

import sys
from pathlib import Path

CARPETA_MUNDOS = Path(__file__).resolve().parents[2] / "mundos"


def punto_de_entrada() -> int:
    """Corre la aplicacion completa. Retorna el codigo de salida del proceso."""
    try:
        import pygame
    except ImportError:
        print(
            "No se encontro pygame-ce. Activa el entorno virtual e instala las "
            "dependencias con: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    from .archivos.lector_mundo import ErrorMundo
    from .gui.panel_control import (ALGORITMOS_DISPONIBLES, AlgoritmoNoDisponible,
                                    ejecutar_seleccion)
    from .gui.pantalla_aviso import mostrar_aviso
    from .gui.pantalla_inicio import crear_ventana, ejecutar_inicio
    from .gui.ventana_principal import SALIR, VentanaPrincipal

    pantalla = crear_ventana()
    try:
        saltar_bienvenida = False
        while True:
            seleccion = ejecutar_inicio(pantalla, CARPETA_MUNDOS, saltar_bienvenida)
            if seleccion is None:  # el usuario cerro la ventana o pulso Esc
                return 0
            saltar_bienvenida = True  # al volver de la busqueda, directo a la seleccion

            try:
                ejecucion = ejecutar_seleccion(seleccion)
            except ErrorMundo as error:
                if not mostrar_aviso(pantalla, "No se pudo cargar el mundo", str(error)):
                    return 0
                continue
            except AlgoritmoNoDisponible as error:
                disponibles = ", ".join(a.value for a in ALGORITMOS_DISPONIBLES)
                mensaje = (error.algoritmo.value + " todavía no está implementado. "
                           "Por ahora puedes usar: " + disponibles + ".")
                if not mostrar_aviso(pantalla, "Algoritmo no disponible", mensaje):
                    return 0
                continue

            if VentanaPrincipal(pantalla, ejecucion).ejecutar(pantalla) == SALIR:
                return 0
    finally:
        pygame.quit()


if __name__ == "__main__":
    sys.exit(punto_de_entrada())
