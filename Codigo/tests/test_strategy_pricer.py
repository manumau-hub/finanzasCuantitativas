"""
Tests para pricing de estrategias por composición.
"""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Codigo.pricing import (
    opcion_europea_bs,
    precio_estrategia,
    precio_estrategia_nombre,
    ESTRATEGIA_PIERNAS,
)

S, K, T, r, sigma, div = 100.0, 100.0, 1.0, 0.05, 0.25, 0.0


class TestPrecioEstrategia(unittest.TestCase):
    """Tests para precio_estrategia con piernas explícitas."""

    def test_bull_call_spread_manual(self):
        piernas = [("C", 90, 1), ("C", 110, -1)]
        p = precio_estrategia(piernas, S, T, r, sigma, div)
        p_manual = opcion_europea_bs("C", S, 90, T, r, sigma, div) - opcion_europea_bs(
            "C", S, 110, T, r, sigma, div
        )
        self.assertAlmostEqual(p, p_manual, places=8)

    def test_straddle_manual(self):
        piernas = [("C", K, 1), ("P", K, 1)]
        p = precio_estrategia(piernas, S, T, r, sigma, div)
        p_manual = opcion_europea_bs("C", S, K, T, r, sigma, div) + opcion_europea_bs(
            "P", S, K, T, r, sigma, div
        )
        self.assertAlmostEqual(p, p_manual, places=8)


class TestPrecioEstrategiaNombre(unittest.TestCase):
    """Tests para precio_estrategia_nombre."""

    def test_bull_call_spread(self):
        p = precio_estrategia_nombre(
            "bull_call_spread", S, T, r, sigma, div, K1=90, K2=110
        )
        p_manual = opcion_europea_bs("C", S, 90, T, r, sigma, div) - opcion_europea_bs(
            "C", S, 110, T, r, sigma, div
        )
        self.assertAlmostEqual(p, p_manual, places=8)
        self.assertGreater(p, 0)
        self.assertLess(p, 20)  # Max payoff Bull CS = K2 - K1 = 20

    def test_straddle(self):
        p = precio_estrategia_nombre("straddle", S, T, r, sigma, div, K=100)
        p_manual = opcion_europea_bs("C", S, K, T, r, sigma, div) + opcion_europea_bs(
            "P", S, K, T, r, sigma, div
        )
        self.assertAlmostEqual(p, p_manual, places=8)

    def test_strangle(self):
        p = precio_estrategia_nombre("strangle", S, T, r, sigma, div, K1=110, K2=90)
        p_manual = opcion_europea_bs("C", S, 110, T, r, sigma, div) + opcion_europea_bs(
            "P", S, 90, T, r, sigma, div
        )
        self.assertAlmostEqual(p, p_manual, places=8)

    def test_estrategia_invalida_raise(self):
        with self.assertRaises(ValueError):
            precio_estrategia_nombre("no_existe", S, T, r, sigma, div, K=100)


if __name__ == "__main__":
    unittest.main()
