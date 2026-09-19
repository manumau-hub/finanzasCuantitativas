import math
import numpy as np


def opcion_europea_bin(tipo, S, K, T, r, sigma, div, pasos):
    """
    Calcula el precio de una opción europea (call o put) utilizando el modelo binomial de Cox-Ross-Rubinstein (CRR).
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    dt = T / pasos
    tasa_forward = math.exp((r - div) * dt)
    descuento = math.exp(-r * dt)
    # Factores de subida/bajada CRR: u = exp(sigma*sqrt(dt)), d = 1/u
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    q_prob = (tasa_forward - d) / (u - d)
    ST_precios = S * u ** np.arange(pasos, -1, -1) * d ** np.arange(0, pasos + 1)
    if tipo == "P":
        opcion_precios = np.maximum(K - ST_precios, 0)
    elif tipo == "C":
        opcion_precios = np.maximum(ST_precios - K, 0)
    else:
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put)")
    for _ in range(pasos):
        opcion_precios = descuento * (q_prob * opcion_precios[:-1] + (1 - q_prob) * opcion_precios[1:])
    return opcion_precios[0]
