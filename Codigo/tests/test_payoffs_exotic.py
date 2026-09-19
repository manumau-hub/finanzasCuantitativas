"""
Tests para payoffs exóticos: digitales, Asian, Barrier.
"""
import unittest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Codigo.analytics.payoffs import (
    payoff_digital_call,
    payoff_digital_put,
    payoff_asset_or_nothing_call,
    payoff_asset_or_nothing_put,
    payoff_asian_call,
    payoff_asian_put,
    payoff_barrier_up_in_call,
    payoff_barrier_up_in_put,
    payoff_barrier_up_out_call,
    payoff_barrier_up_out_put,
    payoff_barrier_down_in_call,
    payoff_barrier_down_in_put,
    payoff_barrier_down_out_call,
    payoff_barrier_down_out_put,
    payoff_call,
    payoff_put,
)


class TestDigitalPayoffs(unittest.TestCase):
    """Tests para opciones digitales."""

    def test_digital_call_itm(self):
        self.assertEqual(payoff_digital_call(110, 100), 1.0)
        self.assertEqual(payoff_digital_call(110, 100, Q=10), 10.0)

    def test_digital_call_otm(self):
        self.assertEqual(payoff_digital_call(90, 100), 0.0)

    def test_digital_put_itm(self):
        self.assertEqual(payoff_digital_put(90, 100), 1.0)
        self.assertEqual(payoff_digital_put(90, 100, Q=5), 5.0)

    def test_digital_put_otm(self):
        self.assertEqual(payoff_digital_put(110, 100), 0.0)

    def test_asset_or_nothing_call(self):
        self.assertEqual(payoff_asset_or_nothing_call(110, 100), 110)
        self.assertEqual(payoff_asset_or_nothing_call(90, 100), 0.0)

    def test_asset_or_nothing_put(self):
        self.assertEqual(payoff_asset_or_nothing_put(90, 100), 90)
        self.assertEqual(payoff_asset_or_nothing_put(110, 100), 0.0)

    def test_digital_vectorized(self):
        S = np.array([95, 100, 105])
        result = payoff_digital_call(S, 100)
        np.testing.assert_array_equal(result, [0, 0, 1])


class TestAsianPayoffs(unittest.TestCase):
    """Tests para opciones Asian (media aritmética)."""

    def test_asian_call_itm(self):
        self.assertEqual(payoff_asian_call(105, 100), 5.0)

    def test_asian_call_otm(self):
        self.assertEqual(payoff_asian_call(95, 100), 0.0)

    def test_asian_put_itm(self):
        self.assertEqual(payoff_asian_put(95, 100), 5.0)

    def test_asian_put_otm(self):
        self.assertEqual(payoff_asian_put(105, 100), 0.0)


class TestBarrierPayoffs(unittest.TestCase):
    """Tests para opciones barrier."""

    def test_up_in_call_hit(self):
        # Barrier hit -> vanilla call
        p = payoff_barrier_up_in_call(110, 100, 120, barrier_hit=True)
        self.assertEqual(p, payoff_call(110, 100))

    def test_up_in_call_no_hit(self):
        p = payoff_barrier_up_in_call(110, 100, 120, barrier_hit=False)
        self.assertEqual(p, 0.0)

    def test_up_out_call_hit(self):
        # Barrier hit -> knock out, payoff 0
        p = payoff_barrier_up_out_call(110, 100, 120, barrier_hit=True)
        self.assertEqual(p, 0.0)

    def test_up_out_call_no_hit(self):
        p = payoff_barrier_up_out_call(110, 100, 120, barrier_hit=False)
        self.assertEqual(p, payoff_call(110, 100))

    def test_down_in_put_hit(self):
        p = payoff_barrier_down_in_put(90, 100, 80, barrier_hit=True)
        self.assertEqual(p, payoff_put(90, 100))

    def test_down_out_put_no_hit(self):
        p = payoff_barrier_down_out_put(90, 100, 80, barrier_hit=False)
        self.assertEqual(p, payoff_put(90, 100))

    def test_barrier_vectorized(self):
        S = np.array([95, 100, 105])
        hit = np.array([True, False, True])
        p = payoff_barrier_up_in_call(S, 100, 120, hit)
        expected = np.array([0, 0, 5])  # 95<100->0, 100 no hit->0, 105 hit and ITM->5
        np.testing.assert_array_equal(p, expected)


if __name__ == "__main__":
    unittest.main()
