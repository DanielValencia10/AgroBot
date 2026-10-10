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
PENDIENTE:
    - Criterio de desempate cuando varios sucesores de un mismo nodo podrian llevar a
      la meta en el mismo nivel (depende del orden de los operadores, ver
      modelo/movimiento.py).
"""
