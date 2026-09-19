# -*- coding: utf-8 -*-
"""
Precio de opción americana con Monte Carlo Longstaff-Schwartz (LSM).

Método de regresión por mínimos cuadrados para estimar la frontera de ejercicio
óptimo. Implementación casera sin QuantLib, en el espíritu de los códigos nativos.

Misma firma que opcion_americana_bin (pasos = número de caminos MC).
"""
import numpy as np


def opcion_americana_mc(tipo, S, K, T, r, sigma, div, pasos, n_steps=20):
    """
    Calcula el precio de una opción americana con Monte Carlo Longstaff-Schwartz.

    Parámetros:
        tipo (str): "C" (call) o "P" (put).
        S, K, T, r, sigma, div: estándar.
        pasos (int): Número de caminos de Monte Carlo.
        n_steps (int): Número de pasos temporales para la simulación (default 20).

    Retorna:
        float: Precio de la opción.
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")
    if tipo not in ("C", "P"):
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")

    dt = T / n_steps
    drift = (r - div - 0.5 * sigma ** 2) * dt
    vol = sigma * np.sqrt(dt)

    # Generar caminos: (pasos, n_steps+1)
    z = np.random.normal(0, 1, (pasos, n_steps))
    log_returns = drift + vol * z
    paths = S * np.exp(np.concatenate([np.zeros((pasos, 1)), np.cumsum(log_returns, axis=1)], axis=1))

    # Payoff al vencimiento
    if tipo == "C":
        payoff = np.maximum(paths - K, 0)
    else:
        payoff = np.maximum(K - paths, 0)

    # Valor de continuación (descontado un paso)
    valor = payoff.copy()
    df = np.exp(-r * dt)

    # Retroceso: de n_steps-1 a 1
    for t in range(n_steps - 1, 0, -1):
        S_t = paths[:, t]
        continuacion = df * valor[:, t + 1]

        if tipo == "C":
            itm = S_t > K
            intrínseco = S_t - K
        else:
            itm = S_t < K
            intrínseco = K - S_t

        if np.sum(itm) > 0:
            # Base polinomial: 1, S, S^2 (solo paths ITM)
            X = np.column_stack([np.ones(np.sum(itm)), S_t[itm], S_t[itm] ** 2])
            Y = continuacion[itm]
            coef, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
            predicho = np.zeros(pasos)
            predicho[itm] = X @ coef

            # Ejercer si intrínseco > continuación estimada
            ejercer = itm & (intrínseco > predicho)
            valor[ejercer, t] = intrínseco[ejercer]
            valor[~ejercer, t] = continuacion[~ejercer]
        else:
            valor[:, t] = continuacion

    # Valor en t=0: descontar un paso
    return float(np.mean(df * valor[:, 1]))
