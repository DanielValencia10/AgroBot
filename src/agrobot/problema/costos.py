"""
Archivo:       src/agrobot/problema/costos.py
Objetivo:      Determinar el costo numerico de aplicar un movimiento desde un estado
               dado, distinguiendo el movimiento normal (costo 1) del movimiento en
               avioneta con combustible disponible (costo 1/2).
Responsabilidad:
    SI hace:
        - Calcular el costo de un paso: 1 si el robot se mueve caminando (e=falso, o
          e=verdadero con k=0, situacion que no deberia darse); 1/2 si el robot se
          mueve en la avioneta con combustible disponible (e=verdadero y k>0 antes del
          movimiento).
    NO hace:
        - No decide si el movimiento es aplicable (eso es de operadores.py).
        - No aplica efectos sobre el estado.
        - No acumula el costo de un camino completo: eso lo hace busqueda/nodo.py al
          sumar el costo de cada paso.
Importa de:
    - modelo.estado (Estado): para leer los componentes (e, k) del estado antes de
      moverse y decidir el costo del paso.
    - modelo.movimiento (Movimiento): para saber si el movimiento es el que sube a la
      avioneta (caso especial, ver PENDIENTE).
    - constantes: para referenciar los valores de capacidad/combustible si la
      representacion numerica de costos los necesita.
Lo importan:
    - problema/agrobot_problema.py (para anotar el costo de cada sucesor generado).
    - busqueda/no_informada/costo_uniforme.py y busqueda/informada/a_estrella.py (de
      forma indirecta, a traves del contrato del problema: estos algoritmos usan el
      costo que el problema reporta por cada paso, sin importar costos.py
      directamente, respetando que busqueda/ no importa de problema/).
Contrato previsto:
    - costo_de_movimiento(estado_antes_de_moverse, movimiento): retorna el costo
      numerico (1 o 1/2) del paso, segun si el robot viaja en avioneta con combustible
      en el momento de iniciar el movimiento.
Decisiones de equipo (antes PENDIENTE):
    - El movimiento que sube a la avioneta cuesta 1: al iniciarlo el robot aun va a pie
      (e=falso), y el costo depende solo de (e, k) ANTES de moverse.
    - El movimiento que gasta la ultima unidad de combustible cuesta 1/2: se inicia con
      e=verdadero y k=1, aunque termine en e=falso.
    - Los costos son float. 1 y 1/2 son exactos en binario, y toda suma de multiplos de
      1/2 tambien lo es, asi que comparar y acumular costos no pierde precision.
"""
from __future__ import annotations

COSTO_A_PIE = 1.0
COSTO_EN_AVIONETA = 0.5


def costo_de_movimiento(estado_antes_de_moverse, movimiento) -> float:
    """Costo del paso: 1/2 si va en avioneta con combustible, 1 en cualquier otro caso."""
    if estado_antes_de_moverse.en_avioneta and estado_antes_de_moverse.combustible > 0:
        return COSTO_EN_AVIONETA
    return COSTO_A_PIE

