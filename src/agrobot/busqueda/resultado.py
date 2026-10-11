"""
Archivo:       src/agrobot/busqueda/resultado.py
Objetivo:      Definir el contrato de salida comun que cada algoritmo de busqueda
               entrega, y que la GUI consume para animar la solucion y mostrar el
               reporte de metricas.
Responsabilidad:
    SI hace:
        - Definir la estructura que agrupa: el camino de movimientos de la solucion
          (desde el estado inicial hasta el estado meta), el numero de nodos
          expandidos durante la busqueda, la profundidad de la solucion (numero de
          movimientos del camino, NO es lo mismo que su costo), el tiempo de computo
          de la busqueda, y el costo total de la solucion (este ultimo campo solo
          tiene sentido para Costo uniforme y A*; en los demas algoritmos queda sin
          definir o en None).
    NO hace:
        - No calcula ninguna de estas metricas: cada algoritmo las calcula y llena un
          Resultado al terminar.
        - No dibuja ni anima nada.
Importa de:
    - (ninguno del proyecto fuera de busqueda/): es una estructura de datos pura.
Lo importan:
    - busqueda/no_informada/amplitud.py, costo_uniforme.py, profundidad.py.
    - busqueda/informada/avara.py, a_estrella.py.
    - gui/animacion.py (consume el camino de movimientos).
    - gui/panel_reporte.py (consume nodos expandidos, profundidad, tiempo y costo).
Contrato previsto:
    - Resultado: clase con los campos camino_de_movimientos, nodos_expandidos,
      profundidad_de_la_solucion, tiempo_de_computo y costo_total (opcional, solo para
      Costo uniforme y A*).
    - camino_de_estados (extra): los estados por los que pasa la solucion, del inicial
      al meta; permite dibujar y animar sin volver a aplicar los movimientos.
    - solucion_encontrada (extra): False cuando la busqueda termino sin hallar meta; en
      ese caso los caminos quedan vacios y profundidad_de_la_solucion en 0.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Resultado:
    camino_de_movimientos: tuple
    nodos_expandidos: int
    profundidad_de_la_solucion: int
    tiempo_de_computo: float
    costo_total: Optional[float] = None
    camino_de_estados: tuple = ()
    solucion_encontrada: bool = True

