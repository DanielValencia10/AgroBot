"""
Archivo:       herramientas/animar_robot.py
Objetivo:      Generar las poses de caminar del robot (robot_<dir>_paso1.png y
               robot_<dir>_paso2.png) a partir de sus 4 sprites en reposo.
Uso:           python herramientas/animar_robot.py        (desde la raiz del repositorio)
Requiere:      Pillow y numpy (pip install pillow numpy). Solo hacen falta para regenerar
               los PNG, no para ejecutar el programa.
Que hace:      Para cada direccion (n, e, s, o) parte de assets/sprites/robot_<dir>.png y
               crea dos poses: en una se levanta la rueda izquierda y se balancea el
               brazo; en la otra la rueda derecha y el brazo contrario; en ambas el
               cuerpo sube un pixel. Las zonas de brazos y ruedas (VISTAS) estan medidas
               sobre los sprites de 64 x 64 px: si se cambian los sprites en reposo hay
               que revisar esas coordenadas.
Animacion:     reposo -> paso1 -> reposo -> paso2 -> (repite), unos 6 a 8 cuadros por
               segundo mientras el robot se mueve de una casilla a otra.
"""
import argparse
import numpy as np
from PIL import Image
from pathlib import Path

LADO = 64
RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ / "assets" / "sprites"

def cargar(n): return np.asarray(Image.open(ORIGEN / (n + ".png")).convert("RGBA")).copy()

def desplazar_vertical(a, caja, dy, estirar=True):
    """Mueve el contenido de la caja (x0,y0,x1,y1 inclusive) dy filas; lo que queda vacio es transparente."""
    x0, y0, x1, y1 = caja
    zona = a[y0:y1 + 1, x0:x1 + 1].copy()
    a[y0:y1 + 1, x0:x1 + 1] = 0
    ny0, ny1 = y0 + dy, y1 + dy
    src0 = max(0, -dy); dst0 = ny0 + src0
    h = zona.shape[0] - abs(dy)
    destino = a[dst0:dst0 + h, x0:x1 + 1]
    trozo = zona[src0:src0 + h]
    mascara = trozo[..., 3] > 0
    destino[mascara] = trozo[mascara]
    if dy < 0 and estirar and y1 + 1 < LADO:
        # al subir el miembro queda a la vista lo que tenia detras (la parte alta de la rueda)
        debajo = a[y1 + 1, x0:x1 + 1].copy()
        for k in range(-dy):
            fila = a[y1 - k, x0:x1 + 1]
            vacia = fila[..., 3] == 0
            fila[vacia] = debajo[vacia]
    if dy > 0 and estirar:
        # el miembro se estira hacia el hombro para no quedar despegado del cuerpo
        for k in range(dy):
            fila = a[y0 + k, x0:x1 + 1]
            vacia = fila[..., 3] == 0
            fila[vacia] = zona[0][vacia]

def rodar_interior(a, caja, filas):
    """Desplaza con vuelta (rueda) el interior de la rueda 'filas' hacia abajo."""
    x0, y0, x1, y1 = caja
    a[y0:y1 + 1, x0:x1 + 1] = np.roll(a[y0:y1 + 1, x0:x1 + 1], filas, axis=0)

def subir_cuerpo(a, y_corte, dy=1):
    """Sube dy pixeles todo lo que esta por encima de y_corte (el cuerpo); las ruedas se quedan."""
    parte = a[:y_corte + 1].copy()
    a[:y_corte + 1] = 0
    a[:y_corte + 1 - dy] = parte[dy:]
    a[y_corte + 1 - dy:y_corte + 1] = parte[-dy:] if dy else 0   # estira la ultima fila
    # la fila estirada no debe tapar la rueda: se queda solo donde habia cuerpo
    return a

def girar_hub(a, centro, medio, cuartos):
    cx, cy = centro
    zona = a[cy - medio:cy + medio + 1, cx - medio:cx + medio + 1].copy()
    a[cy - medio:cy + medio + 1, cx - medio:cx + medio + 1] = np.rot90(zona, -cuartos)

def desplazar_filas(a, x0, x1, filas, dx):
    for y in filas:
        fila = a[y, x0:x1 + 1].copy()
        nueva = np.roll(fila, dx, axis=0)
        if dx > 0: nueva[:dx] = fila[0]
        if dx < 0: nueva[dx:] = fila[-1]
        a[y, x0:x1 + 1] = nueva

# --- configuracion por vista (coordenadas de los dibujos de 64 x 64)
# ruedas: (x0, x1, y0) de cada rueda; brazos: caja (x0, y0, x1, y1)
VISTAS = {
    "robot_n": dict(ruedas=[(8, 19, 52), (43, 54, 52)], brazo_i=(5, 36, 15, 47), brazo_d=(47, 36, 58, 47)),
    "robot_s": dict(ruedas=[(6, 17, 52), (42, 52, 52)], brazo_i=(4, 36, 15, 47), brazo_d=(47, 41, 58, 47)),
    "robot_e": dict(ruedas=[(18, 31, 53), (37, 50, 53)], brazo=(33, 47, 42, 52)),
    "robot_o": dict(ruedas=[(11, 24, 53), (31, 44, 53)], brazo=(21, 47, 30, 52)),
}

# (rueda izquierda sube, rueda derecha sube, brazo izquierdo, brazo derecho, cuerpo sube)
POSES = [
    (2, 0, -2, +2, 1),    # paso1
    (0, 2, +2, -2, 1),    # paso2
]

def levantar_rueda(a, rueda, dy):
    x0, x1, y0 = rueda
    desplazar_vertical(a, (x0, y0, x1, LADO - 1), -dy)

def subir_cuerpo(a, y_corte, dy=1):
    """Sube dy filas todo lo que esta por encima de y_corte; la fila que queda libre toma la de abajo."""
    original = a.copy()
    a[:y_corte + 1 - dy] = original[dy:y_corte + 1]
    a[y_corte + 1 - dy:y_corte + 1] = original[y_corte + 1]

def frame(nombre, pose):
    cfg = VISTAS[nombre]; a = cargar(nombre)
    ri, rd, bi, bd, sube = pose
    for rueda, dy in zip(cfg["ruedas"], (ri, rd)):
        if dy: levantar_rueda(a, rueda, dy)
    if "brazo_i" in cfg:
        if bi: desplazar_vertical(a, cfg["brazo_i"], bi)
        if bd: desplazar_vertical(a, cfg["brazo_d"], bd)
    else:
        x0, y0, x1, y1 = cfg["brazo"]
        desplazar_filas(a, x0, x1, range(y0, y1 + 1), {-2: -1, 0: 0, 2: 1}[bi])
    if sube: subir_cuerpo(a, 49 if "brazo_i" in cfg else 50, 1)
    return a

def generar(origen=ORIGEN, destino=None):
    global ORIGEN
    ORIGEN = Path(origen)
    destino = Path(destino) if destino else ORIGEN
    destino.mkdir(parents=True, exist_ok=True)
    nombres = []
    for nombre in ("robot_n", "robot_e", "robot_s", "robot_o"):
        for i, pose in enumerate(POSES, start=1):
            n = f"{nombre}_paso{i}"
            Image.fromarray(frame(nombre, pose), "RGBA").save(destino / (n + ".png"))
            nombres.append(n)
    return nombres


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Genera las poses de caminar del robot")
    analizador.add_argument("--origen", default=str(ORIGEN), help="carpeta con robot_<dir>.png")
    analizador.add_argument("--destino", default=None, help="carpeta de salida (por defecto, la misma)")
    argumentos = analizador.parse_args()
    for nombre in generar(argumentos.origen, argumentos.destino):
        print(nombre + ".png")
