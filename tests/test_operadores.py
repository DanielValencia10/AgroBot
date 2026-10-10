"""
Archivo:       tests/test_operadores.py
Objetivo:      Documentar que se va a verificar sobre problema/operadores.py, sin
               implementar aun los casos de prueba.
Responsabilidad:
    QUE VERIFICARA (cuando se implemente), usando como referencia el mundo
    mundos/Prueba1.txt (robot en (4,0), deposito en (0,2), avioneta en (0,6),
    cultivos en (4,3), (5,3) y (6,8)):
        - Que un movimiento hacia una casilla fuera de la cuadricula no sea aplicable.
        - Que un movimiento hacia una casilla obstaculo no sea aplicable.
        - Que al entrar al deposito, el fertilizante vuelva a su capacidad maxima
          (constantes.CAPACIDAD_FERTILIZANTE).
        - Que al entrar a un cultivo seco pendiente con fertilizante disponible
          (phi > 0), el fertilizante disminuya en 1 y la casilla salga del conjunto de
          pendientes P.
        - Que al entrar a un cultivo seco pendiente SIN fertilizante (phi = 0), el
          cultivo NO se fertilice ni salga de P.
        - Que al entrar por primera vez a la posicion original de la avioneta, el
          robot quede montado (e = verdadero) sin consumir combustible en ese mismo
          movimiento.
        - Que, estando montado en la avioneta con combustible disponible, cada
          movimiento consuma una unidad de combustible (k <- k - 1).
        - Que al llegar el combustible a 0, la avioneta quede agotada (e <- falso).
Importa de:
    - problema.operadores (al implementarse): para invocar es_aplicable y aplicar
      sobre estados de prueba.
    - modelo.estado, modelo.movimiento, modelo.mundo: para construir los estados y
      movimientos de prueba.
PENDIENTE:
    - Framework de pruebas a usar (por ejemplo pytest o unittest de la libreria
      estandar).
"""
