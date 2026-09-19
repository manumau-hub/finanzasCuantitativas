"""
Unit tests para los 7 modelos de pricing de opciones.

Parámetros de prueba:
    S=100, K=100, T=1, r=0.05, sigma=0.25, div=0.0
"""
import unittest
import sys
from pathlib import Path

# Asegurar que el proyecto está en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Codigo.pricing import (
    opcion_europea_bs,
    opcion_europea_bin,
    opcion_europea_bin_c,
    opcion_europea_mc,
    opcion_europea_mc_fv,
    opcion_europea_fd,
    opcion_americana_bin,
    opcion_americana_fd,
    opcion_americana_bs,
    opcion_americana_mc,
)

# Parámetros estándar para todos los tests
S, K, T, r, sigma, div = 100.0, 100.0, 1.0, 0.05, 0.25, 0.0
PASOS = 1000
PASOS_MC = 50000


class TestEuropeanBS(unittest.TestCase):
    """Tests para opcion_europea_bs (Black-Scholes)."""

    def test_call_price_positive(self):
        price = opcion_europea_bs("C", S, K, T, r, sigma, div)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_europea_bs("P", S, K, T, r, sigma, div)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_put_call_parity(self):
        c = opcion_europea_bs("C", S, K, T, r, sigma, div)
        p = opcion_europea_bs("P", S, K, T, r, sigma, div)
        import math
        fwd = S * math.exp(-div * T) - K * math.exp(-r * T)
        self.assertAlmostEqual(c - p, fwd, places=6)

    def test_invalid_tipo_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_bs("X", S, K, T, r, sigma, div)

    def test_invalid_sigma_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_bs("C", S, K, T, r, 0, div)

    def test_invalid_T_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_bs("C", S, K, 0, r, sigma, div)


class TestEuropeanBinomial(unittest.TestCase):
    """Tests para opcion_europea_bin (binomial CRR)."""

    def test_call_price_positive(self):
        price = opcion_europea_bin("C", S, K, T, r, sigma, div, PASOS)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_europea_bin("P", S, K, T, r, sigma, div, PASOS)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_converges_to_bs(self):
        c_bin = opcion_europea_bin("C", S, K, T, r, sigma, div, PASOS)
        c_bs = opcion_europea_bs("C", S, K, T, r, sigma, div)
        self.assertAlmostEqual(c_bin, c_bs, delta=0.5)

    def test_invalid_pasos_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_bin("C", S, K, T, r, sigma, div, 0)


class TestEuropeanBinomialClosed(unittest.TestCase):
    """Tests para opcion_europea_bin_c (binomial forma cerrada)."""

    def test_call_price_positive(self):
        price = opcion_europea_bin_c("C", S, K, T, r, sigma, div, PASOS)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_europea_bin_c("P", S, K, T, r, sigma, div, PASOS)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_matches_binomial_tree(self):
        c_closed = opcion_europea_bin_c("C", S, K, T, r, sigma, div, PASOS)
        c_tree = opcion_europea_bin("C", S, K, T, r, sigma, div, PASOS)
        self.assertAlmostEqual(c_closed, c_tree, places=8)

    def test_invalid_pasos_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_bin_c("C", S, K, T, r, sigma, div, 0)


class TestEuropeanMC(unittest.TestCase):
    """Tests para opcion_europea_mc (Monte Carlo)."""

    def test_call_price_positive(self):
        price = opcion_europea_mc("C", S, K, T, r, sigma, div, PASOS_MC)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_europea_mc("P", S, K, T, r, sigma, div, PASOS_MC)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_converges_to_bs(self):
        import random
        random.seed(42)
        import numpy as np
        np.random.seed(42)
        c_mc = opcion_europea_mc("C", S, K, T, r, sigma, div, PASOS_MC)
        c_bs = opcion_europea_bs("C", S, K, T, r, sigma, div)
        self.assertAlmostEqual(c_mc, c_bs, delta=1.0)

    def test_invalid_pasos_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_mc("C", S, K, T, r, sigma, div, 0)


class TestEuropeanMCFV(unittest.TestCase):
    """Tests para opcion_europea_mc_fv (Monte Carlo antithetic variates)."""

    def test_call_price_positive(self):
        price = opcion_europea_mc_fv("C", S, K, T, r, sigma, div, PASOS_MC)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_europea_mc_fv("P", S, K, T, r, sigma, div, PASOS_MC)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_converges_to_bs(self):
        import numpy as np
        np.random.seed(42)
        c_mc = opcion_europea_mc_fv("C", S, K, T, r, sigma, div, PASOS_MC)
        c_bs = opcion_europea_bs("C", S, K, T, r, sigma, div)
        self.assertAlmostEqual(c_mc, c_bs, delta=1.0)

    def test_invalid_pasos_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_mc_fv("C", S, K, T, r, sigma, div, 0)


class TestEuropeanFD(unittest.TestCase):
    """Tests para opcion_europea_fd (diferencias finitas implícitas)."""

    def test_call_price_positive(self):
        price = opcion_europea_fd("C", S, K, T, r, sigma, div)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_europea_fd("P", S, K, T, r, sigma, div)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_converges_to_bs(self):
        c_fd = opcion_europea_fd("C", S, K, T, r, sigma, div, M=200)
        c_bs = opcion_europea_bs("C", S, K, T, r, sigma, div)
        self.assertAlmostEqual(c_fd, c_bs, delta=0.5)

    def test_invalid_T_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_fd("C", S, K, 0, r, sigma, div)

    def test_invalid_M_raises(self):
        with self.assertRaises(ValueError):
            opcion_europea_fd("C", S, K, T, r, sigma, div, M=1)


class TestAmericanBinomial(unittest.TestCase):
    """Tests para opcion_americana_bin (binomial americano)."""

    def test_call_price_positive(self):
        price = opcion_americana_bin("C", S, K, T, r, sigma, div, PASOS)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_americana_bin("P", S, K, T, r, sigma, div, PASOS)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_american_geq_european_call(self):
        c_ame = opcion_americana_bin("C", S, K, T, r, sigma, div, PASOS)
        c_eur = opcion_europea_bin("C", S, K, T, r, sigma, div, PASOS)
        self.assertGreaterEqual(c_ame, c_eur)

    def test_american_geq_european_put(self):
        p_ame = opcion_americana_bin("P", S, K, T, r, sigma, div, PASOS)
        p_eur = opcion_europea_bin("P", S, K, T, r, sigma, div, PASOS)
        self.assertGreaterEqual(p_ame, p_eur)

    def test_invalid_pasos_raises(self):
        with self.assertRaises(ValueError):
            opcion_americana_bin("C", S, K, T, r, sigma, div, 0)


class TestAmericanFD(unittest.TestCase):
    """Tests para opcion_americana_fd (diferencias finitas americano)."""

    def test_call_price_positive(self):
        price = opcion_americana_fd("C", S, K, T, r, sigma, div)
        self.assertGreater(price, 0)
        self.assertLess(price, S)

    def test_put_price_positive(self):
        price = opcion_americana_fd("P", S, K, T, r, sigma, div)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_american_geq_european_put(self):
        p_ame = opcion_americana_fd("P", S, K, T, r, sigma, div, M=200)
        p_eur = opcion_europea_fd("P", S, K, T, r, sigma, div, M=200)
        self.assertGreaterEqual(p_ame, p_eur)

    def test_invalid_T_raises(self):
        with self.assertRaises(ValueError):
            opcion_americana_fd("C", S, K, 0, r, sigma, div)

    def test_invalid_M_raises(self):
        with self.assertRaises(ValueError):
            opcion_americana_fd("C", S, K, T, r, sigma, div, M=1)


class TestAmericanBS(unittest.TestCase):
    """Tests para opcion_americana_bs (Barone-Adesi-Whaley)."""

    def test_put_price_positive(self):
        price = opcion_americana_bs("P", S, K, T, r, sigma, div)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_baw_close_to_binomial(self):
        p_baw = opcion_americana_bs("P", S, K, T, r, sigma, div)
        p_bin = opcion_americana_bin("P", S, K, T, r, sigma, div, PASOS)
        self.assertAlmostEqual(p_baw, p_bin, delta=0.5)

    def test_american_geq_european_put(self):
        p_ame = opcion_americana_bs("P", S, K, T, r, sigma, div)
        p_eur = opcion_europea_bs("P", S, K, T, r, sigma, div)
        self.assertGreaterEqual(p_ame, p_eur)


class TestAmericanMC(unittest.TestCase):
    """Tests para opcion_americana_mc (Longstaff-Schwartz LSM)."""

    def test_put_price_positive(self):
        import numpy as np
        np.random.seed(42)
        price = opcion_americana_mc("P", S, K, T, r, sigma, div, 5000)
        self.assertGreater(price, 0)
        self.assertLess(price, K)

    def test_lsm_close_to_binomial(self):
        import numpy as np
        np.random.seed(42)
        p_mc = opcion_americana_mc("P", S, K, T, r, sigma, div, 5000)
        p_bin = opcion_americana_bin("P", S, K, T, r, sigma, div, PASOS)
        self.assertAlmostEqual(p_mc, p_bin, delta=2.0)  # Tolerancia MC

    def test_invalid_pasos_raises(self):
        with self.assertRaises(ValueError):
            opcion_americana_mc("P", S, K, T, r, sigma, div, 0)


if __name__ == "__main__":
    unittest.main()
