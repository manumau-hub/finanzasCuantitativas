# -*- coding: utf-8 -*-
"""
Payoffs de opciones y estrategias.

Incluye:
- Vanilla y estrategias (spreads, straddles, butterflies, etc.)
- Digitales (cash-or-nothing, asset-or-nothing)
- Asian (media aritmética, path-dependent)
- Barrier (up/down, in/out, call/put; path-dependent)

Todas las funciones aceptan escalares o arrays de NumPy.
S: precio del subyacente al vencimiento (o S_avg para Asian).
K, K1, K2, B: strikes y barreras.
"""
from __future__ import annotations

import numpy as np
from typing import Union

# Tipo para precios y strikes (escalar o array)
_Num = Union[float, np.ndarray]


def payoff_call(S: _Num, K: _Num) -> _Num:
    """
    Payoff de una opción call europea.

    max(S - K, 0)
    """
    return np.maximum(S - K, 0)


def payoff_put(S: _Num, K: _Num) -> _Num:
    """
    Payoff de una opción put europea.

    max(K - S, 0)
    """
    return np.maximum(K - S, 0)


def payoff_forwardSintetico(S: _Num, K: _Num) -> _Num:
    """
    Payoff de un forward sintético (long): Call(K) - Put(K).

    Equivale a S - K (posición larga en forward).
    """
    return payoff_call(S, K) - payoff_put(S, K)


def payoff_combo(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un combo / risk reversal: Call(K2) - Put(K1).

    Convención típica: K1 < K2 (call OTM arriba, put OTM abajo).
    """
    return payoff_call(S, K2) - payoff_put(S, K1)


def payoff_BullCS(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un Bull Call Spread: Call(K1) - Call(K2).

    Long call en K1, short call en K2. Convención: K1 < K2.
    """
    if np.any(K1 >= K2):
        raise ValueError("En Bull Call Spread se espera K1 < K2.")
    return payoff_call(S, K1) - payoff_call(S, K2)


def payoff_BearCS(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un Bear Call Spread: Call(K2) - Call(K1).

    Short call en K1, long call en K2. Convención: K1 < K2.
    """
    if np.any(K1 >= K2):
        raise ValueError("En Bear Call Spread se espera K1 < K2.")
    return payoff_call(S, K2) - payoff_call(S, K1)


def payoff_BullPS(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un Bull Put Spread: Put(K1) - Put(K2).

    Long put en K1, short put en K2. Convención: K1 < K2.
    """
    if np.any(K1 >= K2):
        raise ValueError("En Bull Put Spread se espera K1 < K2.")
    return payoff_put(S, K1) - payoff_put(S, K2)


def payoff_BearPS(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un Bear Put Spread: Put(K2) - Put(K1).

    Short put en K1, long put en K2. Convención: K1 < K2.
    """
    if np.any(K1 >= K2):
        raise ValueError("En Bear Put Spread se espera K1 < K2.")
    return payoff_put(S, K2) - payoff_put(S, K1)


def payoff_CButterflyS(S: _Num, K1: _Num, K2: _Num, K3: _Num) -> _Num:
    """
    Payoff de un Call Butterfly: Call(K1) - 2*Call(K2) + Call(K3).

    Convención: K1 < K2 < K3 (K2 suele ser ATM).
    """
    if np.any(K1 >= K2) or np.any(K2 >= K3):
        raise ValueError("En Call Butterfly se espera K1 < K2 < K3.")
    return payoff_call(S, K1) - 2 * payoff_call(S, K2) + payoff_call(S, K3)


def payoff_PButterflyS(S: _Num, K1: _Num, K2: _Num, K3: _Num) -> _Num:
    """
    Payoff de un Put Butterfly: Put(K1) - 2*Put(K2) + Put(K3).

    Convención: K1 < K2 < K3 (K2 suele ser ATM).
    """
    if np.any(K1 >= K2) or np.any(K2 >= K3):
        raise ValueError("En Put Butterfly se espera K1 < K2 < K3.")
    return payoff_put(S, K1) - 2 * payoff_put(S, K2) + payoff_put(S, K3)


def payoff_straddle(S: _Num, K: _Num) -> _Num:
    """
    Payoff de un straddle (long): Call(K) + Put(K).

    Beneficio cuando el subyacente se mueve fuerte en cualquier dirección.
    """
    return payoff_call(S, K) + payoff_put(S, K)


def payoff_strangle(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un strangle (long): Call(K1) + Put(K2).

    Convención típica OTM: K1 > K2 (call strike arriba, put strike abajo).
    """
    return payoff_call(S, K1) + payoff_put(S, K2)


def payoff_iron_condor(S: _Num, K1: _Num, K2: _Num, K3: _Num, K4: _Num) -> _Num:
    """
    Payoff de un Iron Condor: Put(K1) - Put(K2) - Call(K3) + Call(K4).

    Long put spread (K1<K2) + long call spread (K3<K4).
    Convención: K1 < K2 < K3 < K4.
    """
    if np.any(K1 >= K2) or np.any(K2 >= K3) or np.any(K3 >= K4):
        raise ValueError("En Iron Condor se espera K1 < K2 < K3 < K4.")
    return payoff_put(S, K1) - payoff_put(S, K2) - payoff_call(S, K3) + payoff_call(S, K4)


def payoff_iron_butterfly(S: _Num, K1: _Num, K2: _Num, K3: _Num) -> _Num:
    """
    Payoff de un Iron Butterfly: Put(K1) - Put(K2) + Call(K3) - Call(K2).

    Short straddle en K2 + long strangle (put K1, call K3).
    Convención: K1 < K2 < K3 (K2 suele ser ATM).
    """
    if np.any(K1 >= K2) or np.any(K2 >= K3):
        raise ValueError("En Iron Butterfly se espera K1 < K2 < K3.")
    return payoff_put(S, K1) - payoff_put(S, K2) + payoff_call(S, K3) - payoff_call(S, K2)


def payoff_condor(S: _Num, K1: _Num, K2: _Num, K3: _Num, K4: _Num) -> _Num:
    """
    Payoff de un Condor (long): Call(K1) - Call(K2) - Call(K3) + Call(K4).

    Long call spread bajo + long call spread alto.
    Convención: K1 < K2 < K3 < K4.
    """
    if np.any(K1 >= K2) or np.any(K2 >= K3) or np.any(K3 >= K4):
        raise ValueError("En Condor se espera K1 < K2 < K3 < K4.")
    return payoff_call(S, K1) - payoff_call(S, K2) - payoff_call(S, K3) + payoff_call(S, K4)


def payoff_short_straddle(S: _Num, K: _Num) -> _Num:
    """
    Payoff de un short straddle: -(Call(K) + Put(K)).

    Beneficio cuando S se mantiene cerca de K.
    """
    return -(payoff_call(S, K) + payoff_put(S, K))


def payoff_short_strangle(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un short strangle: -(Call(K1) + Put(K2)).

    Convención típica OTM: K1 > K2.
    """
    return -(payoff_call(S, K1) + payoff_put(S, K2))


def payoff_covered_call(S: _Num, K: _Num) -> _Num:
    """
    Payoff de covered call: S - Call(K).

    Long subyacente + short call. Cede upside a cambio de prima.
    """
    return S - payoff_call(S, K)


def payoff_covered_put(S: _Num, K: _Num) -> _Num:
    """
    Payoff de covered put: Put(K) - S.

    Short subyacente + long put. Protege la posición corta.
    """
    return payoff_put(S, K) - S


def payoff_protective_put(S: _Num, K: _Num) -> _Num:
    """
    Payoff de protective put: S + Put(K).

    Long subyacente + long put. Protección a la baja (floor en K).
    """
    return S + payoff_put(S, K)


def payoff_ratio_spread(S: _Num, K1: _Num, K2: _Num, n1: int = 1, n2: int = 2) -> _Num:
    """
    Payoff de un ratio spread: n1*Call(K1) - n2*Call(K2).

    Convención: K1 < K2. Típico 1:2 (comprar 1 call, vender 2 calls).
    """
    if np.any(K1 >= K2):
        raise ValueError("En ratio spread se espera K1 < K2.")
    return n1 * payoff_call(S, K1) - n2 * payoff_call(S, K2)


def payoff_collar(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un collar: S + Put(K1) - Call(K2).

    Long subyacente + long put (floor) + short call (cap).
    Convención: K1 < K2.
    """
    if np.any(K1 >= K2):
        raise ValueError("En collar se espera K1 < K2.")
    return S + payoff_put(S, K1) - payoff_call(S, K2)


def payoff_box(S: _Num, K1: _Num, K2: _Num) -> _Num:
    """
    Payoff de un box spread: Call(K1) - Put(K1) - Call(K2) + Put(K2).

    Equivale a K2 - K1 (constante, sin riesgo de mercado).
    Convención: K1 < K2.
    """
    if np.any(K1 >= K2):
        raise ValueError("En box spread se espera K1 < K2.")
    return np.full_like(np.asarray(S, dtype=float), K2 - K1)


# =============================================================================
# DIGITALES (BINARIAS)
# =============================================================================


def payoff_digital_call(S: _Num, K: _Num, Q: _Num = 1.0) -> _Num:
    """
    Payoff de una opción digital call (cash-or-nothing).

    Q si S > K, 0 en caso contrario.
    Q: monto fijo pagado si la opción termina in-the-money.
    """
    return np.where(S > K, np.asarray(Q, dtype=float), 0.0)


def payoff_digital_put(S: _Num, K: _Num, Q: _Num = 1.0) -> _Num:
    """
    Payoff de una opción digital put (cash-or-nothing).

    Q si S < K, 0 en caso contrario.
    """
    return np.where(S < K, np.asarray(Q, dtype=float), 0.0)


def payoff_asset_or_nothing_call(S: _Num, K: _Num) -> _Num:
    """
    Payoff de una opción asset-or-nothing call.

    S si S > K, 0 en caso contrario.
    """
    return np.where(S > K, np.asarray(S, dtype=float), 0.0)


def payoff_asset_or_nothing_put(S: _Num, K: _Num) -> _Num:
    """
    Payoff de una opción asset-or-nothing put.

    S si S < K, 0 en caso contrario.
    """
    return np.where(S < K, np.asarray(S, dtype=float), 0.0)


# =============================================================================
# ASIAN (ARITHMETIC AVERAGE)
# =============================================================================


def payoff_asian_call(S_avg: _Num, K: _Num) -> _Num:
    """
    Payoff de una opción Asian call (media aritmética).

    max(S_avg - K, 0). S_avg es el precio promedio del subyacente durante la vida.
    Path-dependent: requiere S_avg calculado del camino.
    """
    return np.maximum(np.asarray(S_avg, dtype=float) - K, 0)


def payoff_asian_put(S_avg: _Num, K: _Num) -> _Num:
    """
    Payoff de una opción Asian put (media aritmética).

    max(K - S_avg, 0). Path-dependent.
    """
    return np.maximum(K - np.asarray(S_avg, dtype=float), 0)


# =============================================================================
# BARRIER (8 COMBINACIONES: Up/Down x In/Out x Call/Put)
# =============================================================================

_BoolLike = Union[bool, np.ndarray]


def payoff_barrier_up_in_call(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """
    Payoff Up-and-In Call: activa si el precio alcanza B (B > S_0).

    Vanilla call payoff si barrier_hit, 0 si no.
    """
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(hit, payoff_call(S, K), 0.0)


def payoff_barrier_up_in_put(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """Payoff Up-and-In Put: activa si el precio alcanza B (B > S_0)."""
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(hit, payoff_put(S, K), 0.0)


def payoff_barrier_up_out_call(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """
    Payoff Up-and-Out Call: se anula si el precio alcanza B (B > S_0).

    Vanilla call payoff si NO barrier_hit, 0 si sí.
    """
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(~hit, payoff_call(S, K), 0.0)


def payoff_barrier_up_out_put(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """Payoff Up-and-Out Put: se anula si el precio alcanza B (B > S_0)."""
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(~hit, payoff_put(S, K), 0.0)


def payoff_barrier_down_in_call(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """
    Payoff Down-and-In Call: activa si el precio alcanza B (B < S_0).

    Vanilla call payoff si barrier_hit, 0 si no.
    """
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(hit, payoff_call(S, K), 0.0)


def payoff_barrier_down_in_put(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """Payoff Down-and-In Put: activa si el precio alcanza B (B < S_0)."""
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(hit, payoff_put(S, K), 0.0)


def payoff_barrier_down_out_call(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """
    Payoff Down-and-Out Call: se anula si el precio alcanza B (B < S_0).

    Vanilla call payoff si NO barrier_hit, 0 si sí.
    """
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(~hit, payoff_call(S, K), 0.0)


def payoff_barrier_down_out_put(S: _Num, K: _Num, B: _Num, barrier_hit: _BoolLike) -> _Num:
    """Payoff Down-and-Out Put: se anula si el precio alcanza B (B < S_0)."""
    hit = np.asarray(barrier_hit, dtype=bool)
    return np.where(~hit, payoff_put(S, K), 0.0)


# Aliases con nombres PEP8 (compatibilidad hacia adelante)
payoff_forward_sintetico = payoff_forwardSintetico
payoff_bull_call_spread = payoff_BullCS
payoff_bear_call_spread = payoff_BearCS
payoff_bull_put_spread = payoff_BullPS
payoff_bear_put_spread = payoff_BearPS
payoff_call_butterfly = payoff_CButterflyS
payoff_put_butterfly = payoff_PButterflyS


__all__ = [
    "payoff_call",
    "payoff_put",
    "payoff_forwardSintetico",
    "payoff_forward_sintetico",
    "payoff_combo",
    "payoff_BullCS",
    "payoff_bull_call_spread",
    "payoff_BearCS",
    "payoff_bear_call_spread",
    "payoff_BullPS",
    "payoff_bull_put_spread",
    "payoff_BearPS",
    "payoff_bear_put_spread",
    "payoff_CButterflyS",
    "payoff_call_butterfly",
    "payoff_PButterflyS",
    "payoff_put_butterfly",
    "payoff_straddle",
    "payoff_strangle",
    "payoff_iron_condor",
    "payoff_iron_butterfly",
    "payoff_condor",
    "payoff_short_straddle",
    "payoff_short_strangle",
    "payoff_covered_call",
    "payoff_covered_put",
    "payoff_protective_put",
    "payoff_ratio_spread",
    "payoff_collar",
    "payoff_box",
    # Digitales
    "payoff_digital_call",
    "payoff_digital_put",
    "payoff_asset_or_nothing_call",
    "payoff_asset_or_nothing_put",
    # Asian
    "payoff_asian_call",
    "payoff_asian_put",
    # Barrier
    "payoff_barrier_up_in_call",
    "payoff_barrier_up_in_put",
    "payoff_barrier_up_out_call",
    "payoff_barrier_up_out_put",
    "payoff_barrier_down_in_call",
    "payoff_barrier_down_in_put",
    "payoff_barrier_down_out_call",
    "payoff_barrier_down_out_put",
]
