# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:39:03 2019

@author: dpedroso
"""

import sys
sys.path.append('..')

from DataBaseAccess import DatabaseAccess
from Dividend_calculation_methods import constant
from implied_vol_calculator import ImpliedVolatilityCalculator
from volatility_surface import gaussian_smooth
import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# # variables definition:
# =============================================================================
ticker = 'AAPL' # security to evaluate
date = '2019-04-04' #evaluation date

# initiating database access 
print("****************************** \n Initiate database connection \n ******************************")
db_vendor = DatabaseAccess.createInstanceOfDatabaseAccess('Vendor', server ='PROD-VNDR-DB',
                                                          database = 'IvyDBUS',
                                                          username = 'tqa_user',
                                                          password = 'tqa_user')

# testing database connection
print("****************************** \n testing connection... \n ******************************")
securityID = db_vendor.getSecurityIDFromTicker(ticker) # getting secutiry ID
print ("For ticker "+ticker+" securityID is: "+securityID)

print("****************************** \n Dividend calculation... \n ******************************")
# initiate dividend calculation methods:

div_method = constant()

div_list = db_vendor.pullDividendListFromTicker(securityID, date)
# ...and calculate the distribution yield
spot=db_vendor.getUnderlyingSpotPriceFromSecurityID(securityID, date)
dividend_yield = div_method.get_dividend_yield(securityID, 
                                                date,
                                                 args_dict={'dividend_list' : div_list,
                                                                           'spot' : spot})

                                                                                       # dividend calculation


print("****************************** \n Zero coupon rate \n ******************************")
# get zero rate curve
ZC_curve = db_vendor.pullZCurve(date)
#ZC_curve['TTM']=ZC_curve['Days']/daycount
print(ZC_curve.columns)
print(ZC_curve.head())

print("****************************** \n Security price list \n ******************************")
# get price list
price_list = db_vendor.pullOptionPricesTable(securityID, date)

print("****************************** \n Implied volatility \n ******************************")


root_finder_max_iter = 50
pricing_model_max_iter = 500
min_ttm =0


root_finder_method_1 = 'bisection' #'ridder'#'toms748'#'brent'#, 'bisection' #'newton', 'jakel'
root_finder_method_2 = 'jakel' #'ridder'#'toms748'#'brent'#, 'bisection' #'newton', 'jakel'

model_1='CRR'
model_2='LR'
model_3='QL_Eur'
model_4='QL_Ame'
model_5='Trinomial'
model_6='BlackScholes'

""" 1 1"""
iVol_obj_11 = ImpliedVolatilityCalculator(root_finder_method_1,
                                          model_1,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_11 = iVol_obj_11.calculateImpliedVol()


""" 1 2"""
iVol_obj_12 = ImpliedVolatilityCalculator(root_finder_method_1,
                                          model_2,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_12 = iVol_obj_12.calculateImpliedVol()

#""" 1 3"""
#
#iVol_obj_13 = ImpliedVolatilityCalculator(root_finder_method_1,
#                                   model_3,
#                                   ZC_curve, 
#                                   dividend_yield, 
#                                   price_list, 
#                                   date, 
#                                   min_ttm,
#                                   root_finder_max_iter,
#                                   pricing_model_max_iter)
#model_13 = iVol_obj_13.calculateImpliedVol()
#
#""" 1 4"""
#iVol_obj_14 = ImpliedVolatilityCalculator(root_finder_method_1,
#                                   model_4,
#                                   ZC_curve, 
#                                   dividend_yield, 
#                                   price_list, 
#                                   date, 
#                                   min_ttm,
#                                   root_finder_max_iter,
#                                   pricing_model_max_iter)
#model_14 = iVol_obj_14.calculateImpliedVol()

""" 1 5"""
iVol_obj_15 = ImpliedVolatilityCalculator(root_finder_method_1,
                                          model_5,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_15 = iVol_obj_15.calculateImpliedVol()

""" 1 6"""
iVol_obj_16 = ImpliedVolatilityCalculator(root_finder_method_1,
                                          model_6,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_16 = iVol_obj_16.calculateImpliedVol()

""" 2 1"""
iVol_obj_21 = ImpliedVolatilityCalculator(root_finder_method_2,
                                          model_1,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_21 = iVol_obj_21.calculateImpliedVol()


""" 2 2"""
iVol_obj_22 = ImpliedVolatilityCalculator(root_finder_method_2,
                                          model_2,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_22 = iVol_obj_22.calculateImpliedVol()
#
#""" 2 3"""
#
#iVol_obj_23 = ImpliedVolatilityCalculator(root_finder_method_2,
#                                   model_3,
#                                   ZC_curve, 
#                                   dividend_yield, 
#                                   price_list, 
#                                   date, 
#                                   min_ttm,
#                                   root_finder_max_iter,
#                                   pricing_model_max_iter)
#model_23 = iVol_obj_23.calculateImpliedVol()
#
#""" 2 4"""
#iVol_obj_24 = ImpliedVolatilityCalculator(root_finder_method_2,
#                                   model_4,
#                                   ZC_curve, 
#                                   dividend_yield, 
#                                   price_list, 
#                                   date, 
#                                   min_ttm,
#                                   root_finder_max_iter,
#                                   pricing_model_max_iter)
#model_24 = iVol_obj_24.calculateImpliedVol()

""" 2 5"""
iVol_obj_25 = ImpliedVolatilityCalculator(root_finder_method_2,
                                          model_5,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_25 = iVol_obj_25.calculateImpliedVol()

""" 2 6"""
iVol_obj_26 = ImpliedVolatilityCalculator(root_finder_method_2,
                                          model_6,
                                          ZC_curve,
                                          dividend_yield,
                                          price_list,
                                          date,
                                          min_ttm,
                                          root_finder_max_iter,
                                          pricing_model_max_iter)
model_26 = iVol_obj_26.calculateImpliedVol()

vs_11 = gaussian_smooth()
vs_12 = gaussian_smooth()
vs_15 = gaussian_smooth()
vs_16 = gaussian_smooth()

vs_21 = gaussian_smooth()
vs_22 = gaussian_smooth()
vs_25 = gaussian_smooth()
vs_26 = gaussian_smooth()

vol_surface_11 = vs_11.generate_volatility_surface(model_11)
vol_surface_12 = vs_12.generate_volatility_surface(model_12)
vol_surface_15 = vs_15.generate_volatility_surface(model_15)
vol_surface_16 = vs_16.generate_volatility_surface(model_16)

vol_surface_21 = vs_21.generate_volatility_surface(model_21)
vol_surface_22 = vs_22.generate_volatility_surface(model_22)
vol_surface_25 = vs_25.generate_volatility_surface(model_25)
vol_surface_26 = vs_26.generate_volatility_surface(model_26)


vol_surface_vendor = db_vendor.pullVolatilitySurfaceOfSecurityID(securityID, date)
