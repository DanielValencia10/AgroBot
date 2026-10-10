"""
Archivo:       tests/test_algoritmos.py
Objetivo:      Documentar que se va a verificar sobre los cinco algoritmos de busqueda
               (Amplitud, Costo uniforme, Profundidad, Avara, A*), sin implementar aun
               los casos de prueba.
Responsabilidad:
    QUE VERIFICARA (cuando se implemente), usando como referencia el mundo
    mundos/Prueba1.txt (robot en (4,0), deposito en (0,2), avioneta en (0,6),
    cultivos en (4,3), (5,3) y (6,8)):
        - Que cada uno de los cinco algoritmos encuentre una solucion valida: un
          camino de movimientos que, aplicado desde el estado inicial, termina en un
          estado meta (P vacio).
        - Que el Resultado de cada algoritmo tenga nodos_expandidos,
          profundidad_de_la_solucion y tiempo_de_computo con valores coherentes
          (por ejemplo, nodos_expandidos >= profundidad_de_la_solucion + 1).
        - Que Costo uniforme y A* reporten costo_total, y que ese costo sea el minimo
          posible para este mundo (verificable de forma independiente o comparando
          contra el otro).
        - Que Amplitud, Costo uniforme y Profundidad no usen la heuristica (no
          dependen de busqueda/informada/heuristica.py).
        - Que Avara y A* usen la heuristica definida en
          busqueda/informada/heuristica.py.
        - Que el criterio de nodos expandidos sea consistente entre algoritmos:
          expandir un nodo es verificar si es meta y, si no lo es, generar sus hijos;
          al expandir una meta no se generan hijos.
Importa de:
    - busqueda.no_informada.amplitud, busqueda.no_informada.costo_uniforme,
      busqueda.no_informada.profundidad, busqueda.informada.avara,
      busqueda.informada.a_estrella (al implementarse): para ejecutar cada algoritmo.
    - problema.agrobot_problema (AgroBotProblema): para construir el problema de
      prueba.
    - archivos.lector_mundo: para cargar mundos/Prueba1.txt.
PENDIENTE:
    - Framework de pruebas a usar (por ejemplo pytest o unittest de la libreria
      estandar).
    - Depende de que queden resueltos los PENDIENTE de costos.py, ciclos.py y
      heuristica.py para poder verificar valores exactos de costo y de admisibilidad.
"""
