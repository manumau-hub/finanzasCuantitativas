# -*- coding: utf-8 -*-
"""
Precio de opción europea con Black-Scholes usando QuantLib.
Misma firma que opcion_europea_bs.
"""
import QuantLib as ql

from ._ql_common import _build_european_option


def opcion_europea_bs_ql(tipo, S, K, T, r, sigma, div):
    """
    Calcula el precio de una opción europea usando Black-Scholes (QuantLib).

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S (float): Precio spot del activo.
        K (float): Strike.
        T (float): Tiempo al vencimiento en años.
        r (float): Tasa libre de riesgo (anualizada).
        sigma (float): Volatilidad (anualizada).
        div (float): Tasa de dividendos continuos (anualizada).

    Retorna:
        float: Precio de la opción.
    """
    option, bsm_process = _build_european_option(tipo, S, K, T, r, sigma, div)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    return float(option.NPV())
