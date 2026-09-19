import numpy as np


def opcion_europea_fd(tipo, S, K, T, r, sigma, div, M=150):
    """
    Calcula el precio de una opción europea usando diferencias finitas implícitas.
    Esquema implícito: resuelve A @ V_{t} = V_{t+dt} hacia atrás en el tiempo.
    """
    if T <= 0 or M < 2:
        raise ValueError("T debe ser positivo y M >= 2.")

    # Criterio de estabilidad: N >= S*M/(3*T) para el esquema implícito
    N = max(int(np.ceil(S * M / (3 * T))), 1)
    dt = T / N
    S_vec = np.linspace(0, 2 * S, M + 1)
    t_vec = np.linspace(0, T, N + 1)
    j = np.arange(M + 1)
    sigma2 = sigma ** 2
    aj = np.zeros(M + 1)
    bj = np.ones(M + 1)
    cj = np.zeros(M + 1)
    aj[1:M] = -0.5 * dt * (sigma2 * j[1:M]**2 - (r - div) * j[1:M])
    bj[1:M] = 1 + dt * (sigma2 * j[1:M]**2 + r)
    cj[1:M] = -0.5 * dt * (sigma2 * j[1:M]**2 + (r - div) * j[1:M])
    # Matriz tridiagonal: subdiag aj[1..M], diag bj, superdiag cj[0..M-1]
    A = np.diag(bj)
    A += np.diag(aj[1:M+1], k=-1)
    A += np.diag(cj[0:M], k=1)
    opcion_precios = np.zeros((M + 1, N + 1))
    if tipo == "C":
        opcion_precios[:, -1] = np.maximum(S_vec - K, 0)
    elif tipo == "P":
        opcion_precios[:, -1] = np.maximum(K - S_vec, 0)
    else:
        raise ValueError("tipo debe ser 'C' (call) o 'P' (put)")
    # Condiciones de frontera en S=0 y S->inf
    if tipo == "C":
        opcion_precios[0, :] = 0
        opcion_precios[-1, :] = S_vec[-1] * np.exp(-div * (T - t_vec)) - K * np.exp(-r * (T - t_vec))
    else:
        opcion_precios[0, :] = K * np.exp(-r * (T - t_vec))
        opcion_precios[-1, :] = 0

    A_inv = np.linalg.inv(A)
    for i in reversed(range(N)):
        opcion_precios[:, i] = A_inv @ opcion_precios[:, i + 1]
    return float(np.interp(S, S_vec, opcion_precios[:, 0]))
