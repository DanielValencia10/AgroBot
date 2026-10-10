"""
Archivo:       src/agrobot/main.py
Objetivo:      Punto de entrada de la aplicacion AgroBot: crear la interfaz grafica y
               conectar todas las piezas del proyecto (modelo, problema, busqueda,
               archivos y gui).
Responsabilidad:
    SI hace:
        - Inicializar y mostrar la ventana principal de la aplicacion.
        - Ser el unico archivo del proyecto que puede importar de todos los paquetes
          (modelo/, problema/, busqueda/ y gui/), ya que su rol es de composicion.
    NO hace:
        - No implementa logica propia de dominio, busqueda ni interfaz: delega todo en
          los paquetes correspondientes.
Importa de:
    - gui.ventana_principal (VentanaPrincipal): para crear y mostrar la interfaz.
    - (de forma indirecta, a traves de la composicion general del proyecto, puede
      necesitar referenciar modelo/, problema/, busqueda/ y archivos/ segun como se
      resuelva la inicializacion, pero la composicion principal pasa por gui/).
Lo importan:
    - (ninguno; es el punto de entrada del programa, se ejecuta directamente).
Contrato previsto:
    - punto_de_entrada() / bloque principal: crea la VentanaPrincipal y arranca la
      aplicacion.
"""
