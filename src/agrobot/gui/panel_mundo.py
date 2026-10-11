"""
Archivo:       src/agrobot/gui/panel_mundo.py
Objetivo:      Dibujar la cuadricula 10x10 del mundo en su estado inicial: obstaculos,
               deposito, avioneta, cultivos secos y posicion inicial del robot.
Responsabilidad:
    SI hace:
        - Recorrer el Mundo cargado y dibujar cada casilla segun su tipo (libre,
          obstaculo, robot, cultivo seco, deposito, avioneta), usando los codigos de
          constantes.py como referencia de que representa cada uno.
    NO hace:
        - No anima movimientos (eso es responsabilidad de animacion.py).
        - No calcula ni conoce la solucion de busqueda.
        - No lee archivos de texto (recibe un Mundo ya construido).
Importa de:
    - modelo.mundo (Mundo): para conocer los elementos fijos del mundo a dibujar.
    - constantes: para los codigos de celda usados al decidir como dibujar cada
      casilla.
    - gui.cargador_sprites: Sprites.estatico(obtener_nombre_sprite_por_codigo(codigo))
      da la imagen de cada codigo de celda (es el unico archivo que conoce la ruta de
      assets/sprites/).
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
    - gui/animacion.py (puede reutilizar el dibujo base de la cuadricula antes de
      animar sobre ella).
Contrato previsto:
    - PanelMundo: componente de interfaz que, dado un Mundo, dibuja la cuadricula
      10x10 en su estado inicial.
PENDIENTE:
    - Libreria de GUI a usar (depende de la misma decision de ventana_principal.py).
"""
