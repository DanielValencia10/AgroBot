"""
Archivo:       src/agrobot/gui/panel_control.py
Objetivo:      Ofrecer al usuario los controles para elegir el tipo y algoritmo de
               busqueda a ejecutar, y para cargar el archivo de mundo sobre el que se
               va a resolver el problema.
Responsabilidad:
    SI hace:
        - Permitir elegir entre "No informada" (con sub-opciones Amplitud, Costo
          uniforme, Profundidad evitando ciclos) o "Informada" (con sub-opciones
          Avara, A*).
        - Permitir cargar un archivo de mundo (.txt) usando archivos/lector_mundo.py.
        - Al confirmar, construir el AgroBotProblema a partir del Mundo cargado,
          ejecutar el algoritmo de busqueda elegido y entregar el Resultado obtenido a
          quien ensambla la ventana (ventana_principal.py), para que lo propague a
          animacion.py y panel_reporte.py.
    NO hace:
        - No dibuja la cuadricula ni anima el camino (eso es de panel_mundo.py y
          animacion.py).
        - No implementa la logica interna de ningun algoritmo de busqueda.
Importa de:
    - busqueda.no_informada.amplitud, busqueda.no_informada.costo_uniforme,
      busqueda.no_informada.profundidad, busqueda.informada.avara,
      busqueda.informada.a_estrella: para ejecutar el algoritmo elegido por el
      usuario.
    - problema.agrobot_problema (AgroBotProblema): para construir el problema a partir
      del Mundo cargado, antes de pasarlo al algoritmo elegido.
    - archivos.lector_mundo: para cargar el Mundo desde el archivo .txt seleccionado.
    - modelo.mundo (Mundo): para pasarlo entre lector_mundo y agrobot_problema.
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
Contrato previsto:
    - PanelControl: componente de interfaz que expone la seleccion de algoritmo, la
      carga de archivo, y al confirmar entrega un Resultado (ejecutando el algoritmo
      elegido sobre el problema construido) para que la ventana principal lo propague
      a los demas paneles.
PENDIENTE:
    - Libreria de GUI a usar (depende de la misma decision de ventana_principal.py).
"""
