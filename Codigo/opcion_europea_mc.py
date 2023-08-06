import numpy as np
import math

"""
opcion_europea_mc
Def
    Calculador del precio de una opcion Europea con el modelo de MonteCarlo
Inputs
    - tipo : string - Tipo de contrato entre ["CALL","PUT"]
    - S : float - Spot price del activo
    - K : float - Strike price del contrato
    - T : float - Tiempo hasta la expiracion (en años)
    - r : float - Tasa 'libre de riesgo' (anualizada)
    - sigma : float - Volatilidad implicita (anualizada)
    - div : float - Tasa de dividendos continuos (anualizada)
    - pasos : int - Cantidad de caminos de montecarlo
Outputs
    - precio_MC: float - Precio del contrato
"""

def opcion_europea_mc(tipo, S, K, T, r, sigma, div, pasos):

    z = np.random.normal(0,1,pasos)
    opcion = np.zeros(pasos)
    for i in range(0,pasos):
        if tipo == "C":
            payoff = max( 0 , S * math.exp((r-div - 0.5 * math.pow(sigma,2)) * T + sigma * math.sqrt(T)  * z[i]) - K)
        elif tipo == "P":
            payoff = max(0, K - S * math.exp((r-div - 0.5 * math.pow(sigma, 2)) * T + sigma * math.sqrt(T) * z[i]) )

        opcion[i] = math.exp(-r * T) * payoff

    precio_MC = np.mean(opcion)

    var= np.var(opcion)

    #print('var ', var)

    return precio_MC


def opcion_europea_mc_fv(tipo, S, K, T, r, sigma, div, pasos):
    """ 
        Reducci'on de varianza
                   https://en.wikipedia.org/wiki/Antithetic_variates

        y aceleración
    """

    z = np.random.normal(0,1,pasos)

    opcion = np.zeros(pasos)
    B = sigma * math.sqrt(T)
    A = (r-div - 0.5 * math.pow(sigma,2)) * T
    B_z = B * z
    if tipo == "C":
        payoff1 = np.maximum( 0 , S * np.exp( A + B_z) - K)
        payoff2 = np.maximum( 0 , S * np.exp(A - B_z) - K)
    elif tipo == "P":
        payoff1 = np.maximum(0, K - S * np.exp(A + B_z) )
        payoff2 = np.maximum(0, K - S * np.exp(A - B_z) )
    payoff = .5 * (payoff1+ payoff2)

    opcion = math.exp(-r * T) * payoff

    precio_MC = np.mean(opcion)

    var= np.var(opcion)

    print('var ', var)

    return precio_MC
