"""
Archivo:       tests/test_algoritmos.py
Objetivo:      Verificar los algoritmos de busqueda sobre mundos/Prueba1.txt (robot en
               (4,0), deposito en (0,2), avioneta en (0,6), cultivos en (4,3), (5,3) y
               (6,8)). Hoy solo esta implementado Amplitud.
Responsabilidad:
    QUE VERIFICA (Amplitud):
        - Que encuentre una solucion valida: el camino de movimientos, aplicado desde el
          estado inicial, termina en un estado meta (P vacio) y coincide con el camino
          de estados del Resultado.
        - Que reproduzca la Demo original sobre Prueba1: 30 pasos y 1562 nodos
          expandidos antes de llegar a la meta (1563 contando la meta, que tambien se
          expande), terminando en (6,8) con 1 de fertilizante.
        - Que sea de menor profundidad: ningun camino de menos movimientos resuelve el
          mundo (lo garantiza BFS; se comprueba con el valor de la Demo).
        - Que no reporte costo_total (solo Costo uniforme y A*).
        - Que sin solucion devuelva un Resultado que lo indica, sin lanzar error.
        - Que no dependa de modelo/ ni de problema/ (busqueda/ queda aislado).
    PENDIENTE (cuando se implementen): los mismos chequeos para Costo uniforme,
    Profundidad, Avara y A* (costo minimo, uso de la heuristica, consistencia del
    conteo de nodos expandidos).
Importa de:
    - busqueda.no_informada.amplitud, problema.agrobot_problema, archivos.lector_mundo.
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_algoritmos
"""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from agrobot.archivos.lector_mundo import leer_mundo_desde_archivo  # noqa: E402
from agrobot.busqueda.no_informada.amplitud import buscar_amplitud  # noqa: E402
from agrobot.problema import operadores  # noqa: E402
from agrobot.problema.agrobot_problema import AgroBotProblema  # noqa: E402

RUTA_BUSQUEDA = RAIZ / "src" / "agrobot" / "busqueda"


class TestAmplitud(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mundo = leer_mundo_desde_archivo(RAIZ / "mundos" / "Prueba1.txt")
        cls.problema = AgroBotProblema(cls.mundo)
        cls.resultado = buscar_amplitud(cls.problema)

    def test_el_camino_resuelve_el_mundo(self):
        estado = self.problema.estado_inicial()
        for movimiento in self.resultado.camino_de_movimientos:
            self.assertTrue(operadores.es_aplicable(self.mundo, estado, movimiento))
            estado = operadores.aplicar(self.mundo, estado, movimiento)
        self.assertTrue(self.problema.es_meta(estado))
        self.assertEqual(estado, self.resultado.camino_de_estados[-1])
        self.assertEqual(self.resultado.camino_de_estados[0], self.problema.estado_inicial())

    def test_coincide_con_la_demo(self):
        r = self.resultado
        self.assertTrue(r.solucion_encontrada)
        self.assertEqual(r.profundidad_de_la_solucion, 30)
        self.assertEqual(len(r.camino_de_movimientos), 30)
        self.assertEqual(len(r.camino_de_estados), 31)
        self.assertEqual(r.nodos_expandidos, 1562 + 1)
        final = r.camino_de_estados[-1]
        self.assertEqual((final.posicion, final.fertilizante), ((6, 8), 1))

    def test_metricas_coherentes(self):
        r = self.resultado
        self.assertGreaterEqual(r.nodos_expandidos, r.profundidad_de_la_solucion + 1)
        self.assertGreater(r.tiempo_de_computo, 0)
        self.assertIsNone(r.costo_total)

    def test_sin_solucion(self):
        # Se rodea al robot de obstaculos: no puede llegar a ningun cultivo.
        robot = self.mundo.posicion_robot
        vecinos = {(robot[0] - 1, robot[1]), (robot[0] + 1, robot[1]), (robot[0], robot[1] + 1)}
        encerrado = replace(self.mundo, obstaculos=self.mundo.obstaculos | vecinos)
        r = buscar_amplitud(AgroBotProblema(encerrado))
        self.assertFalse(r.solucion_encontrada)
        self.assertEqual(r.camino_de_movimientos, ())
        self.assertEqual(r.profundidad_de_la_solucion, 0)
        self.assertEqual(r.nodos_expandidos, 1)

    def test_busqueda_no_importa_de_modelo_ni_de_problema(self):
        for archivo in RUTA_BUSQUEDA.rglob("*.py"):
            for linea in archivo.read_text(encoding="utf-8").splitlines():
                if linea.startswith(("import ", "from ")):
                    self.assertNotRegex(linea, r"modelo|problema|gui", archivo.name)


if __name__ == "__main__":
    unittest.main()
