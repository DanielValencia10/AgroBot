"""
Archivo:       herramientas/legado/pixelar_sprites.py
Objetivo:      Convertir las ilustraciones originales del Demo (Demo/sprites/*.png) en los
               sprites en pixel art de AgroBot (assets/sprites/*.png).
Uso:           python herramientas/legado/pixelar_sprites.py --origen RUTA/Demo/sprites
               (desde la raiz del repositorio; el destino por defecto es assets/sprites)
Requiere:      Pillow y numpy (pip install pillow numpy). Solo hacen falta para regenerar
               los PNG, no para ejecutar el programa.
Que hace:
    1. Recorta cada ilustracion a su silueta y la reduce a 64 x 64 px promediando por
       area (todas las vistas de un mismo personaje comparten escala y no "saltan" de
       tamano al girar).
    2. Realza un poco el color y el contraste.
    3. Reduce todos los sprites juntos a una paleta comun de pocos colores, para que se
       vean como una sola familia.
    4. Dibuja un contorno oscuro de 1 px alrededor de cada silueta.
    El resultado son PNG de 64 x 64 px: cada pixel del dibujo es un pixel de la imagen,
    asi que si el juego los agranda debe hacerlo sin suavizar (pygame.transform.scale).
Para cambiar el aspecto:  ajusta LADO, COLORES, SATURACION o CONTRASTE, o cambia las
               ilustraciones de origen, y vuelve a ejecutar.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

LADO = 64
COLORES = 32
SATURACION = 1.25
CONTRASTE = 1.15
CONTORNO = (40, 24, 10)
UMBRAL_ALFA = 40            # pixeles casi transparentes no cuentan para la silueta

# destino -> archivo de origen (sin .png)
FAMILIAS = {
    # personaje: todas las vistas comparten escala y se apoyan en el mismo suelo
    "robot": {
        "robot_n": "robot_n", "robot_e": "robot_e", "robot_s": "robot_s", "robot_o": "robot_o",
    },
    # avioneta sola y con el robot montado, vistas desde arriba
    "avioneta": {
        "avioneta": "avioneta_e",
        "robot_en_avioneta_n": "avioneta_robot_n", "robot_en_avioneta_e": "avioneta_robot_e",
        "robot_en_avioneta_s": "avioneta_robot_s", "robot_en_avioneta_o": "avioneta_robot_o",
    },
    "deposito": {"deposito": "deposito_1"},
    # las dos plantas comparten escala para que el cambio seco -> tratado no "salte"
    "cultivos": {"cultivo_seco": "planta_marchita", "cultivo_tratado": "planta_sana"},
}
# Casillas que cubren toda la celda (se escalan a 64 x 64 sin recortar la silueta)
BALDOSAS = {"casilla_libre": "casilla_libre", "obstaculo": "obstaculo"}
MARGEN_BALDOSA = 0.03       # se descarta este borde de la ilustracion (marco de la casilla)
APOYO_ABAJO = {"robot"}     # familias cuyo dibujo se apoya abajo de la casilla


def _silueta(imagen):
    return imagen.getchannel("A").point(lambda a: 255 if a > UMBRAL_ALFA else 0).getbbox()


def _reducir(imagen, ancho, alto):
    """Reduce promediando por area con el alfa premultiplicado (sin halos en los bordes)."""
    datos = np.asarray(imagen).astype(np.float32)
    alfa = datos[..., 3:4] / 255.0
    premultiplicado = np.concatenate([datos[..., :3] * alfa, datos[..., 3:4]], axis=2)
    canales = [np.asarray(Image.fromarray(premultiplicado[..., i], mode="F")
                          .resize((ancho, alto), Image.BOX)) for i in range(4)]
    reducido = np.stack(canales, axis=2)
    a = reducido[..., 3] / 255.0
    rgb = np.clip(reducido[..., :3] / np.maximum(a[..., None], 1e-3), 0, 255)
    salida = np.zeros((alto, ancho, 4), dtype=np.uint8)
    salida[..., :3] = rgb.astype(np.uint8)
    salida[..., 3] = np.where(a >= 0.5, 255, 0)
    return Image.fromarray(salida, "RGBA")


def _realzar(imagen):
    alfa = imagen.getchannel("A")
    rgb = ImageEnhance.Contrast(ImageEnhance.Color(imagen.convert("RGB")).enhance(SATURACION)
                                ).enhance(CONTRASTE)
    rgb.putalpha(alfa)
    return rgb


def _contorno(imagen):
    visible = np.asarray(imagen.getchannel("A")) > 0
    relleno = np.pad(visible, 1)
    vecino = (relleno[:-2, 1:-1] | relleno[2:, 1:-1] | relleno[1:-1, :-2] | relleno[1:-1, 2:])
    datos = np.asarray(imagen).copy()
    datos[vecino & ~visible] = CONTORNO + (255,)
    return Image.fromarray(datos, "RGBA")


def _paleta_comun(imagenes):
    """Reduce todas las imagenes a la misma paleta de COLORES colores."""
    pixeles = np.concatenate([np.asarray(i).reshape(-1, 4)[np.asarray(i).reshape(-1, 4)[:, 3] > 0][:, :3]
                              for i in imagenes.values()]).astype(np.uint8)
    lado = int(np.ceil(np.sqrt(len(pixeles))))
    matriz = np.zeros((lado * lado, 3), dtype=np.uint8)
    matriz[:len(pixeles)] = pixeles
    muestra = Image.fromarray(matriz.reshape(lado, lado, 3), "RGB")
    paleta = muestra.quantize(colors=COLORES, method=Image.MEDIANCUT, dither=Image.NONE)
    resultado = {}
    for nombre, imagen in imagenes.items():
        reducida = imagen.convert("RGB").quantize(palette=paleta, dither=Image.NONE).convert("RGB")
        reducida.putalpha(imagen.getchannel("A"))
        resultado[nombre] = reducida
    return resultado


def _familia(origen, familia, archivos):
    """Pone cada vista de la familia en un lienzo de LADO x LADO con una escala comun."""
    recortes = {}
    for destino, archivo in archivos.items():
        imagen = Image.open(origen / (archivo + ".png")).convert("RGBA")
        recortes[destino] = imagen.crop(_silueta(imagen))
    maximo = LADO - 2
    escala = min(min(maximo / r.width, maximo / r.height) for r in recortes.values())
    lienzos = {}
    for destino, recorte in recortes.items():
        ancho, alto = max(1, round(recorte.width * escala)), max(1, round(recorte.height * escala))
        pequeno = _reducir(recorte, ancho, alto)
        lienzo = Image.new("RGBA", (LADO, LADO), (0, 0, 0, 0))
        x = (LADO - ancho) // 2
        y = LADO - alto - 1 if familia in APOYO_ABAJO else (LADO - alto) // 2
        lienzo.paste(pequeno, (x, y))
        lienzos[destino] = _realzar(lienzo)
    return lienzos


def _baldosa(origen, archivo):
    imagen = Image.open(origen / (archivo + ".png")).convert("RGBA")
    mx, my = int(imagen.width * MARGEN_BALDOSA), int(imagen.height * MARGEN_BALDOSA)
    imagen = imagen.crop((mx, my, imagen.width - mx, imagen.height - my))
    imagen.putalpha(255)
    return _realzar(_reducir(imagen, LADO, LADO))


def pixelar(origen, destino):
    origen, destino = Path(origen), Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    imagenes = {}
    for familia, archivos in FAMILIAS.items():
        imagenes.update(_familia(origen, familia, archivos))
    baldosas = {nombre: _baldosa(origen, archivo) for nombre, archivo in BALDOSAS.items()}
    todas = _paleta_comun({**imagenes, **baldosas})
    for nombre, imagen in todas.items():
        if nombre not in BALDOSAS:
            imagen = _contorno(imagen)
        imagen.save(destino / (nombre + ".png"))
    return sorted(todas)


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[2]
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    analizador.add_argument("--origen", required=True, help="carpeta con las ilustraciones (Demo/sprites)")
    analizador.add_argument("--destino", default=str(raiz / "assets" / "sprites"))
    argumentos = analizador.parse_args()
    for nombre in pixelar(argumentos.origen, argumentos.destino):
        print(nombre + ".png")
