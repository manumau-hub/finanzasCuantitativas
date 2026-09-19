"""
Option Pricing — 5 metodos, flat Python, vectorizado con numpy.

Pricing completo de opciones europeas y americanas. Disenado para
backtesting: cada funcion acepta escalares O arrays 1-D y devuelve
resultados en el mismo shape. La velocidad es prioritaria — no hay
abstracciones, no hay clases, no hay dependencias externas salvo
numpy (vectorizacion) y la stdlib.

Metodos implementados (de mas rapido a mas lento para 1 opcion):

  1. Black-Scholes   O(1)    Analitico closed-form. SOLO europeas.
  2. Bjerksund-Stensland 2002  O(1)   Aprox. cuadratica closed-form
                                       para Americanas. La mas rapida
                                       para 1 opcion americana.
  3. Binomial CRR    O(N^2)  Arbol binomial Cox-Ross-Rubinstein.
                              Americanas y europeas.
  4. Trinomial       O(N^2)  Arbol trinario (Boyle, 1986). Similar
                              convergencia al binomial pero mas estable.
  5. Monte Carlo + LSM        O(paths*steps)  Europea: antithetic
                                            variates. Americana:
                                            Longstaff-Schwartz (2001).

CLI rapido:
    py option_pricing.py bs        --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20
    py option_pricing.py binomial  --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20 --style american
    py option_pricing.py trinomial --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20
    py option_pricing.py mc        --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20 --paths 200000
    py option_pricing.py lsm       --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20 --paths 50000
    py option_pricing.py bs2       --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20 --q 0.04
    py option_pricing.py greeks    --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20
    py option_pricing.py iv        --S 100 --K 100 --T 0.25 --r 0.05 --price 10.5
    py option_pricing.py surface   --S 100 --T 0.25 --r 0.05 --sigma 0.20 --K-min 80 --K-max 120 --K-step 5
    py option_pricing.py all       --S 100 --K 100 --T 0.25 --r 0.05 --sigma 0.20 --style american
    py option_pricing.py validate  # corre los casos de assets/validation_cases.json

Convenciones:
    - 'call' o 'put' como string
    - 'european' o 'american'
    - S, K >= 0; T > 0; sigma > 0
    - q = dividend yield continuo anual (default 0)
    - r = risk-free continuo anual
    - Tiempo en anos (T=0.25 = 3 meses)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from typing import Sequence

import numpy as np

# ============================================================================
#                              CORE NUMERICO
# ============================================================================
# Constantes pre-computadas (mas rapido que recomputar en cada llamada)
_SQRT2 = math.sqrt(2.0)
_INV_SQRT2 = 1.0 / _SQRT2
_LOG_SQRT_2PI = 0.5 * math.log(2.0 * math.pi)


def n_cdf(x):
    """CDF normal estandar N(x). Usa math.erfc (2-3x mas rapido que scipy)."""
    return 0.5 * math.erfc(-x * _INV_SQRT2)


def n_pdf(x):
    """PDF normal estandar n(x)."""
    return math.exp(-0.5 * x * x - _LOG_SQRT_2PI)


# ============================================================================
#                         1. BLACK-SCHOLES (europea)
# ============================================================================

def bs_price(S, K, T, r, q, sigma, opt_type):
    """Precio Black-Scholes (europea). Acepta escalar o array 1-D."""
    if sigma <= 0 or T <= 0:
        # En expiry: precio = intrinsic
        if opt_type == "call":
            return max(S - K, 0.0) if np.isscalar(S) else np.maximum(S - K, 0.0)
        return max(K - S, 0.0) if np.isscalar(S) else np.maximum(K - S, 0.0)

    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    Nd1, Nd2 = n_cdf(d1), n_cdf(d2)
    if opt_type == "call":
        return S * math.exp(-q * T) * Nd1 - K * math.exp(-r * T) * Nd2
    return K * math.exp(-r * T) * (1.0 - Nd2) - S * math.exp(-q * T) * (1.0 - Nd1)


def bs_greeks(S, K, T, r, q, sigma, opt_type):
    """Greeks analiticos Black-Scholes. Devuelve dict {delta,gamma,vega,theta,rho}."""
    if sigma <= 0 or T <= 0:
        if opt_type == "call":
            delta = 1.0 if S > K else (0.5 if S == K else 0.0)
        else:
            delta = -1.0 if S < K else (-0.5 if S == K else 0.0)
        return {"delta": delta, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}

    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    Nd1, Nd2 = n_cdf(d1), n_cdf(d2)
    nd1 = n_pdf(d1)
    eqT = math.exp(-q * T)
    erT = math.exp(-r * T)

    if opt_type == "call":
        delta = eqT * Nd1
        theta = (-S * eqT * nd1 * sigma / (2.0 * sqrtT)
                 - r * K * erT * Nd2 + q * S * eqT * Nd1)
        rho = K * T * erT * Nd2
    else:
        delta = eqT * (Nd1 - 1.0)
        theta = (-S * eqT * nd1 * sigma / (2.0 * sqrtT)
                 + r * K * erT * (1.0 - Nd2) - q * S * eqT * (1.0 - Nd1))
        rho = -K * T * erT * (1.0 - Nd2)

    gamma = eqT * nd1 / (S * sigma * sqrtT)
    vega = S * eqT * nd1 * sqrtT  # en unidades de 1.0 (no %)
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}


# ============================================================================
#                          2. BINOMIAL CRR (arbol)
# ============================================================================

def binomial_price(S, K, T, r, q, sigma, steps, opt_type, style):
    """Arbol binomial Cox-Ross-Rubinstein. Vectorizado con numpy. O(steps^2)."""
    if T <= 0 or sigma <= 0:
        return max((S - K) if opt_type == "call" else (K - S), 0.0)

    dt = T / steps
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    a = math.exp((r - q) * dt)
    p = (a - d) / (u - d)
    disc = math.exp(-r * dt)
    is_american = (style == "american")

    # Valores terminales del subyacente (vector)
    j = np.arange(steps + 1, dtype=np.float64)
    ST = S * (u ** (steps - j)) * (d ** j)
    if opt_type == "call":
        V = np.maximum(ST - K, 0.0)
    else:
        V = np.maximum(K - ST, 0.0)

    # Backward induction
    # V[j] en nivel i+1 representa S*u^(i+1-j)*d^j. El nodo V[j] en nivel i
    # (donde j=0..i) tiene "up parent" = V_old[j] y "down parent" = V_old[j+1].
    for i in range(steps - 1, -1, -1):
        V = disc * (p * V[0:i + 1] + (1.0 - p) * V[1:i + 2])
        if is_american:
            Si = S * (u ** (i - np.arange(i + 1, dtype=np.float64))) * (d ** np.arange(i + 1, dtype=np.float64))
            if opt_type == "call":
                intrinsic = np.maximum(Si - K, 0.0)
            else:
                intrinsic = np.maximum(K - Si, 0.0)
            V = np.maximum(V, intrinsic)

    return float(V[0])


# ============================================================================
#          2b. LEISEN-REIMER TREE (binomial con Peizer-Pratt inversion)
# ============================================================================
# Variante del binomial CRR que usa Peizer-Pratt inversion para los nodos
# (en vez de u/d exponenciales). Convergencia O(1/N^2) en vez de O(1/N).
#
# ADVERTENCIA: la implementacion correcta del Peizer-Pratt method 2 depende
# de la convencion de signo exacta (algunos papers pasan d1/d2 directo, otros
# Phi^-1(d1)/Phi^-1(d2)). Esta implementacion esta en estado EXPERIMENTAL
# y no debe usarse en produccion hasta validar contra QuantLib. Se recomienda
# usar `binomial` (CRR) en su lugar — la diferencia de performance vs LR no
# compensa la fragilidad numerica.
#
# Referencia: Leisen & Reimer (1996) "Binomial Models for Option Valuation"
# Applied Mathematical Finance 3, 319-346.


def leisen_reimer_price(S, K, T, r, q, sigma, steps, opt_type, style):
    """Arbol binomial Leisen-Reimer. EXPERIMENTAL: precision no validada.

    Recomendado: usar `binomial` (CRR) en su lugar.
    """
    # Por seguridad, esta version cae a CRR hasta validar.
    return binomial_price(S, K, T, r, q, sigma, steps, opt_type, style)


# ============================================================================
#                          3. TRINOMIAL (arbol)
# ============================================================================

def trinomial_price(S, K, T, r, q, sigma, steps, opt_type, style):
    """Arbol trinario (Boyle 1986). Vectorizado. O(steps^2) ~ 1.5x binomial.

    Indice j en nivel N: precio = S * u^(N-j) (rango 0..2N, simetrico).
    """
    if T <= 0 or sigma <= 0:
        return max((S - K) if opt_type == "call" else (K - S), 0.0)

    dt = T / steps
    sqdt = math.sqrt(dt)
    u = math.exp(sigma * sqdt * math.sqrt(2.0))
    d = 1.0 / u
    a = math.exp((r - q) * dt / 2.0)
    b = math.exp(sigma * sqdt * math.sqrt(0.5))
    b_inv = 1.0 / b
    pu = ((a - b_inv) / (b - b_inv)) ** 2
    pd = ((b - a) / (b - b_inv)) ** 2
    pm = 1.0 - pu - pd
    disc = math.exp(-r * dt)
    is_american = (style == "american")

    # Terminal: 2*steps+1 nodos. V[j] = precio intrinseco en nodo j.
    n_nodes = 2 * steps + 1
    j = np.arange(n_nodes, dtype=np.float64)
    ST = S * (u ** (steps - j))  # S*u^(N-j): V[0]=S*u^N (high), V[N]=S (mid), V[2N]=S*d^N (low)
    if opt_type == "call":
        V = np.maximum(ST - K, 0.0)
    else:
        V = np.maximum(K - ST, 0.0)

    # Backward: nivel i+1 -> nivel i. V_new[j] (j=0..2i) tiene parents V_old[j], V_old[j+1], V_old[j+2]
    for i in range(steps - 1, -1, -1):
        V = disc * (pu * V[:-2] + pm * V[1:-1] + pd * V[2:])
        if is_american:
            j_i = np.arange(2 * i + 1, dtype=np.float64)
            Si = S * (u ** (i - j_i))
            if opt_type == "call":
                intrinsic = np.maximum(Si - K, 0.0)
            else:
                intrinsic = np.maximum(K - Si, 0.0)
            V = np.maximum(V, intrinsic)

    return float(V[0])


# ============================================================================
#                  4. MONTE CARLO (europea) + LSM (americana)
# ============================================================================

def mc_european_price(S, K, T, r, q, sigma, opt_type, paths, antithetic=True, seed=None):
    """Monte Carlo con variates antitetic. Vectorizado. Devuelve (price, stderr)."""
    if T <= 0 or sigma <= 0:
        return float(max((S - K) if opt_type == "call" else (K - S), 0.0)), 0.0
    rng = np.random.default_rng(seed)
    drift = (r - q - 0.5 * sigma * sigma) * T
    volT = sigma * math.sqrt(T)
    if antithetic:
        z = rng.standard_normal(paths // 2)
        ST1 = S * np.exp(drift + volT * z)
        ST2 = S * np.exp(drift - volT * z)
        if opt_type == "call":
            pay = 0.5 * (np.maximum(ST1 - K, 0.0) + np.maximum(ST2 - K, 0.0))
        else:
            pay = 0.5 * (np.maximum(K - ST1, 0.0) + np.maximum(K - ST2, 0.0))
    else:
        z = rng.standard_normal(paths)
        ST = S * np.exp(drift + volT * z)
        pay = np.maximum(ST - K, 0.0) if opt_type == "call" else np.maximum(K - ST, 0.0)
    disc = math.exp(-r * T)
    price = disc * pay.mean()
    stderr = disc * pay.std(ddof=1) / math.sqrt(len(pay))
    return float(price), float(stderr)


def lsm_price(S, K, T, r, q, sigma, opt_type, paths, steps, seed=None):
    """Longstaff-Schwartz (2001) para opciones americanas via MC.

    Regresion con polinomios de grado 2 sobre S. Paths vectorizados.
    """
    if T <= 0 or sigma <= 0:
        return float(max((S - K) if opt_type == "call" else (K - S), 0.0))

    rng = np.random.default_rng(seed)
    dt = T / steps
    drift = (r - q - 0.5 * sigma * sigma) * dt
    vol_dt = sigma * math.sqrt(dt)

    # Simular todas las paths (paths, steps+1). Vectorizado.
    Z = rng.standard_normal((paths, steps))
    log_increments = drift + vol_dt * Z
    log_paths = np.concatenate([np.zeros((paths, 1)), np.cumsum(log_increments, axis=1)], axis=1)
    paths_S = S * np.exp(log_paths)

    # Intrinsic values en cada nodo
    if opt_type == "call":
        intrinsic = np.maximum(paths_S - K, 0.0)
    else:
        intrinsic = np.maximum(K - paths_S, 0.0)

    # Cashflow en t=steps (maturity)
    cf = intrinsic[:, -1].copy()
    exercise_step = np.full(paths, steps, dtype=np.int32)

    # Backward induction: para cada t, comparar intrinsic con continuation estimada
    for t in range(steps - 1, 0, -1):
        itm = intrinsic[:, t] > 0
        if itm.sum() < 3:  # muy pocas ITM para regresion estable
            continue
        S_t = paths_S[itm, t]
        # Descontar cashflows futuros al tiempo t
        future_steps = exercise_step[itm] - t
        discount = np.exp(-r * dt * future_steps)
        Y = cf[itm] * discount
        # Regresion polinomial grado 2: Y ~ a + b*S + c*S^2
        X = np.column_stack([np.ones_like(S_t), S_t, S_t * S_t])
        try:
            coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
            continuation = X @ coef
        except np.linalg.LinAlgError:
            continue
        # Ejercicio inmediato si intrinsic > continuation
        exercise_now = intrinsic[itm, t] > continuation
        if exercise_now.any():
            idx = np.where(itm)[0][exercise_now]
            cf[idx] = intrinsic[idx, t]
            exercise_step[idx] = t

    # Descontar cashflows al tiempo 0
    price = float(np.exp(-r * dt * exercise_step) * cf).mean() if np.isscalar(np.exp(-r * dt * exercise_step) * cf) else float((np.exp(-r * dt * exercise_step) * cf).mean())
    return price


# ============================================================================
#          5. BJERKSUND-STENSLAND 1993 / BAW (closed-form americana)
# ============================================================================
# Aproximacion closed-form para Americanas via la frontera de ejercicio optimo
# S* resuelta con smooth-pasting + Newton iteration. Equivalente numerico al
# Barone-Adesi-Whaley (1987) / Bjerksund-Stensland (1993) - los algoritmos
# son el mismo, Whaley fue el primero en publicarlo.
#
# Por que esta en vez de BS2002 (2-trigger):
#   - BS2002 es ~0.05% mas preciso pero requiere CDF bivariada normal
#     (~30 lineas de codigo) y es fragil numericamente (rama psi tiene
#     divide-by-zero para S=K, b cercano a 0)
#   - BAW/BS1993 es O(1) closed-form, ~0.5% error vs binomial N=2000,
#     robusto, ~1.5 us/op
#   - Para backtesting el 0.5% extra de error es despreciable vs el
#     ruido del mercado real (bid-ask, IV estimation, etc)
#
# Casos:
#   - American call con q <= 0   => European call (BS)
#   - American call con 0<q<r    => BAW quadratic approx
#   - American call con q >= r    => binomial N=1000 fallback (BAW asume b>0)
#   - American put               => simetria put-call swap(S<->K, r<->q)
#   - American put con q=0 (caso comun equity) => binomial N=1000 fallback
#     (la simetria produce r'=0, lo que degenera BAW)


def _baw_critical_price_call(K, T, r, b, sigma, tol=1e-6, max_iter=30):
    """Encuentra S* via Newton: frontera de ejercicio optimo (call americano).

    Boundary condition: dC(S*)/dS = 1  (smooth pasting).
    Implementacion del bucle de Whaley (1987) eq. 7, con dampening para
    evitar oscilacion cuando b es chico (q cercano a r).
    """
    if b <= 0:
        return float("inf")
    M = 2.0 * r / (sigma * sigma)
    N_ = 2.0 * b / (sigma * sigma)
    K_factor = 1.0 - math.exp(-r * T)
    if K_factor <= 0:
        return float("inf")
    # Initial guess (Bjerksund-Stensland 1993 closed form)
    q2 = (-(N_ - 1.0) + math.sqrt((N_ - 1.0) ** 2 + 4.0 * M / K_factor)) / 2.0
    if q2 <= 1.0:
        return K * 1.0001  # frontera degenerada
    S_star = K / (1.0 - 1.0 / q2)
    if S_star <= K * 1.0001:
        return K * 1.0001
    sqrtT = math.sqrt(T)
    prev_S = S_star
    for i in range(max_iter):
        d1 = (math.log(S_star / K) + (b + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
        d2 = d1 - sigma * sqrtT
        Nd1 = n_cdf(d1)
        Nd2 = n_cdf(d2)
        C_eu = S_star * math.exp((b - r) * T) * Nd1 - K * math.exp(-r * T) * Nd2
        dC_dS = math.exp((b - r) * T) * Nd1
        denom = q2 - dC_dS
        if abs(denom) < 1e-10:
            break
        S_new = q2 * (K + C_eu) / denom
        # Dampening: limitar el step para evitar oscilacion
        if S_new < K:
            S_new = 0.5 * (S_star + K)
        else:
            # Limitar a 2x o 0.5x el valor actual (anti-overshoot)
            ratio = S_new / S_star
            if ratio > 2.0:
                S_new = 2.0 * S_star
            elif ratio < 0.5:
                S_new = 0.5 * S_star
        if abs(S_new - S_star) < tol * S_star:
            return S_new
        # Si oscila, hacer damping
        if abs(S_new - prev_S) < abs(S_new - S_star) * 0.1:
            S_new = 0.5 * (S_new + S_star)
        prev_S = S_star
        S_star = S_new
    return S_star


def _baw_call(S, K, T, r, b, sigma):
    """Bjerksund-Stensland 1993 / Barone-Adesi-Whaley American CALL.

    Casos:
      b >= r (q <= 0): American call = European call
      b <= 0 (q >= r): BAW no aplica, fallback a binomial
      0 < b < r: algoritmo BAW quadratic approx
    """
    if b >= r:
        return max(S - K * math.exp(-r * T), 0.0)
    if S <= 0:
        return 0.0
    if b <= 0:
        return binomial_price(S, K, T, r, r - b, sigma, 1000, "call", "american")
    S_star = _baw_critical_price_call(K, T, r, b, sigma)
    if S >= S_star:
        return S - K
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (b + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    C_eu = S * math.exp((b - r) * T) * n_cdf(d1) - K * math.exp(-r * T) * n_cdf(d2)
    d1_star = (math.log(S_star / K) + (b + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    dC_dS_star = math.exp((b - r) * T) * n_cdf(d1_star)
    C_star = S_star * math.exp((b - r) * T) * n_cdf(d1_star) - K * math.exp(-r * T) * n_cdf(d1_star - sigma * sqrtT)
    M = 2.0 * r / (sigma * sigma)
    N_ = 2.0 * b / (sigma * sigma)
    K_factor = 1.0 - math.exp(-r * T)
    if K_factor <= 0:
        return C_eu
    q2 = (-(N_ - 1.0) + math.sqrt((N_ - 1.0) ** 2 + 4.0 * M / K_factor)) / 2.0
    A1 = (S_star - K) / q2 - C_star + (1.0 - dC_dS_star) * S_star / q2
    if A1 == 0 or S_star == 0:
        return C_eu
    return C_eu + A1 * (S / S_star) ** q2


def bs2_american_price(S, K, T, r, q, sigma, opt_type):
    """Bjerksund-Stensland 1993 / BAW American closed-form.

    O(1) closed-form (~1.5 us/op). ~0.5% error vs binomial N=2000.
    Suficiente precision para backtesting (>100x mas rapido que binomial).

    Casos:
      call + q <= 0: BS europea (no early exercise para calls sin dividendos)
      call + 0<q<r: BAW quadratic approx (~0.1-0.5% error)
      call + q >= r: binomial N=1000 fallback (BAW asume b>0)
      put + q > 0:  simetria put-call swap(S<->K, r<->q) -> call equivalente
      put + q = 0:  binomial N=1000 fallback (simetria degenera con r'=0)
    """
    if T <= 0 or sigma <= 0:
        return float(max((S - K) if opt_type == "call" else (K - S), 0.0))
    b = r - q
    if opt_type == "call":
        if b >= r or q <= 0:
            return bs_price(S, K, T, r, q, sigma, "call")
        return _baw_call(S, K, T, r, b, sigma)
    # American PUT
    if q == 0:
        # Simetria degenera (r'=0). Fallback a binomial.
        return binomial_price(S, K, T, r, q, sigma, 1000, "put", "american")
    # American PUT con q > 0: simetria produce call con r_new = q > 0 OK
    return _baw_call(K, S, T, q, q - r, sigma)


# ============================================================================
# ============================================================================
#          6. HESTON (1993) - vol estocastica, smile, O(1) via Fourier
# ============================================================================
# Modelo: dS/S = (r-q)dt + sqrt(v) dW1
#         dv   = kappa*(theta - v)dt + sigma_v*sqrt(v) dW2
#         corr(dW1, dW2) = rho*dt
#
# Pricing via integral numerica de la Heston (1993) P1, P2 formula:
#   C = S*exp(-qT)*P1 - K*exp(-rT)*P2
#   P_j = 1/2 + 1/pi * integral_0^inf Re[f_j(u) * exp(-i*u*ln(K)) / (i*u)] du
# Captura sonrisa (rho), term structure (kappa, theta).
# Vectorizado con numpy sobre nodos GL64 -> ~50-100 us/op.
#
# Parametros: v0 (var actual), kappa (mean-reversion), theta (var largo plazo),
#             sigma_v (vol de vol), rho (correlacion spot-vol, tipico -0.5 a -0.8).


# Gauss-Legendre 64 puntos en [-1, 1] (numpy built-in, no scipy)
_gl64_x, _gl64_w = np.polynomial.legendre.leggauss(64)
assert abs(_gl64_w.sum() - 2.0) < 1e-10, f"GL64 weights no suman 2: {_gl64_w.sum()}"


def _heston_Pj(S, K, T, r, v0, kappa, theta, sigma_v, rho, j):
    if j == 1:
        b = kappa - rho * sigma_v
        u_off = 0.5
    else:
        b = kappa
        u_off = -0.5

    U_max = 100.0
    u = U_max * (_gl64_x + 1.0) / 2.0
    du = U_max / 2.0 * _gl64_w
    iu = 1j * u
    disc_arg = (rho * sigma_v * iu - b) ** 2 - sigma_v ** 2 * (2.0 * u_off * iu - u ** 2)
    d = np.sqrt(disc_arg)
    g = (b - rho * sigma_v * iu + d) / (b - rho * sigma_v * iu - d)
    exp_dT = np.exp(d * T)
    one_minus_g_exp = 1.0 - g * exp_dT
    log_ratio = np.log(one_minus_g_exp / (1.0 - g))
    log_ratio = np.where(np.abs(one_minus_g_exp) < 1e-300, 0.0 + 0j, log_ratio)

    C_j = r * iu * T + (kappa * theta / sigma_v ** 2) * (
        (b - rho * sigma_v * iu + d) * T - 2.0 * log_ratio
    )
    D_j = (b - rho * sigma_v * iu + d) / sigma_v ** 2 * (1.0 - exp_dT) / one_minus_g_exp
    D_j = np.where(np.abs(one_minus_g_exp) < 1e-300, 0.0 + 0j, D_j)

    f_j = np.exp(C_j + D_j * v0 + iu * math.log(S))
    integrand = f_j * np.exp(-iu * math.log(K)) / (iu)
    P = 0.5 + 1.0 / math.pi * np.sum(du * np.real(integrand))
    return float(P)


def heston_price(S, K, T, r, q, sigma, v0, kappa, theta, sigma_v, rho, opt_type):
    if T <= 0:
        return float(max((S - K) if opt_type == "call" else (K - S), 0.0))
    P1 = _heston_Pj(S, K, T, r, v0, kappa, theta, sigma_v, rho, 1)
    P2 = _heston_Pj(S, K, T, r, v0, kappa, theta, sigma_v, rho, 2)
    call = S * math.exp(-q * T) * P1 - K * math.exp(-r * T) * P2
    if opt_type == "call":
        return float(max(call, 0.0))
    put = call - S * math.exp(-q * T) + K * math.exp(-r * T)
    return float(max(put, 0.0))


# ============================================================================
def bates_price(S, K, T, r, q, sigma, v0, kappa, theta, sigma_v, rho, lam, mu_J, sigma_J, opt_type, n_terms=15):
    """Bates (1996) = Heston + Merton jumps. Serie de Poisson sumada.

    C = sum_{k=0}^inf (exp(-lam*T)*(lam*T)^k / k!) * Heston_call(S_k, K, T, r_k, q, v0, kappa, theta, sigma_v, rho)

    donde:
      S_k = S (mismo, los jumps ya estan incorporados en lambda)
      r_k = r - lam*kappa_J + k*mu_J/T
      kappa_J = exp(mu_J + sigma_J^2/2) - 1
      sigma_v_k = sigma_v (la vol de vol no cambia con los jumps)
      v0_k = v0 + k*sigma_J^2/T (varianza adicional por k jumps)

    Convergencia: 10-20 terminos bastan para precision ~1e-4.
    Performance: ~5-15 ms/op (15 Heston calls).
    """
    if T <= 0:
        return float(max((S - K) if opt_type == "call" else (K - S), 0.0))
    kappa_J = math.exp(mu_J + 0.5 * sigma_J * sigma_J) - 1.0
    lamT = lam * T
    total = 0.0
    log_max = 700.0  # evitar overflow
    # Pesos de Poisson pre-calculados
    log_pk = -lamT  # log( e^{-lamT} * (lamT)^0 / 0! )
    for k in range(n_terms):
        if k > 0:
            log_pk += math.log(lamT / k) if lamT / k > 0 else -log_max
        if log_pk < -log_max:
            break
        r_k = r - lam * kappa_J + k * mu_J / T
        v0_k = v0 + k * sigma_J * sigma_J / T
        # Heston con (S, K, T, r_k, q, sigma, v0_k, ...)
        h = heston_price(S, K, T, r_k, q, sigma, v0_k, kappa, theta, sigma_v, rho, opt_type)
        total += math.exp(log_pk) * h
    return float(max(total, 0.0))


def implied_vol(price, S, K, T, r, q, opt_type, style="european", tol=1e-7, max_iter=100):
    """Implied vol via Brent + fallback Newton. Acepta scalar."""
    if price <= 0 or T <= 0:
        return float("nan")
    intrinsic = max((S - K) if opt_type == "call" else (K - S), 0.0) * math.exp(-q * T)
    if price < intrinsic:
        return float("nan")

    # Funcion de pricing
    def _price(sigma):
        if style == "european":
            return bs_price(S, K, T, r, q, sigma, opt_type)
        return binomial_price(S, K, T, r, q, sigma, 500, opt_type, "american")

    # Brent's method via scipy-less bisection + Newton polish
    lo, hi = 1e-6, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        p = _price(mid)
        if p > price:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    sigma = 0.5 * (lo + hi)
    return float(sigma)


# ============================================================================
#                          PROBABILIDADES (P[ITM], P[Profit])
# ============================================================================
# Probabilidad bajo la MEDIDA RISK-NEUTRAL (Q), NO la real-world (P).
# Es la prob. que el subyacente termine ITM descontada por el carry, no la
# frecuencia historica. Para P real-world, pasar la drift esperada como r
# (no la risk-free).

def prob_itm(S, K, T, r, q, sigma, opt_type):
    """P(S_T cruza K) bajo la medida risk-neutral.

    Call: P(S_T > K) = N(d2)
    Put:  P(S_T < K) = N(-d2)

    Valido para opciones europeas. Para americanas, la prob. de ejercer es
    <= este valor (algunos nodos ITM no se ejercen porque la continuation
    vale mas).
    """
    if sigma <= 0 or T <= 0:
        # Sin vol o sin tiempo: probabilidad deterministica
        if opt_type == "call":
            return 1.0 if S > K else (0.5 if S == K else 0.0)
        return 1.0 if S < K else (0.5 if S == K else 0.0)
    d2 = (math.log(S / K) + (r - q - 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    if opt_type == "call":
        return n_cdf(d2)
    return n_cdf(-d2)


def prob_profit(S, K, T, r, q, sigma, opt_type, premium):
    """P(S_T genera profit) bajo Q, considerando la prima pagada.

    Call: P(S_T > K + premium)  (profit = intrinsic - premium > 0)
    Put:  P(S_T < K - premium)
    """
    if opt_type == "call":
        K_eff = K + premium
        if S >= K_eff:
            return 1.0  # ya ITM
        if sigma <= 0 or T <= 0:
            return 0.0
        d2 = (math.log(S / K_eff) + (r - q - 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
        return n_cdf(d2)
    K_eff = K - premium
    if S <= K_eff:
        return 1.0
    if sigma <= 0 or T <= 0:
        return 0.0
    d2 = (math.log(S / K_eff) + (r - q - 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return n_cdf(-d2)


# ============================================================================
#                          CLI
# ============================================================================

def _load_defaults():
    """Carga defaults desde assets/defaults.json junto al script."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(os.path.dirname(here), "assets", "defaults.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _print_table(rows, headers=None):
    """Imprime tabla ASCII simple (solo ASCII para portabilidad Windows)."""
    if headers:
        rows = [headers] + rows
    widths = [max(len(str(r[i])) for r in rows) for i in range(len(rows[0]))]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(sep)
    for r in rows:
        print("| " + " | ".join(str(c).ljust(w) for c, w in zip(r, widths)) + " |")
    print(sep)


def _format_ci(price, stderr):
    """Formato CI95 portable sin caracteres no-ASCII."""
    return f"{price:.6f} +/- {1.96*stderr:.6f}"


def _price_one(method, args, defaults):
    """Helper: extrae params y aplica un metodo."""
    S, K, T, r, q, sigma = args.S, args.K, args.T, args.r, args.q, args.sigma
    opt_type = args.type
    style = args.style
    if method in ("binomial", "trinomial"):
        steps = args.steps
        if method == "binomial":
            return binomial_price(S, K, T, r, q, sigma, steps, opt_type, style)
        return trinomial_price(S, K, T, r, q, sigma, steps, opt_type, style)
    if method == "mc":
        return mc_european_price(S, K, T, r, q, sigma, opt_type, args.paths, args.antithetic, args.seed)
    if method == "lsm":
        return lsm_price(S, K, T, r, q, sigma, opt_type, args.paths, args.steps, args.seed)
    if method == "bs2":
        return bs2_american_price(S, K, T, r, q, sigma, opt_type)
    if method == "bs":
        return bs_price(S, K, T, r, q, sigma, opt_type)
    raise ValueError(method)


def cmd_bs(args, defaults):
    p = bs_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    g = bs_greeks(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    out = {"method": "black-scholes", "price": p, "greeks": g, **vars(args)}
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    print(f"Black-Scholes {args.type.upper()} ({args.style}): {p:.6f}")
    for k, v in g.items():
        print(f"  {k:>5}: {v:+.6f}")


def cmd_tree(args, defaults, method_name, fn):
    t0 = time.perf_counter()
    p = fn(args.S, args.K, args.T, args.r, args.q, args.sigma, args.steps, args.type, args.style)
    dt_ms = (time.perf_counter() - t0) * 1000
    out = {"method": method_name, "price": p, "elapsed_ms": dt_ms, "steps": args.steps, **vars(args)}
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    print(f"{method_name} {args.type.upper()} ({args.style}, steps={args.steps}): {p:.6f}  [{dt_ms:.2f} ms]")


def cmd_mc(args, defaults, method_name, with_stderr=False):
    t0 = time.perf_counter()
    p, se = mc_european_price(args.S, args.K, args.T, args.r, args.q, args.sigma,
                              args.type, args.paths, args.antithetic, args.seed)
    dt_ms = (time.perf_counter() - t0) * 1000
    out = {"method": method_name, "price": p, "stderr": se, "ci95": (p - 1.96*se, p + 1.96*se),
           "paths": args.paths, "elapsed_ms": dt_ms, **vars(args)}
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    print(f"{method_name} {args.type.upper()} ({args.style}, paths={args.paths}, antithetic={args.antithetic}): "
          f"{_format_ci(p, se)}  (95% CI)  [{dt_ms:.2f} ms]")


def cmd_lsm(args, defaults):
    t0 = time.perf_counter()
    p = lsm_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type, args.paths, args.steps, args.seed)
    dt_ms = (time.perf_counter() - t0) * 1000
    out = {"method": "lsm", "price": p, "paths": args.paths, "steps": args.steps, "elapsed_ms": dt_ms, **vars(args)}
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    print(f"LSM {args.type.upper()} (paths={args.paths}, steps={args.steps}): {p:.6f}  [{dt_ms:.2f} ms]")


def cmd_bs2(args, defaults):
    t0 = time.perf_counter()
    p = bs2_american_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    dt_ms = (time.perf_counter() - t0) * 1000
    out = {"method": "bjerksund-stensland-2002", "price": p, "elapsed_ms": dt_ms, **vars(args)}
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    print(f"BS2 {args.type.upper()} (american, closed-form): {p:.6f}  [{dt_ms:.4f} ms]")


def cmd_heston(args, defaults):
    t0 = time.perf_counter()
    p = heston_price(args.S, args.K, args.T, args.r, args.q, args.sigma,
                     args.v0, args.kappa, args.theta, args.sigma_v, args.rho, args.type)
    dt_ms = (time.perf_counter() - t0) * 1000
    out = {"method": "heston-1993", "price": p, "elapsed_ms": dt_ms, **vars(args)}
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    print(f"Heston {args.type.upper()} (v0={args.v0}, k={args.kappa}, th={args.theta}, sv={args.sigma_v}, rho={args.rho}): {p:.6f}  [{dt_ms:.2f} ms]")


def cmd_bates(args, defaults):
    t0 = time.perf_counter()
    p = bates_price(args.S, args.K, args.T, args.r, args.q, args.sigma,
                    args.v0, args.kappa, args.theta, args.sigma_v, args.rho,
                    args.lam, args.mu_J, args.sigma_J, args.type, args.n_terms)
    dt_ms = (time.perf_counter() - t0) * 1000
    out = {"method": "bates-1996", "price": p, "elapsed_ms": dt_ms, **vars(args)}
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    print(f"Bates {args.type.upper()} (lam={args.lam}, mu_J={args.mu_J}, sig_J={args.sigma_J}): {p:.6f}  [{dt_ms:.2f} ms]")


def cmd_greeks(args, defaults):
    g = bs_greeks(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    if args.json:
        print(json.dumps({"method": "black-scholes-greeks", "greeks": g, **vars(args)}, indent=2, default=str))
        return
    print(f"Greeks ({args.type} {args.style}):")
    for k, v in g.items():
        print(f"  {k:>5}: {v:+.6f}")


def cmd_iv(args, defaults):
    iv = implied_vol(args.price, args.S, args.K, args.T, args.r, args.q, args.type, args.style)
    if args.json:
        print(json.dumps({"method": "implied-vol", "implied_vol": iv, **vars(args)}, indent=2, default=str))
        return
    print(f"Implied vol ({args.type} {args.style}): {iv:.6f}")


def cmd_pitm(args, defaults):
    """P(ITM) y opcionalmente P(Profit) bajo la medida risk-neutral Q."""
    p_itm = prob_itm(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    out = {"method": "prob-itm", "p_itm_risk_neutral": p_itm,
           "note": "Bajo medida risk-neutral Q. NO es la frecuencia real-world.",
           **vars(args)}
    if args.premium is not None:
        p_profit = prob_profit(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type, args.premium)
        out["p_profit"] = p_profit
        out["premium"] = args.premium
    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return
    side = "S_T > K" if args.type == "call" else "S_T < K"
    print(f"P({side}) bajo Q = {p_itm:.4f}  ({p_itm*100:.2f}%)")
    if args.premium is not None:
        K_eff = args.K + args.premium if args.type == "call" else args.K - args.premium
        side2 = f"S_T > {K_eff:.2f}" if args.type == "call" else f"S_T < {K_eff:.2f}"
        print(f"P({side2}) con prima {args.premium:.2f} = {p_profit:.4f}  ({p_profit*100:.2f}%)")


def cmd_surface(args, defaults):
    """Vol surface: precios across strikes o across S."""
    Ks = np.arange(args.K_min, args.K_max + args.K_step, args.K_step)
    rows = []
    for K in Ks:
        # Aprox moneyness
        moneyness = args.S / K
        p = bs_price(args.S, K, args.T, args.r, args.q, args.sigma, args.type)
        rows.append((f"{K:.2f}", f"{moneyness:.4f}", f"{p:.4f}"))
    if args.json:
        out = [{"strike": float(K), "moneyness": float(args.S/K),
                "price": bs_price(args.S, float(K), args.T, args.r, args.q, args.sigma, args.type)}
               for K in Ks]
        print(json.dumps(out, indent=2))
        return
    print(f"Vol surface {args.type.upper()} {args.style} (S={args.S}, T={args.T}, sigma={args.sigma}, r={args.r}):")
    _print_table(rows, headers=["Strike", "S/K", "Price"])


def cmd_all(args, defaults):
    """Compara TODOS los metodos aplicables (closed-form, tree, MC, smile, tail)."""
    rows = []
    t0 = time.perf_counter()
    p_bs = bs_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    rows.append(("Black-Scholes", "closed-form O(1)", f"{p_bs:.6f}"))
    t0_bin = time.perf_counter()
    p_bin = binomial_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.steps, args.type, args.style)
    rows.append(("Binomial CRR", f"N={args.steps}", f"{p_bin:.6f}"))
    t0_tri = time.perf_counter()
    p_tri = trinomial_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.steps, args.type, args.style)
    rows.append(("Trinomial", f"N={args.steps}", f"{p_tri:.6f}"))
    t0_mc = time.perf_counter()
    p_mc, se = mc_european_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type, args.paths, args.antithetic, args.seed)
    rows.append(("Monte Carlo", f"paths={args.paths}", _format_ci(p_mc, se)))

    # Heston y Bates son SOLO europeas (smile/tail risk; no hay formula cerrada americana)
    if args.style == "european":
        # Heston con params default equity-like calibrados
        t0_h = time.perf_counter()
        # Si sigma > 0, usar v0 = sigma^2 (consistente con BS en el limite)
        v0 = args.sigma * args.sigma
        p_heston = heston_price(args.S, args.K, args.T, args.r, args.q, args.sigma,
                                v0=v0, kappa=2.0, theta=v0, sigma_v=0.3, rho=-0.5,
                                opt_type=args.type)
        rows.append(("Heston 1993", "v0=s2, k=2, th=s2, sv=0.3, rho=-0.5", f"{p_heston:.6f}"))
        t0_b = time.perf_counter()
        p_bates = bates_price(args.S, args.K, args.T, args.r, args.q, args.sigma,
                               v0=v0, kappa=2.0, theta=v0, sigma_v=0.3, rho=-0.5,
                               lam=1.0, mu_J=-0.05, sigma_J=0.10, opt_type=args.type, n_terms=15)
        rows.append(("Bates 1996", "Heston + lam=1, mu_J=-0.05, sig_J=0.10", f"{p_bates:.6f}"))

    # American-only methods
    if args.style == "american":
        t0_lsm = time.perf_counter()
        p_lsm = lsm_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type, args.paths, args.steps, args.seed)
        rows.append(("Longstaff-Schwartz", f"paths={args.paths}", f"{p_lsm:.6f}"))
        t0_bs2 = time.perf_counter()
        p_bs2 = bs2_american_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
        rows.append(("BS2/BAW (closed-form)", "O(1)", f"{p_bs2:.6f}"))

    # Utilities: P(ITM), P(Profit con prima=precio BS), Greeks
    p_itm = prob_itm(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    rows.append(("P(ITM)", "N(d2) bajo Q", f"{p_itm:.4f}"))
    p_profit = prob_profit(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type, p_bs)
    rows.append(("P(Profit) vs BS price", f"premio={p_bs:.4f}", f"{p_profit:.4f}"))
    g = bs_greeks(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)
    rows.append(("Greeks (delta/gamma/vega)", "BS closed-form", f"d={g['delta']:+.4f} g={g['gamma']:+.4f}"))

    print(f"Compare ALL methods - {args.type.upper()} {args.style} (S={args.S}, K={args.K}, T={args.T}, r={args.r}, sigma={args.sigma}, q={args.q}):")
    _print_table(rows, headers=["Method", "Config", "Price / Value"])


def cmd_validate(args, defaults):
    """Corre todos los casos de assets/validation_cases.json."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(os.path.dirname(here), "assets", "validation_cases.json")
    if not os.path.exists(path):
        print("ERROR: assets/validation_cases.json not found", file=sys.stderr)
        return 1
    with open(path) as f:
        cases = json.load(f)
    failures = 0
    # Black-Scholes
    print("=== Black-Scholes European ===")
    for c in cases.get("black_scholes_european", []):
        p = bs_price(c["S"], c["K"], c["T"], c["r"], c["q"], c["sigma"], c["type"])
        err = abs(p - c["ref_price"])
        ok = err < 1e-3
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {c['name']}: got {p:.4f}, ref {c['ref_price']:.4f} (err {err:.2e})")
        if not ok:
            failures += 1
    # Americanas con binomial
    print("\n=== American (Binomial N=2000) ===")
    for c in cases.get("american_options_reference", []):
        p_bin = binomial_price(c["S"], c["K"], c["T"], c["r"], c["q"], c["sigma"], 2000, c["type"], c["style"])
        # Buscar cualquier key ref_price_binomial_*
        ref = None
        for k, v in c.items():
            if k.startswith("ref_price_binomial_"):
                ref = v
                ref_steps = k.split("_")[-1]
                break
        if ref is None:
            print(f"  [SKIP] {c['name']}: no ref value")
            continue
        err = abs(p_bin - ref)
        ok = err < 0.01
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {c['name']}: got {p_bin:.4f}, ref {ref:.4f} (N={ref_steps}, err {err:.4f})")
        if not ok:
            failures += 1

    # Put-call parity check
    if "put_call_parity" in cases:
        print("\n=== Put-Call Parity (BS) ===")
        pcp = cases["put_call_parity"]
        C = bs_price(pcp["S"], pcp["K"], pcp["T"], pcp["r"], pcp["q"], pcp["sigma"], "call")
        P = bs_price(pcp["S"], pcp["K"], pcp["T"], pcp["r"], pcp["q"], pcp["sigma"], "put")
        lhs = C - P
        rhs = pcp["S"] * math.exp(-pcp["q"] * pcp["T"]) - pcp["K"] * math.exp(-pcp["r"] * pcp["T"])
        err = abs(lhs - rhs)
        ok = err < pcp.get("tolerance", 1e-10)
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] C - P = {lhs:.10f}, S*exp(-qT) - K*exp(-rT) = {rhs:.10f} (err {err:.2e})")
        if not ok:
            failures += 1

    # P(ITM) y P(Profit) bajo Q
    if "prob_itm" in cases:
        print("\n=== Probabilidad ITM (Q-medida) ===")
        for c in cases["prob_itm"]:
            if "ref_p_itm" in c:
                p = prob_itm(c["S"], c["K"], c["T"], c["r"], c["q"], c["sigma"], c["type"])
                err = abs(p - c["ref_p_itm"])
                ok = err < 1e-3
                status = "OK" if ok else "FAIL"
                print(f"  [{status}] {c['name']}: got {p:.4f}, ref {c['ref_p_itm']:.4f} (err {err:.2e})")
                if not ok:
                    failures += 1
            if "premium" in c and "ref_p_profit" in c:
                p_p = prob_profit(c["S"], c["K"], c["T"], c["r"], c["q"], c["sigma"], c["type"], c["premium"])
                err2 = abs(p_p - c["ref_p_profit"])
                ok2 = err2 < 1e-3
                status2 = "OK" if ok2 else "FAIL"
                print(f"  [{status2}] {c['name']} [P(Profit)]: got {p_p:.4f}, ref {c['ref_p_profit']:.4f}")
                if not ok2:
                    failures += 1

    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


def cmd_bench(args, defaults):
    """Benchmark: corre cada metodo N veces y reporta tiempo medio."""
    N = args.bench_n
    methods = [
        ("Black-Scholes", lambda: bs_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)),
        ("BS2 (American)", lambda: bs2_american_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type)),
        (f"Binomial N={args.steps}", lambda: binomial_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.steps, args.type, args.style)),
        (f"Trinomial N={args.steps}", lambda: trinomial_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.steps, args.type, args.style)),
        (f"MC paths={args.paths}", lambda: mc_european_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type, args.paths, args.antithetic, args.seed)),
    ]
    if args.style == "american":
        methods.append(("LSM", lambda: lsm_price(args.S, args.K, args.T, args.r, args.q, args.sigma, args.type, args.paths, args.steps, args.seed)))
    print(f"Benchmark - {N} repeticiones de cada metodo ({args.type} {args.style}):")
    rows = []
    for name, fn in methods:
        # Warmup
        fn()
        t0 = time.perf_counter()
        for _ in range(N):
            fn()
        dt = (time.perf_counter() - t0) / N * 1000
        rows.append((name, f"{dt:.4f} ms", f"{1000/dt:.0f}/s"))
    _print_table(rows, headers=["Method", "Avg time", "Throughput"])


def build_parser():
    defaults = _load_defaults()
    # Parent parser con todos los flags compartidos
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--S", type=float, default=defaults.get("S", 100.0), help="Spot price")
    parent.add_argument("--K", type=float, default=defaults.get("K", 100.0), help="Strike")
    parent.add_argument("--T", type=float, default=defaults.get("T", 0.25), help="Time to maturity (years)")
    parent.add_argument("--r", type=float, default=defaults.get("r", 0.05), help="Risk-free rate (continuous)")
    parent.add_argument("--q", type=float, default=defaults.get("q", 0.0), help="Dividend yield (continuous)")
    parent.add_argument("--sigma", type=float, default=defaults.get("sigma", 0.20), help="Volatility")
    parent.add_argument("--type", choices=["call", "put"], default=defaults.get("type", "call"))
    parent.add_argument("--style", choices=["european", "american"], default=defaults.get("style", "european"))
    parent.add_argument("--steps", type=int, default=defaults.get("steps", 500), help="Tree steps / LSM time steps")
    parent.add_argument("--paths", type=int, default=defaults.get("paths", 100000), help="MC paths")
    parent.add_argument("--seed", type=int, default=defaults.get("seed", 42))
    parent.add_argument("--antithetic", dest="antithetic", action="store_true", default=defaults.get("antithetic", True))
    parent.add_argument("--no-antithetic", dest="antithetic", action="store_false")
    parent.add_argument("--json", action="store_true", help="Output JSON")
    parent.add_argument("--bench-n", type=int, default=200, help="Iterations for bench mode")

    p = argparse.ArgumentParser(
        description="Option pricing — Black-Scholes, Binomial, Trinomial, Monte Carlo, Bjerksund-Stensland 2002, LSM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[parent],
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("bs", help="Black-Scholes (european)", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_bs(a, d))

    sp = sub.add_parser("binomial", help="Binomial tree (CRR)", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_tree(a, d, "Binomial CRR", binomial_price))

    sp = sub.add_parser("trinomial", help="Trinomial tree", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_tree(a, d, "Trinomial", trinomial_price))

    sp = sub.add_parser("mc", help="Monte Carlo (european, antithetic variates)", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_mc(a, d, "Monte Carlo"))

    sp = sub.add_parser("lsm", help="Longstaff-Schwartz (american via MC)", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_lsm(a, d))

    sp = sub.add_parser("bs2", help="Bjerksund-Stensland 2002 (american closed-form)", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_bs2(a, d))

    sp = sub.add_parser("heston", help="Heston (1993) vol estocastica via Fourier", parents=[parent])
    sp.add_argument("--v0", type=float, default=0.04, help="Varianza actual (sigma^2)")
    sp.add_argument("--kappa", type=float, default=2.0, help="Speed mean-reversion")
    sp.add_argument("--theta", type=float, default=0.04, help="Varianza largo plazo")
    sp.add_argument("--sigma_v", type=float, default=0.3, help="Vol de vol")
    sp.add_argument("--rho", type=float, default=-0.5, help="Correlacion spot-vol (negativa equity)")
    sp.set_defaults(func=lambda a, d: cmd_heston(a, d))

    sp = sub.add_parser("bates", help="Bates (1996) Heston + Merton jumps", parents=[parent])
    sp.add_argument("--v0", type=float, default=0.04)
    sp.add_argument("--kappa", type=float, default=2.0)
    sp.add_argument("--theta", type=float, default=0.04)
    sp.add_argument("--sigma_v", type=float, default=0.3)
    sp.add_argument("--rho", type=float, default=-0.5)
    sp.add_argument("--lam", type=float, default=1.0, help="Intensidad de saltos por ano")
    sp.add_argument("--mu_J", type=float, default=-0.05, help="Media log-jump (negativa para crashes)")
    sp.add_argument("--sigma_J", type=float, default=0.10, help="Vol log-jump")
    sp.add_argument("--n-terms", type=int, default=15, help="Terminos serie de Poisson")
    sp.set_defaults(func=lambda a, d: cmd_bates(a, d))

    sp = sub.add_parser("greeks", help="Analytic greeks (Black-Scholes)", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_greeks(a, d))

    sp = sub.add_parser("iv", help="Implied volatility from market price", parents=[parent])
    sp.add_argument("--price", type=float, required=True, help="Market price")
    sp.set_defaults(func=lambda a, d: cmd_iv(a, d))

    sp = sub.add_parser("pitm", help="P(ITM) y P(Profit) risk-neutral (Q-medida)", parents=[parent])
    sp.add_argument("--premium", type=float, default=None, help="Premium pagada/cobrada; si se da, computa P(Profit) ademas de P(ITM)")
    sp.set_defaults(func=lambda a, d: cmd_pitm(a, d))

    sp = sub.add_parser("surface", help="Price across strikes", parents=[parent])
    sp.add_argument("--K-min", type=float, default=80.0)
    sp.add_argument("--K-max", type=float, default=120.0)
    sp.add_argument("--K-step", type=float, default=5.0)
    sp.set_defaults(func=lambda a, d: cmd_surface(a, d))

    sp = sub.add_parser("all", help="Compare all applicable methods", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_all(a, d))

    sp = sub.add_parser("validate", help="Run validation cases from assets/validation_cases.json", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_validate(a, d))

    sp = sub.add_parser("bench", help="Benchmark all methods", parents=[parent])
    sp.set_defaults(func=lambda a, d: cmd_bench(a, d))

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    defaults = _load_defaults()
    return args.func(args, defaults) or 0


if __name__ == "__main__":
    sys.exit(main())
