# -*- coding: utf-8 -*-
"""
Griegas analíticas para opciones europeas Black-Scholes.

Incluye las griegas de QuantLib AnalyticEuropeanEngine:
Delta, Gamma, Vega, Rho, Theta, ThetaPerDay, DividendRho, StrikeSensitivity, Elasticity.
"""
import math
from scipy.stats import norm


def _d1_d2(S, K, T, r, sigma, div):
    if sigma <= 0 or T <= 0:
        raise ValueError("sigma y T deben ser positivos.")
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r - div + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    return d1, d2


def delta_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """Delta: dV/dS. Call: exp(-div*T)*N(d1). Put: exp(-div*T)*(N(d1)-1)."""
    d1, _ = _d1_d2(S, K, T, r, sigma, div)
    nd1 = norm.cdf(d1)
    if tipo == "C":
        return math.exp(-div * T) * nd1
    return math.exp(-div * T) * (nd1 - 1)


def gamma_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """Gamma: d²V/dS². Igual para call y put."""
    d1, _ = _d1_d2(S, K, T, r, sigma, div)
    nd1_pdf = norm.pdf(d1)
    return math.exp(-div * T) * nd1_pdf / (S * sigma * math.sqrt(T))


def vega_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """Vega: dV/d(sigma). Igual para call y put."""
    d1, _ = _d1_d2(S, K, T, r, sigma, div)
    nd1_pdf = norm.pdf(d1)
    return S * math.exp(-div * T) * nd1_pdf * math.sqrt(T)


def rho_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """Rho: dV/dr. Call: K*T*exp(-r*T)*N(d2). Put: -K*T*exp(-r*T)*N(-d2)."""
    _, d2 = _d1_d2(S, K, T, r, sigma, div)
    if tipo == "C":
        return K * T * math.exp(-r * T) * norm.cdf(d2)
    return -K * T * math.exp(-r * T) * norm.cdf(-d2)


def theta_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """Theta: dV/dT (por año). Negativo = decay temporal."""
    d1, d2 = _d1_d2(S, K, T, r, sigma, div)
    nd1_pdf = norm.pdf(d1)
    sqrt_T = math.sqrt(T)
    term1 = -S * math.exp(-div * T) * nd1_pdf * sigma / (2 * sqrt_T)
    if tipo == "C":
        term2 = -r * K * math.exp(-r * T) * norm.cdf(d2)
        term3 = div * S * math.exp(-div * T) * norm.cdf(d1)
    else:
        term2 = r * K * math.exp(-r * T) * norm.cdf(-d2)
        term3 = -div * S * math.exp(-div * T) * norm.cdf(-d1)
    return term1 + term2 + term3


def theta_per_day_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """Theta por día: dV/dT / 365 (decay temporal diario)."""
    return theta_bs(tipo, S, K, T, r, sigma, div) / 365.0


def dividend_rho_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """DividendRho: dV/d(div). Call: -T*S*exp(-div*T)*N(d1). Put: T*S*exp(-div*T)*N(-d1)."""
    d1, _ = _d1_d2(S, K, T, r, sigma, div)
    nd1 = norm.cdf(d1)
    nd1_put = norm.cdf(-d1)
    factor = T * S * math.exp(-div * T)
    if tipo == "C":
        return -factor * nd1
    return factor * nd1_put


def strike_sensitivity_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """StrikeSensitivity: dV/dK. Call: -exp(-r*T)*N(d2). Put: exp(-r*T)*N(-d2)."""
    _, d2 = _d1_d2(S, K, T, r, sigma, div)
    factor = math.exp(-r * T)
    if tipo == "C":
        return -factor * norm.cdf(d2)
    return factor * norm.cdf(-d2)


def elasticity_bs(tipo: str, S: float, K: float, T: float, r: float, sigma: float, div: float) -> float:
    """Elasticity: S * delta / V. Cambio porcentual del precio ante 1% cambio en S."""
    from Codigo.pricing.european_bs import opcion_europea_bs  # evita circular import

    V = opcion_europea_bs(tipo, S, K, T, r, sigma, div)
    if V <= 0:
        return float("nan")
    d = delta_bs(tipo, S, K, T, r, sigma, div)
    return S * d / V
