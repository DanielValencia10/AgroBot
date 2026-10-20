"""
Archivo:       src/agrobot/busqueda/informada/avara.py
Objetivo:      Implementar busqueda Avara (Greedy Best-First Search) sobre el problema
               AgroBot recibido como parametro, expandiendo siempre el nodo que parece
               mas cercano a la meta segun la heuristica.
Responsabilidad:
    SI hace:
        - Usar una cola de prioridad ordenada unicamente por el valor de la heuristica
          h(estado) (sin considerar el costo acumulado g) como frontera de expansion.
          Las entradas son (h, contador, nodo): el contador sube en 1 con cada nodo
          insertado y desempata por orden de insercion (el primero en entrar sale
          primero), porque los Nodo no se pueden comparar entre si.
        - En cada expansion: verificar si el nodo es meta; si no lo es, generar sus
          hijos (segun problema.sucesores), calcular h(estado_hijo) e insertarlos en
          la cola de prioridad. Expandir un nodo cuenta 1 hacia nodos_expandidos; al
          expandir una meta no se crean hijos (la meta tambien cuenta como expandida).
        - Evitar ciclos por rama, igual que Profundidad: a sucesores se le pasa el
          conjunto de estados del camino desde la raiz hasta el nodo expandido.
        - Llenar el Resultado con: camino de movimientos, nodos_expandidos,
          profundidad de la solucion (profundidad evitando ciclos, no el costo) y
          tiempo de computo. No llena costo_total (campo exclusivo de Costo uniforme y
          A*), aunque cada Nodo si acumula su costo.
    NO hace:
        - No conoce Mundo, Estado ni detalles del dominio: solo usa el objeto
          "problema" recibido como parametro, a traves de su contrato: estado_inicial(),
          es_meta(estado), sucesores(estado, camino_de_la_rama).
        - No crea la heuristica: la recibe ya armada (ver crear_heuristica en
          heuristica.py), porque necesita datos del Mundo (el deposito).
        - No garantiza camino optimo en costo ni en numero de movimientos: al mirar solo
          h ignora lo que ya gasto (por ejemplo, no va por la avioneta si esta lo aleja
          de los cultivos). Sin control de ciclos una Avara pura podria quedar atrapada
          en un minimo local; aqui lo evita el control por rama. En un mundo sin
          solucion explora todas las ramas y puede tardar mucho.
Importa de:
    - busqueda.nodo (Nodo): para construir los nodos del arbol de busqueda.
    - busqueda.resultado (Resultado): para construir la salida final.
    (No importa heuristica.py: recibe la funcion h como parametro.)
Lo importan:
    - gui/panel_control.py, mediante la funcion puente _avara, que crea la heuristica con
      el deposito del mundo y llama a buscar_avara.
Contrato:
    - buscar_avara(problema, heuristica): `problema` cumple el contrato de problema
      (estado_inicial, es_meta, sucesores) y `heuristica` es una funcion estado ->
      numero >= 0 (la que devuelve crear_heuristica). Retorna un Resultado con la
      solucion encontrada guiada por la heuristica (o la indicacion de que no hay
      solucion).
Decision de equipo (antes PENDIENTE):
    - Desempate entre nodos con el mismo h: orden de insercion en la cola.
PENDIENTE:
    - Confirmar con el profesor si Avara debe evitar ciclos por rama (como Profundidad)
      o con un conjunto global de estados generados (como Amplitud).
"""

from __future__ import annotations

import heapq
import time
from itertools import count

from ..nodo import Nodo, reconstruir_camino, reconstruir_camino_de_estados
from ..resultado import Resultado

def buscar_avara(problema, heuristica) -> Resultado:
    inicio = time.perf_counter()
    raiz = Nodo(problema.estado_inicial())
    desempate = count()
    frontera = [(heuristica(raiz.estado), next(desempate), raiz)]
    nodos_expandidos = 0

    while frontera:
        _, _, nodo = heapq.heappop(frontera)
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
        rama = set(reconstruir_camino_de_estados(nodo))
        for movimiento, estado, costo in problema.sucesores(nodo.estado, rama):
            hijo = Nodo(estado, nodo, movimiento, nodo.profundidad + 1,
                        nodo.costo_acumulado + costo)
            heapq.heappush(frontera, (heuristica(estado), next(desempate), hijo))

    return Resultado(
        camino_de_movimientos=(),
        nodos_expandidos=nodos_expandidos,
        profundidad_de_la_solucion=0,
        tiempo_de_computo=time.perf_counter() - inicio,
        solucion_encontrada=False,
    )