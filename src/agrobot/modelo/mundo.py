"""
Archivo:       src/agrobot/modelo/mundo.py
Objetivo:      Representar la parte CONSTANTE del entorno sobre la que se mueve el AgroBot:
               todo lo que no cambia durante la busqueda (obstaculos, ubicacion del
               deposito y de la avioneta, posicion inicial del robot y cultivos secos
               iniciales).
Responsabilidad:
    SI hace:
        - Almacenar el conjunto de casillas obstaculo.
        - Almacenar la posicion del unico deposito (no se agota, es un solo punto fijo).
        - Almacenar la posicion inicial de la unica avioneta.
        - Almacenar la posicion inicial del robot.
        - Almacenar el conjunto de cultivos secos iniciales.
        - Responder consultas de solo lectura: si una casilla dada es obstaculo, y si
          una coordenada dada esta dentro de los limites de la cuadricula (usa
          constantes.TAMANO_CUADRICULA).
    NO hace:
        - No modela el estado dinamico del robot (fertilizante, combustible, cultivos
          pendientes): eso es responsabilidad de estado.py.
        - No conoce operadores, costos ni logica de busqueda.
        - No lee archivos de texto: eso es responsabilidad de archivos/lector_mundo.py,
          que construye un objeto Mundo a partir del .txt.
Importa de:
    - constantes: para el tamano de la cuadricula (TAMANO_CUADRICULA) usado en la
      validacion de limites.
Lo importan:
    - problema/agrobot_problema.py (para conocer el entorno fijo al generar sucesores).
    - problema/operadores.py (para validar precondiciones de movimiento: limites y
      obstaculos).
    - archivos/lector_mundo.py (lo construye a partir del archivo .txt).
    - gui/panel_mundo.py (para dibujar la cuadricula inicial).
Contrato previsto:
    - Mundo: clase que encapsula obstaculos (conjunto de coordenadas), posicion del
      deposito, posicion inicial de la avioneta, posicion inicial del robot y conjunto
      de cultivos secos iniciales. Se construye a partir de estos datos ya validados
      (la validacion del formato del archivo vive en lector_mundo.py).
    - es_obstaculo(coordenada): recibe una coordenada (fila, columna) y retorna si
      corresponde a una casilla obstaculo.
    - esta_dentro_de_cuadricula(coordenada): recibe una coordenada (fila, columna) y
      retorna si esta dentro del rango valido de la cuadricula 10x10.
    - Atributos de solo lectura: obstaculos (frozenset), deposito, avioneta,
      posicion_robot (posicion inicial) y cultivos_secos (frozenset, los iniciales).
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import constantes


@dataclass(frozen=True)
class Mundo:
    obstaculos: frozenset
    deposito: tuple
    avioneta: tuple
    posicion_robot: tuple
    cultivos_secos: frozenset

    def es_obstaculo(self, coordenada) -> bool:
        return coordenada in self.obstaculos

    def esta_dentro_de_cuadricula(self, coordenada) -> bool:
        fila, columna = coordenada
        limite = constantes.TAMANO_CUADRICULA
        return 0 <= fila < limite and 0 <= columna < limite

