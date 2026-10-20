"""
Archivo:       src/agrobot/busqueda/informada/a_estrella.py
Objetivo:      Implementar busqueda A* sobre el problema AgroBot recibido como
               parametro, expandiendo siempre el nodo de menor f = g + h, combinando
               costo acumulado real y estimacion heuristica.
Responsabilidad:
    SI hace:
        - Usar una cola de prioridad ordenada por f(nodo) = costo_acumulado(nodo) +
          h(estado_del_nodo) como frontera de expansion.
        - En cada expansion: verificar si el nodo es meta; si no lo es, generar sus
          hijos con su costo acumulado (segun problema.sucesores) y su valor de f, e
          insertarlos en la cola de prioridad. Expandir un nodo cuenta 1 hacia
          nodos_expandidos; al expandir una meta no se crean hijos.
        - Llenar el Resultado con: camino de movimientos, nodos_expandidos,
          profundidad de la solucion (profundidad evitando ciclos, no el costo),
          tiempo de computo y costo_total (este algoritmo SI llena este campo).
        - Garantizar optimalidad en costo siempre que la heuristica usada
          (busqueda/informada/heuristica.py) sea admisible.
    NO hace:
        - No conoce Mundo, Estado ni detalles del dominio: solo usa el objeto
          "problema" recibido como parametro, a traves de su contrato: estado_inicial(),
          es_meta(estado), sucesores(estado, camino_de_la_rama) -> lista de
          (movimiento, estado_sucesor, costo_del_paso).
        - No demuestra la admisibilidad de la heuristica: esa justificacion vive en
          heuristica.py y en el informe.
Importa de:
    - busqueda.nodo (Nodo): para construir los nodos del arbol de busqueda, incluyendo
      su costo_acumulado.
    - busqueda.resultado (Resultado): para construir la salida final.
    - busqueda.informada.heuristica: para calcular h(estado) de cada nodo generado.
Lo importan:
    - gui/panel_control.py (al seleccionar "Informada" > "A*") y main.py.
Contrato previsto:
    - buscar_a_estrella(problema): recibe un objeto que cumple el contrato de problema
      (estado_inicial, es_meta, sucesores con costo por paso) y retorna un Resultado
      con la solucion de menor costo (o la indicacion de que no hay solucion).
PENDIENTE:
    - Criterio de desempate entre nodos con el mismo valor de f en la cola de
      prioridad (por ejemplo, priorizar mayor g o menor h).
"""
from __future__ import annotations

import heapq
import time
from itertools import count

from ..nodo import Nodo, reconstruir_camino, reconstruir_camino_de_estados
from ..resultado import Resultado

def buscar_a_estrella(problema, heuristica) -> Resultado:
    
    inicio = time.perf_counter()
    raiz = Nodo(problema.estado_inicial())
    desempate = count()
    heur_raiz = heuristica(raiz.estado)
    frontera = [(heur_raiz, next(desempate), raiz)]   # (f, orden de insercion, nodo)
    mejor_costo = {raiz.estado: 0.0}            # menor costo conocido de cada estado
    nodos_expandidos = 0

    while frontera:
        _, _, nodo = heapq.heappop(frontera)
        if nodo.costo_acumulado > mejor_costo[nodo.estado]:
            continue   # entrada vieja: ya se encontro un camino mas barato a este estado
        nodos_expandidos += 1
        if problema.es_meta(nodo.estado):
            movimientos = reconstruir_camino(nodo)
            return Resultado(
                camino_de_movimientos=tuple(movimientos),
                nodos_expandidos=nodos_expandidos,
                profundidad_de_la_solucion=len(movimientos),
                tiempo_de_computo=time.perf_counter() - inicio,
                costo_total=nodo.costo_acumulado,
                camino_de_estados=tuple(reconstruir_camino_de_estados(nodo)),
            )
        for movimiento, estado, costo_del_paso in problema.sucesores(nodo.estado, reconstruir_camino_de_estados(nodo)):
            nuevo_costo = nodo.costo_acumulado + costo_del_paso
            if estado in mejor_costo and nuevo_costo >= mejor_costo[estado]:
                continue
            mejor_costo[estado] = nuevo_costo
            hijo = Nodo(estado, nodo, movimiento, nodo.profundidad + 1, nuevo_costo)
            heapq.heappush(frontera, (nuevo_costo + heuristica(estado), next(desempate), hijo))

    return Resultado(
        camino_de_movimientos=(),
        nodos_expandidos=nodos_expandidos,
        profundidad_de_la_solucion=0,
        tiempo_de_computo=time.perf_counter() - inicio,
        solucion_encontrada=False,
    )