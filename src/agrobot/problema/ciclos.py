"""
Archivo:       src/agrobot/problema/ciclos.py
Objetivo:      Evitar que, dentro de una misma rama de busqueda, se repita un estado ya
               visitado previamente en esa rama, salvo en las excepciones explicitas
               permitidas por el enunciado del problema.
Responsabilidad:
    SI hace:
        - Determinar si un estado candidato repetiria un estado ya presente en el
          camino actual desde la raiz (rama), para que ese sucesor se descarte.
        - Garantizar las excepciones en las que SI se permite volver a una casilla ya
          visitada en la rama (no con codigo aparte: salen solas de la definicion de
          "mismo estado", ver mas abajo):
            - Volver a la casilla donde esta la avioneta (para subirse a ella).
            - Volver a un cultivo seco pendiente teniendo fertilizante disponible
              (phi > 0) para fertilizarlo.
            - Volver al deposito (para recargar fertilizante).
    NO hace:
        - No decide que algoritmo usar ni como recorrer el arbol de busqueda: solo
          ofrece el criterio de "este sucesor repite un estado de la rama".
        - No calcula costos ni aplica efectos de movimiento.
Importa de:    (nada del proyecto: recibe los estados como parametros).
Lo importan:
    - problema/agrobot_problema.py (para filtrar sucesores que violan la restriccion
      de ciclos antes de devolverlos a los algoritmos de busqueda).
Contrato previsto:
    - es_repetido_en_rama(estado_candidato, camino_de_estados_en_la_rama, mundo):
      retorna si el estado candidato debe descartarse por repetir un estado previo en
      la rama (cualquier contenedor de Estado que acepte `in`: lista, tupla o conjunto).
Definicion de ciclo (diapositivas del profesor, Tema 4):
    - "Evitar ciclos" = evitar que sobre una misma rama se alcance un estado previo.
Decision de equipo (2026-10-19): el combustible k SE OMITE al comparar estados.
    - Dos estados se consideran el mismo si coinciden en (f, c, phi, e, P): posicion,
      fertilizante, si va en avioneta y cultivos pendientes. El combustible k no se mira.
    - Por que: mientras el robot va en la avioneta cada paso baja k en 1; si k se
      comparara, volver a una casilla ya pisada en avioneta siempre parecería un estado
      nuevo y el robot podria ir y venir hasta gastar los 30 movimientos.
    - Las tres excepciones se cumplen solas: volver a la avioneta, a un cultivo seco con
      fertilizante o al deposito CAMBIA e, P o phi, asi que no cuenta como repetido.
    - Consecuencias a tener presentes:
        * Con la misma posicion, phi y P, "avioneta sin usar" (e=falso, k=30) y "avioneta
          agotada" (e=falso, k=0) cuentan como el mismo estado. No se pierde ninguna
          solucion (el estado con avioneta disponible nunca tiene menos opciones), pero
          no es la tupla completa.
        * Los nodos expandidos y los caminos de Profundidad dependen de este criterio y
          difieren de comparar la tupla completa (f, c, phi, e, k, P).
    - Amplitud y Costo uniforme no usan este filtro (llaman a sucesores sin rama).
PENDIENTE:
    - El parametro `mundo` queda en el contrato por si el equipo cambia la comparacion;
      hoy no se usa.
"""
from __future__ import annotations


def _clave_ciclo(estado):
    """Clave para identificar ciclos en la rama.

    No incluye `combustible` (k), porque mientras el robot va en la avioneta cada
    paso decrementa k en 1. Si se incluyera k, cualquier casilla ya visitada pareceria
    un estado nuevo por tener menos combustible, haciendo que el robot oscile
    indefinidamente entre casillas hasta quemar los 30 movimientos.

    Las excepciones del problema se cumplen naturalmente:
    - Entrar a la avioneta cambia `en_avioneta` (False -> True), permitiendo salir
      del callejon hacia la casilla previa. Una vez afuera con en_avioneta=True, volver
      a entrar a la avioneta si se detecta como ciclo.
    - Entrar al deposito cambia `fertilizante` (phi -> 2).
    - Entrar a un cultivo seco con fertilizante cambia `pendientes` y `fertilizante`.
    """
    return (
        estado.fila,
        estado.columna,
        estado.fertilizante,
        estado.en_avioneta,
        estado.pendientes,
    )


def es_repetido_en_rama(estado_candidato, camino_de_estados_en_la_rama, mundo=None) -> bool:
    """True si el candidato repite un estado de la rama (comparando sin combustible)."""
    clave_candidato = _clave_ciclo(estado_candidato)
    for estado_previo in camino_de_estados_en_la_rama:
        clave_previo = _clave_ciclo(estado_previo) if hasattr(estado_previo, "fila") else estado_previo
        if clave_candidato == clave_previo:
            return True
    return False

