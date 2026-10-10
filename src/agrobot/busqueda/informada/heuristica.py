"""
Archivo:       src/agrobot/busqueda/informada/heuristica.py
Objetivo:      Definir la funcion heuristica h(estado) usada por los algoritmos de
               busqueda informada (Avara y A*) para estimar que tan cerca esta un
               estado de ser meta.
Responsabilidad:
    SI hace:
        - Calcular, para un estado dado (tratado como valor opaco que expone al menos
          posicion y cultivos secos pendientes, segun el contrato que el objeto
          problema garantiza), un valor numerico que estima el costo restante hasta
          alcanzar un estado meta (P vacio).
        - Ser ADMISIBLE: nunca debe sobreestimar el costo real restante hasta la meta,
          requisito que el informe del curso exige explicar y justificar.
    NO hace:
        - No conoce Mundo ni Estado directamente como clases concretas: opera sobre el
          valor de estado que le entrega el algoritmo de busqueda, respetando que
          busqueda/ no importa de modelo/ ni de problema/.
        - No decide el orden de expansion: solo provee el valor h(estado); el orden lo
          decide cada algoritmo (avara.py usa solo h, a_estrella.py usa f = g + h).
Importa de:
    - (ninguno del proyecto fuera de busqueda/): la heuristica opera sobre los campos
      del estado que recibe como parametro, sin importar las clases concretas de
      modelo/.
Lo importan:
    - busqueda/informada/avara.py (usa h(estado) como unico criterio de orden).
    - busqueda/informada/a_estrella.py (usa f(estado) = g(estado) + h(estado)).
Contrato previsto:
    - calcular_heuristica(estado): recibe un estado y retorna un numero no negativo
      que estima el costo restante hasta la meta, cumpliendo admisibilidad.
PENDIENTE:
    - Definicion exacta de la heuristica (por ejemplo, alguna combinacion de distancia
      al cultivo seco pendiente mas cercano, numero de cultivos pendientes, distancia
      al deposito o a la avioneta, considerando el costo reducido de los movimientos en
      avioneta). Debe quedar documentada aqui junto con su demostracion/justificacion
      de admisibilidad para el informe.
"""
