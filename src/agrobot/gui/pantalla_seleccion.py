"""
Archivo:       src/agrobot/gui/pantalla_seleccion.py
Objetivo:      Mostrar la segunda pantalla de AgroBot, donde el usuario elige el mundo
               (archivo .txt), el tipo de busqueda y el algoritmo antes de pasar a la
               ventana principal.
Responsabilidad:
    SI hace:
        - Listar los archivos .txt de la carpeta de mundos y dejar elegir uno.
        - Dejar elegir el tipo de busqueda ("No informada" o "Informada") y, segun el
          tipo, uno de sus algoritmos (ver catalogo_algoritmos.py).
        - Habilitar el boton "Iniciar" solo cuando hay un mundo y un algoritmo
          elegidos, y entregar esa eleccion a quien llamo la pantalla.
        - Ofrecer "Volver al inicio" para regresar a la bienvenida.
        - Seguir el mockup "2 - Seleccion" (colores, medidas y textos).
    NO hace:
        - No lee ni valida el contenido del archivo de mundo (eso es de
          archivos/lector_mundo.py): solo entrega la ruta elegida.
        - No ejecuta el algoritmo ni construye el problema (eso lo hace
          panel_control.py cuando se integre).
        - No decide que pantalla viene antes o despues: lo hace pantalla_inicio.py.
Importa de:
    - gui.catalogo_algoritmos: tipos de busqueda, algoritmos y sus descripciones.
    - gui.estilo: colores, tipografias, matica y utilidades de dibujo.
    - pygame (pygame-ce): libreria de interfaz del proyecto.
Lo importan:
    - gui/pantalla_inicio.py (flujo bienvenida -> seleccion).
Contrato previsto:
    - SeleccionInicio: dato inmutable con la ruta del mundo elegido y el Algoritmo
      elegido (el tipo de busqueda se obtiene con la propiedad tipo).
    - VOLVER: valor que retorna ejecutar() cuando el usuario pide volver al inicio.
    - listar_mundos(carpeta): retorna la lista ordenada de archivos .txt de la carpeta.
    - PantallaSeleccion(carpeta_mundos).ejecutar(pantalla): muestra la pantalla y bloquea
      hasta que el usuario pulsa "Iniciar" (retorna una SeleccionInicio), "Volver al
      inicio" (retorna VOLVER) o cierra la ventana / pulsa Esc (retorna None).
PENDIENTE:
    - Mostrar una vista previa del mundo seleccionado cuando exista lector_mundo.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from . import estilo
from .catalogo_algoritmos import (
    ALGORITMOS_POR_TIPO,
    DESCRIPCIONES,
    Algoritmo,
    TipoBusqueda,
    tipo_de,
)

VOLVER = "volver"

# ---------------------------------------------------------------- medidas (mockup)
FILAS_VISIBLES = 5          # archivos de mundo visibles a la vez
ALTO_FILA_MUNDO = 58
PASO_FILA_MUNDO = 68
ALTO_AVISO = 75
SEPARACION_AVISO = 19

ANCHO_FILA_ALGORITMO = 583
SEPARACION_ALGORITMOS = 15
ALTO_BASE_ALGORITMO = 64    # relleno + nombre + espacio (sin las lineas de descripcion)
ALTO_LINEA_DESCRIPCION = 20
MARGEN_TEXTO_ALGORITMO = 54  # desde el borde izquierdo de la fila hasta el nombre
MAX_LINEAS_DESCRIPCION = 2

TEXTO_VACIO = "No hay archivos .txt en la carpeta mundos/. Agrega uno y vuelve a abrir."
TEXTO_AVISO = "Agrega más archivos .txt a la carpeta mundos/ y aparecerán aquí."


@dataclass(frozen=True)
class SeleccionInicio:
    """Lo que el usuario eligio en la pantalla de seleccion."""

    ruta_mundo: Path
    algoritmo: Algoritmo

    @property
    def tipo(self) -> TipoBusqueda:
        return tipo_de(self.algoritmo)


def listar_mundos(carpeta) -> list:
    """Archivos .txt de la carpeta, ordenados por nombre (lista vacia si no existe)."""
    carpeta = Path(carpeta)
    if not carpeta.is_dir():
        return []
    return sorted(carpeta.glob("*.txt"), key=lambda ruta: ruta.name.lower())


class PantallaSeleccion:
    def __init__(self, carpeta_mundos):
        self.carpeta_mundos = Path(carpeta_mundos)
        self.mundos = listar_mundos(self.carpeta_mundos)
        self.indice_mundo = None            # como en el mockup, nada elegido al inicio
        self.tipo = TipoBusqueda.NO_INFORMADA
        self.algoritmo = None
        self.primera_fila_visible = 0
        self._zonas = self._calcular_zonas()

    # ================================================================
    # Estado de la eleccion (sin dibujo: se puede probar sin ventana)
    # ================================================================
    def esta_lista(self) -> bool:
        return self.indice_mundo is not None and self.algoritmo is not None

    def seleccion(self):
        """La eleccion actual, o None si todavia falta el mundo o el algoritmo."""
        if not self.esta_lista():
            return None
        return SeleccionInicio(self.mundos[self.indice_mundo], self.algoritmo)

    def elegir_mundo(self, indice: int) -> None:
        if 0 <= indice < len(self.mundos):
            self.indice_mundo = indice

    def elegir_tipo(self, tipo: TipoBusqueda) -> None:
        self.tipo = tipo
        # Si el algoritmo elegido no es de este tipo, se descarta
        if self.algoritmo is not None and self.algoritmo not in ALGORITMOS_POR_TIPO[tipo]:
            self.algoritmo = None

    def elegir_algoritmo(self, algoritmo: Algoritmo) -> None:
        if algoritmo in ALGORITMOS_POR_TIPO[self.tipo]:
            self.algoritmo = algoritmo

    def desplazar_lista(self, filas: int) -> None:
        ultima_primera = max(0, len(self.mundos) - FILAS_VISIBLES)
        self.primera_fila_visible = max(0, min(ultima_primera, self.primera_fila_visible + filas))

    def recargar_mundos(self) -> None:
        """Vuelve a leer la carpeta (por si se agregaron archivos) conservando la eleccion."""
        elegido = self.mundos[self.indice_mundo] if self.indice_mundo is not None else None
        self.mundos = listar_mundos(self.carpeta_mundos)
        self.indice_mundo = self.mundos.index(elegido) if elegido in self.mundos else None
        self.desplazar_lista(0)

    # ================================================================
    # Zonas (las usan tanto el dibujo como los clics)
    # ================================================================
    @staticmethod
    def _calcular_zonas() -> dict:
        return {
            "tarjeta_mundos": pygame.Rect(40, 123, 376, 536),
            "tarjeta_busqueda": pygame.Rect(441, 123, 639, 536),
            "lista_mundos": pygame.Rect(68, 237, 320, ALTO_FILA_MUNDO),
            "tipo_no_informada": pygame.Rect(468, 203, 286, 54),
            "tipo_informada": pygame.Rect(766, 203, 286, 54),
            "boton_iniciar": pygame.Rect(851, 669, 228, 62),
            "volver": pygame.Rect(930, 54, 140, 28),
        }

    def _filas_mundo(self) -> list:
        """Pares (indice, rect) de los archivos que se ven ahora en la lista."""
        base = self._zonas["lista_mundos"]
        ultimo = min(len(self.mundos), self.primera_fila_visible + FILAS_VISIBLES)
        filas = []
        for posicion, indice in enumerate(range(self.primera_fila_visible, ultimo)):
            filas.append((indice, pygame.Rect(base.x, base.y + posicion * PASO_FILA_MUNDO,
                                              base.w, ALTO_FILA_MUNDO)))
        return filas

    def _lineas_descripcion(self, algoritmo) -> list:
        ancho = ANCHO_FILA_ALGORITMO - MARGEN_TEXTO_ALGORITMO - 26
        lineas = estilo.envolver(DESCRIPCIONES[algoritmo], estilo.fuente_texto(14, 400), ancho)
        return lineas[:MAX_LINEAS_DESCRIPCION]

    def _filas_algoritmo(self) -> list:
        """Ternas (Algoritmo, rect, lineas de descripcion) del tipo de busqueda actual."""
        filas = []
        y = 331
        for algoritmo in ALGORITMOS_POR_TIPO[self.tipo]:
            lineas = self._lineas_descripcion(algoritmo)
            alto = ALTO_BASE_ALGORITMO + ALTO_LINEA_DESCRIPCION * max(1, len(lineas)) + 0
            filas.append((algoritmo, pygame.Rect(468, y, ANCHO_FILA_ALGORITMO, alto), lineas))
            y += alto + SEPARACION_ALGORITMOS
        return filas

    # ================================================================
    # Eventos
    # ================================================================
    def procesar_evento(self, evento):
        """Aplica un evento de pygame. Retorna "iniciar", "volver", "salir" o None."""
        if evento.type == pygame.QUIT:
            return "salir"
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "salir"
            if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.esta_lista():
                return "iniciar"
        elif evento.type == pygame.MOUSEWHEEL:
            if self._zonas["tarjeta_mundos"].collidepoint(pygame.mouse.get_pos()):
                self.desplazar_lista(-evento.y)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self._procesar_clic(evento.pos)
        return None

    def _procesar_clic(self, posicion):
        if self._zonas["volver"].collidepoint(posicion):
            return "volver"
        if self._zonas["boton_iniciar"].collidepoint(posicion):
            return "iniciar" if self.esta_lista() else None
        for indice, rect in self._filas_mundo():
            if rect.collidepoint(posicion):
                self.elegir_mundo(indice)
                return None
        if self._zonas["tipo_no_informada"].collidepoint(posicion):
            self.elegir_tipo(TipoBusqueda.NO_INFORMADA)
        elif self._zonas["tipo_informada"].collidepoint(posicion):
            self.elegir_tipo(TipoBusqueda.INFORMADA)
        else:
            for algoritmo, rect, _ in self._filas_algoritmo():
                if rect.collidepoint(posicion):
                    self.elegir_algoritmo(algoritmo)
                    break
        return None

    # ================================================================
    # Bucle principal
    # ================================================================
    def ejecutar(self, pantalla):
        """Muestra la pantalla. Retorna SeleccionInicio, VOLVER, o None si se cierra."""
        self.recargar_mundos()
        reloj = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                accion = self.procesar_evento(evento)
                if accion == "salir":
                    return None
                if accion == "volver":
                    return VOLVER
                if accion == "iniciar":
                    return self.seleccion()
            self._dibujar(pantalla)
            pygame.display.flip()
            reloj.tick(60)

    # ================================================================
    # Dibujo
    # ================================================================
    def _dibujar(self, pantalla) -> None:
        mouse = pygame.mouse.get_pos()
        pantalla.fill(estilo.COLOR_FONDO)
        self._dibujar_encabezado(pantalla, mouse)
        self._dibujar_tarjeta_mundos(pantalla, mouse)
        self._dibujar_tarjeta_busqueda(pantalla, mouse)
        self._dibujar_pie(pantalla, mouse)

    def _dibujar_encabezado(self, pantalla, mouse) -> None:
        estilo.dibujar_matica(pantalla, 46, 39, 3)
        fuente = estilo.fuente_pixel_ajustada("AgroBot", 185, 700)
        ancho_agro = fuente.size("Agro")[0]
        estilo.texto_linea_base(pantalla, "Agro", fuente, estilo.COLOR_SALVIA, 115, 70)
        estilo.texto_linea_base(pantalla, "Bot", fuente, estilo.COLOR_LINO, 115 + ancho_agro, 70)
        subtitulo = "Prepara tu siembra: elige el mundo y la forma de buscar."
        medida = estilo.fuente_texto(100, 400).size(subtitulo)[0]
        fuente_sub = estilo.fuente_texto(max(10, round(100 * 414 / max(1, medida))), 400)
        estilo.texto(pantalla, subtitulo, fuente_sub, estilo.COLOR_SALVIA_TENUE,
                     (115, 93), ancla="midleft")

        volver = self._zonas["volver"]
        color = estilo.COLOR_LINO if volver.collidepoint(mouse) else estilo.COLOR_SALVIA
        estilo.texto(pantalla, "←  Volver al inicio", estilo.fuente_texto(15, 500), color,
                     (volver.right, volver.centery), ancla="midright")

    def _dibujar_tarjeta_mundos(self, pantalla, mouse) -> None:
        tarjeta = self._zonas["tarjeta_mundos"]
        estilo.dibujar_tarjeta(pantalla, tarjeta)
        self._titulo_paso(pantalla, 1, "Mundo", (87, 170))
        estilo.texto(pantalla, "Archivos de la carpeta mundos/", estilo.fuente_texto(14, 400),
                     estilo.COLOR_SALVIA_TENUE, (68, 213), ancla="midleft")

        lista = self._zonas["lista_mundos"]
        fuente = estilo.fuente_texto(17, 500)
        if not self.mundos:
            self._dibujar_aviso(pantalla, pygame.Rect(lista.x, lista.y, lista.w, ALTO_AVISO),
                                TEXTO_VACIO, estilo.COLOR_LINO)
            return

        for indice, rect in self._filas_mundo():
            elegida = indice == self.indice_mundo
            self._dibujar_fila(pantalla, rect, elegida, rect.collidepoint(mouse), radio=14)
            nombre = estilo.recortar(self.mundos[indice].name, fuente, rect.w - 36)
            estilo.texto(pantalla, nombre, fuente,
                         estilo.COLOR_LINO if elegida else estilo.COLOR_CREMA,
                         (rect.x + 18, rect.centery), ancla="midleft")

        filas_a_la_vista = len(self._filas_mundo())
        if len(self.mundos) <= FILAS_VISIBLES - 1:
            y = lista.y + (filas_a_la_vista - 1) * PASO_FILA_MUNDO + ALTO_FILA_MUNDO + SEPARACION_AVISO
            self._dibujar_aviso(pantalla, pygame.Rect(lista.x, y, lista.w, ALTO_AVISO),
                                TEXTO_AVISO, estilo.COLOR_SALVIA_TENUE)

        # Barra de desplazamiento, solo si hay mas archivos que filas visibles
        if len(self.mundos) > FILAS_VISIBLES:
            alto_lista = (FILAS_VISIBLES - 1) * PASO_FILA_MUNDO + ALTO_FILA_MUNDO
            pista = pygame.Rect(lista.right + 12, lista.y, 6, alto_lista)
            pygame.draw.rect(pantalla, estilo.COLOR_FONDO, pista, border_radius=3)
            alto_barra = max(24, int(pista.h * FILAS_VISIBLES / len(self.mundos)))
            recorrido = pista.h - alto_barra
            ultima_primera = len(self.mundos) - FILAS_VISIBLES
            y_barra = pista.y + int(recorrido * self.primera_fila_visible / ultima_primera)
            pygame.draw.rect(pantalla, estilo.COLOR_OLIVA,
                             pygame.Rect(pista.x, y_barra, pista.w, alto_barra), border_radius=3)

    def _dibujar_aviso(self, pantalla, rect, contenido, color) -> None:
        estilo.dibujar_borde_punteado(pantalla, rect, estilo.COLOR_BORDE)
        fuente = estilo.fuente_texto(13, 400)
        for numero, linea in enumerate(estilo.envolver(contenido, fuente, rect.w - 36)[:3]):
            estilo.texto(pantalla, linea, fuente, color,
                         (rect.x + 18, rect.y + 28 + numero * 20), ancla="midleft")

    def _dibujar_tarjeta_busqueda(self, pantalla, mouse) -> None:
        tarjeta = self._zonas["tarjeta_busqueda"]
        estilo.dibujar_tarjeta(pantalla, tarjeta)
        self._titulo_paso(pantalla, 2, "Tipo de búsqueda", (487, 172))

        fuente_tipo = estilo.fuente_pixel(18, 700)
        for tipo, clave in ((TipoBusqueda.NO_INFORMADA, "tipo_no_informada"),
                            (TipoBusqueda.INFORMADA, "tipo_informada")):
            rect = self._zonas[clave]
            if tipo == self.tipo:
                pygame.draw.rect(pantalla, estilo.COLOR_OLIVA, rect, border_radius=14)
                color = estilo.COLOR_FONDO
            else:
                pygame.draw.rect(pantalla, estilo.COLOR_FONDO, rect, border_radius=14)
                borde = estilo.COLOR_OLIVA if rect.collidepoint(mouse) else estilo.COLOR_BORDE
                pygame.draw.rect(pantalla, borde, rect, 2, border_radius=14)
                color = estilo.COLOR_CREMA
            estilo.texto(pantalla, tipo.value, fuente_tipo, color, rect.center, ancla="center")

        self._titulo_paso(pantalla, 3, "Algoritmo", (487, 298))
        fuente_nombre = estilo.fuente_pixel(20, 700)
        fuente_desc = estilo.fuente_texto(14, 400)
        for algoritmo, rect, lineas in self._filas_algoritmo():
            elegida = algoritmo == self.algoritmo
            self._dibujar_fila(pantalla, rect, elegida, rect.collidepoint(mouse), radio=14)
            self._dibujar_radio(pantalla, (rect.x + 28, rect.centery), elegida)
            x_texto = rect.x + MARGEN_TEXTO_ALGORITMO
            estilo.texto(pantalla, algoritmo.value, fuente_nombre,
                         estilo.COLOR_LINO if elegida else estilo.COLOR_CREMA,
                         (x_texto, rect.y + 31), ancla="midleft")
            for numero, linea in enumerate(lineas):
                estilo.texto(pantalla, linea, fuente_desc, estilo.COLOR_SALVIA,
                             (x_texto, rect.y + 57 + numero * ALTO_LINEA_DESCRIPCION),
                             ancla="midleft")

    def _dibujar_pie(self, pantalla, mouse) -> None:
        if self.esta_lista():
            mensaje = "Listo: " + self.mundos[self.indice_mundo].name + "  ·  " + self.algoritmo.value
        elif not self.mundos:
            mensaje = "Falta un archivo de mundo en la carpeta mundos/."
        else:
            mensaje = "Elige un mundo y un algoritmo para continuar."
        fuente = estilo.fuente_texto(17, 700)
        estilo.texto(pantalla, estilo.recortar(mensaje, fuente, 780), fuente,
                     estilo.COLOR_LINO, (40, 689), ancla="midleft")
        estilo.texto(pantalla, "Enter: iniciar · Esc: salir", estilo.fuente_texto(13, 400),
                     estilo.COLOR_SALVIA_TENUE, (40, 721), ancla="midleft")

        boton = self._zonas["boton_iniciar"]
        estilo.dibujar_boton(pantalla, boton, "Iniciar", self.esta_lista(),
                             boton.collidepoint(mouse))

    # ---------------------------------------------------------------- utilidades
    @staticmethod
    def _dibujar_fila(pantalla, rect, elegida, con_mouse, radio) -> None:
        relleno = estilo.COLOR_FILA_ENCIMA if con_mouse and not elegida else estilo.COLOR_FONDO
        pygame.draw.rect(pantalla, relleno, rect, border_radius=radio)
        if elegida:
            pygame.draw.rect(pantalla, estilo.COLOR_OLIVA, rect, 2, border_radius=radio)

    @staticmethod
    def _dibujar_radio(pantalla, centro, elegida) -> None:
        pygame.draw.circle(pantalla, estilo.COLOR_OLIVA if elegida else estilo.COLOR_SALVIA_TENUE,
                           centro, 11)
        pygame.draw.circle(pantalla, estilo.COLOR_FONDO, centro, 8)
        if elegida:
            pygame.draw.circle(pantalla, estilo.COLOR_OLIVA, centro, 5)

    @staticmethod
    def _titulo_paso(pantalla, numero, contenido, centro) -> None:
        pygame.draw.circle(pantalla, estilo.COLOR_OLIVA, centro, 19)
        estilo.texto(pantalla, str(numero), estilo.fuente_pixel(18, 700), estilo.COLOR_FONDO,
                     centro, ancla="center")
        estilo.texto(pantalla, contenido, estilo.fuente_pixel(26, 700), estilo.COLOR_CREMA,
                     (centro[0] + 32, centro[1] + 1), ancla="midleft")
