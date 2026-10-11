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
Decisiones de equipo (antes PENDIENTE):
    - Orden de los efectos al entrar a una casilla: primero el consumo de combustible
      (segun el e de ANTES de moverse), luego avioneta, deposito y cultivo. En los
      mundos de prueba no coinciden dos de ellos en una casilla, pero el orden queda fijo.
    - La avioneta "no usada" es la que cumple e=falso y k=COMBUSTIBLE_INICIAL_AVIONETA;
      una avioneta ya agotada (e=falso, k=0) no vuelve a subir al robot.
    - Orden de los movimientos: el de modelo/movimiento.py (arriba, abajo, izquierda,
      derecha).
"""
from __future__ import annotations

from dataclasses import replace

from .. import constantes
from ..modelo.estado import Estado
from ..modelo.movimiento import obtener_desplazamiento


def _destino(estado: Estado, movimiento) -> tuple:
    delta_fila, delta_columna = obtener_desplazamiento(movimiento)
    return (estado.fila + delta_fila, estado.columna + delta_columna)


def es_aplicable(mundo, estado: Estado, movimiento) -> bool:
    """El destino esta dentro de la cuadricula y no es un obstaculo."""
    destino = _destino(estado, movimiento)
    return mundo.esta_dentro_de_cuadricula(destino) and not mundo.es_obstaculo(destino)


def aplicar(mundo, estado: Estado, movimiento) -> Estado:
    """Estado resultante de mover al robot y aplicar los efectos de la casilla destino.

    Asume que es_aplicable(mundo, estado, movimiento) ya se verifico.
    """
    destino = _destino(estado, movimiento)
    fertilizante = estado.fertilizante
    en_avioneta = estado.en_avioneta
    combustible = estado.combustible
    pendientes = estado.pendientes

    if en_avioneta:  # viajaba en avioneta: este paso gasta una unidad
        combustible -= 1
        if combustible == 0:  # avioneta agotada
            en_avioneta = False

    if (destino == mundo.avioneta and not en_avioneta
            and combustible == constantes.COMBUSTIBLE_INICIAL_AVIONETA):
        en_avioneta = True  # sube sin gastar combustible en este movimiento

    if destino == mundo.deposito:
        fertilizante = constantes.CAPACIDAD_FERTILIZANTE

    if destino in pendientes and fertilizante > 0:
        fertilizante -= 1
        pendientes = pendientes - {destino}

    return replace(
        estado,
        fila=destino[0],
        columna=destino[1],
        fertilizante=fertilizante,
        en_avioneta=en_avioneta,
        combustible=combustible,
        pendientes=pendientes,
    )

