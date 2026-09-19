# -*- coding: utf-8 -*-
"""
Precio de opción americana con Monte Carlo (Longstaff-Schwartz) usando QuantLib.

MCAmericanEngine implementa el método LSM de Longstaff-Schwartz (2001).
Misma firma que opcion_americana_bin (con pasos = caminos MC).
"""
import QuantLib as ql

from ._ql_common import _build_american_option


def opcion_americana_mc_ql(tipo, S, K, T, r, sigma, div, pasos):
    """
    Calcula el precio de una opción americana con Monte Carlo Longstaff-Schwartz (QuantLib).

    Usa regresión por mínimos cuadrados para estimar la frontera de ejercicio óptimo.
    Es el engine que invoca la calculadora QL cuando se selecciona MC + Americana.

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S, K, T, r, sigma, div: estándar.
        pasos (int): Número de caminos de Monte Carlo.

    Retorna:
        float: Precio de la opción.
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    option, bsm_process = _build_american_option(tipo, S, K, T, r, sigma, div)
    option.setPricingEngine(
        ql.MCAmericanEngine(
            bsm_process,
            "PseudoRandom",
            timeSteps=20,
            requiredSamples=pasos,
        )
    )
    return float(option.NPV())
