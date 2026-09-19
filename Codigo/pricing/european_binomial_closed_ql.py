# -*- coding: utf-8 -*-
"""
Precio de opción europea binomial (QuantLib).
QL no tiene fórmula cerrada explícita; el árbol binomial converge al mismo valor.
Misma firma que opcion_europea_bin_c.
"""
import QuantLib as ql

from ._ql_common import _build_european_option


def opcion_europea_bin_c_ql(tipo, S, K, T, r, sigma, div, pasos):
    """
    Calcula el precio de una opción europea con árbol binomial CRR (QuantLib).
    Equivalente numérico a la fórmula cerrada opcion_europea_bin_c.

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S, K, T, r, sigma, div: estándar.
        pasos (int): Número de pasos del árbol.

    Retorna:
        float: Precio de la opción.
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    option, bsm_process = _build_european_option(tipo, S, K, T, r, sigma, div)
    option.setPricingEngine(ql.BinomialVanillaEngine(bsm_process, "crr", pasos))
    return float(option.NPV())
