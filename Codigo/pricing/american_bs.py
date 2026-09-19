# -*- coding: utf-8 -*-
"""
Precio de opción americana con aproximación Barone-Adesi-Whaley (BAW).

Aproximación analítica estándar para americanas. No es Black-Scholes exacto
(no existe fórmula cerrada para americanas), sino la corrección BAW sobre el
precio europeo. Implementación casera sin QuantLib.

Misma firma que opcion_europea_bs (sin pasos).
"""
import math
from scipy.stats import norm

from .european_bs import opcion_europea_bs


def _baw_call(S, K, T, r, div, sigma):
    """
    Aproximación BAW para call americana.
    Si b >= r (sin dividendos o div bajo), la call americana = europea.
    """
    b = r - div  # cost of carry
    if b >= r:
        return opcion_europea_bs("C", S, K, T, r, sigma, div)

    Sk = _critical_price_call(K, T, r, b, sigma)
    N = 2 * b / (sigma ** 2)
    k = 2 * r / (sigma ** 2 * (1 - math.exp(-r * T)))
    sqrt_T = math.sqrt(T)
    d1 = (math.log(Sk / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    Q2 = (-(N - 1) + math.sqrt((N - 1) ** 2 + 4 * k)) / 2
    a2 = (Sk / Q2) * (1 - math.exp((b - r) * T) * norm.cdf(d1))

    if S < Sk:
        return opcion_europea_bs("C", S, K, T, r, sigma, div) + a2 * (S / Sk) ** Q2
    return S - K


def _baw_put(S, K, T, r, div, sigma):
    """Aproximación BAW para put americana."""
    b = r - div
    Sk = _critical_price_put(K, T, r, b, sigma)
    N = 2 * b / (sigma ** 2)
    k = 2 * r / (sigma ** 2 * (1 - math.exp(-r * T)))
    sqrt_T = math.sqrt(T)
    d1 = (math.log(Sk / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    Q1 = (-(N - 1) - math.sqrt((N - 1) ** 2 + 4 * k)) / 2
    a1 = -(Sk / Q1) * (1 - math.exp((b - r) * T) * norm.cdf(-d1))

    if S > Sk:
        return opcion_europea_bs("P", S, K, T, r, sigma, div) + a1 * (S / Sk) ** Q1
    return K - S


def _critical_price_call(K, T, r, b, sigma, tol=0.001, max_iter=100):
    """Precio crítico S* para call americana (Newton)."""
    N = 2 * b / (sigma ** 2)
    m = 2 * r / (sigma ** 2)
    q2u = (-(N - 1) + math.sqrt((N - 1) ** 2 + 4 * m)) / 2
    su = K / (1 - 1 / q2u)
    h2 = -(b * T + 2 * sigma * math.sqrt(T)) * K / (su - K)
    Si = K + (su - K) * (1 - math.exp(h2))

    k = 2 * r / (sigma ** 2 * (1 - math.exp(-r * T)))
    sqrt_T = math.sqrt(T)
    Q2 = (-(N - 1) + math.sqrt((N - 1) ** 2 + 4 * k)) / 2

    for _ in range(max_iter):
        d1 = (math.log(Si / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
        LHS = Si - K
        RHS = opcion_europea_bs("C", Si, K, T, r, sigma, r - b) + (
            1 - math.exp((b - r) * T) * norm.cdf(d1)
        ) * Si / Q2
        bi = math.exp((b - r) * T) * norm.cdf(d1) * (1 - 1 / Q2) + (
            1 - math.exp((b - r) * T) * norm.pdf(d1) / (sigma * sqrt_T)
        ) / Q2

        if abs(LHS - RHS) / K < tol:
            return Si
        Si = (K + RHS - bi * Si) / (1 - bi)
    return Si


def _critical_price_put(K, T, r, b, sigma, tol=0.001, max_iter=100):
    """Precio crítico S* para put americana (Newton)."""
    N = 2 * b / (sigma ** 2)
    m = 2 * r / (sigma ** 2)
    q1u = (-(N - 1) - math.sqrt((N - 1) ** 2 + 4 * m)) / 2
    su = K / (1 - 1 / q1u)
    h1 = (b * T - 2 * sigma * math.sqrt(T)) * K / (K - su)
    Si = su + (K - su) * math.exp(h1)

    k = 2 * r / (sigma ** 2 * (1 - math.exp(-r * T)))
    sqrt_T = math.sqrt(T)
    Q1 = (-(N - 1) - math.sqrt((N - 1) ** 2 + 4 * k)) / 2

    for _ in range(max_iter):
        d1 = (math.log(Si / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
        LHS = K - Si
        RHS = opcion_europea_bs("P", Si, K, T, r, sigma, r - b) - (
            1 - math.exp((b - r) * T) * norm.cdf(-d1)
        ) * Si / Q1
        bi = -math.exp((b - r) * T) * norm.cdf(-d1) * (1 - 1 / Q1) - (
            1 + math.exp((b - r) * T) * norm.pdf(-d1) / (sigma * sqrt_T)
        ) / Q1

        if abs(LHS - RHS) / K < tol:
            return Si
        Si = (K - RHS + bi * Si) / (1 + bi)
    return Si


def opcion_americana_bs(tipo, S, K, T, r, sigma, div):
    """
    Calcula el precio de una opción americana con aproximación Barone-Adesi-Whaley.

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S, K, T, r, sigma, div: estándar.

    Retorna:
        float: Precio de la opción.
    """
    if sigma <= 0 or T <= 0:
        raise ValueError("sigma y T deben ser positivos.")
    if tipo not in ("C", "P"):
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")

    if tipo == "C":
        return _baw_call(S, K, T, r, div, sigma)
    return _baw_put(S, K, T, r, div, sigma)
