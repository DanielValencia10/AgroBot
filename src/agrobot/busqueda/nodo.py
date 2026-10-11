"""
Archivo:       src/agrobot/busqueda/nodo.py
Objetivo:      Representar un nodo del arbol de busqueda: el estado que contiene, su
               nodo padre, el movimiento que lo genero, su profundidad y su costo
               acumulado desde la raiz.
Responsabilidad:
    SI hace:
        - Guardar una referencia al estado (de tipo compatible con el que entrega el
          objeto problema recibido por el algoritmo; busqueda/ no conoce la clase
          Estado de modelo/, solo la trata como un valor opaco comparable/hasheable).
        - Guardar una referencia al nodo padre (o ninguna, si es la raiz).
        - Guardar el movimiento que genero este nodo a partir del padre (o ninguno, si
          es la raiz).
        - Guardar la profundidad del nodo, entendida como el numero de movimientos
          desde la raiz evitando ciclos (ver criterio en los algoritmos que la usan).
        - Guardar el costo acumulado desde la raiz hasta este nodo.
        - Permitir reconstruir el camino de movimientos desde la raiz hasta este nodo,
          siguiendo la cadena de padres.
    NO hace:
        - No conoce el objeto problema ni como generar sucesores: eso lo hace cada
          algoritmo de busqueda, que recibe el problema como parametro y crea los
          nodos hijos usando su contrato (estado inicial, es_meta, sucesores, costo).
        - No decide criterios de expansion u orden: eso es responsabilidad de cada
          algoritmo (amplitud.py, costo_uniforme.py, etc.).
Importa de:
    - (ninguno del proyecto fuera de busqueda/): busqueda/ no importa de problema/ ni
      de modelo/; el "estado" que guarda un Nodo es tratado como un valor opaco que
      debe cumplir el contrato minimo de ser comparable y hasheable (lo que en la
      practica cumple modelo.estado.Estado, pero ese acoplamiento se da por el objeto
      problema que crea los nodos, no por un import directo aqui).
Lo importan:
    - busqueda/no_informada/amplitud.py, costo_uniforme.py, profundidad.py.
    - busqueda/informada/avara.py, a_estrella.py.
    - busqueda/resultado.py (para reconstruir el camino de movimientos de la solucion).
Contrato previsto:
    - Nodo: clase con los campos estado, padre, movimiento, profundidad y
      costo_acumulado.
    - reconstruir_camino(nodo): recibe el nodo meta y retorna la lista ordenada de
      movimientos desde la raiz hasta ese nodo, siguiendo la cadena de padres.
    - reconstruir_camino_de_estados(nodo): igual, pero retorna los estados desde la raiz
      hasta ese nodo (incluidos ambos); la GUI los usa para dibujar cada paso.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Nodo:
    estado: Any
    padre: Optional["Nodo"] = None
    movimiento: Any = None
    profundidad: int = 0
    costo_acumulado: float = 0.0


def _cadena_desde_la_raiz(nodo: Nodo) -> list:
    cadena = []
    while nodo is not None:
        cadena.append(nodo)
        nodo = nodo.padre
    cadena.reverse()
    return cadena


def reconstruir_camino(nodo: Nodo) -> list:
    """Movimientos desde la raiz hasta `nodo` (la raiz no tiene movimiento)."""
    return [paso.movimiento for paso in _cadena_desde_la_raiz(nodo)[1:]]


def reconstruir_camino_de_estados(nodo: Nodo) -> list:
    """Estados desde la raiz hasta `nodo`, ambos incluidos."""
    return [paso.estado for paso in _cadena_desde_la_raiz(nodo)]

