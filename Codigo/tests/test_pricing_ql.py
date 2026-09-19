"""
Unit tests para los wrappers QuantLib (_ql).
Comparan precios con los modelos nativos.

Parámetros: S=100, K=100, T=1, r=0.05, sigma=0.25, div=0.0
"""
import unittest
import sys
from pathlib import Path

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
from Codigo.pricing import (
    opcion_europea_bs_ql,
    opcion_europea_bin_ql,
    opcion_europea_bin_c_ql,
    opcion_europea_mc_ql,
    opcion_europea_mc_fv_ql,
    opcion_europea_fd_ql,
    opcion_americana_bin_ql,
    opcion_americana_fd_ql,
    opcion_americana_bs_ql,
    opcion_americana_mc_ql,
    _QL_AVAILABLE,
)

S, K, T, r, sigma, div = 100.0, 100.0, 1.0, 0.05, 0.25, 0.0
PASOS = 1000
PASOS_MC = 2000  # Menos MC para tests más rápidos


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestEuropeanBSQL(unittest.TestCase):
    """Compara opcion_europea_bs_ql con opcion_europea_bs."""

    def test_matches_native_bs(self):
        p_native = opcion_europea_bs("C", S, K, T, r, sigma, div)
        p_ql = opcion_europea_bs_ql("C", S, K, T, r, sigma, div)
        self.assertAlmostEqual(p_native, p_ql, places=6)

    def test_put_matches_native(self):
        p_native = opcion_europea_bs("P", S, K, T, r, sigma, div)
        p_ql = opcion_europea_bs_ql("P", S, K, T, r, sigma, div)
        self.assertAlmostEqual(p_native, p_ql, places=6)


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestEuropeanBinomialQL(unittest.TestCase):
    """Compara opcion_europea_bin_ql con opcion_europea_bin."""

    def test_matches_native_binomial(self):
        p_native = opcion_europea_bin("C", S, K, T, r, sigma, div, PASOS)
        p_ql = opcion_europea_bin_ql("C", S, K, T, r, sigma, div, PASOS)
        self.assertAlmostEqual(p_native, p_ql, places=3)  # Pequeñas diferencias numéricas QL vs nuestro CRR


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestEuropeanBinomialClosedQL(unittest.TestCase):
    """Compara opcion_europea_bin_c_ql con opcion_europea_bin_c."""

    def test_matches_native_closed(self):
        p_native = opcion_europea_bin_c("C", S, K, T, r, sigma, div, PASOS)
        p_ql = opcion_europea_bin_c_ql("C", S, K, T, r, sigma, div, PASOS)
        self.assertAlmostEqual(p_native, p_ql, places=3)  # QL usa árbol, nosotros fórmula cerrada


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestEuropeanMCQL(unittest.TestCase):
    """Compara opcion_europea_mc_ql con opcion_europea_mc (tolerancia MC)."""

    def test_close_to_native_mc(self):
        p_native = opcion_europea_mc("C", S, K, T, r, sigma, div, PASOS_MC)
        p_ql = opcion_europea_mc_ql("C", S, K, T, r, sigma, div, PASOS_MC)
        p_bs = opcion_europea_bs("C", S, K, T, r, sigma, div)
        # Ambos deben estar cerca de BS (tolerancia MC ~1-2%)
        self.assertAlmostEqual(p_native, p_bs, delta=2.0)
        self.assertAlmostEqual(p_ql, p_bs, delta=2.0)


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestEuropeanMCFVQL(unittest.TestCase):
    """Compara opcion_europea_mc_fv_ql con opcion_europea_mc_fv."""

    def test_close_to_native_mc_fv(self):
        p_native = opcion_europea_mc_fv("C", S, K, T, r, sigma, div, PASOS_MC)
        p_ql = opcion_europea_mc_fv_ql("C", S, K, T, r, sigma, div, PASOS_MC)
        p_bs = opcion_europea_bs("C", S, K, T, r, sigma, div)
        self.assertAlmostEqual(p_native, p_bs, delta=1.5)
        self.assertAlmostEqual(p_ql, p_bs, delta=1.5)


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestEuropeanFDQL(unittest.TestCase):
    """Compara opcion_europea_fd_ql con opcion_europea_fd."""

    def test_close_to_native_fd(self):
        p_native = opcion_europea_fd("C", S, K, T, r, sigma, div, M=150)
        p_ql = opcion_europea_fd_ql("C", S, K, T, r, sigma, div, M=150)
        p_bs = opcion_europea_bs("C", S, K, T, r, sigma, div)
        self.assertAlmostEqual(p_native, p_bs, delta=0.5)
        self.assertAlmostEqual(p_ql, p_bs, delta=0.5)


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestAmericanBinomialQL(unittest.TestCase):
    """Compara opcion_americana_bin_ql con opcion_americana_bin."""

    def test_matches_native_binomial(self):
        p_native = opcion_americana_bin("P", S, K, T, r, sigma, div, PASOS)
        p_ql = opcion_americana_bin_ql("P", S, K, T, r, sigma, div, PASOS)
        self.assertAlmostEqual(p_native, p_ql, places=3)  # Pequeñas diferencias en árbol americano


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestAmericanFDQL(unittest.TestCase):
    """Compara opcion_americana_fd_ql con opcion_americana_fd."""

    def test_close_to_native_fd(self):
        p_native = opcion_americana_fd("P", S, K, T, r, sigma, div, M=150)
        p_ql = opcion_americana_fd_ql("P", S, K, T, r, sigma, div, M=150)
        self.assertAlmostEqual(p_native, p_ql, delta=0.5)  # Grillas pueden diferir


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestAmericanBSQL(unittest.TestCase):
    """opcion_americana_bs_ql vs opcion_americana_bs (BAW casero)."""

    def test_ql_matches_native_baw(self):
        p_native = opcion_americana_bs("P", S, K, T, r, sigma, div)
        p_ql = opcion_americana_bs_ql("P", S, K, T, r, sigma, div)
        self.assertAlmostEqual(p_native, p_ql, delta=0.5)  # BAW casero vs QL

    def test_baw_put_positive(self):
        p = opcion_americana_bs_ql("P", S, K, T, r, sigma, div)
        self.assertGreater(p, 0)
        self.assertLess(p, K)


@unittest.skipIf(not _QL_AVAILABLE, "QuantLib no instalado")
class TestAmericanMCQL(unittest.TestCase):
    """opcion_americana_mc_ql usa Longstaff-Schwartz (LSM)."""

    def test_lsm_close_to_binomial(self):
        p_mc = opcion_americana_mc_ql("P", S, K, T, r, sigma, div, PASOS_MC)
        p_bin = opcion_americana_bin("P", S, K, T, r, sigma, div, PASOS)
        self.assertAlmostEqual(p_mc, p_bin, delta=2.0)  # MC LSM vs binomial

    def test_lsm_put_positive(self):
        p = opcion_americana_mc_ql("P", S, K, T, r, sigma, div, PASOS_MC)
        self.assertGreater(p, 0)
        self.assertLess(p, K)


if __name__ == "__main__":
    unittest.main()
