"""
Archivo:       src/agrobot/busqueda/no_informada/costo_uniforme.py
Objetivo:      Implementar busqueda de Costo uniforme (Uniform Cost Search) sobre el
               problema AgroBot recibido como parametro, garantizando el camino de
               menor costo acumulado.
Responsabilidad:
    SI hace:
        - Usar una cola de prioridad ordenada por costo acumulado desde la raiz (g)
          como frontera de expansion: siempre se expande el nodo de menor costo
          acumulado disponible en la frontera.
        - En cada expansion: verificar si el nodo es meta; si no lo es, generar sus
          hijos con su costo acumulado (costo del padre + costo del paso, segun
          problema.sucesores) e insertarlos en la cola de prioridad. Expandir un nodo
          cuenta 1 hacia nodos_expandidos; al expandir una meta no se crean hijos.
        - Llenar el Resultado con: camino de movimientos, nodos_expandidos,
          profundidad de la solucion (profundidad evitando ciclos, no el costo),
          tiempo de computo y costo_total (este algoritmo SI llena este campo).
    NO hace:
        - No conoce Mundo, Estado ni detalles del dominio: solo usa el objeto
          "problema" recibido como parametro, a traves del contrato: estado_inicial(),
          es_meta(estado), sucesores(estado, camino_de_la_rama) -> lista de
          (movimiento, estado_sucesor, costo_del_paso).
        - No usa heuristica (eso es de busqueda/informada/).
Importa de:
    - busqueda.nodo (Nodo): para construir los nodos del arbol de busqueda, incluyendo
      su costo_acumulado.
    - busqueda.resultado (Resultado): para construir la salida final.
Lo importan:
    - gui/panel_control.py (al seleccionar "No informada" > "Costo uniforme") y main.py.
Contrato previsto:
    - buscar_costo_uniforme(problema): recibe un objeto que cumple el contrato de
      problema (estado_inicial, es_meta, sucesores con costo por paso) y retorna un
      Resultado con la solucion de menor costo (o la indicacion de que no hay
      solucion).
Decisiones de equipo (antes PENDIENTE):
    - Desempate: entre nodos con el mismo costo acumulado sale primero el que se
      inserto antes en la cola de prioridad (se usa un contador creciente como segundo
      criterio, asi nunca se comparan Nodos entre si).
    - Estados repetidos: se guarda el menor costo con el que se ha generado cada estado.
      Un estado solo se vuelve a insertar si se llega a el con un costo MENOR. A
      problema.sucesores se le pasa un camino vacio (igual que en amplitud.py).
    - Entradas viejas: si al sacar un nodo de la cola su costo ya es mayor que el mejor
      conocido para ese estado, se descarta sin expandirlo ni contarlo.
    - nodos_expandidos cuenta tambien el nodo meta (verificarlo cuenta como expandirlo).
    - La meta se verifica al sacar el nodo de la cola (no al generarlo); asi el primer
      nodo meta que sale es el de menor costo.
"""
from __future__ import annotations

import heapq
import time
from itertools import count

from ..nodo import Nodo, reconstruir_camino, reconstruir_camino_de_estados
from ..resultado import Resultado


def buscar_costo_uniforme(problema) -> Resultado:
    """Costo uniforme sobre `problema`. Si no hay solucion, el Resultado lo indica."""
    inicio = time.perf_counter()
    raiz = Nodo(problema.estado_inicial())
    desempate = count()
    frontera = [(0.0, next(desempate), raiz)]   # (costo acumulado, orden de insercion, nodo)
    mejor_costo = {raiz.estado: 0.0}            # menor costo conocido de cada estado
    nodos_expandidos = 0

    while frontera:
        costo, _, nodo = heapq.heappop(frontera)
        if costo > mejor_costo[nodo.estado]:
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
        for movimiento, estado, costo_del_paso in problema.sucesores(nodo.estado, ()):
            nuevo_costo = nodo.costo_acumulado + costo_del_paso
            if estado in mejor_costo and nuevo_costo >= mejor_costo[estado]:
                continue
            mejor_costo[estado] = nuevo_costo
            hijo = Nodo(estado, nodo, movimiento, nodo.profundidad + 1, nuevo_costo)
            heapq.heappush(frontera, (nuevo_costo, next(desempate), hijo))

    return Resultado(
        camino_de_movimientos=(),
        nodos_expandidos=nodos_expandidos,
        profundidad_de_la_solucion=0,
        tiempo_de_computo=time.perf_counter() - inicio,
        solucion_encontrada=False,
    )