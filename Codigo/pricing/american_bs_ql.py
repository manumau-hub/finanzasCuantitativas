# -*- coding: utf-8 -*-
"""
Precio de opción americana con aproximación Barone-Adesi-Whaley (BAW) usando QuantLib.

No existe fórmula cerrada tipo Black-Scholes para americanas; BAW es la aproximación
analítica estándar. Misma firma que opcion_europea_bs (sin pasos).
"""
import QuantLib as ql

from ._ql_common import _build_american_option


def opcion_americana_bs_ql(tipo, S, K, T, r, sigma, div):
    """
    Calcula el precio de una opción americana con aproximación Barone-Adesi-Whaley (QuantLib).

    La aproximación BAW es la estándar para americanas cuando se selecciona
    "Analítico (BS/BAW)" en la calculadora QL.

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S, K, T, r, sigma, div: estándar.

    Retorna:
        float: Precio de la opción.
    """
    option, bsm_process = _build_american_option(tipo, S, K, T, r, sigma, div)
    option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process))
    return float(option.NPV())
