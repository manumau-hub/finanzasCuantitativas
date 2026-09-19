# -*- coding: utf-8 -*-
"""
Precio de opción europea con Monte Carlo usando QuantLib.
Misma firma que opcion_europea_mc.
"""
import QuantLib as ql

from ._ql_common import _build_european_option


def opcion_europea_mc_ql(tipo, S, K, T, r, sigma, div, pasos):
    """
    Calcula el precio de una opción europea con Monte Carlo (QuantLib).

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S, K, T, r, sigma, div: estándar.
        pasos (int): Número de caminos de Monte Carlo.

    Retorna:
        float: Precio de la opción.
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    option, bsm_process = _build_european_option(tipo, S, K, T, r, sigma, div)
    option.setPricingEngine(
        ql.MCEuropeanEngine(
            bsm_process,
            "PseudoRandom",
            timeSteps=20,
            requiredSamples=pasos,
        )
    )
    return float(option.NPV())
