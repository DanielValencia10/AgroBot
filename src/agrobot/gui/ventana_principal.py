"""
Archivo:       src/agrobot/gui/ventana_principal.py
Objetivo:      Ensamblar la ventana principal de la aplicacion, integrando el panel de
               control, el panel del mundo, la animacion y el panel de reporte en una
               sola interfaz coherente.
Responsabilidad:
    SI hace:
        - Crear la ventana/raiz de la aplicacion y organizar en ella los paneles:
          panel_control (seleccion de algoritmo y carga de archivo), panel_mundo
          (dibujo de la cuadricula), animacion (reproduccion del camino solucion) y
          panel_reporte (metricas de la busqueda).
        - Coordinar el flujo entre paneles: cuando panel_control dispara una busqueda,
          pasar el resultado a animacion y panel_reporte.
    NO hace:
        - No implementa la logica de dibujo detallada de cada panel (eso vive en cada
          archivo de gui/ correspondiente).
        - No implementa algoritmos de busqueda ni lectura de archivos: delega en
          busqueda/, problema/ y archivos/.
Importa de:
    - gui.panel_control: para la seleccion de algoritmo y carga de mundo.
    - gui.panel_mundo: para mostrar la cuadricula inicial.
    - gui.animacion: para reproducir el camino solucion.
    - gui.panel_reporte: para mostrar las metricas del Resultado.
    - modelo.mundo (Mundo): para pasar el mundo cargado a los paneles que lo
      necesitan.
Lo importan:
    - main.py (unico punto que crea la ventana principal).
Contrato previsto:
    - VentanaPrincipal: clase que construye y organiza los paneles de la aplicacion y
      expone el punto de entrada para mostrarla (por ejemplo, iniciar el bucle
      principal de la interfaz).
PENDIENTE:
    - Libreria de GUI a usar (por ejemplo tkinter de la libreria estandar, u otra),
      decision que afecta la forma concreta de este archivo y de los demas en gui/.
"""
