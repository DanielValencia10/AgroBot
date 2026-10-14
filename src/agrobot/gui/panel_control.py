"""
Archivo:       src/agrobot/gui/panel_control.py
Objetivo:      Convertir la eleccion del usuario (mundo + algoritmo, hecha en
               pantalla_seleccion.py) en una busqueda ejecutada: cargar el mundo,
               construir el problema, correr el algoritmo y entregar todo lo que la
               ventana principal necesita para mostrarlo.
Responsabilidad:
    SI hace:
        - Cargar el Mundo del archivo elegido (archivos/lector_mundo.py).
        - Construir el AgroBotProblema a partir del Mundo.
        - Traducir el Algoritmo elegido a la funcion que lo ejecuta y correrla.
        - Decir que algoritmos estan disponibles (los que ya tienen implementacion).
        - Avisar con excepciones claras cuando algo falla: ErrorMundo (archivo no valido)
          o AlgoritmoNoDisponible (algoritmo elegido sin implementar).
    NO hace:
        - No dibuja nada: la eleccion la hace pantalla_seleccion.py y el resultado lo
          muestra ventana_principal.py.
        - No implementa la logica interna de ningun algoritmo de busqueda.
Importa de:
    - busqueda.no_informada.amplitud: buscar_amplitud.
    - busqueda.no_informada.costo_uniforme: buscar_costo_uniforme.
    - problema.agrobot_problema (AgroBotProblema): para construir el problema.
    - archivos.lector_mundo: para cargar el Mundo desde el archivo .txt elegido.
    - gui.catalogo_algoritmos (Algoritmo) y gui.pantalla_seleccion (SeleccionInicio).
Lo importan:
    - main.py (flujo seleccion -> busqueda -> ventana principal).
Contrato previsto:
    - ALGORITMOS_DISPONIBLES: diccionario Algoritmo -> funcion buscar_*(problema) que
      retorna un Resultado. AL IMPLEMENTAR UN ALGORITMO NUEVO HAY QUE AGREGARLO AQUI
      (Costo uniforme, Profundidad, Avara y A* aun no estan).
    - ejecutar_seleccion(seleccion): retorna una EjecucionBusqueda (ruta_mundo,
      algoritmo, mundo, problema, resultado). Lanza ErrorMundo o AlgoritmoNoDisponible.
    - AlgoritmoNoDisponible: subclase de NotImplementedError; su atributo `algoritmo`
      dice cual fue.
Decision de equipo:
    - La eleccion de tipo/algoritmo y de archivo se hace en pantalla_seleccion.py (ya
      implementada); este archivo conserva el nombre panel_control.py del esqueleto pero
      es el "controlador" de esa eleccion, no un panel con botones.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..archivos.lector_mundo import leer_mundo_desde_archivo
from ..busqueda.no_informada.amplitud import buscar_amplitud
from ..busqueda.no_informada.costo_uniforme import buscar_costo_uniforme
from ..busqueda.no_informada.profundidad import buscar_profundidad
from ..problema.agrobot_problema import AgroBotProblema
from .catalogo_algoritmos import Algoritmo

ALGORITMOS_DISPONIBLES = {
    Algoritmo.AMPLITUD: buscar_amplitud,
    Algoritmo.COSTO_UNIFORME: buscar_costo_uniforme,
    Algoritmo.PROFUNDIDAD: buscar_profundidad,
}


class AlgoritmoNoDisponible(NotImplementedError):
    def __init__(self, algoritmo: Algoritmo):
        super().__init__(algoritmo.value + " todavia no esta implementado.")
        self.algoritmo = algoritmo


@dataclass(frozen=True)
class EjecucionBusqueda:
    """Una busqueda ya ejecutada, lista para mostrarse."""

    ruta_mundo: object
    algoritmo: Algoritmo
    mundo: object
    problema: object
    resultado: object


def ejecutar_seleccion(seleccion) -> EjecucionBusqueda:
    """Carga el mundo, construye el problema y corre el algoritmo elegido."""
    buscar = ALGORITMOS_DISPONIBLES.get(seleccion.algoritmo)
    if buscar is None:
        raise AlgoritmoNoDisponible(seleccion.algoritmo)
    mundo = leer_mundo_desde_archivo(seleccion.ruta_mundo)  # lanza ErrorMundo
    problema = AgroBotProblema(mundo)
    return EjecucionBusqueda(
        ruta_mundo=seleccion.ruta_mundo,
        algoritmo=seleccion.algoritmo,
        mundo=mundo,
        problema=problema,
        resultado=buscar(problema),
    )