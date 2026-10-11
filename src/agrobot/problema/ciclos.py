"""
Archivo:       src/agrobot/problema/ciclos.py
Objetivo:      Evitar que, dentro de una misma rama de busqueda, se repita un estado ya
               visitado previamente en esa rama, salvo en las excepciones explicitas
               permitidas por el enunciado del problema.
Responsabilidad:
    SI hace:
        - Determinar si un estado candidato repetiria un estado ya presente en el
          camino actual desde la raiz (rama), para que ese sucesor se descarte.
        - Documentar y aplicar las excepciones en las que SI se permite volver a un
          estado ya visitado en la rama:
            - Volver a la casilla donde esta la avioneta (para subirse a ella).
            - Volver a un cultivo seco pendiente teniendo fertilizante disponible
              (phi > 0) para fertilizarlo.
            - Volver al deposito (para recargar fertilizante).
    NO hace:
        - No decide que algoritmo usar ni como recorrer el arbol de busqueda: solo
          ofrece el criterio de "este sucesor repite estado y no cae en una excepcion".
        - No calcula costos ni aplica efectos de movimiento.
Importa de:
    - modelo.estado (Estado): para comparar estados (posicion, fertilizante,
      combustible, pendientes) segun el criterio que se defina.
    - modelo.mundo (Mundo): para identificar si una casilla es el deposito o la
      posicion de la avioneta (necesario para reconocer las excepciones).
    - constantes: en caso de necesitar referenciar codigos o capacidades al evaluar
      las excepciones.
Lo importan:
    - problema/agrobot_problema.py (para filtrar sucesores que violan la restriccion
      de ciclos antes de devolverlos a los algoritmos de busqueda).
Contrato previsto:
    - es_repetido_en_rama(estado_candidato, camino_de_estados_en_la_rama, mundo):
      retorna si el estado candidato debe descartarse por repetir un estado previo en
      la rama, considerando las excepciones (avioneta, cultivo seco con fertilizante,
      deposito).
Decision de equipo (antes PENDIENTE):
    - "Es el mismo estado" significa igualdad de la tupla completa (f, c, phi, e, k, P),
      igual que la clave de visitados de la Demo.
    - Con esa definicion las tres excepciones se cumplen solas: volver a la avioneta, a
      un cultivo seco con fertilizante o al deposito CAMBIA e/k, P o phi, asi que el
      estado resultante es distinto y no cuenta como repetido. Solo se descarta un paso
      que deja TODO igual que un estado anterior de la rama.
PENDIENTE:
    - El parametro `mundo` queda en el contrato por si el equipo cambia la comparacion
      (por ejemplo, solo posicion con excepciones explicitas); hoy no se usa.
"""
from __future__ import annotations


def es_repetido_en_rama(estado_candidato, camino_de_estados_en_la_rama, mundo=None) -> bool:
    """True si el candidato repite un estado de la rama (cualquier contenedor con `in`)."""
    return estado_candidato in camino_de_estados_en_la_rama

