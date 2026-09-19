# -*- coding: utf-8 -*-
"""
Griegas para opciones americanas usando BAW (QuantLib) + diferenciación numérica.

Delta, Gamma, Vega, Theta. BAW no expone griegas analíticas; se usan diferencias finitas.
"""
import QuantLib as ql

from ._ql_common import _build_american_option


def _price_baw(tipo, S, K, T, r, sigma, div):
    """Precio BAW."""
    option, bsm_process = _build_american_option(tipo, S, K, T, r, sigma, div)
    option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bsm_process))
    return float(option.NPV())


def gregas_americana_baw_ql(tipo, S, K, T, r, sigma, div, h_S=0.01, h_sigma=0.001, h_T=1/365):
    """
    Griegas para opción americana (BAW + diferencias finitas).

    Parámetros:
        tipo: "C" o "P"
        S, K, T, r, sigma, div: estándar
        h_S, h_sigma, h_T: bump para dif. numérica

    Retorna:
        dict con delta, gamma, vega, theta
    """
    if sigma <= 0 or T <= 0:
        return {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}

    p0 = _price_baw(tipo, S, K, T, r, sigma, div)

    # Delta: (P(S+h)-P(S-h))/(2h)
    h_s = max(S * h_S, 0.1)
    p_up = _price_baw(tipo, S + h_s, K, T, r, sigma, div)
    p_dn = _price_baw(tipo, S - h_s, K, T, r, sigma, div)
    delta = (p_up - p_dn) / (2 * h_s)

    # Gamma: (P(S+h)-2P(S)+P(S-h))/h^2
    gamma = (p_up - 2 * p0 + p_dn) / (h_s * h_s) if h_s > 0 else 0.0

    # Vega: (P(sigma+h)-P(sigma-h))/(2h) — por 1% de vol
    sigma_safe = max(sigma, 0.01)
    h_v = max(sigma_safe * h_sigma, 0.0001)
    p_vol_up = _price_baw(tipo, S, K, T, r, sigma + h_v, div)
    p_vol_dn = _price_baw(tipo, S, K, T, r, max(sigma - h_v, 0.001), div)
    vega = (p_vol_up - p_vol_dn) / (2 * h_v)  # por unidad de sigma (1.0 = 100%)

    # Theta: (P(T-h)-P(T+h))/(2h) — decay por año
    T_safe = max(T, 1/365)
    h_t = min(h_T, T_safe / 2)
    p_t_up = _price_baw(tipo, S, K, T + h_t, r, sigma, div)
    p_t_dn = _price_baw(tipo, S, K, max(T - h_t, 1/365), r, sigma, div)
    theta = (p_t_dn - p_t_up) / (2 * h_t)

    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta}
