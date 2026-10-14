"""
Archivo:       src/agrobot/busqueda/no_informada/profundidad.py
Objetivo:      Implementar busqueda en Profundidad (DFS) sobre el problema AgroBot
               recibido como parametro, explorando cada rama hasta el fondo antes de
               retroceder, evitando ciclos dentro de cada rama.
Responsabilidad:
    SI hace:
        - Usar una pila (LIFO) o recursion equivalente como mecanismo de expansion,
          de modo que se profundice en una rama antes de explorar ramas hermanas.
        - En cada expansion: verificar si el nodo es meta; si no lo es, generar sus
          hijos (segun problema.sucesores, que ya descarta ciclos dentro de la misma
          rama salvo las excepciones definidas en problema/ciclos.py) y apilarlos.
          Expandir un nodo cuenta 1 hacia nodos_expandidos; al expandir una meta no se
          crean hijos.
        - Llenar el Resultado con: camino de movimientos, nodos_expandidos,
          profundidad de la solucion (profundidad evitando ciclos, no el costo) y
          tiempo de computo. No llena costo_total (campo exclusivo de Costo uniforme y
          A*).
    NO hace:
        - No conoce Mundo, Estado ni detalles del dominio: solo usa el objeto
          "problema" recibido como parametro, a traves de su contrato: estado_inicial(),
          es_meta(estado), sucesores(estado, camino_de_la_rama).
        - No garantiza camino minimo en movimientos ni en costo.
        - No implementa limite de profundidad (DFS simple, no iterativo con limite),
          salvo que el equipo decida lo contrario (ver PENDIENTE).
Importa de:
    - busqueda.nodo (Nodo): para construir los nodos del arbol de busqueda.
    - busqueda.resultado (Resultado): para construir la salida final.
Lo importan:
    - gui/panel_control.py (al seleccionar "No informada" > "Profundidad") y main.py.
Contrato previsto:
    - buscar_profundidad(problema): recibe un objeto que cumple el contrato de
      problema (estado_inicial, es_meta, sucesores) y retorna un Resultado con la
      primera solucion encontrada por la rama explorada (o la indicacion de que no hay
      solucion).
PENDIENTE:
    - Si se necesita un limite de profundidad para garantizar terminacion en mundos sin
      solucion, o si el control de ciclos de problema/ciclos.py es suficiente para
      garantizar que el arbol de busqueda es finito.
    - Orden en que se apilan/exploran los hijos de un nodo (afecta cual solucion se
      encuentra primero).
"""
from __future__ import annotations

import time

from ..nodo import Nodo, reconstruir_camino, reconstruir_camino_de_estados
from ..resultado import Resultado


def buscar_profundidad(problema) -> Resultado:
    """DFS sobre `problema` evitando ciclos dentro de cada rama. Si no hay solucion, el Resultado lo indica."""
    inicio = time.perf_counter()
    raiz = Nodo(problema.estado_inicial())
    pila = [raiz]
    nodos_expandidos = 0

    while pila:
        nodo = pila.pop()
        nodos_expandidos += 1
        if problema.es_meta(nodo.estado):
            movimientos = reconstruir_camino(nodo)
            return Resultado(
                camino_de_movimientos=tuple(movimientos),
                nodos_expandidos=nodos_expandidos,
                profundidad_de_la_solucion=len(movimientos),
                tiempo_de_computo=time.perf_counter() - inicio,
                camino_de_estados=tuple(reconstruir_camino_de_estados(nodo)),
            )
        camino_de_la_rama = set(reconstruir_camino_de_estados(nodo))
        for movimiento, estado, costo in reversed(
            problema.sucesores(nodo.estado, camino_de_la_rama)
        ):
            pila.append(
                Nodo(
                    estado,
                    nodo,
                    movimiento,
                    nodo.profundidad + 1,
                    nodo.costo_acumulado + costo,
                )
            )

    return Resultado(
        camino_de_movimientos=(),
        nodos_expandidos=nodos_expandidos,
        profundidad_de_la_solucion=0,
        tiempo_de_computo=time.perf_counter() - inicio,
        solucion_encontrada=False,
    )
