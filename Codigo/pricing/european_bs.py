import math
from scipy.stats import norm


def opcion_europea_bs(tipo, S, K, T, r, sigma, div):
    """
    Calcula el precio de una opción europea (call o put) usando la fórmula de Black-Scholes.

    Parámetros:
        tipo (str): Tipo de opción, "C" para call o "P" para put.
        S (float): Precio actual del activo subyacente.
        K (float): Precio de ejercicio de la opción.
        T (float): Tiempo hasta el vencimiento en años.
        r (float): Tasa de interés libre de riesgo (anualizada).
        sigma (float): Volatilidad del activo subyacente (desviación estándar anualizada).
        div (float): Tasa de dividendos continuos (anualizada).

    Retorna:
        float: Precio teórico de la opción europea.
    """
    # Validación de inputs para evitar división por cero
    if sigma <= 0 or T <= 0:
        raise ValueError("sigma y T deben ser positivos.")

    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r - div + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    if tipo == "C":
        precio_BS = math.exp(-div * T) * S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif tipo == "P":
        precio_BS = K * math.exp(-r * T) * norm.cdf(-d2) - math.exp(-div * T) * S * norm.cdf(-d1)
    else:
        raise ValueError("El tipo de opción debe ser 'C' (call) o 'P' (put).")
    return precio_BS
