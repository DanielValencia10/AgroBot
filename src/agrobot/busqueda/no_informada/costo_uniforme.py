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
PENDIENTE:
    - Criterio de desempate entre nodos con el mismo costo acumulado en la cola de
      prioridad (por ejemplo, orden de insercion, profundidad, o el orden de los
      operadores).
"""
