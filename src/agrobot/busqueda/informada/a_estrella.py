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
