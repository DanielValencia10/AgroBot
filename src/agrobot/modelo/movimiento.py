"""
Archivo:       src/agrobot/modelo/movimiento.py
Objetivo:      Definir los cuatro movimientos basicos que puede ejecutar el AgroBot sobre
               la cuadricula (arriba, abajo, izquierda, derecha) y el desplazamiento de
               fila/columna que cada uno produce.
Responsabilidad:
    SI hace:
        - Enumerar los cuatro movimientos posibles.
        - Asociar a cada movimiento su desplazamiento como par (delta_fila, delta_columna).
    NO hace:
        - No valida si un movimiento es aplicable desde una posicion dada (eso es de
          problema/operadores.py, que conoce el Mundo y sus limites/obstaculos).
        - No aplica efectos sobre el estado (fertilizante, combustible, etc.).
Importa de:
    - constantes: no requiere valores de constantes para los desplazamientos en si,
      pero se deja la dependencia permitida por la regla (modelo/ solo importa de
      constantes) en caso de que se necesite para nombrar o validar movimientos.
Lo importan:
    - problema/operadores.py (para conocer el desplazamiento de cada movimiento al
      calcular la casilla destino).
    - problema/agrobot_problema.py (para iterar sobre los movimientos posibles al
      generar sucesores).
    - busqueda/nodo.py (un nodo guarda el movimiento que lo genero).
    - gui/animacion.py (para traducir cada movimiento del camino solucion en un
      desplazamiento visual).
Contrato previsto:
    - Movimiento: enumeracion con los cuatro valores ARRIBA, ABAJO, IZQUIERDA, DERECHA.
    - obtener_desplazamiento(movimiento): recibe un Movimiento y retorna el par
      (delta_fila, delta_columna) correspondiente.
Decision de equipo (antes PENDIENTE):
    - Orden de los movimientos al generar sucesores: ARRIBA, ABAJO, IZQUIERDA, DERECHA
      (el orden de definicion del enum; afecta el desempate y el orden de expansion).
"""
from __future__ import annotations

from enum import Enum


class Movimiento(Enum):
    ARRIBA = "arriba"
    ABAJO = "abajo"
    IZQUIERDA = "izquierda"
    DERECHA = "derecha"


_DESPLAZAMIENTOS = {
    Movimiento.ARRIBA: (-1, 0),
    Movimiento.ABAJO: (1, 0),
    Movimiento.IZQUIERDA: (0, -1),
    Movimiento.DERECHA: (0, 1),
}


def obtener_desplazamiento(movimiento: Movimiento) -> tuple:
    """Retorna (delta_fila, delta_columna) del movimiento (la fila 0 esta arriba)."""
    return _DESPLAZAMIENTOS[movimiento]

