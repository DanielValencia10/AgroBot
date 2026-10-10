"""
Archivo:       src/agrobot/gui/animacion.py
Objetivo:      Reproducir visualmente, paso a paso, los movimientos del camino
               solucion contenido en un Resultado, sobre la cuadricula dibujada por
               panel_mundo.py.
Responsabilidad:
    SI hace:
        - Recorrer la lista de movimientos del Resultado en orden y, para cada uno,
          actualizar la posicion visual del robot (y, si aplica, de la avioneta) sobre
          la cuadricula.
    NO hace:
        - No calcula el camino solucion (eso lo hace el algoritmo de busqueda elegido).
        - No dibuja el estado inicial completo de la cuadricula (eso es de
          panel_mundo.py; animacion.py dibuja sobre esa base).
Importa de:
    - busqueda.resultado (Resultado): para leer el camino de movimientos a animar.
    - modelo.movimiento (Movimiento): para traducir cada movimiento en un
      desplazamiento visual (fila, columna).
    - modelo.mundo (Mundo): para conocer el contexto fijo sobre el que se anima
      (limites, obstaculos, etc.).
    - gui.cargador_sprites: para obtener los sprites de cada paso (incluyendo el
      cambio a "robot_en_avioneta" y a "cultivo_tratado" segun el estado actual;
      es el unico archivo que conoce la ruta de assets/sprites/).
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
Contrato previsto:
    - PanelAnimacion: componente de interfaz que, dado un Resultado y el Mundo sobre
      el que se calculo, reproduce visualmente el camino de movimientos de la
      solucion.
PENDIENTE:
    - Libreria de GUI a usar (depende de la misma decision de ventana_principal.py).
    - Velocidad/control de reproduccion de la animacion (automatica, paso a paso por
      el usuario, o ambas).
"""
