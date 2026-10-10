# Assets de AgroBot

Esta carpeta contiene los recursos de arte (sprites) usados por la GUI para
dibujar la cuadricula y animar el camino solucion. No contiene codigo.

Solo `src/agrobot/gui/cargador_sprites.py` conoce la ruta de esta carpeta;
ningun otro archivo del proyecto debe leer `assets/` directamente.

## Sprites esperados (`assets/sprites/`)

Formato: PNG con fondo transparente, todos del mismo tamano cuadrado
(se sugiere 64x64 px, lo que da una cuadricula completa de 640x640 px).

| Archivo                     | Representa                                              |
|------------------------------|----------------------------------------------------------|
| `casilla_libre.png`          | Casilla libre (codigo 0).                                |
| `obstaculo.png`               | Obstaculo (codigo 1).                                    |
| `robot.png`                   | AgroBot caminando (codigo 2 / robot fuera de la avioneta).|
| `robot_en_avioneta.png`       | AgroBot mientras va montado en la avioneta (e = verdadero).|
| `avioneta.png`                 | Posicion original de la avioneta sin el robot encima (codigo 5).|
| `deposito.png`                 | Deposito de fertilizante (codigo 4).                     |
| `cultivo_seco.png`             | Cultivo seco pendiente de fertilizar (codigo 3, dentro de P).|
| `cultivo_tratado.png`          | Cultivo ya fertilizado (salio de P durante la animacion).|

Mientras no haya arte definitivo, se puede usar un cuadro de color solido
como marcador temporal para cada sprite y reemplazarlo despues sin tocar
ningun archivo de codigo (solo los archivos en `assets/sprites/`).
