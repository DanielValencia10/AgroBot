"""
Archivo:       tests/test_operadores.py
Objetivo:      Verificar problema/operadores.py, costos.py, ciclos.py y
               agrobot_problema.py usando mundos/Prueba1.txt como referencia (robot en
               (4,0), deposito en (0,2), avioneta en (0,6), cultivos en (4,3), (5,3) y
               (6,8)).
Responsabilidad:
    QUE VERIFICA:
        - Movimientos fuera de la cuadricula u hacia un obstaculo: no aplicables.
        - Deposito: el fertilizante vuelve a su capacidad maxima.
        - Cultivo seco pendiente: con fertilizante se trata (phi - 1 y sale de P); sin
          fertilizante no.
        - Avioneta: la primera vez el robot sube sin gastar combustible; montado, cada
          movimiento gasta una unidad; al llegar a 0 la avioneta queda agotada
          (e = falso) y no vuelve a subir.
        - Costos: 1 a pie, 1/2 en avioneta con combustible (incluido el paso que sube a
          la avioneta = 1 y el que gasta la ultima unidad = 1/2).
        - Ciclos: se descarta un sucesor que deja todo igual que un estado de la rama.
        - AgroBotProblema: estado inicial, prueba de meta y sucesores en el orden
          arriba, abajo, izquierda, derecha.
Importa de:
    - problema.*, modelo.*, archivos.lector_mundo (para cargar Prueba1.txt).
Ejecucion:     Desde la raiz, con el entorno activo:   python -m unittest tests.test_operadores
"""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from agrobot import constantes  # noqa: E402
from agrobot.archivos.lector_mundo import leer_mundo_desde_archivo  # noqa: E402
from agrobot.modelo.estado import Estado  # noqa: E402
from agrobot.modelo.movimiento import Movimiento  # noqa: E402
from agrobot.problema import ciclos, costos, operadores  # noqa: E402
from agrobot.problema.agrobot_problema import AgroBotProblema  # noqa: E402

ARRIBA, ABAJO = Movimiento.ARRIBA, Movimiento.ABAJO
IZQUIERDA, DERECHA = Movimiento.IZQUIERDA, Movimiento.DERECHA
PENDIENTES = frozenset({(4, 3), (5, 3), (6, 8)})


def estado(posicion, fertilizante=0, en_avioneta=False, combustible=30, pendientes=PENDIENTES):
    return Estado(posicion[0], posicion[1], fertilizante, en_avioneta, combustible, pendientes)


class PruebaConMundo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mundo = leer_mundo_desde_archivo(RAIZ / "mundos" / "Prueba1.txt")


class TestPrecondiciones(PruebaConMundo):
    def test_fuera_de_la_cuadricula(self):
        self.assertFalse(operadores.es_aplicable(self.mundo, estado((4, 0)), IZQUIERDA))
        self.assertFalse(operadores.es_aplicable(self.mundo, estado((9, 3)), ABAJO))

    def test_obstaculo(self):
        self.assertFalse(operadores.es_aplicable(self.mundo, estado((3, 0)), DERECHA))
        self.assertFalse(operadores.es_aplicable(self.mundo, estado((1, 0)), ARRIBA))

    def test_casilla_libre(self):
        self.assertTrue(operadores.es_aplicable(self.mundo, estado((4, 0)), ARRIBA))


class TestEfectos(PruebaConMundo):
    def test_deposito_recarga_al_maximo(self):
        despues = operadores.aplicar(self.mundo, estado((1, 2), fertilizante=0), ARRIBA)
        self.assertEqual(despues.posicion, (0, 2))
        self.assertEqual(despues.fertilizante, constantes.CAPACIDAD_FERTILIZANTE)

    def test_cultivo_con_fertilizante_se_trata(self):
        despues = operadores.aplicar(self.mundo, estado((4, 2), fertilizante=2), DERECHA)
        self.assertEqual(despues.posicion, (4, 3))
        self.assertEqual(despues.fertilizante, 1)
        self.assertEqual(despues.pendientes, frozenset({(5, 3), (6, 8)}))

    def test_cultivo_sin_fertilizante_no_se_trata(self):
        despues = operadores.aplicar(self.mundo, estado((4, 2), fertilizante=0), DERECHA)
        self.assertEqual(despues.fertilizante, 0)
        self.assertEqual(despues.pendientes, PENDIENTES)

    def test_sube_a_la_avioneta_sin_gastar_combustible(self):
        despues = operadores.aplicar(self.mundo, estado((1, 6)), ARRIBA)
        self.assertEqual(despues.posicion, (0, 6))
        self.assertTrue(despues.en_avioneta)
        self.assertEqual(despues.combustible, 30)

    def test_en_avioneta_cada_movimiento_gasta_una_unidad(self):
        despues = operadores.aplicar(self.mundo, estado((1, 6), en_avioneta=True, combustible=30), ABAJO)
        self.assertEqual(despues.combustible, 29)
        self.assertTrue(despues.en_avioneta)

    def test_al_llegar_a_cero_la_avioneta_queda_agotada(self):
        despues = operadores.aplicar(self.mundo, estado((1, 6), en_avioneta=True, combustible=1), ABAJO)
        self.assertEqual(despues.combustible, 0)
        self.assertFalse(despues.en_avioneta)

    def test_avioneta_agotada_no_vuelve_a_subir(self):
        despues = operadores.aplicar(self.mundo, estado((1, 6), combustible=0), ARRIBA)
        self.assertEqual(despues.posicion, (0, 6))
        self.assertFalse(despues.en_avioneta)

    def test_el_estado_original_no_cambia(self):
        antes = estado((4, 2), fertilizante=2)
        operadores.aplicar(self.mundo, antes, DERECHA)
        self.assertEqual(antes, estado((4, 2), fertilizante=2))


class TestCostos(unittest.TestCase):
    def test_a_pie_cuesta_1(self):
        self.assertEqual(costos.costo_de_movimiento(estado((4, 0)), ARRIBA), 1)

    def test_en_avioneta_cuesta_medio(self):
        self.assertEqual(costos.costo_de_movimiento(estado((4, 0), en_avioneta=True), ARRIBA), 0.5)

    def test_paso_que_sube_cuesta_1_y_el_que_gasta_la_ultima_unidad_cuesta_medio(self):
        self.assertEqual(costos.costo_de_movimiento(estado((1, 6), en_avioneta=False), ARRIBA), 1)
        self.assertEqual(
            costos.costo_de_movimiento(estado((1, 6), en_avioneta=True, combustible=1), ARRIBA), 0.5)

    def test_avioneta_agotada_cuesta_1(self):
        self.assertEqual(costos.costo_de_movimiento(estado((4, 0), combustible=0), ARRIBA), 1)


class TestCiclos(unittest.TestCase):
    def test_repetir_un_estado_de_la_rama_se_descarta(self):
        a = estado((4, 0))
        self.assertTrue(ciclos.es_repetido_en_rama(a, [a, estado((3, 0))]))

    def test_volver_a_una_casilla_con_algo_distinto_es_valido(self):
        # Vuelve al deposito, pero ahora con el fertilizante gastado: otro estado.
        en_el_deposito = estado((0, 2), fertilizante=2)
        de_vuelta = estado((0, 2), fertilizante=2, pendientes=PENDIENTES - {(4, 3)})
        self.assertFalse(ciclos.es_repetido_en_rama(de_vuelta, [en_el_deposito]))


class TestAgroBotProblema(PruebaConMundo):
    def setUp(self):
        self.problema = AgroBotProblema(self.mundo)

    def test_estado_inicial_y_meta(self):
        inicial = self.problema.estado_inicial()
        self.assertEqual(inicial.posicion, (4, 0))
        self.assertFalse(self.problema.es_meta(inicial))
        self.assertTrue(self.problema.es_meta(replace(inicial, pendientes=frozenset())))

    def test_sucesores_del_estado_inicial_en_orden(self):
        sucesores = self.problema.sucesores(self.problema.estado_inicial())
        self.assertEqual([m for m, _, _ in sucesores], [ARRIBA, ABAJO, DERECHA])
        self.assertEqual([e.posicion for _, e, _ in sucesores], [(3, 0), (5, 0), (4, 1)])
        self.assertEqual([c for _, _, c in sucesores], [1, 1, 1])

    def test_sucesores_descarta_estados_repetidos_de_la_rama(self):
        inicial = self.problema.estado_inicial()
        arriba = self.problema.sucesores(inicial)[0][1]
        de_vuelta = self.problema.sucesores(arriba, [inicial, arriba])
        self.assertNotIn(inicial.posicion, [e.posicion for _, e, _ in de_vuelta])


if __name__ == "__main__":
    unittest.main()
