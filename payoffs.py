# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 21:06:03 2021

@author: manue
"""

import numpy as np
from matplotlib import pyplot as plt

def payoff_call(S,K):
    return np.maximum(S-K,0)

def payoff_put(S,K):
    return np.maximum(K-S,0)

def payoff_forwardSintetico(S,K):
    return payoff_call(S,K) - payoff_put(S, K)

def payoff_combo(S,K1,K2):
    return payoff_call(S,K2) - payoff_put(S, K1)




#Spreads

def payoff_BullCS(S,K1,K2):
    return payoff_call(S,K1) - payoff_call(S, K2)
def payoff_BearCS(S,K1,K2):
    return payoff_call(S,K2) - payoff_call(S, K1)


def payoff_BullPS(S,K1,K2):
    return payoff_put(S,K1) - payoff_put(S, K2)

def payoff_BearPS(S,K1,K2):
    return payoff_put(S,K2) - payoff_put(S, K1)

#Butterflies




def payoff_CButterflyS(S,K1,K2,K3):
    return payoff_call(S,K1) - 2*payoff_call(S, K2) + payoff_call(S, K3)

def payoff_PButterflyS(S,K1,K2,K3):
    return payoff_put(S,K1) - 2*payoff_put(S, K2) + payoff_put(S, K3)

#Volatility strategies

def payoff_straddle(S,K):
    return payoff_call(S,K) + payoff_put(S, K)

def payoff_strangle(S,K1,K2):
    return payoff_call(S,K1) + payoff_put(S, K2)
