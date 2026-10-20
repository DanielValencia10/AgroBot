"""
Archivo:       src/agrobot/busqueda/informada/heuristica.py
Objetivo:      Definir la funcion heuristica h(estado) usada por los algoritmos de
               busqueda informada (Avara y A*) para estimar el costo que falta hasta
               un estado meta.
Responsabilidad:
    SI hace:
        - Ofrecer una "fabrica": crear_heuristica(deposito) recibe una sola vez la
          posicion del deposito (que vive en el Mundo, no en el Estado) y devuelve la
          funcion h(estado). Asi esta funcion no necesita conocer el Mundo.
        - Calcular, para un estado dado (valor que expone fila, columna, fertilizante
          y pendientes), una estimacion del costo restante hasta un estado meta
          (P vacio): h = 0,5 x movimientos minimos, donde
              movimientos minimos = D + (n - 1)
              n = cultivos pendientes
              D = distancia Manhattan hasta el cultivo pendiente mas cercano si el
                  robot tiene fertilizante; si NO tiene, distancia Manhattan al
                  deposito mas la del deposito al cultivo pendiente mas cercano.
          En un estado meta (n = 0) devuelve 0.
        - Ser ADMISIBLE: nunca sobreestima el costo real restante (justificacion
          abajo, para el informe del curso).
    NO hace:
        - No importa Mundo ni Estado: opera sobre los campos del estado que recibe,
          respetando que busqueda/ no importa de modelo/ ni de problema/.
        - No decide el orden de expansion: solo provee el valor h(estado); el orden lo
          decide cada algoritmo (avara.py usa solo h, a_estrella.py usara f = g + h).
Importa de:
    - (nada del proyecto): solo usa los campos del estado y el deposito recibido.
Lo importan:
    - gui/panel_control.py: crea la heuristica con el deposito del mundo y se la pasa
      a buscar_avara (y, cuando exista, a A*). Los algoritmos de busqueda reciben la
      funcion h como parametro y no importan este modulo.
Contrato:
    - distancia_manhattan(a, b): pasos minimos entre dos casillas (fila, columna), sin
      contar obstaculos.
    - crear_heuristica(deposito): retorna calcular_heuristica(estado), que retorna un
      numero >= 0 (float) y 0 si el estado es meta.
    - COSTO_MINIMO_POR_PASO = 0,5: costo del paso mas barato (caminar en avioneta).
Justificacion de admisibilidad (para el informe):
    1. Cada paso cuesta al menos 0,5, asi que el costo real restante es >= 0,5 x (numero
       de movimientos que falten).
    2. Los movimientos que faltan son >= D + (n - 1):
        - Cada movimiento cambia fila o columna en 1, y los obstaculos solo pueden
          alargar el camino; por eso Manhattan nunca supera los pasos reales.
        - Con fertilizante, hasta tratar el primer cultivo hacen falta >= la distancia
          Manhattan a algun cultivo pendiente, que es >= la del mas cercano.
        - Sin fertilizante, el unico lugar donde se consigue es el deposito, asi que
          antes de tratar el primer cultivo hay que ir al deposito y de ahi a un
          cultivo: >= (robot -> deposito) + (deposito -> cultivo mas cercano).
        - Los otros n - 1 cultivos estan en casillas distintas, cada una exige al
          menos un movimiento mas.
    3. Por tanto h <= costo real restante en todo estado, y h = 0 en la meta.
Limitaciones (no afectan la admisibilidad, solo la precision):
    - Manhattan ignora las paredes (el deposito y la avioneta de Prueba1 estan en
      callejones).
    - Usa 0,5 por paso aunque el robot vaya a pie o la avioneta ya este agotada.
    - No cuenta las visitas extra al deposito cuando el fertilizante no alcanza para
      todos los cultivos (capacidad 2).
PENDIENTE:
    - Pruebas en tests/test_heuristica.py (hoy solo documenta lo que verificara).
    - Posibles mejoras si se quiere una h mas informada, siempre admisible.
"""

from __future__ import annotations

COSTO_MINIMO_POR_PASO = 0.5


def distancia_manhattan(a, b):
    """Pasos minimos entre dos casillas (fila, columna) sin contar obstaculos."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def crear_heuristica(deposito):
    def calcular_heuristica(estado):
        pendientes = estado.pendientes
        if not pendientes:
            return 0.0

        posicion = (estado.fila, estado.columna)
        if estado.fertilizante > 0:
            hasta_primer_cultivo = min(
                distancia_manhattan(posicion, cultivo) for cultivo in pendientes
            )
        else:
            al_deposito = distancia_manhattan(posicion, deposito)
            del_deposito = min(
                distancia_manhattan(deposito, cultivo) for cultivo in pendientes
            )
            hasta_primer_cultivo = al_deposito + del_deposito        
            
        movimientos_minimos = hasta_primer_cultivo + (len(pendientes) - 1)
        return COSTO_MINIMO_POR_PASO * movimientos_minimos

    return calcular_heuristica

