"""
Archivo:       src/agrobot/problema/agrobot_problema.py
Objetivo:      Definir el problema de busqueda AgroBot como lo consumen los algoritmos
               de busqueda: estado inicial, prueba de meta, generacion de sucesores y
               costo de cada paso, integrando Mundo, Estado, operadores, costos y
               control de ciclos.
Responsabilidad:
    SI hace:
        - Construir el estado inicial del problema a partir de un Mundo ya cargado.
        - Determinar si un estado es meta: el conjunto de cultivos secos pendientes P
          esta vacio.
        - Generar, para un estado dado, la lista de sucesores (par movimiento, estado
          resultante, costo del paso), aplicando en orden: precondicion y efectos de
          operadores.py, costo de costos.py, y filtro de ciclos de ciclos.py.
        - Exponer el costo de un paso ya calculado para que los algoritmos de busqueda
          lo acumulen.
    NO hace:
        - No implementa ningun algoritmo de busqueda (eso vive en busqueda/).
        - No dibuja ni anima nada (eso es de gui/).
        - No lee archivos de texto (recibe un Mundo ya construido por
          archivos/lector_mundo.py).
Importa de:
    - modelo.mundo (Mundo): entorno fijo sobre el que se construye el problema.
    - modelo.estado (Estado): representacion del estado inicial y de los sucesores.
    - modelo.movimiento (Movimiento): para iterar los movimientos posibles.
    - problema.operadores: para validar precondiciones y aplicar efectos al generar
      cada sucesor.
    - problema.costos: para asignar el costo de cada paso generado.
    - problema.ciclos: para descartar sucesores que repiten estado en la misma rama
      (salvo excepciones).
    - constantes: para valores iniciales (capacidad de fertilizante, combustible
      inicial) al construir el estado inicial.
Lo importan:
    - busqueda/* (no importan este modulo directamente, pues busqueda/ no puede
      importar de problema/; en su lugar, una instancia de AgroBotProblema se les pasa
      como parametro y los algoritmos la usan a traves del contrato descrito en sus
      propias cabeceras).
    - gui/panel_control.py y main.py (para construir el problema a partir del Mundo
      leido y pasarlo al algoritmo de busqueda elegido).
Contrato previsto:
    - AgroBotProblema: clase que envuelve un Mundo y expone el contrato esperado por
      los algoritmos de busqueda:
        - estado_inicial(): retorna el Estado inicial del problema.
        - es_meta(estado): retorna si el estado dado es un estado meta (P vacio).
        - sucesores(estado, camino_de_la_rama): retorna la lista de tuplas
          (movimiento, estado_sucesor, costo_del_paso) validas desde el estado dado,
          ya filtradas por precondicion, efectos y control de ciclos.
PENDIENTE:
    - Si la generacion de sucesores recibe el camino completo de la rama (para
      ciclos.py) o una estructura mas liviana (por ejemplo, un conjunto de estados
      visitados en la rama); esto depende de la decision tomada en ciclos.py.
"""
