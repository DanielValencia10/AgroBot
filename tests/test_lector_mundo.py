"""
Archivo:       tests/test_lector_mundo.py
Objetivo:      Documentar que se va a verificar sobre archivos/lector_mundo.py, sin
               implementar aun los casos de prueba.
Responsabilidad:
    QUE VERIFICARA (cuando se implemente):
        - Que un archivo de mundo valido de 10x10 (por ejemplo mundos/Prueba1.txt) se
          lee correctamente y produce un Mundo con: obstaculos, deposito en (0,2),
          avioneta en (0,6), robot en (4,0) y cultivos secos en (4,3), (5,3) y (6,8)
          (fila 0 arriba, coordenadas (fila, columna) desde 0).
        - Que se rechacen archivos que no tengan exactamente 10 filas o 10 columnas.
        - Que se rechacen archivos con codigos de celda fuera del rango valido (0 a 5).
        - Que se rechacen archivos sin exactamente un 2 (AgroBot).
        - Que se rechacen archivos sin exactamente un 4 (deposito).
        - Que se rechacen archivos sin exactamente un 5 (avioneta).
        - Que se rechacen archivos sin al menos un 3 (cultivo seco).
Importa de:
    - archivos.lector_mundo (al implementarse): para invocar la funcion de lectura
      sobre archivos de prueba validos e invalidos.
    - mundos/Prueba1.txt: como archivo de referencia para el caso valido.
PENDIENTE:
    - Framework de pruebas a usar (por ejemplo pytest o unittest de la libreria
      estandar).
"""
