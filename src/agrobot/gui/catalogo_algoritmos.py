"""
Archivo:       src/agrobot/gui/catalogo_algoritmos.py
Objetivo:      Listar en un solo lugar los tipos de busqueda y los algoritmos que ofrece
               la aplicacion, con el texto corto que la interfaz muestra de cada uno.
Responsabilidad:
    SI hace:
        - Definir los dos tipos de busqueda: "No informada" e "Informada".
        - Definir los cinco algoritmos del proyecto y a que tipo pertenece cada uno:
          No informada (Amplitud, Costo uniforme, Profundidad evitando ciclos) e
          Informada (Avara, A*).
        - Guardar una descripcion corta de cada algoritmo para mostrarla al usuario.
    NO hace:
        - No ejecuta ningun algoritmo ni importa de busqueda/: solo nombra las
          opciones. Quien traduce un Algoritmo a la funcion que lo ejecuta
          (buscar_amplitud, buscar_costo_uniforme, ...) es panel_control.py.
        - No usa ninguna libreria de interfaz (es independiente de pygame).
Importa de:    (nada del proyecto; solo la libreria estandar).
Lo importan:   gui/pantalla_seleccion.py. Mas adelante tambien gui/panel_control.py y
               gui/panel_reporte.py (por ejemplo, para decidir si se muestra el costo).
Contrato previsto:
    - TipoBusqueda: enumeracion con NO_INFORMADA e INFORMADA; su valor es el texto
      que se muestra en pantalla.
    - Algoritmo: enumeracion con AMPLITUD, COSTO_UNIFORME, PROFUNDIDAD, AVARA y
      A_ESTRELLA; su valor es el texto que se muestra en pantalla.
    - ALGORITMOS_POR_TIPO: diccionario TipoBusqueda -> tupla de Algoritmo, en el orden
      en que se muestran.
    - DESCRIPCIONES: diccionario Algoritmo -> texto corto que explica la idea del
      algoritmo.
    - tipo_de(algoritmo): retorna el TipoBusqueda al que pertenece el algoritmo.
"""
from __future__ import annotations

from enum import Enum


class TipoBusqueda(Enum):
    NO_INFORMADA = "No informada"
    INFORMADA = "Informada"


class Algoritmo(Enum):
    AMPLITUD = "Amplitud"
    COSTO_UNIFORME = "Costo uniforme"
    PROFUNDIDAD = "Profundidad evitando ciclos"
    AVARA = "Avara"
    A_ESTRELLA = "A*"


ALGORITMOS_POR_TIPO = {
    TipoBusqueda.NO_INFORMADA: (
        Algoritmo.AMPLITUD,
        Algoritmo.COSTO_UNIFORME,
        Algoritmo.PROFUNDIDAD,
    ),
    TipoBusqueda.INFORMADA: (
        Algoritmo.AVARA,
        Algoritmo.A_ESTRELLA,
    ),
}

DESCRIPCIONES = {
    Algoritmo.AMPLITUD: "Expande nivel por nivel. Encuentra la solución con menos movimientos.",
    Algoritmo.COSTO_UNIFORME: "Expande primero el nodo de menor costo acumulado g(n). Garantiza el menor costo.",
    Algoritmo.PROFUNDIDAD: "Baja por una rama hasta el fondo, sin repetir estados dentro de ella.",
    Algoritmo.AVARA: "Elige el nodo con menor heurística h(n). Rápida, pero no garantiza la mejor solución.",
    Algoritmo.A_ESTRELLA: "Combina costo y heurística: f(n) = g(n) + h(n). Óptima si h es admisible.",
}


def tipo_de(algoritmo: Algoritmo) -> TipoBusqueda:
    """Retorna el tipo de busqueda (No informada / Informada) del algoritmo dado."""
    for tipo, algoritmos in ALGORITMOS_POR_TIPO.items():
        if algoritmo in algoritmos:
            return tipo
    raise ValueError("Algoritmo sin tipo asignado: " + str(algoritmo))
