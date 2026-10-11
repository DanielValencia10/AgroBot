# Assets de AgroBot

Esta carpeta contiene los recursos de arte (sprites) usados por la GUI para
dibujar la cuadricula y animar el camino solucion. Solo contiene imagenes y dos scripts de ejemplo.

Solo `src/agrobot/gui/cargador_sprites.py` conoce la ruta de esta carpeta;
ningun otro archivo del proyecto debe leer `assets/` directamente.

## Estilo

Los sprites estan en **pixel art**: son las ilustraciones del Demo reducidas a 64 x 64 px,
con una paleta comun de 32 colores y un contorno oscuro de 1 px. Cada pixel del dibujo es
un pixel de la imagen, asi que la cuadricula completa de 10 x 10 casillas mide 640 x 640 px.
Si el juego los agranda, debe hacerlo sin suavizar: `pygame.transform.scale`, nunca
`smoothscale`, y con un factor entero (2x, 3x...) para que los pixeles no se deformen.

Los sprites actuales son de elaboracion propia del equipo. `herramientas/legado/` guarda
`pixelar_sprites.py` y `animar_robot.py`, que generaron la version anterior (PNG planos) y
no producen la estructura actual de subcarpetas; se conservan por si se reutilizan.

## Sprites (`assets/sprites/`)

Formato: PNG de 64 x 64 px, organizados en una carpeta por objeto. `casilla_libre` y
`obstaculo` cubren toda la casilla; los demas tienen fondo transparente y se dibujan encima
de `casilla_libre`. El sufijo de direccion es `n` (arriba), `e` (derecha), `s` (abajo) y
`o` (izquierda); las diagonales son `ne`, `no`, `se` y `so`.

| Carpeta / archivo                         | Representa                                                          |
|-------------------------------------------|---------------------------------------------------------------------|
| `mundo/casilla_libre.png`                 | Casilla libre (codigo 0): tierra.                                   |
| `mundo/obstaculo.png`                     | Obstaculo (codigo 1): piedras.                                      |
| `robot/robot_<n,e,s,o>_<0,1,2>.png`       | AgroBot caminando. Cuadro 0 = reposo, 1 = paso adelante, 2 = paso atras. |
| `robot/robot_trans_<ne,no,se,so>.png`     | AgroBot en las diagonales, solo se ve mientras gira.                |
| `avioneta/avioneta_<8 dir>_<0,1,2>.png`   | AgroBot montado en la avioneta (e = verdadero); los 3 cuadros son la helice girando. |
| `avioneta/avioneta base.png`              | Avioneta vacia en su posicion original (codigo 5).                  |
| `deposito/deposito.png`                   | Deposito de fertilizante (codigo 4).                                |
| `cultivo/planta_trans_<0..8>.png`         | Cultivo: 0 = seco pendiente de fertilizar (codigo 3), 8 = tratado; 1 a 7 son la transicion. |

La direccion del robot es la del ultimo movimiento; antes del primer movimiento se usa
`s`.

## Animaciones

Los tiempos y el orden de los cuadros viven en `src/agrobot/gui/animacion.py`:

- Caminata del robot: cuadros `0 -> 1 -> 0 -> 2` (170 ms cada uno), solo mientras se mueve y no gira.
- Giro: pasa por cada direccion intermedia del anillo `n, ne, e, se, s, so, o, no` por el
  lado mas corto (70 ms por cuadro). Para el robot las diagonales usan `robot_trans_*`.
- Helice de la avioneta: cuadros `0 -> 1 -> 2 -> 1` (55 ms), siempre girando.
- Planta: los 9 cuadros en orden al fertilizarla (130 ms cada uno).

`ejemplo_pygame.py` y `ejemplo_planta_pygame.py` (en `assets/sprites/`) muestran estas
animaciones por separado; son la referencia visual. Ejecutarlos desde esa carpeta.
