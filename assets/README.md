# Assets de AgroBot

Esta carpeta contiene los recursos de arte (sprites) usados por la GUI para
dibujar la cuadricula y animar el camino solucion. No contiene codigo.

Solo `src/agrobot/gui/cargador_sprites.py` conoce la ruta de esta carpeta;
ningun otro archivo del proyecto debe leer `assets/` directamente.

## Estilo

Los sprites estan en **pixel art**: son las ilustraciones del Demo reducidas a 64 x 64 px,
con una paleta comun de 32 colores y un contorno oscuro de 1 px. Cada pixel del dibujo es
un pixel de la imagen, asi que la cuadricula completa de 10 x 10 casillas mide 640 x 640 px.
Si el juego los agranda, debe hacerlo sin suavizar: `pygame.transform.scale`, nunca
`smoothscale`, y con un factor entero (2x, 3x...) para que los pixeles no se deformen.

Los PNG se generan con `herramientas/pixelar_sprites.py` a partir de las ilustraciones
originales (`Demo/sprites/`). Para regenerarlos o cambiar el aspecto (colores, saturacion,
resolucion), ver la cabecera de ese script (necesita `pip install pillow numpy`).

## Sprites (`assets/sprites/`)

Formato: PNG de 64 x 64 px. `casilla_libre` y `obstaculo` cubren toda la casilla; los
demas tienen fondo transparente y se dibujan encima de `casilla_libre`.

| Archivo                          | Representa                                                         |
|----------------------------------|--------------------------------------------------------------------|
| `casilla_libre.png`              | Casilla libre (codigo 0): tierra.                                  |
| `obstaculo.png`                  | Obstaculo (codigo 1): piedras.                                     |
| `robot_n.png`                    | AgroBot caminando hacia arriba (visto de espaldas).                |
| `robot_e.png`                    | AgroBot caminando hacia la derecha.                                |
| `robot_s.png`                    | AgroBot caminando hacia abajo (visto de frente).                   |
| `robot_o.png`                    | AgroBot caminando hacia la izquierda.                              |
| `robot_en_avioneta_n.png`        | AgroBot montado en la avioneta, hacia arriba (e = verdadero).      |
| `robot_en_avioneta_e.png`        | Igual, hacia la derecha.                                           |
| `robot_en_avioneta_s.png`        | Igual, hacia abajo.                                                |
| `robot_en_avioneta_o.png`        | Igual, hacia la izquierda.                                         |
| `robot_<dir>_paso1.png`          | Pose de caminar 1 (rueda y brazo izquierdos arriba), para cada direccion. |
| `robot_<dir>_paso2.png`          | Pose de caminar 2 (rueda y brazo derechos arriba), para cada direccion.   |
| `avioneta.png`                   | Avioneta en su posicion original, sin el robot encima (codigo 5).  |
| `deposito.png`                   | Deposito de fertilizante (codigo 4).                               |
| `cultivo_seco.png`               | Cultivo seco pendiente de fertilizar (codigo 3, dentro de P).      |
| `cultivo_tratado.png`            | Cultivo ya fertilizado (salio de P durante la animacion).          |

El sufijo de direccion es `_n` (arriba), `_e` (derecha), `_s` (abajo) y `_o` (izquierda).
La direccion del robot es la del ultimo movimiento; antes del primer movimiento se usa
`robot_s`.

## Animacion de caminar

Cada direccion tiene 3 imagenes: la de reposo (`robot_n.png`) y dos poses (`robot_n_paso1.png`
y `robot_n_paso2.png`). Mientras el robot se mueve de una casilla a otra se alternan asi:

    reposo -> paso1 -> reposo -> paso2 -> (repite)

a unos 6 a 8 cuadros por segundo; al llegar a la casilla se vuelve a la imagen de reposo.
Las poses se generan con `herramientas/animar_robot.py` a partir de las 4 imagenes de reposo
(levanta una rueda, balancea los brazos y sube el cuerpo 1 px). La avioneta con el robot no
tiene poses: se mueve deslizandose de una casilla a otra.
