import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('../')

from Codigo.opcion_europea_bs import opcion_europea_bs

if __name__ == '__main__':
    start = 40
    stop = 160
    N = stop - start
    SS = np.linspace(start, stop, N)
    c_s = np.array([opcion_europea_bs(tipo='C', S=S, K=100, T=1, r=.01, sigma=.1, div=.0) 
                                                        for S in SS])

    Delta = np.diff(c_s)
    Delta2 = np.diff(Delta)
    max_delta = Delta2.max()

    plt.plot(SS[1:], Delta)
    plt.plot(SS[2:], Delta2/max_delta)
    plt.show()

    print(max_delta, Delta[np.argmax(Delta2)])

