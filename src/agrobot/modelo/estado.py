"""
Archivo:       src/agrobot/modelo/estado.py
Objetivo:      Representar un estado s = (f, c, phi, e, k, P) del problema AgroBot:
               posicion del robot, nivel de fertilizante, si va montado en la avioneta,
               combustible restante de la avioneta y conjunto de cultivos secos
               pendientes de fertilizar.
Responsabilidad:
    SI hace:
        - Definir la tupla de componentes del estado:
            f, c: fila y columna de la posicion actual del robot.
            phi (fertilizante): entero entre 0 y constantes.CAPACIDAD_FERTILIZANTE.
            e (en_avioneta): booleano, si el robot va montado en la avioneta.
            k (combustible): entero entre 0 y constantes.COMBUSTIBLE_INICIAL_AVIONETA.
            P (pendientes): conjunto de coordenadas de cultivos secos aun sin fertilizar.
        - Ser inmutable (no se modifica un Estado existente; los operadores producen
          un Estado nuevo) y comparable/hasheable, de forma que pueda usarse como
          elemento de conjuntos y claves de diccionario (necesario para control de
          ciclos y para conjuntos de nodos visitados).
        - Documentar la tabla de situaciones posibles de la avioneta segun (e, k):
            (e=falso, k=30): avioneta sin usar, en su posicion original.
            (e=verdadero, k>0): avioneta en uso, con combustible disponible.
            (e=falso, k=0): avioneta agotada (ya se uso y se quedo sin combustible).
          (la combinacion (e=verdadero, k=0) no deberia ocurrir: al llegar a 0 el
          combustible, e pasa a falso en el mismo paso, segun operadores.py).
    NO hace:
        - No decide que movimientos son validos ni aplica efectos: eso es
          responsabilidad de problema/operadores.py.
        - No calcula costos: eso es responsabilidad de problema/costos.py.
Importa de:
    - constantes: para los rangos validos de fertilizante y combustible
      (CAPACIDAD_FERTILIZANTE, COMBUSTIBLE_INICIAL_AVIONETA) usados en validaciones
      o documentacion de invariantes.
Lo importan:
    - modelo/mundo.py no lo importa (mundo.py es la parte constante, estado.py es la
      parte dinamica); problema/agrobot_problema.py, problema/operadores.py,
      problema/costos.py, problema/ciclos.py, busqueda/nodo.py (cada nodo envuelve un
      Estado),
      gui/panel_mundo.py y gui/animacion.py (para dibujar cada estado del camino).
Contrato previsto:
    - Estado: clase inmutable con los seis componentes (f, c, phi, e, k, P). Expone
      igualdad y hash basados en el valor de sus componentes (P como estructura
      inmutable/ordenable para poder hashear), de modo que dos estados con los mismos
      valores sean considerados el mismo estado.
    - construir_estado_inicial(mundo): a partir de los datos fijos del Mundo arma el
      Estado inicial con phi=0 (el robot arranca SIN fertilizante y lo consigue en el
      deposito), e=falso, k=COMBUSTIBLE_INICIAL_AVIONETA y P = cultivos secos iniciales.
Decisiones de equipo (antes PENDIENTE):
    - El Estado inicial se construye aqui (construir_estado_inicial); agrobot_problema.py
      solo lo llama.
    - El robot empieza con fertilizante 0, no con CAPACIDAD_FERTILIZANTE.
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import constantes


@dataclass(frozen=True)
class Estado:
    fila: int
    columna: int
    fertilizante: int        # phi: 0 a CAPACIDAD_FERTILIZANTE
    en_avioneta: bool        # e
    combustible: int         # k: 0 a COMBUSTIBLE_INICIAL_AVIONETA
    pendientes: frozenset    # P: coordenadas (fila, columna) de cultivos secos sin tratar

    @property
    def posicion(self) -> tuple:
        return (self.fila, self.columna)

    def describir(self) -> str:
        """Texto corto del estado, para depurar o mostrar en consola."""
        return (
            "pos=" + str(self.posicion)
            + " fert=" + str(self.fertilizante)
            + " cultivos_faltan=" + str(len(self.pendientes))
            + " avioneta=" + ("si" if self.en_avioneta else "no")
            + " comb=" + str(self.combustible)
        )


def construir_estado_inicial(mundo) -> Estado:
    """Estado con el que arranca la busqueda sobre `mundo` (un modelo.mundo.Mundo)."""
    fila, columna = mundo.posicion_robot
    return Estado(
        fila=fila,
        columna=columna,
        fertilizante=0,
        en_avioneta=False,
        combustible=constantes.COMBUSTIBLE_INICIAL_AVIONETA,
        pendientes=frozenset(mundo.cultivos_secos),
    )

