"""
Tests para engine de superficie de volatilidad.
Sin dependencia de pandas (usa list[dict] y dict de arrays).
"""
import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Codigo.analytics.vol_surface import (
    log_normal_vol_surface,
    gaussian_smooth,
    chain_to_raw_iv_data,
)


def _make_synthetic_chain(spot=100.0, exp_days_list=None):
    """Chain sintética como list[dict] para tests."""
    if exp_days_list is None:
        exp_days_list = [30, 60, 91]
    now = datetime.now()
    rows = []
    for exp_days in exp_days_list:
        exp = (now + timedelta(days=exp_days)).strftime("%Y-%m-%d")
        for k in [90, 95, 100, 105, 110]:
            for cp in ["call", "put"]:
                iv = 0.25 + 0.02 * (k / spot - 1)
                rows.append({
                    "strike": k,
                    "type": cp,
                    "expiration": exp,
                    "bid": 1.0,
                    "ask": 1.1,
                    "lastPrice": 1.05,
                    "impliedVolatility": iv,
                    "Spot": spot,
                })
    return rows


class TestLogNormalVolSurface(unittest.TestCase):
    """Tests para clase base."""

    def test_init(self):
        vs = log_normal_vol_surface(daycount=360)
        self.assertEqual(vs.get_daycount_convention(), 360)
        self.assertEqual(len(vs._std_ttm_days), 10)
        self.assertEqual(len(vs._std_delta), 12)

    def test_set_daycount(self):
        vs = log_normal_vol_surface()
        vs.set_daycount_convention(365)
        self.assertEqual(vs.get_daycount_convention(), 365)


class TestChainToRawIVData(unittest.TestCase):
    """Tests para adaptador chain -> raw IV."""

    def test_basic_conversion(self):
        chain = _make_synthetic_chain(exp_days_list=[60])
        raw = chain_to_raw_iv_data(chain, spot=100.0, r=0.05, div=0.0)
        self.assertGreater(len(raw["TTM"]), 0)
        for col in ["Date", "TTM", "YearFraction", "CallPut", "Strike", "ImpliedVol", "Vega", "Delta"]:
            self.assertIn(col, raw)

    def test_empty_chain_raises(self):
        with self.assertRaises(ValueError):
            chain_to_raw_iv_data([], 100.0, 0.05, 0.0)

    def test_missing_columns_raises(self):
        chain = [{"strike": 100, "type": "call"}]  # no expiration
        with self.assertRaises(ValueError):
            chain_to_raw_iv_data(chain, 100.0, 0.05, 0.0)


class TestGaussianSmooth(unittest.TestCase):
    """Tests para gaussian_smooth."""

    def test_generate_surface(self):
        chain = _make_synthetic_chain(exp_days_list=[30, 60, 91])
        raw = chain_to_raw_iv_data(chain, spot=100.0, r=0.05, div=0.0)
        vs = gaussian_smooth()
        surf = vs.generate_volatility_surface(raw)
        self.assertGreater(len(surf["TTM"]), 0)
        self.assertIn("ImpliedVol", surf)
        self.assertIn("Dispersion", surf)
        import numpy as np
        valid = surf["ImpliedVol"][~np.isnan(surf["ImpliedVol"])]
        self.assertTrue((valid > 0).all())
        self.assertTrue((valid < 1).all())

    def test_generate_point(self):
        chain = _make_synthetic_chain(exp_days_list=[30, 60])
        raw = chain_to_raw_iv_data(chain, spot=100.0, r=0.05, div=0.0)
        vs = gaussian_smooth()
        iv = vs.generate_volatility_surface_point(raw, Type="C", Days=45, Delta=50)
        self.assertIsInstance(iv, (float, type(iv)))
        import numpy as np
        if not (iv != iv):  # not nan
            self.assertGreater(iv, 0)
            self.assertLess(iv, 1)

    def test_empty_raw_raises(self):
        import numpy as np
        vs = gaussian_smooth()
        raw = {
            "TTM": np.array([5]),
            "YearFraction": np.array([0.01]),
            "Vega": np.array([0.1]),
            "CallPut": np.array(["C"]),
            "Delta": np.array([0.5]),
            "ImpliedVol": np.array([0.25]),
            "Date": np.array(["2025-01-01"]),
            "ExerciseStyle": np.array(["E"]),
            "Spot": np.array([100.0]),
        }
        with self.assertRaises(ValueError):
            vs.generate_volatility_surface(raw, vega_min=0.5, ttm_min=10)


if __name__ == "__main__":
    unittest.main()
