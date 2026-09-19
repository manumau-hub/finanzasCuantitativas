import numpy as np
import math


def opcion_americana_bin(tipo, S, K, T, r, sigma, div, pasos):
    """
    Calcula el precio de una opción americana con el modelo binomial CRR.
    En cada nodo se toma el máximo entre el valor europeo (hold) y el payoff de ejercicio temprano.
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    dt = T / pasos
    tasa_forward = math.exp((r - div) * dt)
    descuento = math.exp(-r * dt)
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    q_prob = (tasa_forward - d) / (u - d)

    # Precios del subyacente al vencimiento en cada nodo
    ST_precios = np.zeros(pasos + 1)
    for i in range(pasos + 1):
        ST_precios[pasos - i] = (u ** (2 * i - pasos)) * S

    opcion_precios = np.zeros((pasos + 1, pasos + 1))
    # Payoff al vencimiento (columna pasos)
    for i in range(pasos + 1):
        if tipo == "P":
            opcion_precios[i, pasos] = max(0, K - ST_precios[i])
        elif tipo == "C":
            opcion_precios[i, pasos] = max(0, ST_precios[i] - K)
        else:
            raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")

    # Retropropagación: valor europeo vs ejercicio temprano
    for j in range(1, pasos + 1):
        for i in range(pasos + 1 - j):
            eur = q_prob * opcion_precios[i, pasos - j + 1] + (1 - q_prob) * opcion_precios[i + 1, pasos - j + 1]
            spot_nodo = S * (u ** (-2 * i + pasos - j))
            if tipo == "P":
                opcion_precios[i, pasos - j] = descuento * max(eur, K - spot_nodo)
            elif tipo == "C":
                opcion_precios[i, pasos - j] = descuento * max(eur, spot_nodo - K)

    return opcion_precios[0, 0]
