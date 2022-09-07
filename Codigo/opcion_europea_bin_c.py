import math
import numpy as np

"""
opcion_europea_bin_c
Def
    Calculador del precio de una opcion Europea con una formula cerrada
Inputs
    - tipo : string - Tipo de contrato entre ["CALL","PUT"]
    - S : float - Spot price del activo
    - K : float - Strike price del contrato
    - T : float - Tiempo hasta la expiracion (en años)
    - r : float - Tasa 'libre de riesgo' (anualizada)
    - sigma : float - Volatilidad implicita (anualizada)
    - div : float - Tasa de dividendos continuos (anualizada)
    - pasos : int - Cantidad de pasos del arbol binomial
Outputs
    - precio_BIN: float - Precio del contrato
"""

import operator as op
from functools import reduce

def ncr(n, r):
    try:
        return math.comb( n, r)
    except Exception as e:
        print(f'Error {e}')
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        return numer // denom  # or / in Python 2


def nCr(n, r):
    f = math.factorial
    return f(n) / f(r) / f(n - r)


def opcion_europea_bin_c(tipo, S, K, T, r, sigma, div, pasos):

    #auxiliares
    dt = T / pasos
    tasa_forward = math.exp((r - div) * dt)
    descuento = math.exp(-r * dt)

    #modelo CRR
    u = math.exp(sigma * math.pow(dt, 0.5))
    d = 1 / u
    #probabilidad de riesgo neutral
    q_prob = (tasa_forward - d) / (u - d)

    temp = 0

    for k in range(pasos):
        if tipo == "C":
            payoff = max(0, S * math.pow(u,k) * math.pow(d,pasos-k)-K)
        elif tipo == "P":
            payoff = max(0, K - S * math.pow(u, k) * math.pow(d, pasos - k))
        temp = temp +ncr(pasos, k) * math.pow(q_prob,k) * math.pow((1-q_prob),pasos-k) * payoff



    precio_BIN_c = math.exp(-r*T)*temp

    return precio_BIN_c
