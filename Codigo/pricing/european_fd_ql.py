# -*- coding: utf-8 -*-
"""
Precio de opción europea con diferencias finitas usando QuantLib.
Misma firma que opcion_europea_fd.
"""
import QuantLib as ql

from ._ql_common import _build_european_option


def opcion_europea_fd_ql(tipo, S, K, T, r, sigma, div, M=150):
    """
    Calcula el precio de una opción europea con diferencias finitas (QuantLib).

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S, K, T, r, sigma, div: estándar.
        M (int): Puntos de la grilla espacial (default 150).

    Retorna:
        float: Precio de la opción.
    """
    if T <= 0 or M < 2:
        raise ValueError("T debe ser positivo y M >= 2.")

    option, bsm_process = _build_european_option(tipo, S, K, T, r, sigma, div)

    # tGrid: pasos temporales según criterio de estabilidad
    t_grid = max(int(M * T * S / 3), 20)
    x_grid = M

    option.setPricingEngine(
        ql.FdBlackScholesVanillaEngine(bsm_process, t_grid, x_grid)
    )
    return float(option.NPV())
