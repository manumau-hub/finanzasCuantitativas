import numpy as np


def opcion_europea_mc(tipo, S, K, T, r, sigma, div, pasos):
    """Calcula el precio de una opción europea usando Monte Carlo."""
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    z = np.random.normal(0, 1, pasos)
    ST = S * np.exp((r - div - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * z)
    if tipo == "C":
        payoff = np.maximum(0, ST - K)
    elif tipo == "P":
        payoff = np.maximum(0, K - ST)
    else:
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put)")
    opcion = np.exp(-r * T) * payoff
    return np.mean(opcion)


def opcion_europea_mc_fv(tipo, S, K, T, r, sigma, div, pasos):
    """
    Monte Carlo con reducción de varianza (antithetic variates).
    Usa pares (z, -z) para reducir la varianza del estimador.
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1.")

    z = np.random.normal(0, 1, pasos)
    # Coeficientes del log-normal: ST = S * exp(A + B*z)
    B = sigma * np.sqrt(T)
    A = (r - div - 0.5 * sigma**2) * T
    B_z = B * z
    if tipo == "C":
        payoff1 = np.maximum(0, S * np.exp(A + B_z) - K)
        payoff2 = np.maximum(0, S * np.exp(A - B_z) - K)
    elif tipo == "P":
        payoff1 = np.maximum(0, K - S * np.exp(A + B_z))
        payoff2 = np.maximum(0, K - S * np.exp(A - B_z))
    else:
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")
    payoff = 0.5 * (payoff1 + payoff2)
    return np.mean(np.exp(-r * T) * payoff)
