"""
Archivo:       src/agrobot/busqueda/informada/avara.py
Objetivo:      Implementar busqueda Avara (Greedy Best-First Search) sobre el problema
               AgroBot recibido como parametro, expandiendo siempre el nodo que parece
               mas cercano a la meta segun la heuristica.
Responsabilidad:
    SI hace:
        - Usar una cola de prioridad ordenada unicamente por el valor de la heuristica
          h(estado) (sin considerar el costo acumulado g) como frontera de expansion.
        - En cada expansion: verificar si el nodo es meta; si no lo es, generar sus
          hijos (segun problema.sucesores), calcular h(estado_hijo) e insertarlos en
          la cola de prioridad. Expandir un nodo cuenta 1 hacia nodos_expandidos; al
          expandir una meta no se crean hijos.
        - Llenar el Resultado con: camino de movimientos, nodos_expandidos,
          profundidad de la solucion (profundidad evitando ciclos, no el costo) y
          tiempo de computo. No llena costo_total (campo exclusivo de Costo uniforme y
          A*).
    NO hace:
        - No conoce Mundo, Estado ni detalles del dominio: solo usa el objeto
          "problema" recibido como parametro, a traves de su contrato: estado_inicial(),
          es_meta(estado), sucesores(estado, camino_de_la_rama).
        - No garantiza camino optimo en costo ni en numero de movimientos (la busqueda
          avara no es completa ni optima en general).
Importa de:
    - busqueda.nodo (Nodo): para construir los nodos del arbol de busqueda.
    - busqueda.resultado (Resultado): para construir la salida final.
    - busqueda.informada.heuristica: para calcular h(estado) de cada nodo generado.
Lo importan:
    - gui/panel_control.py (al seleccionar "Informada" > "Avara") y main.py.
Contrato previsto:
    - buscar_avara(problema): recibe un objeto que cumple el contrato de problema
      (estado_inicial, es_meta, sucesores) y retorna un Resultado con la solucion
      encontrada guiada por la heuristica (o la indicacion de que no hay solucion).
PENDIENTE:
    - Criterio de desempate entre nodos con el mismo valor de heuristica en la cola de
      prioridad.
"""
