import numpy as np
from scipy.interpolate import interp1d


def opcion_americana_fd(tipo, S, K, T, r, sigma, div, M=150):
    """
    Calcula el precio de una opción americana con diferencias finitas implícitas.
    En cada paso temporal se aplica max(valor_implícito, payoff_ejercicio) para el ejercicio temprano.
    """
    if T <= 0 or M < 2:
        raise ValueError("T debe ser positivo y M >= 2.")

    # Criterio de estabilidad para el esquema implícito. Cap N para T muy chico (evita N enorme).
    N = max(int(np.ceil(S * M / (2 * T))), 1)
    N = min(N, 5000)  # T chico → N enorme; cap para no colgar
    dt = T / N
    S_vec = np.linspace(0, 2 * S, M + 1)
    t_vec = np.linspace(0, T, N + 1)
    j = np.arange(1, M + 1)
    j2 = np.zeros(M + 1)
    aj = np.zeros(M + 1)
    bj = np.zeros(M + 1)
    cj = np.zeros(M + 1)
    sigma2 = sigma**2
    # Coeficientes de la matriz tridiagonal del esquema implícito
    for index in range(M + 1):
        if index == 0:
            bj[index] = 1
        elif index == M:
            bj[index] = 1
        else:
            j2[index] = j[index] * j[index]
            aj[index] = - 0.5 * dt * (sigma2 * j2[index] - (r-div) * j[index])
            bj[index] = 1 + dt * (sigma2 * j2[index] + r)
            cj[index] = - 0.5 * dt * (sigma2 * j2[index] + (r-div) * j[index])
    A = np.diag(bj)
    for index in range(1, M):
        A[index, index - 1] = aj[index]
        A[index, index + 1] = cj[index]
    opcion_precios = np.zeros((M + 1, N + 1))
    # Condición final: payoff al vencimiento
    if tipo == "C":
        opcion_precios[:, -1] = np.maximum(S_vec - K, 0)
    elif tipo == "P":
        opcion_precios[:, -1] = np.maximum(K - S_vec, 0)
    else:
        raise ValueError("tipo debe ser 'C' (call) o 'P' (put).")

    # Condiciones de frontera en S=0 y S->inf
    if tipo == "C":
        opcion_precios[0, :] = 0
        opcion_precios[-1, :] = S_vec[-1]*np.exp(-div*np.flip(t_vec)) - K * np.exp(-r*np.flip(t_vec))
    elif tipo == "P":
        opcion_precios[0, :] = K * np.exp(-r * np.flip(t_vec))
        opcion_precios[-1, :] = 0
    # Corrección de bordes para la matriz tridiagonal
    offsetConstants = np.array((aj[0], cj[-1]))
    B = np.linalg.inv(A)
    for i in reversed(range(N)):
        temp = opcion_precios
        temp[:, i] = B @ temp[:, i + 1]
        temp[[1, M - 1], i] = temp[[1, M - 1], i] + offsetConstants * temp[[0, M], i + 1]
        if tipo == "C":
            opcion_precios[:, i] = np.maximum(temp[:, i], (S_vec - K))
        elif tipo == "P":
            opcion_precios[:, i] = np.maximum(temp[:, i], (K - S_vec))
    f = interp1d(S_vec, opcion_precios[:, 0])
    return float(f(S))
