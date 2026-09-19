import math
import numpy as np

"""
opcion_europea_bin
Def
    Calculador del precio de una opcion Europea con el modelo del Arbol Binomial (CRR)
Inputs
    - tipo : string - Tipo de contrato entre ["C","P"]
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


def opcion_europea_bin(tipo, S, K, T, r, sigma, div, pasos):

    #auxiliares
    dt = T / pasos
    tasa_forward = math.exp((r - div) * dt)
    descuento = math.exp(-r * dt)

    #modelo CRR
    u = math.exp(sigma * math.pow(dt, 0.5))
    d = 1 / u
    #probabilidad de riesgo neutral
    q_prob = (tasa_forward - d) / (u - d)

    #Precios finales
    ST_precios=np.zeros((pasos+1))

    for i in range(0,pasos+1):
        ST_precios[pasos-i] = math.pow(u, 2 * i - pasos) * S

    #Matriz de precios de la opcion
    opcion_precios = np.zeros((pasos+1, pasos+1))

    #Payoff
    for i in range (0, pasos+1):
        if tipo == "P":
            opcion_precios[i][pasos] = max(0, (K - ST_precios[i]))
        elif tipo == "C":
            opcion_precios[i][pasos] = max(0, (ST_precios[i] - K))

    for j in range(1, pasos+1):
        for i in range(0, pasos+1 - j):
            opcion_precios[i][pasos - j] = descuento * (q_prob * opcion_precios[i][pasos - j + 1] + (1  - q_prob) * opcion_precios[i + 1][pasos - j + 1])

    precio_BIN = opcion_precios[0][0]
    return precio_BIN


