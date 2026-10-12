"""
Archivo:       src/agrobot/gui/panel_reporte.py
Objetivo:      Mostrar al usuario el reporte de metricas de la busqueda ejecutada:
               nodos expandidos, profundidad de la solucion, tiempo de computo y,
               cuando aplique, el costo total.
Responsabilidad:
    SI hace:
        - Leer los campos del Resultado entregado (nodos_expandidos,
          profundidad_de_la_solucion, tiempo_de_computo y costo_total) y mostrarlos de
          forma legible.
        - Mostrar el campo costo_total solo cuando el algoritmo ejecutado fue Costo
          uniforme o A* (los demas algoritmos no lo calculan).
    NO hace:
        - No calcula ninguna de estas metricas: solo las muestra.
        - No anima el camino de movimientos (eso es de animacion.py).
Importa de:
    - busqueda.resultado (Resultado): para leer los campos a mostrar.
    - constantes: capacidades para mostrar fertilizante y combustible como "x/max".
    - gui.estilo: paleta, tipografias y dibujar_tarjeta.
Lo importan:
    - gui/ventana_principal.py (lo integra como uno de sus paneles).
Contrato previsto:
    - PanelReporte(resultado, algoritmo): componente de interfaz que, dado un Resultado
      y el nombre del algoritmo ejecutado, muestra sus metricas (mostrando costo_total
      solo cuando el Resultado lo trae, es decir, con Costo uniforme y A*).
    - filas_del_estado(estado, paso, costo=None): filas (paso, posicion, fertilizante,
      combustible, cultivos secos, avioneta y, si se da, costo acumulado) de cualquier
      Estado; la usa filas_del_robot y la pantalla de resultados para el nodo elegido.
    - dibujar(pantalla, area, animacion=None): dibuja el reporte en `area` (ALTO_RECOMENDADO
      de alto). Si se le pasa el PanelAnimacion, agrega ademas el estado actual del
      robot (paso, posicion, fertilizante, combustible, cultivos, avioneta) y el mensaje
      de estado: REPRODUCIENDO, PAUSADO, META ALCANZADA o SIN SOLUCION.
Origen:        Panel derecho de Demo/main.py (dibujar_panel), con la paleta de estilo.py.
"""
from __future__ import annotations

from .. import constantes
from . import estilo

ALTO_RECOMENDADO = 316
ALTO_FILA = 23
MARGEN = 18


class PanelReporte:
    def __init__(self, resultado, algoritmo: str):
        self.resultado = resultado
        self.algoritmo = algoritmo

    # ------------------------------------------------------------ contenido
    def filas_de_busqueda(self) -> list:
        """Pares (etiqueta, valor) con las metricas de la busqueda."""
        resultado = self.resultado
        filas = [
            ("Nodos expandidos", str(resultado.nodos_expandidos)),
            ("Profundidad", str(resultado.profundidad_de_la_solucion)),
            ("Tiempo", f"{resultado.tiempo_de_computo:.4f} s"),
        ]
        if resultado.costo_total is not None:
            filas.append(("Costo total", f"{resultado.costo_total:g}"))
        return filas

    @staticmethod
    def filas_del_estado(estado, paso: str, costo=None) -> list:
        """Pares (etiqueta, valor) de un Estado cualquiera (no solo el actual).
        `paso` es el texto de la fila "Paso"; si se da `costo`, agrega "Costo acumulado"."""
        filas = [
            ("Paso", paso),
            ("Posición", "(" + str(estado.fila) + ", " + str(estado.columna) + ")"),
            ("Fertilizante", str(estado.fertilizante) + "/" + str(constantes.CAPACIDAD_FERTILIZANTE)),
            ("Combustible", str(estado.combustible) + "/" + str(constantes.COMBUSTIBLE_INICIAL_AVIONETA)),
            ("Cultivos secos", str(len(estado.pendientes))),
            ("En avioneta", "Sí" if estado.en_avioneta else "No"),
        ]
        if costo is not None:
            filas.append(("Costo acumulado", f"{costo:g}"))
        return filas

    @staticmethod
    def filas_del_robot(animacion) -> list:
        """Pares (etiqueta, valor) del estado actual de la animacion."""
        return PanelReporte.filas_del_estado(
            animacion.estado_actual,
            str(animacion.paso) + "/" + str(animacion.total_pasos))

    def mensaje(self, animacion=None):
        """(texto, color) del estado de la reproduccion, o None si no hay animacion."""
        if not self.resultado.solucion_encontrada:
            return "SIN SOLUCIÓN", estilo.COLOR_ALERTA
        if animacion is None:
            return None
        if animacion.terminada:
            return "META ALCANZADA", estilo.COLOR_LINO
        if animacion.pausada:
            return "PAUSADO", estilo.COLOR_SALVIA_TENUE
        return "REPRODUCIENDO", estilo.COLOR_OLIVA

    # ------------------------------------------------------------ dibujo
    def dibujar(self, pantalla, area, animacion=None) -> None:
        estilo.dibujar_tarjeta(pantalla, area, radio=14)
        izquierda = area.x + MARGEN
        derecha = area.right - MARGEN
        y = area.y + MARGEN

        titulo = estilo.fuente_pixel(20, 700)
        estilo.texto(pantalla, estilo.recortar(self.algoritmo, titulo, derecha - izquierda),
                     titulo, estilo.COLOR_SALVIA, (izquierda, y))
        y += 34

        mensaje = self.mensaje(animacion)
        if mensaje is not None:
            estilo.texto(pantalla, mensaje[0], estilo.fuente_pixel(16, 700), mensaje[1],
                         (izquierda, y))
            y += 30

        filas = self.filas_de_busqueda()
        if animacion is not None:
            filas = filas + [None] + self.filas_del_robot(animacion)
        for fila in filas:
            if fila is None:  # separador entre busqueda y estado del robot
                y += 6
                continue
            etiqueta, valor = fila
            estilo.texto(pantalla, etiqueta, estilo.fuente_texto(15, 400),
                         estilo.COLOR_SALVIA_TENUE, (izquierda, y))
            estilo.texto(pantalla, valor, estilo.fuente_texto(15, 700),
                         estilo.COLOR_CREMA, (derecha, y), ancla="topright")
            y += ALTO_FILA