# -*- coding: utf-8 -*-
"""
Pricing de estrategias por composición de opciones vanilla.

Cada estrategia se descompone en piernas (tipo, K, coef). El precio total
es la suma de coef * precio_vanilla(tipo, K) para cada pierna.

Las piernas se definen en ESTRATEGIA_PIERNAS; el pricer vanilla es inyectable
(BS, binomial, MC, FD) para máxima flexibilidad.
"""
from .european_bs import opcion_europea_bs
from .american_binomial import opcion_americana_bin


def _piernas_bull_call_spread(K1, K2):
    """Call(K1) - Call(K2). K1 < K2."""
    return [("C", K1, 1), ("C", K2, -1)]


def _piernas_bear_call_spread(K1, K2):
    """Call(K2) - Call(K1). K1 < K2."""
    return [("C", K2, 1), ("C", K1, -1)]


def _piernas_bull_put_spread(K1, K2):
    """Put(K1) - Put(K2). K1 < K2."""
    return [("P", K1, 1), ("P", K2, -1)]


def _piernas_bear_put_spread(K1, K2):
    """Put(K2) - Put(K1). K1 < K2."""
    return [("P", K2, 1), ("P", K1, -1)]


def _piernas_straddle(K):
    """Call(K) + Put(K)."""
    return [("C", K, 1), ("P", K, 1)]


def _piernas_strangle(K1, K2):
    """Call(K1) + Put(K2). Típico OTM: K1 > K2."""
    return [("C", K1, 1), ("P", K2, 1)]


def _piernas_combo(K1, K2):
    """Call(K2) - Put(K1). Risk reversal. K1 < K2."""
    return [("C", K2, 1), ("P", K1, -1)]


def _piernas_call_butterfly(K1, K2, K3):
    """Call(K1) - 2*Call(K2) + Call(K3). K1 < K2 < K3."""
    return [("C", K1, 1), ("C", K2, -2), ("C", K3, 1)]


def _piernas_put_butterfly(K1, K2, K3):
    """Put(K1) - 2*Put(K2) + Put(K3). K1 < K2 < K3."""
    return [("P", K1, 1), ("P", K2, -2), ("P", K3, 1)]


def _piernas_iron_condor(K1, K2, K3, K4):
    """Put(K1) - Put(K2) - Call(K3) + Call(K4). K1 < K2 < K3 < K4."""
    return [("P", K1, 1), ("P", K2, -1), ("C", K3, -1), ("C", K4, 1)]


def _piernas_iron_butterfly(K1, K2, K3):
    """Put(K1) - Put(K2) + Call(K3) - Call(K2). K1 < K2 < K3."""
    return [("P", K1, 1), ("P", K2, -1), ("C", K3, 1), ("C", K2, -1)]


def _piernas_condor(K1, K2, K3, K4):
    """Call(K1) - Call(K2) - Call(K3) + Call(K4). K1 < K2 < K3 < K4."""
    return [("C", K1, 1), ("C", K2, -1), ("C", K3, -1), ("C", K4, 1)]


def _piernas_short_straddle(K):
    """-(Call(K) + Put(K))."""
    return [("C", K, -1), ("P", K, -1)]


def _piernas_short_strangle(K1, K2):
    """-(Call(K1) + Put(K2))."""
    return [("C", K1, -1), ("P", K2, -1)]


def _piernas_ratio_spread(K1, K2, n1=1, n2=2):
    """n1*Call(K1) - n2*Call(K2). K1 < K2."""
    return [("C", K1, n1), ("C", K2, -n2)]


def _piernas_box(K1, K2):
    """Call(K1) - Put(K1) - Call(K2) + Put(K2). K1 < K2. Payoff constante K2-K1."""
    return [("C", K1, 1), ("P", K1, -1), ("C", K2, -1), ("P", K2, 1)]


def _piernas_covered_call(K):
    """S - Call(K). Incluye subyacente; aquí solo -Call(K) para la parte opcional."""
    return [("C", K, -1)]


def _piernas_protective_put(K):
    """S + Put(K). Solo pierna opcional."""
    return [("P", K, 1)]


def _piernas_collar(K1, K2):
    """S + Put(K1) - Call(K2). K1 < K2. Solo piernas opcionales."""
    return [("P", K1, 1), ("C", K2, -1)]


# Registro: nombre -> función que retorna lista de (tipo, K, coef)
ESTRATEGIA_PIERNAS = {
    "bull_call_spread": _piernas_bull_call_spread,
    "bear_call_spread": _piernas_bear_call_spread,
    "bull_put_spread": _piernas_bull_put_spread,
    "bear_put_spread": _piernas_bear_put_spread,
    "straddle": _piernas_straddle,
    "strangle": _piernas_strangle,
    "combo": _piernas_combo,
    "call_butterfly": _piernas_call_butterfly,
    "put_butterfly": _piernas_put_butterfly,
    "iron_condor": _piernas_iron_condor,
    "iron_butterfly": _piernas_iron_butterfly,
    "condor": _piernas_condor,
    "short_straddle": _piernas_short_straddle,
    "short_strangle": _piernas_short_strangle,
    "ratio_spread": _piernas_ratio_spread,
    "box": _piernas_box,
    "covered_call": _piernas_covered_call,
    "protective_put": _piernas_protective_put,
    "collar": _piernas_collar,
}


def precio_estrategia(
    piernas,
    S,
    T,
    r,
    sigma,
    div,
    pricer=None,
    **pricer_kwargs,
):
    """
    Precio de una estrategia por composición de opciones vanilla.

    Parámetros
    ----------
    piernas : list
        Lista de (tipo, K, coef). tipo in ("C","P"), K strike, coef multiplicador.
    S, T, r, sigma, div : float
        Parámetros estándar del modelo.
    pricer : callable, optional
        Función (tipo, S, K, T, r, sigma, div, ...) -> precio. Default: opcion_europea_bs.
    pricer_kwargs
        Argumentos extra para el pricer (ej. pasos para binomial/MC).

    Retorna
    -------
    float
        Precio total de la estrategia.

    Ejemplo
    -------
    piernas = [("C", 90, 1), ("C", 110, -1)]  # Bull Call Spread
    precio = precio_estrategia(piernas, 100, 1, 0.05, 0.25, 0)
    """
    if pricer is None:
        pricer = opcion_europea_bs

    total = 0.0
    for tipo, K, coef in piernas:
        p = pricer(tipo, S, K, T, r, sigma, div, **pricer_kwargs)
        total += coef * p
    return total


# Kwargs que van al pricer, no a la definición de piernas
_PRICER_KWARGS = {"pasos", "M", "n_steps"}


def precio_estrategia_nombre(
    nombre,
    S,
    T,
    r,
    sigma,
    div,
    pricer=None,
    **kwargs,
):
    """
    Precio de una estrategia por nombre y parámetros.

    Parámetros
    ----------
    nombre : str
        Clave de ESTRATEGIA_PIERNAS (ej. "bull_call_spread", "straddle").
    S, T, r, sigma, div : float
        Parámetros estándar.
    pricer : callable, optional
        Función vanilla (default opcion_europea_bs).
    kwargs
        Argumentos para la estrategia (K, K1, K2, K3, K4, n1, n2)
        y para el pricer (pasos, M, n_steps).

    Retorna
    -------
    float
        Precio de la estrategia.

    Ejemplo
    -------
    precio_estrategia_nombre("bull_call_spread", 100, 1, 0.05, 0.25, 0, K1=90, K2=110)
    """
    if nombre not in ESTRATEGIA_PIERNAS:
        raise ValueError(
            f"Estrategia '{nombre}' no reconocida. "
            f"Disponibles: {list(ESTRATEGIA_PIERNAS.keys())}"
        )

    estrategia_kwargs = {k: v for k, v in kwargs.items() if k not in _PRICER_KWARGS}
    pricer_kwargs = {k: v for k, v in kwargs.items() if k in _PRICER_KWARGS}

    piernas = ESTRATEGIA_PIERNAS[nombre](**estrategia_kwargs)
    return precio_estrategia(
        piernas, S, T, r, sigma, div, pricer=pricer, **pricer_kwargs
    )
