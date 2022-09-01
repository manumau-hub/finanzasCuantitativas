# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 22:02:29 2021

@author: manue
"""

import math
import numpy as np

import sys
sys.path.append('..')

from Codigo.opcion_europea_bin import opcion_europea_bin
from Codigo.opcion_europea_bin_c import opcion_europea_bin_c
from Codigo.opcion_americana_bin import opcion_americana_bin
from Codigo.opcion_europea_bs import opcion_europea_bs

#Ejemplo de algoritmo de biseccion

#Uso este algoritmo de biseccion en el codigo futuro

def samesign(a, b):
    return a * b > 0

def bisect(func, low, high, iters=100):
    'Find root of continuous function where f(low) and f(high) have opposite signs'

    assert not samesign(func(low), func(high))

    for i in range(iters):
        midpoint = (low + high) / 2.0
        if samesign(func(low), func(midpoint)):
            low = midpoint
        else:
            high = midpoint

    return midpoint

# Defino la funcion de volatilidad implicita. Busco el cero de la funcion O_T-O_M (opcion teorica menos opcion mercado)
def impvolfunc_bs(tipo, S, K, T, r, precio_mercado, div):
    
    
    func = lambda sigma: (opcion_europea_bs(tipo, S, K, T, r, sigma, div) - precio_mercado)

    impvol = bisect(func,0.0001, 6, 100)
    return impvol


def impvolfunc_bin(tipo, S, K, T, r, precio_mercado, div, pasos = 1000):
    func = lambda sigma: (opcion_americana_bin(tipo, S, K, T, r, sigma, div, pasos) - precio_mercado)
    
    impvol = bisect(func,0.0001, 6, 100)
    return impvol


def print_res(tipo, impvol_bin, impvol_bs):
    print(f'Vol Imp Opcion tipo {tipo} '
          f'Modelo Bin {round(impvol_bin, 4)} '
          f'Modelo BS {round(impvol_bs, 4)}')


def main():
    tipo = 'C'
    impvol_c_bin = impvolfunc_bin(tipo, 100, 200, 1, 0.03, 50, 0.01, pasos=100)
    impvol_c_bs = impvolfunc_bs(tipo, 100, 200, 1, 0.03, 50, 0.01)

    print_res(tipo, impvol_bin=impvol_c_bin, impvol_bs=impvol_c_bs)

    tipo = 'P'
    impvol_p_bin = impvolfunc_bin(tipo, 100, 80, 1, 0.03, 50, 0.01, pasos=100)
    impvol_p_bs = impvolfunc_bs(tipo, 100, 80, 1, 0.03, 50, 0.01)

    print_res(tipo, impvol_bin=impvol_p_bin, impvol_bs=impvol_p_bs)
    
if __name__ == '__main__':
    main()
