"""
Archivo:       src/agrobot/main.py
Objetivo:      Punto de entrada de la aplicacion AgroBot: crear la interfaz grafica y
               conectar todas las piezas del proyecto (modelo, problema, busqueda,
               archivos y gui).
Responsabilidad:
    SI hace:
        - Orquestar el flujo de la aplicacion: ventana -> pantallas de inicio
          (bienvenida y seleccion de mundo y algoritmo) -> etapa siguiente.
        - Ser el unico archivo del proyecto que puede importar de todos los paquetes
          (modelo/, problema/, busqueda/ y gui/), ya que su rol es de composicion.
    NO hace:
        - No implementa logica propia de dominio, busqueda ni interfaz: delega todo en
          los paquetes correspondientes.
Importa de:
    - gui.pantalla_inicio (crear_ventana, ejecutar_inicio).
Lo importan:
    - (ninguno; es el punto de entrada del programa, se ejecuta directamente).
Ejecucion:
    Desde la raiz del repositorio:   python ejecutar.py
    Desde la carpeta src/:           python -m agrobot.main
Como conectar la siguiente etapa:
    El flujo ya entrega la SeleccionInicio (mundo, tipo y algoritmo) a
    _etapa_principal(). Cuando exista VentanaPrincipal, solo hay que reemplazar el
    cuerpo de esa funcion; el resto del flujo no cambia.
PENDIENTE:
    - _etapa_principal(): cargar el mundo (archivos.lector_mundo), construir el
      problema (problema.agrobot_problema), lanzar el algoritmo elegido y mostrar el
      resultado con gui.ventana_principal.
"""
from __future__ import annotations

import sys
from pathlib import Path

CARPETA_MUNDOS = Path(__file__).resolve().parents[2] / "mundos"


def _etapa_principal(pantalla, seleccion) -> None:
    """Etapa posterior a la seleccion. Aun sin implementar: solo informa lo elegido."""
    print("Mundo:", seleccion.ruta_mundo)
    print("Tipo:", seleccion.tipo.value)
    print("Algoritmo:", seleccion.algoritmo.value)


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

    from .gui.pantalla_inicio import crear_ventana, ejecutar_inicio

    pantalla = crear_ventana()
    try:
        seleccion = ejecutar_inicio(pantalla, CARPETA_MUNDOS)
        if seleccion is None:  # el usuario cerro la ventana o pulso Esc
            return 0
        _etapa_principal(pantalla, seleccion)
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(punto_de_entrada())
