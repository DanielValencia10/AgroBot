"""
Archivo:       src/agrobot/busqueda/no_informada/amplitud.py
Objetivo:      Implementar busqueda en Amplitud (BFS) sobre el problema AgroBot
               recibido como parametro, explorando nivel por nivel desde la raiz.
Responsabilidad:
    SI hace:
        - Usar una cola FIFO (primero en entrar, primero en salir) como frontera de
          expansion, de modo que todos los nodos de una profundidad se expandan antes
          de pasar a la siguiente.
        - En cada expansion: verificar si el nodo es meta (segun problema.es_meta); si
          no lo es, generar sus hijos (segun problema.sucesores) y encolarlos. Expandir
          un nodo cuenta 1 hacia nodos_expandidos; al expandir una meta no se crean
          hijos.
        - Llenar el Resultado con: camino de movimientos (reconstruido desde el nodo
          meta), nodos_expandidos, profundidad de la solucion (= numero de movimientos
          del camino, contando profundidad evitando ciclos) y tiempo de computo.
          No llena costo_total (ese campo es solo para Costo uniforme y A*).
    NO hace:
        - No conoce la clase Mundo, Estado ni ningun detalle del dominio AgroBot: solo
          usa el objeto "problema" recibido como parametro, a traves del contrato:
          estado_inicial(), es_meta(estado), sucesores(estado, camino_de_la_rama) ->
          lista de (movimiento, estado_sucesor, costo_del_paso).
        - No garantiza camino de costo minimo (BFS minimiza numero de movimientos, no
          costo, salvo que todos los costos sean iguales).
Importa de:
    - busqueda.nodo (Nodo): para construir los nodos del arbol de busqueda.
    - busqueda.resultado (Resultado): para construir la salida final.
    - (no importa de modelo/ ni de problema/: respeta la regla de que busqueda/ no
      depende de esos paquetes).
Lo importan:
    - gui/panel_control.py (al seleccionar "No informada" > "Amplitud") y main.py.
Contrato previsto:
    - buscar_amplitud(problema): recibe un objeto que cumple el contrato de problema
      (estado_inicial, es_meta, sucesores) y retorna un Resultado con la solucion
      encontrada (o la indicacion de que no hay solucion).
Decisiones de equipo (antes PENDIENTE):
    - Desempate: los hijos se encolan en el orden en que los entrega problema.sucesores
      (arriba, abajo, izquierda, derecha); entre nodos del mismo nivel sale primero el
      que se encolo antes.
    - Estados repetidos: se lleva un conjunto de estados ya generados para todo el arbol
      (como la Demo), no solo de la rama. Es mas fuerte que el control de ciclos por
      rama, asi que a problema.sucesores se le pasa un camino vacio.
    - nodos_expandidos cuenta tambien el nodo meta (verificarlo cuenta como expandirlo).
    - La meta se verifica al sacar el nodo de la cola, no al generarlo.
"""
from __future__ import annotations

import time
from collections import deque

from ..nodo import Nodo, reconstruir_camino, reconstruir_camino_de_estados
from ..resultado import Resultado


def buscar_amplitud(problema) -> Resultado:
    """BFS sobre `problema`. Si no hay solucion, el Resultado lo indica."""
    inicio = time.perf_counter()
    raiz = Nodo(problema.estado_inicial())
    frontera = deque([raiz])
    generados = {raiz.estado}
    nodos_expandidos = 0

    while frontera:
        nodo = frontera.popleft()
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
        for movimiento, estado, costo in problema.sucesores(nodo.estado, ()):
            if estado in generados:
                continue
            generados.add(estado)
            frontera.append(Nodo(estado, nodo, movimiento, nodo.profundidad + 1,
                                 nodo.costo_acumulado + costo))

    return Resultado(
        camino_de_movimientos=(),
        nodos_expandidos=nodos_expandidos,
        profundidad_de_la_solucion=0,
        tiempo_de_computo=time.perf_counter() - inicio,
        solucion_encontrada=False,
    )

