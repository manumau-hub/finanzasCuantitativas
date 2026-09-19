import numpy as np
from scipy.interpolate import interp1d

"""
opcion_europea_fd
Def
    Calculador del precio de una opcion Europea con el modelo de Diferencias Finitas (metodo implícito)
Inputs
    - tipo : string - Tipo de contrato entre ["CALL","PUT"]
    - S : float - Spot price del activo
    - K : float - Strike price del contrato
    - T : float - Tiempo hasta la expiracion (en años)
    - r : float - Tasa 'libre de riesgo' (anualizada)
    - sigma : float - Volatilidad implicita (anualizada)
    - div : float - Tasa de dividendos continuos (anualizada)
Outputs
    - precio_FD: float - Precio del contrato
"""


def opcion_europea_fd(tipo, S, K, T, r, sigma, div, M=150):



    #Hadrcode de la grilla de diferencias finitas
    #M = 160
    #N = 1600
    # PAra que se cumpla N>(TM^2)/(2S^2)
    N = int(np.ceil(S*M/(3*T)))

    #print(N)

    dS = 2 * S / M
    dt = T / N

    # Grilla de spots y tiempos
    S_vec = np.linspace(0, 2*S, M+1)
    t_vec = np.linspace(0, T, N+1)

    # Armado de la matriz tridiagonal
    j = np.arange(0,M+1)
    j2 = np.zeros(M+1)
    aj = np.zeros(M+1)
    bj = np.zeros(M+1)
    cj = np.zeros(M+1)

    sigma2 = sigma*sigma
    for index in range(0,M+1):
        if index == 0:
            bj[index] = 1
        elif index == M:
            bj[index] = 1
        else:
           j2[index] = j[index] * j[index]
           aj[index] = - 0.5 * dt * (sigma2 * j2[index]- (r-div) * j[index])
           bj[index] = 1 + dt * (sigma2 * j2[index] + r)
           cj[index] = - 0.5 * dt * (sigma2 * j2[index] + (r-div) * j[index])

    # Matriz tridiagonal

    A = np.diag(bj)
    for index in range(1, M):
        A[index, index - 1] = aj[index]  # terms below the diagonal
        A[index, index + 1] = cj[index]  # terms above the diagonal

    # Matriz de precios de la opcion
    opcion_precios = np.zeros((M+1,N+1))

    #Condiciones de contorno

    # Condicion final - Payoff

    if tipo == "C":
        opcion_precios[:,-1] = np.maximum(S_vec - K, 0)
    elif tipo == "P":
        opcion_precios[:,-1] = np.maximum(K - S_vec, 0)

    # Casos limite en S=0 y S~inf

    if tipo == "C":
        opcion_precios[0, :] = 0
        opcion_precios[-1, :] = S_vec[-1]*np.exp(-div*np.flip(t_vec)) - K * np.exp(-r*np.flip(t_vec))
    elif tipo == "P":
        opcion_precios[0, :] = K * np.exp(-r * np.flip(t_vec))
        opcion_precios[-1, :] = 0 #K * np.exp(-r * np.flip(t_vec))

    # Calculo in el interior
    # variable auxiliar para sumar en la primer y ultimo fila
    offsetConstants = np.array((aj[0], cj[-1]))
    B = np.linalg.inv(A)
    for i in list(reversed(range(0,N))):
        opcion_precios[:,i] = B @ opcion_precios[:,i+1]

        #Offset the first and last terms
        opcion_precios[[1,M-1],i] = opcion_precios[[1,M-1],i] + offsetConstants * opcion_precios[[0, M],i+1];

    #En este punto ya esta TODA la grilla, ahora calculo lo requerido

    f = interp1d(S_vec,opcion_precios[:,0])
    precio_FD = float(f(S))

    return precio_FD
