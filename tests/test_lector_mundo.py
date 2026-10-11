"""
Archivo:       tests/test_lector_mundo.py
Objetivo:      Verificar archivos/lector_mundo.py y las clases base de modelo/ que construye.
Responsabilidad:
    QUE VERIFICA:
        - Que mundos/Prueba1.txt se lee y produce un Mundo con: deposito en (0,2),
          avioneta en (0,6), robot en (4,0) y cultivos secos en (4,3), (5,3) y (6,8)
          (fila 0 arriba, coordenadas (fila, columna) desde 0).
        - Que se rechacen archivos que no tengan exactamente 10 filas o 10 columnas,
          con codigos fuera de 0 a 5, sin exactamente un 2, un 4 y un 5, o sin cultivos
          secos, y que un archivo inexistente de un error claro.
        - Que Estado sea inmutable/hasheable y que el estado inicial empiece sin
          fertilizante, fuera de la avioneta y con el combustible completo.
Importa de:
    - archivos.lector_mundo: para invocar la lectura sobre casos validos e invalidos.
    - modelo.estado, modelo.movimiento: clases base del modelo.
    - mundos/Prueba1.txt: como archivo de referencia para el caso valido.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_lector_mundo
"""
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from agrobot import constantes  # noqa: E402
from agrobot.archivos.lector_mundo import (  # noqa: E402
    ErrorMundo,
    construir_mundo,
    leer_mundo_desde_archivo,
)
from agrobot.modelo.estado import Estado, construir_estado_inicial  # noqa: E402
from agrobot.modelo.movimiento import Movimiento, obtener_desplazamiento  # noqa: E402

PRUEBA1 = RAIZ / "mundos" / "Prueba1.txt"


def matriz_valida():
    matriz = [[0] * 10 for _ in range(10)]
    matriz[0][0] = constantes.CODIGO_AGROBOT
    matriz[0][1] = constantes.CODIGO_DEPOSITO
    matriz[0][2] = constantes.CODIGO_AVIONETA
    matriz[5][5] = constantes.CODIGO_CULTIVO_SECO
    return matriz


class TestLectorMundo(unittest.TestCase):
    def test_prueba1(self):
        mundo = leer_mundo_desde_archivo(PRUEBA1)
        self.assertEqual(mundo.deposito, (0, 2))
        self.assertEqual(mundo.avioneta, (0, 6))
        self.assertEqual(mundo.posicion_robot, (4, 0))
        self.assertEqual(mundo.cultivos_secos, frozenset({(4, 3), (5, 3), (6, 8)}))
        self.assertTrue(mundo.es_obstaculo((0, 0)))
        self.assertFalse(mundo.es_obstaculo((1, 0)))

    def test_limites_de_la_cuadricula(self):
        mundo = construir_mundo(matriz_valida())
        self.assertTrue(mundo.esta_dentro_de_cuadricula((0, 0)))
        self.assertTrue(mundo.esta_dentro_de_cuadricula((9, 9)))
        self.assertFalse(mundo.esta_dentro_de_cuadricula((-1, 0)))
        self.assertFalse(mundo.esta_dentro_de_cuadricula((0, 10)))

    def test_rechaza_filas_o_columnas_incorrectas(self):
        with self.assertRaises(ErrorMundo):
            construir_mundo(matriz_valida()[:9])
        con_columna_de_mas = matriz_valida()
        con_columna_de_mas[3].append(0)
        with self.assertRaises(ErrorMundo):
            construir_mundo(con_columna_de_mas)

    def test_rechaza_codigo_fuera_de_rango(self):
        matriz = matriz_valida()
        matriz[9][9] = 6
        with self.assertRaisesRegex(ErrorMundo, "6"):
            construir_mundo(matriz)

    def test_rechaza_elementos_unicos_mal_contados(self):
        for codigo in (constantes.CODIGO_AGROBOT, constantes.CODIGO_DEPOSITO,
                       constantes.CODIGO_AVIONETA):
            faltante = matriz_valida()
            for fila in faltante:
                fila[:] = [0 if c == codigo else c for c in fila]
            with self.assertRaises(ErrorMundo):
                construir_mundo(faltante)
            repetido = matriz_valida()
            repetido[9][9] = codigo
            with self.assertRaises(ErrorMundo):
                construir_mundo(repetido)

    def test_rechaza_mundo_sin_cultivos(self):
        matriz = matriz_valida()
        matriz[5][5] = 0
        with self.assertRaises(ErrorMundo):
            construir_mundo(matriz)

    def test_errores_de_archivo(self):
        with self.assertRaises(ErrorMundo):
            leer_mundo_desde_archivo(RAIZ / "mundos" / "no_existe.txt")
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "malo.txt"
            ruta.write_text("1 2 x\n", encoding="utf-8")
            with self.assertRaisesRegex(ErrorMundo, "linea 1"):
                leer_mundo_desde_archivo(ruta)


class TestModelo(unittest.TestCase):
    def test_estado_inicial(self):
        estado = construir_estado_inicial(leer_mundo_desde_archivo(PRUEBA1))
        self.assertEqual(estado.posicion, (4, 0))
        self.assertEqual(estado.fertilizante, 0)
        self.assertFalse(estado.en_avioneta)
        self.assertEqual(estado.combustible, constantes.COMBUSTIBLE_INICIAL_AVIONETA)
        self.assertEqual(len(estado.pendientes), 3)

    def test_estado_es_inmutable_y_hasheable(self):
        a = Estado(1, 2, 0, False, 30, frozenset({(3, 3)}))
        b = Estado(1, 2, 0, False, 30, frozenset({(3, 3)}))
        self.assertEqual(a, b)
        self.assertEqual(len({a, b}), 1)
        with self.assertRaises(FrozenInstanceError):
            a.fila = 5

    def test_movimientos_en_orden_y_con_su_desplazamiento(self):
        self.assertEqual(
            list(Movimiento),
            [Movimiento.ARRIBA, Movimiento.ABAJO, Movimiento.IZQUIERDA, Movimiento.DERECHA],
        )
        self.assertEqual(obtener_desplazamiento(Movimiento.ARRIBA), (-1, 0))
        self.assertEqual(obtener_desplazamiento(Movimiento.DERECHA), (0, 1))


if __name__ == "__main__":
    unittest.main()
