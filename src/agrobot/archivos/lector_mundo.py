"""
Archivo:       src/agrobot/archivos/lector_mundo.py
Objetivo:      Leer un archivo de texto (.txt) que describe un mundo AgroBot (10 filas
               por 10 numeros separados por espacios) y construir el objeto Mundo
               correspondiente, validando el formato antes de construirlo.
Responsabilidad:
    SI hace:
        - Leer el archivo de texto dado y parsear sus 10 filas de 10 numeros cada una.
        - Validar el formato:
            - Tamano exacto de 10 filas por 10 columnas.
            - Todos los codigos deben ser validos segun constantes (0 a 5).
            - Debe haber exactamente un 2 (AgroBot), un 4 (deposito) y un 5 (avioneta).
            - Debe haber al menos un 3 (cultivo seco).
        - Construir y retornar un objeto Mundo con los datos ya validados: obstaculos,
          posicion del deposito, posicion inicial de la avioneta, posicion inicial del
          robot y conjunto de cultivos secos iniciales.
        - Reportar un error claro cuando el archivo no cumple alguna de las
          validaciones anteriores.
    NO hace:
        - No construye el Estado dinamico del problema (eso puede vivir en estado.py o
          en agrobot_problema.py, segun se resuelva ese PENDIENTE).
        - No conoce algoritmos de busqueda ni la GUI.
Importa de:
    - modelo.mundo (Mundo): para construir y retornar la instancia final.
    - constantes: para los codigos validos de celda (CODIGO_LIBRE, CODIGO_OBSTACULO,
      CODIGO_AGROBOT, CODIGO_CULTIVO_SECO, CODIGO_DEPOSITO, CODIGO_AVIONETA) y el
      tamano esperado de la cuadricula (TAMANO_CUADRICULA) usados en la validacion.
Lo importan:
    - gui/panel_control.py (para cargar el archivo de mundo elegido por el usuario).
    - main.py (eventualmente, si la carga inicial se hace fuera de la GUI).
    - tests/test_lector_mundo.py (para verificar las validaciones).
Contrato previsto:
    - leer_mundo_desde_archivo(ruta_del_archivo): recibe la ruta de un archivo .txt,
      valida su formato segun las reglas descritas arriba y retorna un objeto Mundo
      construido a partir de su contenido. Si el archivo no cumple el formato
      esperado, señala el error de validacion correspondiente en vez de construir un
      Mundo invalido.
    - construir_mundo(matriz): valida una matriz ya leida y construye el Mundo (util
      para probar sin archivos).
    - ErrorMundo (subclase de ValueError): se lanza con un mensaje claro cuando el
      archivo no existe, no se puede leer o incumple alguna validacion.
"""
from __future__ import annotations

from pathlib import Path

from .. import constantes
from ..modelo.mundo import Mundo

_CODIGOS_VALIDOS = range(constantes.CODIGO_LIBRE, constantes.CODIGO_AVIONETA + 1)


class ErrorMundo(ValueError):
    """El archivo de mundo no existe o no cumple el formato esperado."""


def leer_mundo_desde_archivo(ruta_del_archivo) -> Mundo:
    """Lee y valida un archivo de mundo; retorna el Mundo construido."""
    ruta = Path(ruta_del_archivo)
    try:
        contenido = ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ErrorMundo("No se encontro el archivo: " + str(ruta)) from None
    except (OSError, UnicodeDecodeError) as error:
        raise ErrorMundo("No se pudo leer " + ruta.name + ": " + str(error)) from None
    return construir_mundo(_a_matriz(contenido, ruta.name))


def _a_matriz(contenido: str, nombre: str) -> list:
    """Convierte el texto en una matriz de enteros (una lista por fila no vacia)."""
    matriz = []
    for numero_linea, linea in enumerate(contenido.splitlines(), start=1):
        linea = linea.strip()
        if linea == "":
            continue
        try:
            matriz.append([int(numero) for numero in linea.split()])
        except ValueError:
            raise ErrorMundo(
                nombre + ", linea " + str(numero_linea)
                + ": solo se permiten numeros separados por espacios."
            ) from None
    return matriz


def construir_mundo(matriz) -> Mundo:
    """Valida una matriz de codigos de celda y construye el Mundo. Lanza ErrorMundo."""
    tamano = constantes.TAMANO_CUADRICULA
    if len(matriz) != tamano:
        raise ErrorMundo(
            "El mundo debe tener " + str(tamano) + " filas y tiene " + str(len(matriz)) + "."
        )
    for fila, valores in enumerate(matriz):
        if len(valores) != tamano:
            raise ErrorMundo(
                "La fila " + str(fila) + " debe tener " + str(tamano)
                + " columnas y tiene " + str(len(valores)) + "."
            )

    posiciones = {codigo: [] for codigo in _CODIGOS_VALIDOS}
    for fila, valores in enumerate(matriz):
        for columna, codigo in enumerate(valores):
            if codigo not in posiciones:
                raise ErrorMundo(
                    "Codigo invalido " + str(codigo) + " en (" + str(fila) + ", "
                    + str(columna) + "): solo se permiten del 0 al 5."
                )
            posiciones[codigo].append((fila, columna))

    for codigo, nombre in (
        (constantes.CODIGO_AGROBOT, "AgroBot (2)"),
        (constantes.CODIGO_DEPOSITO, "deposito (4)"),
        (constantes.CODIGO_AVIONETA, "avioneta (5)"),
    ):
        if len(posiciones[codigo]) != 1:
            raise ErrorMundo(
                "Debe haber exactamente un " + nombre + " y hay "
                + str(len(posiciones[codigo])) + "."
            )
    if not posiciones[constantes.CODIGO_CULTIVO_SECO]:
        raise ErrorMundo("Debe haber al menos un cultivo seco (3).")

    return Mundo(
        obstaculos=frozenset(posiciones[constantes.CODIGO_OBSTACULO]),
        deposito=posiciones[constantes.CODIGO_DEPOSITO][0],
        avioneta=posiciones[constantes.CODIGO_AVIONETA][0],
        posicion_robot=posiciones[constantes.CODIGO_AGROBOT][0],
        cultivos_secos=frozenset(posiciones[constantes.CODIGO_CULTIVO_SECO]),
    )

