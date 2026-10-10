"""
Archivo:       src/agrobot/gui/panel_reporte.py
Objetivo:      Mostrar al usuario el reporte de metricas de la busqueda ejecutada:
               nodos expandidos, profundidad de la solucion, tiempo de computo y,
               cuando aplique, el costo total.
Responsabilidad:
    SI hace:
        - Leer los campos del Resultado entregado (nodos_expandidos,
          profundidad_de_la_solucion, tiempo_de_computo y costo_total) y mostrarlos de
          forma legible.
        - Mostrar el campo costo_total solo cuando el algoritmo ejecutado fue Costo
          uniforme o A* (los demas algoritmos no lo calculan).
    NO hace:
        - No calcula ninguna de estas metricas: solo las muestra.
        - No anima el camino de movimientos (eso es de animacion.py).
Importa de:
    - busqueda.resultado (Resultado): para leer los campos a mostrar.
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
Contrato previsto:
    - PanelReporte: componente de interfaz que, dado un Resultado y el nombre del
      algoritmo ejecutado, muestra sus metricas (mostrando costo_total solo cuando
      corresponda).
PENDIENTE:
    - Libreria de GUI a usar (depende de la misma decision de ventana_principal.py).
"""
