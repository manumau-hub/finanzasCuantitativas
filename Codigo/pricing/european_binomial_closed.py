import math
import operator as op
from functools import reduce


def ncr(n, r):
    """
    Coeficiente binomial C(n,r). Usa math.comb (Python 3.8+).
    Fallback manual para versiones anteriores.
    """
    try:
        return math.comb(n, r)
    except (AttributeError, TypeError):
        # math.comb no existe en Python < 3.8
        r = min(r, n - r)
        numer = reduce(op.mul, range(n, n - r, -1), 1)
        denom = reduce(op.mul, range(1, r + 1), 1)
        return numer // denom


def opcion_europea_bin_c(tipo, S, K, T, r, sigma, div, pasos):
    """
    Precio de opción europea binomial en forma cerrada.
    Suma explícita: sum_{k=0}^{n} C(n,k) * q^k * (1-q)^(n-k) * payoff(k) * exp(-r*T)
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    dt = T / pasos
    tasa_forward = math.exp((r - div) * dt)
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    q_prob = (tasa_forward - d) / (u - d)

    temp = 0
    # k va de 0 a pasos: cada k representa un nodo de payoff al vencimiento
    # S*u^k*d^(pasos-k) = precio del subyacente en ese nodo
    for k in range(pasos + 1):
        if tipo == "C":
            payoff = max(0, S * (u**k) * (d**(pasos - k)) - K)
        elif tipo == "P":
            payoff = max(0, K - S * (u**k) * (d**(pasos - k)))
        else:
            raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")
        temp += ncr(pasos, k) * (q_prob**k) * ((1 - q_prob)**(pasos - k)) * payoff

    return math.exp(-r * T) * temp
