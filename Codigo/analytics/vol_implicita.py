# -*- coding: utf-8 -*-
"""Volatilidad implícita usando modelos de pricing y rootfinders."""

import math
import numpy as np

from Codigo.pricing.european_bs import opcion_europea_bs
from Codigo.pricing.european_binomial import opcion_europea_bin
from Codigo.pricing.european_binomial_closed import opcion_europea_bin_c
from Codigo.pricing.american_binomial import opcion_americana_bin


def samesign(a, b):
    return a * b > 0


def bisect(func, low, high, iters=100):
    """Find root of continuous function where f(low) and f(high) have opposite signs."""
    assert not samesign(func(low), func(high))
    for i in range(iters):
        midpoint = (low + high) / 2.0
        if samesign(func(low), func(midpoint)):
            low = midpoint
        else:
            high = midpoint
    return midpoint


def impvolfunc_bs(tipo, S, K, T, r, precio_mercado, div):
    func = lambda sigma: (opcion_europea_bs(tipo, S, K, T, r, sigma, div) - precio_mercado)
    return bisect(func, 0.0001, 6, 100)


def impvolfunc_bin(tipo, S, K, T, r, precio_mercado, div, pasos=1000):
    func = lambda sigma: (opcion_americana_bin(tipo, S, K, T, r, sigma, div, pasos) - precio_mercado)
    return bisect(func, 0.0001, 6, 100)
