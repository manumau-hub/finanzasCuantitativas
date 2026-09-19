

# =============================================================================
# stub for pricing calculation test
# =============================================================================

import sys
sys.path.append('..')
from pricingmodel import PricingModel, PricingArguments
import numpy as np
import matplotlib.pyplot as plt





"""Europens"""

args=PricingArguments(
                    putCall =PricingArguments.OptionType.CALL,
                    underlyingPrice =45,
                    strike =50,
                    riskFreeRate =0.03,
                    dividendRate =0.06,
                    timeToExpiry =1,
                    volatility =0.2,
                    QLStartDate='2019-04-04',
                    QLEndDate='2020-04-04',
                    nIterations=5000,
                    )

model_obj_BS = PricingModel.model_factory('BlackScholes')
model_obj_LR = PricingModel.model_factory('LR')
model_obj_CRR = PricingModel.model_factory('CRR')
model_obj_QL_Eur = PricingModel.model_factory('QL_Eur')
model_obj_QL_Ame = PricingModel.model_factory('QL_Ame')
model_obj_Tri = PricingModel.model_factory('Trinomial')

print("\nEuropean Calls")

print("Call BS: ",model_obj_BS.get_calc(args, 'Premium'))

print("Call QL_eur: ", model_obj_QL_Eur.get_calc(args, 'Premium'))

print("\nAmerican Calls")

print("Call CRR: ",model_obj_CRR.get_calc(args, 'Premium'))

print("Call LR: ",model_obj_LR.get_calc(args, 'Premium'))

print("Call Tri: ", model_obj_Tri.get_calc(args, 'Premium'))

print("Call QL_ame: ", model_obj_QL_Ame.get_calc(args, 'Premium'))

print("\n\nEuropean Puts")

args.putCall=PricingArguments.OptionType.PUT

print("Put BS: ",model_obj_BS.get_calc(args, 'Premium'))

print("Put QL_eur: ", model_obj_QL_Eur.get_calc(args, 'Premium'))

print("\nAmerican Puts")

print("Put CRR: ",model_obj_CRR.get_calc(args, 'Premium'))

print("Put LR: ",model_obj_LR.get_calc(args, 'Premium'))

print("Put Tri: ", model_obj_Tri.get_calc(args, 'Premium'))

print("Put QL_ame: ", model_obj_QL_Ame.get_calc(args, 'Premium'))




