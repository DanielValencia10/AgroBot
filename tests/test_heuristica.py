"""
Archivo:       tests/test_heuristica.py
Objetivo:      Documentar que se va a verificar sobre busqueda/informada/heuristica.py,
               sin implementar aun los casos de prueba.
Responsabilidad:
    QUE VERIFICARA (cuando se implemente):
        - Que h(estado) retorne 0 (o un valor no negativo minimo) cuando el estado es
          meta (P vacio).
        - Que h(estado) nunca retorne un valor negativo.
        - Que, para una muestra de estados del mundo mundos/Prueba1.txt (robot en
          (4,0), cultivos en (4,3), (5,3) y (6,8)) con distintos conjuntos de
          pendientes P, h(estado) nunca sobreestime el costo real minimo verificable
          hasta la meta (verificacion de admisibilidad sobre casos concretos).
        - Que h(estado) sea consistente con la definicion documentada en
          heuristica.py (una vez esa definicion quede resuelta).
Importa de:
    - busqueda.informada.heuristica (al implementarse): para invocar
      calcular_heuristica sobre estados de prueba.
PENDIENTE:
    - Framework de pruebas a usar (por ejemplo pytest o unittest de la libreria
      estandar).
    - Depende directamente de que la definicion de la heuristica
      (busqueda/informada/heuristica.py) este resuelta por el equipo.
"""
