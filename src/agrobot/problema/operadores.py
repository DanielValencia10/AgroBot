"""
Archivo:       src/agrobot/problema/operadores.py
Objetivo:      Definir la precondicion de aplicabilidad de un movimiento y los efectos
               automaticos que ocurren al entrar a una casilla, produciendo el Estado
               sucesor a partir de un Estado y un Movimiento.
Responsabilidad:
    SI hace:
        - Verificar la precondicion de un movimiento: la casilla destino debe estar
          dentro de la cuadricula y no debe ser un obstaculo (usa Mundo).
        - Aplicar los efectos automaticos al entrar a la casilla destino, en este orden
          conceptual (el orden exacto de implementacion queda PENDIENTE):
            - Si la casilla es el deposito: fertilizante vuelve a su capacidad maxima
              (phi <- CAPACIDAD_FERTILIZANTE).
            - Si la casilla es un cultivo seco pendiente y phi > 0: se fertiliza
              (phi <- phi - 1) y la casilla sale del conjunto de pendientes P.
            - Si la casilla es la posicion original de la avioneta y esta no ha sido
              usada aun: el robot sube a la avioneta (e <- verdadero), sin consumir
              combustible en ese mismo movimiento.
            - Consumo de combustible: si e era verdadero ANTES de este movimiento,
              se consume una unidad (k <- k - 1); si k llega a 0, la avioneta queda
              agotada (e <- falso).
    NO hace:
        - No decide el costo numerico del movimiento: eso es responsabilidad de
          problema/costos.py.
        - No decide si el estado resultante viola la restriccion de ciclos: eso es
          responsabilidad de problema/ciclos.py.
        - No conoce algoritmos de busqueda.
Importa de:
    - modelo.mundo (Mundo): para validar limites de la cuadricula y obstaculos.
    - modelo.estado (Estado): para construir el Estado sucesor inmutable.
    - modelo.movimiento (Movimiento): para conocer el desplazamiento asociado a cada
      movimiento.
    - constantes: para CAPACIDAD_FERTILIZANTE y COMBUSTIBLE_INICIAL_AVIONETA al aplicar
      los efectos de deposito y de consumo de combustible.
Lo importan:
    - problema/agrobot_problema.py (para generar los sucesores de un estado).
Contrato previsto:
    - es_aplicable(mundo, estado, movimiento): retorna si el movimiento cumple la
      precondicion (destino dentro de la cuadricula y no obstaculo) desde la posicion
      actual del estado.
    - aplicar(mundo, estado, movimiento): retorna el Estado sucesor que resulta de
      aplicar el movimiento (desplazamiento + efectos automaticos descritos arriba)
      sobre el estado dado. Asume que es_aplicable ya fue verificado.
PENDIENTE:
    - Orden exacto de evaluacion de los operadores/efectos cuando una misma casilla
      pudiera activar mas de un efecto (en los mundos de prueba no coinciden deposito,
      cultivo y avioneta en una misma casilla, pero el orden de implementacion debe
      quedar explicito).
    - Orden en que se recorren los movimientos (ver tambien modelo/movimiento.py).
"""
