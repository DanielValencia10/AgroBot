"""
Archivo:       src/agrobot/constantes.py
Objetivo:      Centralizar los valores fijos del dominio AgroBot para que ningun otro
               archivo tenga que repetir numeros "magicos" relacionados con el formato
               de mundo, la capacidad del robot o las dimensiones de la cuadricula.
Responsabilidad:
    SI hace:
        - Definir los codigos numericos usados en los archivos de mundo (.txt):
          0 = libre, 1 = obstaculo, 2 = AgroBot, 3 = cultivo seco, 4 = deposito,
          5 = avioneta.
        - Definir la capacidad maxima de fertilizante del robot (2 unidades).
        - Definir el combustible inicial de la avioneta (30 unidades).
        - Definir el tamano de la cuadricula (10 x 10).
    NO hace:
        - No contiene logica de validacion, lectura de archivos ni estructuras de datos.
        - No importa nada de otros modulos del proyecto.
Importa de:    (nada del proyecto; este es el modulo base de toda la jerarquia).
Lo importan:   modelo/mundo.py, modelo/estado.py, modelo/movimiento.py,
               problema/agrobot_problema.py, problema/operadores.py, problema/costos.py,
               problema/ciclos.py, archivos/lector_mundo.py, y potencialmente main.py.
Contrato previsto:
    - CODIGO_LIBRE, CODIGO_OBSTACULO, CODIGO_AGROBOT, CODIGO_CULTIVO_SECO,
      CODIGO_DEPOSITO, CODIGO_AVIONETA: constantes enteras con los codigos de celda
      descritos arriba.
    - CAPACIDAD_FERTILIZANTE: entero, capacidad maxima de fertilizante que puede
      transportar el robot (2).
    - COMBUSTIBLE_INICIAL_AVIONETA: entero, combustible con el que inicia la avioneta (30).
    - TAMANO_CUADRICULA: entero, numero de filas y de columnas de la cuadricula (10).
"""
